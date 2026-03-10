import os
import json
import random
import glob
import shutil

def split_animations():
    """Tách file animation có nhiều animation thành nhiều file riêng"""
    animations_dir = "staging/target/rp/animations"
    
    if not os.path.exists(animations_dir):
        return
    
    json_files = list(glob.glob(f"{animations_dir}/**/*.json", recursive=True))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            animations = data.get("animations", {})
            
            # Nếu chỉ có 1 animation hoặc không có, bỏ qua
            if len(animations) <= 1:
                continue
            
            format_version = data.get("format_version", "1.8.0")
            if format_version == "1.8":
                format_version = "1.8.0"
            file_dir = os.path.dirname(json_file)
            base_filename = os.path.splitext(os.path.basename(json_file))[0]
            
            # Tách từng animation thành file riêng
            counter = 1
            for anim_name, anim_data in animations.items():
                new_data = {
                    "format_version": format_version,
                    "animations": {
                        anim_name: anim_data
                    }
                }
                
                # Tạo tên file từ tên file gốc + số thứ tự
                new_file = os.path.join(file_dir, f"{base_filename}_{counter}.json")
                counter += 1
                
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=0)
            
            # Xóa file gốc sau khi tách xong
            os.remove(json_file)
            
        except Exception as e:
            continue

def split_animation_controllers():
    """Tách file animation_controllers có nhiều controller thành nhiều file riêng"""
    controllers_dir = "staging/target/rp/animation_controllers"
    
    if not os.path.exists(controllers_dir):
        return
    
    json_files = list(glob.glob(f"{controllers_dir}/**/*.json", recursive=True))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            controllers = data.get("animation_controllers", {})
            
            # Nếu chỉ có 1 controller hoặc không có, bỏ qua
            if len(controllers) <= 1:
                continue
            
            format_version = data.get("format_version", "1.10.0")
            file_dir = os.path.dirname(json_file)
            base_filename = os.path.splitext(os.path.basename(json_file))[0]
            
            # Tách từng controller thành file riêng
            counter = 1
            for controller_name, controller_data in controllers.items():
                new_data = {
                    "format_version": format_version,
                    "animation_controllers": {
                        controller_name: controller_data
                    }
                }
                
                # Tạo tên file từ tên file gốc + số thứ tự
                new_file = os.path.join(file_dir, f"{base_filename}_{counter}.json")
                counter += 1
                
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=0)
            
            # Xóa file gốc sau khi tách xong
            os.remove(json_file)
            
        except Exception as e:
            continue

def split_render_controllers():
    """Tách file render_controllers có nhiều controller thành nhiều file riêng"""
    controllers_dir = "staging/target/rp/render_controllers"
    
    if not os.path.exists(controllers_dir):
        return
    
    json_files = list(glob.glob(f"{controllers_dir}/**/*.json", recursive=True))
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            controllers = data.get("render_controllers", {})
            
            # Nếu chỉ có 1 controller hoặc không có, bỏ qua
            if len(controllers) <= 1:
                continue
            
            format_version = data.get("format_version", "1.10")
            file_dir = os.path.dirname(json_file)
            base_filename = os.path.splitext(os.path.basename(json_file))[0]
            
            # Tách từng controller thành file riêng
            counter = 1
            for controller_name, controller_data in controllers.items():
                new_data = {
                    "format_version": format_version,
                    "render_controllers": {
                        controller_name: controller_data
                    }
                }
                
                # Tạo tên file từ tên file gốc + số thứ tự
                new_file = os.path.join(file_dir, f"{base_filename}_{counter}.json")
                counter += 1
                
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=0)
            
            # Xóa file gốc sau khi tách xong
            os.remove(json_file)
            
        except Exception as e:
            continue

def random_folder_name():
    """Tạo tên thư mục random với prefix campfire_ + 15 ký tự"""
    import string
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def confuse_directory():
    """Xáo trộn file vào thư mục con ngẫu nhiên"""
    directories = [
        "staging/target/rp/attachables",
        "staging/target/rp/animations",
        "staging/target/rp/animation_controllers",
        "staging/target/rp/render_controllers"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        # Thu thập tất cả file JSON ở root của directory (không đệ quy)
        json_files = [f for f in glob.glob(f"{directory}/*.json") if os.path.isfile(f)]
        
        if not json_files:
            continue
        
        # Tạo 1-5 thư mục con ngẫu nhiên
        num_folders = random.randint(1, 5)
        created_dirs = []
        
        for _ in range(num_folders):
            folder_name = random_folder_name()
            folder_path = os.path.join(directory, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            created_dirs.append(folder_path)
        
        # Thu thập tất cả thư mục con (bao gồm cả thư mục vừa tạo và thư mục có sẵn)
        all_dirs = created_dirs.copy()
        for root, dirs, files in os.walk(directory):
            if root != directory:  # Bỏ qua thư mục root
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    if dir_path not in all_dirs:
                        all_dirs.append(dir_path)
        
        # Nếu không có thư mục con nào, chỉ dùng thư mục vừa tạo
        if not all_dirs:
            all_dirs = created_dirs
        
        # Xáo trộn 100% file vào các thư mục con ngẫu nhiên
        for json_file in json_files:
            if all_dirs:
                target_dir = random.choice(all_dirs)
                new_path = os.path.join(target_dir, os.path.basename(json_file))
                
                # Nếu file đã tồn tại, thêm suffix số
                if os.path.exists(new_path):
                    base_name = os.path.splitext(os.path.basename(json_file))[0]
                    counter = 1
                    while os.path.exists(new_path):
                        new_name = f"{base_name}_{counter}.json"
                        new_path = os.path.join(target_dir, new_name)
                        counter += 1
                
                shutil.move(json_file, new_path)

if __name__ == "__main__":
    split_animations()
    split_animation_controllers()
    split_render_controllers()
    confuse_directory()
