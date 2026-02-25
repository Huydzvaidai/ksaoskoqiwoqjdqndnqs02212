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
    """Tạo tên random 15 ký tự chữ cái in thường và số"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def randomize_item_textures():
    """Random tên thư mục và file texture dựa trên item_texture.json"""
    item_texture_path = "staging/target/rp/textures/item_texture.json"
    
    if not os.path.exists(item_texture_path):
        print(f"[DEBUG] Không tìm thấy {item_texture_path}")
        return
    
    print("[DEBUG] Bắt đầu randomize_item_textures()")
    
    # Đọc item_texture.json
    with open(item_texture_path, 'r', encoding='utf-8') as f:
        item_texture_data = json.load(f)
    
    texture_data = item_texture_data.get("texture_data", {})
    path_mapping = {}
    folder_mapping = {}  # Map: đường_dẫn_đầy_đủ → đường_dẫn_mới_đầy_đủ
    
    print(f"[DEBUG] Tìm thấy {len(texture_data)} textures")
    
    # Bước 1: Thu thập tất cả đường dẫn thư mục
    all_folder_paths = set()
    
    for key, value in texture_data.items():
        texture_path = value.get("textures", "")
        if not texture_path.startswith("textures/"):
            continue
        
        parts = texture_path.replace("textures/", "").split("/")
        
        # Thu thập tất cả đường dẫn thư mục (từ gốc đến sâu)
        for i in range(len(parts) - 1):
            folder_path = "/".join(parts[:i+1])
            all_folder_paths.add(folder_path)
    
    # Sắp xếp từ nông đến sâu (để xử lý cha trước con)
    sorted_paths = sorted(all_folder_paths, key=lambda x: x.count('/'))
    
    print(f"[DEBUG] Tìm thấy {len(sorted_paths)} đường dẫn thư mục")
    
    # Bước 2: Tạo mapping cho từng đường dẫn
    for folder_path in sorted_paths:
        parts = folder_path.split("/")
        new_parts = []
        
        for i, part in enumerate(parts):
            parent_path = "/".join(parts[:i]) if i > 0 else ""
            current_path = "/".join(parts[:i+1])
            
            # Nếu đã có mapping cho đường dẫn này rồi, lấy phần cuối
            if current_path in folder_mapping:
                new_parts.append(folder_mapping[current_path].split("/")[-1])
            else:
                # Tạo tên random mới
                new_name = random_short_name()
                
                # Xây dựng đường dẫn đầy đủ mới
                if parent_path and parent_path in folder_mapping:
                    full_new_path = folder_mapping[parent_path] + "/" + new_name
                else:
                    full_new_path = new_name
                
                folder_mapping[current_path] = full_new_path
                new_parts.append(new_name)
    
    # Bước 3: Rename thư mục (từ sâu nhất lên để tránh conflict)
    sorted_paths_reverse = sorted(all_folder_paths, key=lambda x: x.count('/'), reverse=True)
    renamed_folders = 0
    
    for old_folder_path in sorted_paths_reverse:
        old_path = "staging/target/rp/textures/" + old_folder_path
        
        if not os.path.exists(old_path):
            continue
        
        new_folder_path = folder_mapping[old_folder_path]
        new_path = "staging/target/rp/textures/" + new_folder_path
        
        parent_dir = os.path.dirname(new_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        
        shutil.move(old_path, new_path)
        renamed_folders += 1
    
    print(f"[DEBUG] Đã rename {renamed_folders} thư mục")
    
    # Bước 4: Random tên file và cập nhật mapping
    renamed_files = 0
    
    for key, value in texture_data.items():
        texture_path = value.get("textures", "")
        if not texture_path.startswith("textures/"):
            continue
        
        parts = texture_path.replace("textures/", "").split("/")
        old_filename = parts[-1]
        new_filename = random_short_name()
        
        # Lấy đường dẫn thư mục mới
        if len(parts) > 1:
            folder_path = "/".join(parts[:-1])
            new_folder_path = folder_mapping.get(folder_path, folder_path)
            file_dir = "staging/target/rp/textures/" + new_folder_path
            new_texture_path = "textures/" + new_folder_path + "/" + new_filename
        else:
            file_dir = "staging/target/rp/textures"
            new_texture_path = "textures/" + new_filename
        
        # Rename file PNG
        old_png = os.path.join(file_dir, old_filename + ".png")
        new_png = os.path.join(file_dir, new_filename + ".png")
        
        if os.path.exists(old_png):
            shutil.move(old_png, new_png)
            renamed_files += 1
        
        # Cập nhật mapping
        path_mapping[texture_path] = new_texture_path
        texture_data[key]["textures"] = new_texture_path
    
    print(f"[DEBUG] Đã rename {renamed_files} file PNG")
    
    # Bước 5: Cập nhật attachables
    attachables_dir = "staging/target/rp/attachables"
    updated_count = 0
    
    if os.path.exists(attachables_dir):
        json_files = list(glob.glob(f"{attachables_dir}/**/*.json", recursive=True))
        print(f"[DEBUG] Tìm thấy {len(json_files)} attachable JSON")
        
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
                updated_count += 1
        
        print(f"[DEBUG] Đã cập nhật {updated_count} attachable JSON")
    
    # Bước 6: Ghi lại item_texture.json
    with open(item_texture_path, 'w', encoding='utf-8') as f:
        json.dump(item_texture_data, f, ensure_ascii=False, indent=0)
    
    print("[DEBUG] Hoàn thành randomize_item_textures()")

def random_folder_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số cho thư mục"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def rename_json_files():
    """Random tên tất cả file JSON trong attachables, animations, models/entity"""
    print("[DEBUG] Bắt đầu rename_json_files()")
    
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
            json_files = list(glob.glob(f"{directory}/**/*.json", recursive=True))
            print(f"[DEBUG] Rename {len(json_files)} JSON files trong {directory}")
            
            for json_file in json_files:
                dir_path = os.path.dirname(json_file)
                new_name = f"{random_name()}.json"
                new_path = os.path.join(dir_path, new_name)
                os.rename(json_file, new_path)
            
            # Random tên thư mục con (chỉ với attachables và models/entity)
            if directory in ["staging/target/rp/attachables", "staging/target/rp/models/entity"]:
                folders = []
                for root, dirs, files in os.walk(directory, topdown=False):
                    for dir_name in dirs:
                        folders.append(os.path.join(root, dir_name))
                
                print(f"[DEBUG] Rename {len(folders)} thư mục trong {directory}")
                
                for old_dir_path in folders:
                    new_dir_path = os.path.join(os.path.dirname(old_dir_path), random_folder_name())
                    os.rename(old_dir_path, new_dir_path)
    
    print("[DEBUG] Hoàn thành rename_json_files()")

if __name__ == "__main__":
    randomize_item_textures()
    rename_json_files()