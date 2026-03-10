import json
import os
from pathlib import Path
from PIL import Image

animation_counter = 0
render_controllers = {}
existing_configs = {}
texture_to_animation_info = {}  # Map texture path -> (controller_name, anim_name, frame_count)

def create_2d_geometry():
    """Tạo geometry file cho 2D animated items"""
    geometry_dir = Path("staging/target/rp/models/entity")
    geometry_dir.mkdir(parents=True, exist_ok=True)
    
    geometry_file = geometry_dir / "plaiiqhdbbbcassyay.geo.json"
    
    # Kiểm tra nếu file đã tồn tại thì không tạo lại
    if geometry_file.exists():
        return
    
    geometry_data = {"format_version":"1.12.0","minecraft:geometry":[{"description":{"identifier":"geometry.plaiiqhdbbbcassyay","texture_width":32,"texture_height":16,"visible_bounds_width":2,"visible_bounds_height":3.5,"visible_bounds_offset":[0,1.25,0]},"bones":[{"name":"camfire_item","pivot":[0,0,0]},{"name":"bone17","parent":"camfire_item","pivot":[-7,8,0],"cubes":[{"origin":[-8,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[0,15],"uv_size":[1,1]},"east":{"uv":[0,15],"uv_size":[1,1]},"south":{"uv":[0,15],"uv_size":[1,1]},"west":{"uv":[0,15],"uv_size":[1,1]},"up":{"uv":[0,15],"uv_size":[1,1]},"down":{"uv":[0,16],"uv_size":[1,-1]}}},{"origin":[-7.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[1,15],"uv_size":[1,1]},"east":{"uv":[1,15],"uv_size":[1,1]},"south":{"uv":[1,15],"uv_size":[1,1]},"west":{"uv":[1,15],"uv_size":[1,1]},"up":{"uv":[1,15],"uv_size":[1,1]},"down":{"uv":[1,16],"uv_size":[1,-1]}}},{"origin":[-7,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[2,15],"uv_size":[1,1]},"east":{"uv":[2,15],"uv_size":[1,1]},"south":{"uv":[2,15],"uv_size":[1,1]},"west":{"uv":[2,15],"uv_size":[1,1]},"up":{"uv":[2,15],"uv_size":[1,1]},"down":{"uv":[2,16],"uv_size":[1,-1]}}},{"origin":[-6.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[3,15],"uv_size":[1,1]},"east":{"uv":[3,15],"uv_size":[1,1]},"south":{"uv":[3,15],"uv_size":[1,1]},"west":{"uv":[3,15],"uv_size":[1,1]},"up":{"uv":[3,15],"uv_size":[1,1]},"down":{"uv":[3,16],"uv_size":[1,-1]}}},{"origin":[-6,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[4,15],"uv_size":[1,1]},"east":{"uv":[4,15],"uv_size":[1,1]},"south":{"uv":[4,15],"uv_size":[1,1]},"west":{"uv":[4,15],"uv_size":[1,1]},"up":{"uv":[4,15],"uv_size":[1,1]},"down":{"uv":[4,16],"uv_size":[1,-1]}}},{"origin":[-5.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[5,15],"uv_size":[1,1]},"east":{"uv":[5,15],"uv_size":[1,1]},"south":{"uv":[5,15],"uv_size":[1,1]},"west":{"uv":[5,15],"uv_size":[1,1]},"up":{"uv":[5,15],"uv_size":[1,1]},"down":{"uv":[5,16],"uv_size":[1,-1]}}},{"origin":[-5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[6,15],"uv_size":[1,1]},"east":{"uv":[6,15],"uv_size":[1,1]},"south":{"uv":[6,15],"uv_size":[1,1]},"west":{"uv":[6,15],"uv_size":[1,1]},"up":{"uv":[6,15],"uv_size":[1,1]},"down":{"uv":[6,16],"uv_size":[1,-1]}}},{"origin":[-4.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[7,15],"uv_size":[1,1]},"east":{"uv":[7,15],"uv_size":[1,1]},"south":{"uv":[7,15],"uv_size":[1,1]},"west":{"uv":[7,15],"uv_size":[1,1]},"up":{"uv":[7,15],"uv_size":[1,1]},"down":{"uv":[7,16],"uv_size":[1,-1]}}},{"origin":[-4,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[8,15],"uv_size":[1,1]},"east":{"uv":[8,15],"uv_size":[1,1]},"south":{"uv":[8,15],"uv_size":[1,1]},"west":{"uv":[8,15],"uv_size":[1,1]},"up":{"uv":[8,15],"uv_size":[1,1]},"down":{"uv":[8,16],"uv_size":[1,-1]}}},{"origin":[-3.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[9,15],"uv_size":[1,1]},"east":{"uv":[9,15],"uv_size":[1,1]},"south":{"uv":[9,15],"uv_size":[1,1]},"west":{"uv":[9,15],"uv_size":[1,1]},"up":{"uv":[9,15],"uv_size":[1,1]},"down":{"uv":[9,16],"uv_size":[1,-1]}}},{"origin":[-3,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[10,15],"uv_size":[1,1]},"east":{"uv":[10,15],"uv_size":[1,1]},"south":{"uv":[10,15],"uv_size":[1,1]},"west":{"uv":[10,15],"uv_size":[1,1]},"up":{"uv":[10,15],"uv_size":[1,1]},"down":{"uv":[10,16],"uv_size":[1,-1]}}},{"origin":[-2.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[11,15],"uv_size":[1,1]},"east":{"uv":[11,15],"uv_size":[1,1]},"south":{"uv":[11,15],"uv_size":[1,1]},"west":{"uv":[11,15],"uv_size":[1,1]},"up":{"uv":[11,15],"uv_size":[1,1]},"down":{"uv":[11,16],"uv_size":[1,-1]}}},{"origin":[-2,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[12,15],"uv_size":[1,1]},"east":{"uv":[12,15],"uv_size":[1,1]},"south":{"uv":[12,15],"uv_size":[1,1]},"west":{"uv":[12,15],"uv_size":[1,1]},"up":{"uv":[12,15],"uv_size":[1,1]},"down":{"uv":[12,16],"uv_size":[1,-1]}}},{"origin":[-1.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[13,15],"uv_size":[1,1]},"east":{"uv":[13,15],"uv_size":[1,1]},"south":{"uv":[13,15],"uv_size":[1,1]},"west":{"uv":[13,15],"uv_size":[1,1]},"up":{"uv":[13,15],"uv_size":[1,1]},"down":{"uv":[13,16],"uv_size":[1,-1]}}},{"origin":[-1,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[14,15],"uv_size":[1,1]},"east":{"uv":[14,15],"uv_size":[1,1]},"south":{"uv":[14,15],"uv_size":[1,1]},"west":{"uv":[14,15],"uv_size":[1,1]},"up":{"uv":[14,15],"uv_size":[1,1]},"down":{"uv":[14,16],"uv_size":[1,-1]}}},{"origin":[-0.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[15,15],"uv_size":[1,1]},"east":{"uv":[15,15],"uv_size":[1,1]},"south":{"uv":[15,15],"uv_size":[1,1]},"west":{"uv":[15,15],"uv_size":[1,1]},"up":{"uv":[15,15],"uv_size":[1,1]},"down":{"uv":[15,16],"uv_size":[1,-1]}}},{"origin":[0,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[16,15],"uv_size":[1,1]},"east":{"uv":[16,15],"uv_size":[1,1]},"south":{"uv":[16,15],"uv_size":[1,1]},"west":{"uv":[16,15],"uv_size":[1,1]},"up":{"uv":[16,15],"uv_size":[1,1]},"down":{"uv":[16,16],"uv_size":[1,-1]}}},{"origin":[0.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[17,15],"uv_size":[1,1]},"east":{"uv":[17,15],"uv_size":[1,1]},"south":{"uv":[17,15],"uv_size":[1,1]},"west":{"uv":[17,15],"uv_size":[1,1]},"up":{"uv":[17,15],"uv_size":[1,1]},"down":{"uv":[17,16],"uv_size":[1,-1]}}},{"origin":[1,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[18,15],"uv_size":[1,1]},"east":{"uv":[18,15],"uv_size":[1,1]},"south":{"uv":[18,15],"uv_size":[1,1]},"west":{"uv":[18,15],"uv_size":[1,1]},"up":{"uv":[18,15],"uv_size":[1,1]},"down":{"uv":[18,16],"uv_size":[1,-1]}}},{"origin":[1.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[19,15],"uv_size":[1,1]},"east":{"uv":[19,15],"uv_size":[1,1]},"south":{"uv":[19,15],"uv_size":[1,1]},"west":{"uv":[19,15],"uv_size":[1,1]},"up":{"uv":[19,15],"uv_size":[1,1]},"down":{"uv":[19,16],"uv_size":[1,-1]}}},{"origin":[2,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[20,15],"uv_size":[1,1]},"east":{"uv":[20,15],"uv_size":[1,1]},"south":{"uv":[20,15],"uv_size":[1,1]},"west":{"uv":[20,15],"uv_size":[1,1]},"up":{"uv":[20,15],"uv_size":[1,1]},"down":{"uv":[20,16],"uv_size":[1,-1]}}},{"origin":[2.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[21,15],"uv_size":[1,1]},"east":{"uv":[21,15],"uv_size":[1,1]},"south":{"uv":[21,15],"uv_size":[1,1]},"west":{"uv":[21,15],"uv_size":[1,1]},"up":{"uv":[21,15],"uv_size":[1,1]},"down":{"uv":[21,16],"uv_size":[1,-1]}}},{"origin":[3,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[22,15],"uv_size":[1,1]},"east":{"uv":[22,15],"uv_size":[1,1]},"south":{"uv":[22,15],"uv_size":[1,1]},"west":{"uv":[22,15],"uv_size":[1,1]},"up":{"uv":[22,15],"uv_size":[1,1]},"down":{"uv":[22,16],"uv_size":[1,-1]}}},{"origin":[3.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[23,15],"uv_size":[1,1]},"east":{"uv":[23,15],"uv_size":[1,1]},"south":{"uv":[23,15],"uv_size":[1,1]},"west":{"uv":[23,15],"uv_size":[1,1]},"up":{"uv":[23,15],"uv_size":[1,1]},"down":{"uv":[23,16],"uv_size":[1,-1]}}},{"origin":[4,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[24,15],"uv_size":[1,1]},"east":{"uv":[24,15],"uv_size":[1,1]},"south":{"uv":[24,15],"uv_size":[1,1]},"west":{"uv":[24,15],"uv_size":[1,1]},"up":{"uv":[24,15],"uv_size":[1,1]},"down":{"uv":[24,16],"uv_size":[1,-1]}}},{"origin":[4.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[25,15],"uv_size":[1,1]},"east":{"uv":[25,15],"uv_size":[1,1]},"south":{"uv":[25,15],"uv_size":[1,1]},"west":{"uv":[25,15],"uv_size":[1,1]},"up":{"uv":[25,15],"uv_size":[1,1]},"down":{"uv":[25,16],"uv_size":[1,-1]}}},{"origin":[4.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[25,15],"uv_size":[1,1]},"east":{"uv":[25,15],"uv_size":[1,1]},"south":{"uv":[25,15],"uv_size":[1,1]},"west":{"uv":[25,15],"uv_size":[1,1]},"up":{"uv":[25,15],"uv_size":[1,1]},"down":{"uv":[25,16],"uv_size":[1,-1]}}},{"origin":[5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[26,15],"uv_size":[1,1]},"east":{"uv":[26,15],"uv_size":[1,1]},"south":{"uv":[26,15],"uv_size":[1,1]},"west":{"uv":[26,15],"uv_size":[1,1]},"up":{"uv":[26,15],"uv_size":[1,1]},"down":{"uv":[26,16],"uv_size":[1,-1]}}},{"origin":[5.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[27,15],"uv_size":[1,1]},"east":{"uv":[27,15],"uv_size":[1,1]},"south":{"uv":[27,15],"uv_size":[1,1]},"west":{"uv":[27,15],"uv_size":[1,1]},"up":{"uv":[27,15],"uv_size":[1,1]},"down":{"uv":[27,16],"uv_size":[1,-1]}}},{"origin":[6,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[28,15],"uv_size":[1,1]},"east":{"uv":[28,15],"uv_size":[1,1]},"south":{"uv":[28,15],"uv_size":[1,1]},"west":{"uv":[28,15],"uv_size":[1,1]},"up":{"uv":[28,15],"uv_size":[1,1]},"down":{"uv":[28,16],"uv_size":[1,-1]}}},{"origin":[6.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[29,15],"uv_size":[1,1]},"east":{"uv":[29,15],"uv_size":[1,1]},"south":{"uv":[29,15],"uv_size":[1,1]},"west":{"uv":[29,15],"uv_size":[1,1]},"up":{"uv":[29,15],"uv_size":[1,1]},"down":{"uv":[29,16],"uv_size":[1,-1]}}},{"origin":[7,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[30,15],"uv_size":[1,1]},"east":{"uv":[30,15],"uv_size":[1,1]},"south":{"uv":[30,15],"uv_size":[1,1]},"west":{"uv":[30,15],"uv_size":[1,1]},"up":{"uv":[30,15],"uv_size":[1,1]},"down":{"uv":[30,16],"uv_size":[1,-1]}}},{"origin":[7.5,8,-1],"size":[0.5,0.5,1],"uv":{"north":{"uv":[31,15],"uv_size":[1,1]},"east":{"uv":[31,15],"uv_size":[1,1]},"south":{"uv":[31,15],"uv_size":[1,1]},"west":{"uv":[31,15],"uv_size":[1,1]},"up":{"uv":[31,15],"uv_size":[1,1]},"down":{"uv":[31,16],"uv_size":[1,-1]}}}]}]}]}
    
    with open(geometry_file, 'w', encoding='utf-8') as f:
        json.dump(geometry_data, f, ensure_ascii=False)

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

def update_attachables_with_controllers():
    """Cập nhật attachables với render controllers phù hợp"""
    global texture_to_animation_info
    
    attachables_dir = Path("staging/target/rp/attachables")
    if not attachables_dir.exists():
        return
    
    updated_count = 0
    for json_file in attachables_dir.rglob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            attachable = data.get("minecraft:attachable", {})
            description = attachable.get("description", {})
            textures = description.get("textures", {})
            default_texture = textures.get("default", "")
            
            if not default_texture:
                continue
            
            # Kiểm tra xem texture path có trong mapping không
            matched_info = None
            matched_texture_path = None
            for texture_path, animation_info in texture_to_animation_info.items():
                # So sánh cả 2 chiều: texture_path in default_texture HOẶC default_texture endswith texture_path
                # Để xử lý cả trường hợp có prefix khác nhau
                texture_basename = texture_path.split('/')[-1]  # Lấy tên file cuối cùng
                default_basename = default_texture.split('/')[-1]
                
                if texture_basename == default_basename or texture_path in default_texture or default_texture.endswith(texture_path):
                    matched_info = animation_info
                    matched_texture_path = texture_path
                    break
            
            if matched_info:
                controller_name, anim_name, frame_count = matched_info
                
                # Cập nhật render_controllers
                description["render_controllers"] = [controller_name]
                
                # Cập nhật textures - thay "default" bằng các frame textures
                new_textures = {}
                for i in range(frame_count):
                    new_textures[f"{anim_name}_{i}"] = f"textures/{matched_texture_path}/{i}"
                
                # Giữ lại các texture khác (enchanted, etc.)
                for key, value in textures.items():
                    if key != "default":
                        new_textures[key] = value
                
                description["textures"] = new_textures
                
                # Cập nhật geometry - luôn dùng geometry.plaiiqhdbbbcassyay
                description["geometry"] = {anim_name: "geometry.plaiiqhdbbbcassyay"}
                
                # Cập nhật animations
                description["animations"] = {
                    "thirdperson_hand": "animation.campfire.thirdperson_hand",
                    "thirdperson_head": "animation.campfire.thirdperson_head",
                    "firstperson_hand": "animation.campfire.firstperson_hand",
                    "firstperson_head": "animation.campfire.disable"
                }
                
                # Cập nhật scripts
                description["scripts"] = {
                    "initialize": [
                        "v.thirdperson_mainhand_rot_x = 0;",
                        "v.thirdperson_mainhand_rot_y = 0;",
                        "v.thirdperson_mainhand_rot_z = 0;",
                        "v.thirdperson_mainhand_pos_x = 0;",
                        "v.thirdperson_mainhand_pos_y = 1.5;",
                        "v.thirdperson_mainhand_pos_z = 1.25;",
                        "v.thirdperson_mainhand_scale = 0.75;",
                        "v.thirdperson_hand_same = true;",
                        "v.firstperson_mainhand_rot_x = 0;",
                        "v.firstperson_mainhand_rot_y = 0;",
                        "v.firstperson_mainhand_rot_z = 0;",
                        "v.firstperson_mainhand_pos_x = 0.75;",
                        "v.firstperson_mainhand_pos_y = 1.5;",
                        "v.firstperson_mainhand_pos_z = 0.25;",
                        "v.firstperson_mainhand_scale = 0.8;",
                        "v.firstperson_hand_same = true;",
                        "v.thirdperson_head_rot_x = 0;",
                        "v.thirdperson_head_rot_y = 0;",
                        "v.thirdperson_head_rot_z = 0;",
                        "v.thirdperson_head_pos_x = 0;",
                        "v.thirdperson_head_pos_y = 0;",
                        "v.thirdperson_head_pos_z = 0;",
                        "v.thirdperson_head_scale = 0;"
                    ],
                    "pre_animation": [
                        "v.main_hand = c.item_slot=='main_hand';",
                        "v.off_hand = c.item_slot=='off_hand';",
                        "v.head = c.item_slot=='head';"
                    ],
                    "animate": [
                        {"thirdperson_hand": "(v.main_hand||v.off_hand)&&!c.is_first_person"},
                        {"thirdperson_head": "v.head&&!c.is_first_person"},
                        {"firstperson_hand": "(v.main_hand||v.off_hand)&&c.is_first_person"},
                        {"firstperson_head": "c.is_first_person&&v.head"}
                    ]
                }
                
                data["minecraft:attachable"]["description"] = description
                
                # Lưu lại file
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                updated_count += 1
        
        except Exception as e:
            pass
    
    if updated_count > 0:
        pass

def scan_2d_animations():
    global animation_counter
    pack_dir = Path("./pack/assets")
    if not pack_dir.exists():
        return
    
    # Tạo geometry file trước khi xử lý
    create_2d_geometry()
    
    render_controllers_dir = Path("staging/target/rp/render_controllers")
    render_controllers_dir.mkdir(parents=True, exist_ok=True)
    load_existing_render_controllers()
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
            
            for i in range(frame_count):
                frame_img = img.crop((0, i * frame_size, width, (i + 1) * frame_size))
                frame_output_path = frame_dir / f"{i}.png"
                frame_img.save(frame_output_path)
            animation_counter += 1
            anim_name = f"anim_{animation_counter}"
            texture_array = [f"texture.{anim_name}_{i}" for i in range(frame_count)]
            controller_name = f"controller.render.campfire_kaito.{anim_name}"
            render_controllers[controller_name] = {
                "arrays": {
                    "textures": {
                        f"array.anim": texture_array
                    }
                },
                "geometry": f"geometry.{anim_name}",
                "materials": [{"*": "variable.is_enchanted ? material.enchanted : material.default"}],
                "textures": [
                    f"array.anim[math.mod(math.floor(q.life_time * 20 / {frametime}),{frame_count})]",
                    "texture.enchanted"
                ]
            }
            existing_configs[(frametime, frame_count)] = controller_name
            
            # Lưu mapping texture path -> (controller_name, anim_name, frame_count)
            # Texture path trong attachable dạng: "textures/fuben/item/ia_auto/fb_12"
            texture_path_for_attachable = str(relative_texture_path).replace('\\', '/')
            texture_to_animation_info[texture_path_for_attachable] = (controller_name, anim_name, frame_count)
            
            processed += 1
        except Exception as e:
            pass
    
    # Cập nhật attachables với render controllers phù hợp
    if texture_to_animation_info:
        update_attachables_with_controllers()
    
    if render_controllers:
        output_path = Path("staging/target/rp/render_controllers/animations.render_controllers.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_data = {
            "format_version": "1.8.0",
            "render_controllers": render_controllers
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scan_2d_animations()
