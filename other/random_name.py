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
    textures_root = "staging/target/rp/textures"
    
    if not os.path.exists(item_texture_path):
        print(f"[DEBUG] Không tìm thấy {item_texture_path}")
        return
    
    print("[DEBUG] Bắt đầu randomize_item_textures()")
    
    with open(item_texture_path, 'r', encoding='utf-8') as f:
        item_texture_data = json.load(f)
    
    texture_data = item_texture_data.get("texture_data", {})
    path_mapping = {}  # Map đường dẫn cũ -> mới (dạng textures/...)
    
    print(f"[DEBUG] Tìm thấy {len(texture_data)} textures trong item_texture.json")
    
    # Hàm đệ quy để random thư mục và file
    def process_directory(current_path, relative_path=""):
        """
        current_path: đường dẫn tuyệt đối (staging/target/rp/textures/evergreenset)
        relative_path: đường dẫn tương đối (evergreenset)
        """
        if not os.path.exists(current_path):
            return
        
        items = os.listdir(current_path)
        
        # Bước 1: Random tên các file PNG trước
        for item in items:
            item_path = os.path.join(current_path, item)
            if os.path.isfile(item_path) and item.endswith('.png'):
                old_name = item[:-4]  # Bỏ .png
                new_name = random_short_name()
                
                # Rename file
                new_file_path = os.path.join(current_path, new_name + '.png')
                shutil.move(item_path, new_file_path)
                
                # Lưu mapping
                old_texture_path = f"textures/{relative_path}/{old_name}" if relative_path else f"textures/{old_name}"
                new_texture_path = f"textures/{relative_path}/{new_name}" if relative_path else f"textures/{new_name}"
                path_mapping[old_texture_path] = new_texture_path
                
                print(f"[DEBUG] Rename file: {old_name}.png -> {new_name}.png")
        
        # Bước 2: Random tên các thư mục con và đệ quy
        folders = [item for item in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, item))]
        
        for folder in folders:
            old_folder_path = os.path.join(current_path, folder)
            new_folder_name = random_short_name()
            new_folder_path = os.path.join(current_path, new_folder_name)
            
            # Tính relative path cũ và mới
            old_relative = f"{relative_path}/{folder}" if relative_path else folder
            new_relative = f"{relative_path}/{new_folder_name}" if relative_path else new_folder_name
            
            # Đệ quy xử lý thư mục con TRƯỚC KHI rename
            process_directory(old_folder_path, old_relative)
            
            # Sau đó rename thư mục
            shutil.move(old_folder_path, new_folder_path)
            print(f"[DEBUG] Rename folder: {folder} -> {new_folder_name}")
            
            # Cập nhật tất cả mapping có chứa đường dẫn cũ
            updated_mapping = {}
            for old_path, new_path in path_mapping.items():
                if old_path.startswith(f"textures/{old_relative}/"):
                    # Thay thế phần đường dẫn cũ bằng mới
                    updated_path = old_path.replace(f"textures/{old_relative}/", f"textures/{new_relative}/")
                    updated_mapping[old_path] = updated_path
                else:
                    updated_mapping[old_path] = new_path
            path_mapping.clear()
            path_mapping.update(updated_mapping)
    
    # Bắt đầu từ thư mục gốc textures
    process_directory(textures_root)
    
    print(f"[DEBUG] Đã tạo {len(path_mapping)} path mappings")
    
    # Bước 3: Cập nhật item_texture.json
    for key, value in texture_data.items():
        old_texture_path = value.get("textures", "")
        if old_texture_path in path_mapping:
            texture_data[key]["textures"] = path_mapping[old_texture_path]
    
    with open(item_texture_path, 'w', encoding='utf-8') as f:
        json.dump(item_texture_data, f, ensure_ascii=False, indent=0)
    
    print("[DEBUG] Đã cập nhật item_texture.json")
    
    # Bước 4: Cập nhật attachables
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
