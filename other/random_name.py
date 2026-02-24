import os
import random
import string
import glob
import json
import shutil

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
        return
    
    # Đọc item_texture.json
    with open(item_texture_path, 'r', encoding='utf-8') as f:
        item_texture_data = json.load(f)
    
    texture_data = item_texture_data.get("texture_data", {})
    path_mapping = {}
    folder_mapping = {}
    
    # Bước 1: Thu thập tất cả đường dẫn và tạo mapping cho thư mục
    all_folders = set()
    
    for key, value in texture_data.items():
        texture_path = value.get("textures", "")
        if not texture_path.startswith("textures/"):
            continue
        
        parts = texture_path.replace("textures/", "").split("/")
        current = ""
        
        for i in range(len(parts) - 1):
            if current:
                current += "/" + parts[i]
            else:
                current = parts[i]
            all_folders.add(current)
    
    # Tạo mapping cho thư mục
    sorted_folders = sorted(all_folders, key=lambda x: x.count('/'), reverse=True)
    for folder in sorted_folders:
        new_name = random_short_name()
        folder_mapping[folder] = new_name
    
    # Bước 2: Rename thư mục
    for old_folder in sorted_folders:
        old_path = "staging/target/rp/textures/" + old_folder
        
        if not os.path.exists(old_path):
            continue
        
        parts = old_folder.split("/")
        new_parts = [folder_mapping.get("/".join(parts[:i+1]), parts[i]) for i in range(len(parts))]
        new_folder = "/".join(new_parts)
        new_path = "staging/target/rp/textures/" + new_folder
        
        parent_dir = os.path.dirname(new_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        shutil.move(old_path, new_path)
    
    # Bước 3: Random tên file và tạo path mapping
    for key, value in texture_data.items():
        texture_path = value.get("textures", "")
        if not texture_path.startswith("textures/"):
            continue
        
        parts = texture_path.replace("textures/", "").split("/")
        new_parts = []
        
        for i in range(len(parts) - 1):
            folder_path = "/".join(parts[:i+1])
            new_parts.append(folder_mapping.get(folder_path, parts[i]))
        
        old_filename = parts[-1]
        new_filename = random_short_name()
        new_parts.append(new_filename)
        
        old_file_path = "staging/target/rp/textures/" + "/".join(parts[:-1])
        if parts[:-1]:
            folder_path = "/".join(parts[:-1])
            folder_parts = folder_path.split("/")
            new_folder_parts = [folder_mapping.get("/".join(folder_parts[:i+1]), folder_parts[i]) for i in range(len(folder_parts))]
            old_file_path = "staging/target/rp/textures/" + "/".join(new_folder_parts)
        else:
            old_file_path = "staging/target/rp/textures"
        
        old_png = os.path.join(old_file_path, old_filename + ".png")
        new_png = os.path.join(old_file_path, new_filename + ".png")
        
        if os.path.exists(old_png):
            shutil.move(old_png, new_png)
        
        old_path = texture_path
        new_path = "textures/" + "/".join(new_parts)
        path_mapping[old_path] = new_path
        texture_data[key]["textures"] = new_path
    
    # Bước 4: Cập nhật attachables
    attachables_dir = "staging/target/rp/attachables"
    
    if os.path.exists(attachables_dir):
        json_files = list(glob.glob(f"{attachables_dir}/**/*.json", recursive=True))
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as jf:
                attachable_data = json.load(jf)
            
            desc = attachable_data.get("minecraft:attachable", {}).get("description", {})
            textures = desc.get("textures", {})
            updated = False
            
            for tex_key, tex_value in textures.items():
                if tex_value:
                    for old_path, new_path in path_mapping.items():
                        if old_path in tex_value:
                            textures[tex_key] = tex_value.replace(old_path, new_path)
                            updated = True
            
            if updated:
                with open(json_file, 'w', encoding='utf-8') as jf:
                    json.dump(attachable_data, jf, ensure_ascii=False, indent=0)
    
    # Bước 5: Ghi lại item_texture.json
    with open(item_texture_path, 'w', encoding='utf-8') as f:
        json.dump(item_texture_data, f, ensure_ascii=False, indent=0)

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
    randomize_item_textures()
    rename_json_files()