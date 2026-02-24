import os
import random
import string
import glob
import json

def random_name():
    """Tạo tên random 70 ký tự chữ cái in thường và số xen kẽ"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=70))

def random_short_name():
    """Tạo tên random 12 ký tự chữ cái in thường và số"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

def randomize_item_textures():
    """Random tên thư mục và file texture dựa trên item_texture.json"""
    item_texture_path = "staging/target/rp/textures/item_texture.json"
    
    if not os.path.exists(item_texture_path):
        print(f"Không tìm thấy {item_texture_path}")
        return
    
    # Đọc item_texture.json
    with open(item_texture_path, 'r', encoding='utf-8') as f:
        item_texture_data = json.load(f)
    
    texture_data = item_texture_data.get("texture_data", {})
    path_mapping = {}  # Map đường dẫn cũ -> đường dẫn mới
    
    # Bước 1: Random tên trong thư mục textures/ và tạo mapping
    for key, value in texture_data.items():
        texture_path = value.get("textures", "")
        if not texture_path.startswith("textures/"):
            continue
        
        # Tách đường dẫn: textures/evergreenset/key -> ['evergreenset', 'key']
        parts = texture_path.replace("textures/", "").split("/")
        
        # Random tên cho từng phần
        new_parts = []
        current_path = "staging/target/rp/textures"
        
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            new_name = random_short_name()
            new_parts.append(new_name)
            
            if is_last:
                # Phần cuối là tên file
                old_png = os.path.join(current_path, part + ".png")
                if os.path.exists(old_png):
                    new_png = os.path.join(current_path, new_name + ".png")
                    os.rename(old_png, new_png)
            else:
                # Phần giữa là thư mục
                old_dir = os.path.join(current_path, part)
                if os.path.exists(old_dir):
                    new_dir = os.path.join(current_path, new_name)
                    os.rename(old_dir, new_dir)
                    current_path = new_dir
                else:
                    current_path = os.path.join(current_path, new_name)
        
        # Lưu mapping
        old_path = texture_path
        new_path = "textures/" + "/".join(new_parts)
        path_mapping[old_path] = new_path
        
        # Cập nhật trong texture_data
        texture_data[key]["textures"] = new_path
    
    # Bước 2: Cập nhật đường dẫn trong tất cả file JSON của attachables
    attachables_dir = "staging/target/rp/attachables"
    if os.path.exists(attachables_dir):
        for json_file in glob.glob(f"{attachables_dir}/**/*.json", recursive=True):
            with open(json_file, 'r', encoding='utf-8') as jf:
                attachable_data = json.load(jf)
            
            # Kiểm tra và cập nhật đường dẫn texture
            desc = attachable_data.get("minecraft:attachable", {}).get("description", {})
            textures = desc.get("textures", {})
            updated = False
            
            for tex_key, tex_value in textures.items():
                if tex_value:
                    # Kiểm tra xem có đường dẫn nào trong mapping không
                    for old_path, new_path in path_mapping.items():
                        if old_path in tex_value:
                            textures[tex_key] = tex_value.replace(old_path, new_path)
                            updated = True
            
            # Ghi lại file nếu có thay đổi
            if updated:
                with open(json_file, 'w', encoding='utf-8') as jf:
                    json.dump(attachable_data, jf, ensure_ascii=False, indent=0)
    
    # Bước 3: Ghi lại item_texture.json
    with open(item_texture_path, 'w', encoding='utf-8') as f:
        json.dump(item_texture_data, f, ensure_ascii=False, indent=0)
    
    print("Đã random tên texture và cập nhật attachable thành công!")

def random_folder_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số cho thư mục"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def rename_json_files():
    """Random tên tất cả file JSON trong attachables, animations, models/entity"""
    directories = [
        "staging/target/rp/attachables",
        "staging/target/rp/animations", 
        "staging/target/rp/models/entity",
        "staging/target/rp/render_controllers",
        "staging/target/rp/animation_controllers"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            # Random tên file JSON
            for json_file in glob.glob(f"{directory}/**/*.json", recursive=True):
                dir_path = os.path.dirname(json_file)
                new_name = f"{random_name()}.json"
                new_path = os.path.join(dir_path, new_name)
                os.rename(json_file, new_path)
            
            # Random tên thư mục con (chỉ với attachables và models/entity)
            if directory in ["staging/target/rp/attachables", "staging/target/rp/models/entity"]:
                for root, dirs, files in os.walk(directory, topdown=False):
                    for dir_name in dirs:
                        old_dir_path = os.path.join(root, dir_name)
                        new_dir_path = os.path.join(root, random_folder_name())
                        os.rename(old_dir_path, new_dir_path)

if __name__ == "__main__":
    randomize_item_textures()  # Chạy đầu tiên
    rename_json_files()