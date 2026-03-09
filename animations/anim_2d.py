import json
import os
from pathlib import Path
from PIL import Image

animation_counter = 0
render_controllers = {}
existing_configs = {}

def load_existing_render_controllers():
    global existing_configs
    render_dir = Path("staging/target/rp/render_controllers")
    if not render_dir.exists():
        return
    for json_file in render_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            controllers = data.get("render_controllers", {})
            for controller_name, controller_data in controllers.items():
                textures = controller_data.get("textures", [])
                if not textures:
                    continue
                texture_formula = textures[0]
                if "q.life_time * 20 /" in texture_formula and "math.mod" in texture_formula:
                    try:
                        frametime_part = texture_formula.split("q.life_time * 20 /")[1].split(")")[0].strip()
                        frametime = int(frametime_part)
                        frame_count_part = texture_formula.split(",")[-1].split("]")[0].strip()
                        frame_count = int(frame_count_part)
                        existing_configs[(frametime, frame_count)] = controller_name
                    except:
                        pass
        except:
            pass

def scan_2d_animations():
    global animation_counter
    pack_dir = Path("./pack/assets")
    if not pack_dir.exists():
        print("Không tìm thấy thư mục pack")
        return
    print("Bắt đầu quét animation 2D...")
    render_controllers_dir = Path("staging/target/rp/render_controllers")
    render_controllers_dir.mkdir(parents=True, exist_ok=True)
    load_existing_render_controllers()
    print(f"Tìm thấy {len(existing_configs)} config đã tồn tại")
    processed = 0
    for json_file in pack_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get("parent") != "minecraft:item/generated":
                continue
            textures = data.get("textures", {})
            layer0 = textures.get("layer0", "")
            if not layer0:
                continue
            if ":" not in layer0:
                continue
            namespace, texture_path = layer0.split(":", 1)
            texture_file = pack_dir / namespace / "textures" / f"{texture_path}.png"
            if not texture_file.exists():
                continue
            img = Image.open(texture_file)
            width, height = img.size
            if height <= width:
                continue
            if height % width != 0:
                continue
            frame_count = height // width
            if frame_count <= 1:
                continue
            mcmeta_file = Path(str(texture_file) + ".mcmeta")
            frametime = 1
            if mcmeta_file.exists():
                try:
                    with open(mcmeta_file, 'r', encoding='utf-8') as f:
                        mcmeta_data = json.load(f)
                    animation = mcmeta_data.get("animation", {})
                    frametime = animation.get("frametime", 1)
                except:
                    pass
            if (frametime, frame_count) in existing_configs:
                print(f"Bỏ qua duplicate: frametime={frametime}, frames={frame_count}")
                continue
            
            # Tạo đường dẫn output trong staging/target/rp/textures
            # Lấy relative path từ pack/assets/namespace/textures/
            relative_texture_path = texture_file.relative_to(pack_dir / namespace / "textures")
            # Bỏ extension .png
            relative_texture_path = relative_texture_path.with_suffix('')
            
            # Tạo thư mục output trong staging/target/rp/textures
            frame_dir = Path("staging/target/rp/textures") / relative_texture_path
            frame_dir.mkdir(parents=True, exist_ok=True)
            
            frame_size = width
            print(f"Đang xử lý: {texture_file.name} ({frame_count} frames, frametime={frametime})")
            print(f"  → Lưu vào: {frame_dir}")
            
            for i in range(frame_count):
                frame_img = img.crop((0, i * frame_size, width, (i + 1) * frame_size))
                frame_output_path = frame_dir / f"{i + 1}.png"
                frame_img.save(frame_output_path)
            animation_counter += 1
            anim_name = f"anim_{animation_counter}"
            texture_array = [f"texture.{anim_name}_{i}" for i in range(frame_count)]
            controller_name = f"controller.render.campfire_kaito.{anim_name}"
            render_controllers[controller_name] = {
                "arrays": {
                    "textures": {
                        f"array.{anim_name}": texture_array
                    }
                },
                "geometry": f"geometry.{anim_name}",
                "materials": [{"*": "variable.is_enchanted ? material.enchanted : material.default"}],
                "textures": [
                    f"array.{anim_name}[math.mod(math.floor(q.life_time * 20 / {frametime}),{frame_count})]",
                    "texture.enchanted"
                ]
            }
            existing_configs[(frametime, frame_count)] = controller_name
            processed += 1
        except Exception as e:
            # In lỗi chi tiết để debug
            pass
    print(f"Đã xử lý {processed} animation mới")
    if render_controllers:
        output_path = Path("staging/target/rp/render_controllers/animations.render_controllers.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_data = {
            "format_version": "1.8.0",
            "render_controllers": render_controllers
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"Đã lưu render controllers vào {output_path}")
    else:
        print("Không có animation mới để lưu")

if __name__ == "__main__":
    scan_2d_animations()
