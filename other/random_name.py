import os
import random
import string
import glob
import json
import shutil

# Global mapping dictionary để lưu tất cả path mappings
global_path_mapping = {}

def random_name():
    """Tạo tên random 45 ký tự chữ cái in thường và số xen kẽ"""
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=45))

def random_short_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số"""
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def randomize_item_textures():
    """Random tên thư mục và file texture với tracking chính xác 100%"""
    global global_path_mapping
    
    item_texture_path = "staging/target/rp/textures/item_texture.json"
    terrain_texture_path = "staging/target/rp/textures/terrain_texture.json"
    textures_root = "staging/target/rp/textures"
    
    if not os.path.exists(item_texture_path) and not os.path.exists(terrain_texture_path):
        return
    
    # Danh sách thư mục bỏ qua
    skip_folders = ['gui', 'campfire_item']
    
    # Bước 1: Thu thập tất cả texture paths từ JSON files
    all_texture_paths = set()
    
    if os.path.exists(item_texture_path):
        with open(item_texture_path, 'r', encoding='utf-8') as f:
            item_texture_data = json.load(f)
            for key, value in item_texture_data.get("texture_data", {}).items():
                texture_path = value.get("textures", "")
                if texture_path:
                    all_texture_paths.add(texture_path)
    
    if os.path.exists(terrain_texture_path):
        with open(terrain_texture_path, 'r', encoding='utf-8') as f:
            terrain_texture_data = json.load(f)
            for key, value in terrain_texture_data.get("texture_data", {}).items():
                texture_path = value.get("textures", "")
                if texture_path:
                    all_texture_paths.add(texture_path)
    
    print(f"Tìm thấy {len(all_texture_paths)} texture paths cần tracking")
    
    # Bước 2: Tạo exact tracking cho từng file
    file_tracking = {}  # old_texture_path -> current_abs_path
    
    for texture_path in all_texture_paths:
        # Chuyển texture path thành file path
        file_path = texture_path.replace("textures/", "")
        abs_file_path = os.path.join(textures_root, file_path + ".png")
        
        if os.path.exists(abs_file_path):
            file_tracking[texture_path] = abs_file_path
            print(f"[TRACK] {texture_path} -> {abs_file_path}")
    
    print(f"Tracking {len(file_tracking)} files")
    
    # Bước 3: Thu thập tất cả file và thư mục cần rename (chỉ những file được track)
    files_to_rename = []  # [(abs_path, old_texture_path)]
    folders_to_rename = []  # [(abs_path, relative_path)]
    
    # Thu thập file cần rename
    for old_texture_path, abs_file_path in file_tracking.items():
        if os.path.exists(abs_file_path):
            files_to_rename.append((abs_file_path, old_texture_path))
    
    # Thu thập thư mục
    for root, dirs, files in os.walk(textures_root):
        rel_root = os.path.relpath(root, textures_root)
        should_skip = any(rel_root == skip or rel_root.startswith(skip + os.sep) for skip in skip_folders)
        
        if not should_skip:
            for dir_name in dirs:
                if dir_name in skip_folders:
                    continue
                
                abs_path = os.path.join(root, dir_name)
                rel_path = os.path.relpath(abs_path, textures_root)
                folders_to_rename.append((abs_path, rel_path))
    
    # Bước 4: Tạo mapping cho file và thư mục
    file_new_names = {}  # abs_path -> new_name
    folder_new_names = {}  # abs_path -> new_name
    
    for abs_path, old_texture_path in files_to_rename:
        new_name = random_short_name()
        file_new_names[abs_path] = new_name
    
    folders_to_rename.sort(key=lambda x: x[1].count(os.sep), reverse=True)
    for abs_path, rel_path in folders_to_rename:
        new_name = random_short_name()
        folder_new_names[abs_path] = new_name
    
    # Bước 5: Rename files và update tracking
    for abs_path, old_texture_path in files_to_rename:
        if os.path.exists(abs_path):
            new_name = file_new_names[abs_path]
            new_path = os.path.join(os.path.dirname(abs_path), new_name + '.png')
            shutil.move(abs_path, new_path)
            # Update tracking
            file_tracking[old_texture_path] = new_path
            print(f"[RENAME] {abs_path} -> {new_path}")
    
    # Bước 6: Xáo trộn files và update tracking
    all_tracked_files = list(file_tracking.values())
    
    # Tạo danh sách thư mục đích
    target_dirs = set()
    for file_path in all_tracked_files:
        target_dirs.add(os.path.dirname(file_path))
    target_dirs = list(target_dirs)
    
    # Xáo trộn từng file và update tracking
    for old_texture_path, current_abs_path in list(file_tracking.items()):
        if os.path.exists(current_abs_path):
            target_dir = random.choice(target_dirs)
            new_path = os.path.join(target_dir, os.path.basename(current_abs_path))
            
            # Nếu trùng tên, thêm suffix
            if os.path.exists(new_path):
                base_name = os.path.splitext(os.path.basename(current_abs_path))[0]
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}.png"
                    new_path = os.path.join(target_dir, new_name)
                    counter += 1
            
            shutil.move(current_abs_path, new_path)
            # Update tracking
            file_tracking[old_texture_path] = new_path
            print(f"[SHUFFLE] {current_abs_path} -> {new_path}")
    
    # Bước 7: Rename folders và update tracking
    for abs_path, rel_path in folders_to_rename:
        if os.path.exists(abs_path):
            new_name = folder_new_names[abs_path]
            new_path = os.path.join(os.path.dirname(abs_path), new_name)
            shutil.move(abs_path, new_path)
            
            # Update tracking cho tất cả file trong thư mục này
            for old_texture_path, current_file_path in list(file_tracking.items()):
                if current_file_path.startswith(abs_path):
                    # Thay thế đường dẫn thư mục cũ bằng mới
                    updated_path = current_file_path.replace(abs_path, new_path, 1)
                    file_tracking[old_texture_path] = updated_path
                    print(f"[FOLDER_UPDATE] {current_file_path} -> {updated_path}")
    
    # Bước 8: Tạo final mapping từ tracking data
    path_mapping = {}
    
    for old_texture_path, final_abs_path in file_tracking.items():
        if os.path.exists(final_abs_path):
            # Chuyển abs path thành texture path
            rel_path = os.path.relpath(final_abs_path, textures_root)
            new_texture_path = "textures/" + rel_path.replace(os.sep, '/')[:-4]  # Bỏ .png
            path_mapping[old_texture_path] = new_texture_path
            print(f"[FINAL] {old_texture_path} -> {new_texture_path}")
        else:
            print(f"[ERROR] File không tồn tại: {final_abs_path}")
            path_mapping[old_texture_path] = old_texture_path
    
    # Bước 9: Xử lý các texture paths không có file tương ứng (texture động hoặc không tồn tại)
    for texture_path in all_texture_paths:
        if texture_path not in path_mapping:
            print(f"[NO_FILE] Texture path không có file: {texture_path}")
            # Giữ nguyên path cho texture không có file
            path_mapping[texture_path] = texture_path
    
    # Thêm mapping vào global mapping
    global_path_mapping.update(path_mapping)
    print(f"Đã tạo {len(path_mapping)} texture mappings chính xác 100%")

def randomize_2d_animation_textures():
    """Random tên và xáo trộn texture của 2D animations (xử lý thư mục item)"""
    global global_path_mapping
    
    import random
    import shutil
    from pathlib import Path
    
    textures_root = Path("staging/target/rp/textures")
    item_dir = textures_root / "item"
    
    if not item_dir.exists():
        return
    
    print(f"Bắt đầu xử lý thư mục item cho 2D animations")
    
    # Bước 1: Thu thập tất cả file PNG và thư mục con trong item/
    files_to_rename = []  # [(abs_path, relative_path_without_ext)]
    folders_to_rename = []  # [(abs_path, relative_path)]
    
    for root, dirs, files in os.walk(item_dir):
        rel_root = os.path.relpath(root, item_dir)
        
        # Thu thập file PNG
        for file in files:
            if file.endswith('.png'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, item_dir)
                rel_path_no_ext = rel_path[:-4]  # Bỏ .png
                files_to_rename.append((abs_path, rel_path_no_ext))
        
        # Thu thập thư mục con (không bao gồm thư mục item root)
        for dir_name in dirs:
            abs_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(abs_path, item_dir)
            folders_to_rename.append((abs_path, rel_path))
    
    print(f"Tìm thấy {len(files_to_rename)} files và {len(folders_to_rename)} folders trong item")
    
    # Bước 2: Tạo mapping cho file
    file_mapping = {}  # relative_path_no_ext -> new_name
    for abs_path, rel_path_no_ext in files_to_rename:
        new_name = random_short_name()
        file_mapping[rel_path_no_ext] = new_name
    
    # Bước 3: Tạo mapping cho thư mục con (từ sâu nhất lên)
    folder_mapping = {}  # relative_path -> new_name
    folders_to_rename.sort(key=lambda x: x[1].count(os.sep), reverse=True)
    
    for abs_path, rel_path in folders_to_rename:
        new_name = random_short_name()
        folder_mapping[rel_path] = new_name
    
    # Bước 4: Rename files
    for abs_path, rel_path_no_ext in files_to_rename:
        if os.path.exists(abs_path):
            new_name = file_mapping[rel_path_no_ext]
            new_path = os.path.join(os.path.dirname(abs_path), new_name + '.png')
            shutil.move(abs_path, new_path)
    
    # Bước 5: Xáo trộn 100% file PNG trong phạm vi item/
    all_png_files = []
    for root, dirs, files in os.walk(item_dir):
        for file in files:
            if file.endswith('.png'):
                all_png_files.append(os.path.join(root, file))
    
    # Tạo danh sách thư mục đích (tất cả thư mục trong item/)
    target_dirs = []
    for root, dirs, files in os.walk(item_dir):
        target_dirs.append(root)
    
    # Nếu chỉ có thư mục root, tạo thêm một số thư mục con random
    if len(target_dirs) <= 1:
        for i in range(5):
            new_dir = item_dir / random_short_name()
            new_dir.mkdir(parents=True, exist_ok=True)
            target_dirs.append(str(new_dir))
    
    # Xáo trộn file trong phạm vi item/
    for png_file in all_png_files:
        if os.path.exists(png_file):
            target_dir = random.choice(target_dirs)
            new_path = os.path.join(target_dir, os.path.basename(png_file))
            
            # Nếu trùng tên, thêm suffix
            if os.path.exists(new_path):
                base_name = os.path.splitext(os.path.basename(png_file))[0]
                counter = 1
                while os.path.exists(new_path):
                    new_name = f"{base_name}_{counter}.png"
                    new_path = os.path.join(target_dir, new_name)
                    counter += 1
            
            shutil.move(png_file, new_path)
    
    # Bước 6: Rename folders (từ sâu nhất lên)
    for abs_path, rel_path in folders_to_rename:
        if os.path.exists(abs_path):
            new_name = folder_mapping[rel_path]
            new_path = os.path.join(os.path.dirname(abs_path), new_name)
            shutil.move(abs_path, new_path)
    
    # Bước 7: Random tên thư mục item
    new_item_name = random_short_name()
    new_item_path = textures_root / new_item_name
    shutil.move(str(item_dir), str(new_item_path))
    
    # Bước 8: Tạo path mapping cho TẤT CẢ texture paths trong thư mục item
    path_mapping = {}
    
    # Đọc lại texture data để lấy tất cả texture paths có prefix "textures/item/"
    current_item_texture_paths = set()
    
    # Thu thập từ item_texture.json
    item_texture_path = "staging/target/rp/textures/item_texture.json"
    if os.path.exists(item_texture_path):
        with open(item_texture_path, 'r', encoding='utf-8') as f:
            item_texture_data = json.load(f)
            for key, value in item_texture_data.get("texture_data", {}).items():
                texture_path = value.get("textures", "")
                if texture_path and texture_path.startswith("textures/item/"):
                    current_item_texture_paths.add(texture_path)
    
    print(f"Tìm thấy {len(current_item_texture_paths)} item texture paths trong JSON files")
    
    # Thu thập tất cả file PNG hiện có trong thư mục mới (sau khi rename item -> new_item_name)
    current_png_files = {}  # texture_path -> actual_file_path
    for root, dirs, files in os.walk(new_item_path):
        for file in files:
            if file.endswith('.png'):
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, textures_root)
                texture_path = "textures/" + rel_path.replace(os.sep, '/')[:-4]  # Bỏ .png
                current_png_files[texture_path] = abs_path
    
    print(f"Tìm thấy {len(current_png_files)} PNG files trong thư mục item mới")
    
    # Tạo mapping cho tất cả texture paths có prefix "textures/item/"
    for old_texture_path in current_item_texture_paths:
        # Tìm file PNG tương ứng
        found_match = False
        
        # Lấy phần path sau "textures/item/"
        old_path_without_prefix = old_texture_path.replace("textures/item/", "")
        
        # Tìm file khớp dựa trên tên gốc từ file_mapping
        for old_rel_path, new_name in file_mapping.items():
            if old_path_without_prefix == old_rel_path:
                # Tìm file PNG có tên new_name (có thể có suffix)
                for texture_path, file_path in current_png_files.items():
                    file_base = os.path.splitext(os.path.basename(file_path))[0]
                    if file_base == new_name or file_base.startswith(new_name + "_"):
                        path_mapping[old_texture_path] = texture_path
                        found_match = True
                        break
                break
        
        if not found_match:
            # Giữ nguyên path cũ nếu không tìm thấy
            path_mapping[old_texture_path] = old_texture_path
    
    # Thêm mapping vào global mapping
    global_path_mapping.update(path_mapping)
    print(f"Đã tạo {len(path_mapping)} item texture mappings")

def update_all_mappings():
    """Cập nhật tất cả file với global path mapping"""
    global global_path_mapping
    
    if not global_path_mapping:
        print("Không có mapping nào để cập nhật")
        return
    
    print(f"Đang cập nhật {len(global_path_mapping)} texture mappings...")
    
    # Cập nhật item_texture.json và terrain_texture.json
    item_texture_path = "staging/target/rp/textures/item_texture.json"
    terrain_texture_path = "staging/target/rp/textures/terrain_texture.json"
    
    if os.path.exists(item_texture_path):
        with open(item_texture_path, 'r', encoding='utf-8') as f:
            item_texture_data = json.load(f)
        
        item_data = item_texture_data.get("texture_data", {})
        updated_textures = 0
        total_textures = len(item_data)
        
        for key, value in item_data.items():
            old_texture_path = value.get("textures", "")
            if old_texture_path in global_path_mapping:
                new_path = global_path_mapping[old_texture_path]
                item_data[key]["textures"] = new_path
                updated_textures += 1
            else:
                print(f"[DEBUG] No mapping found for {key}: {old_texture_path}")
        
        print(f"Cập nhật {updated_textures}/{total_textures} textures trong item_texture.json")
        
        item_texture_data['texture_data'] = item_data
        with open(item_texture_path, 'w', encoding='utf-8') as f:
            json.dump(item_texture_data, f, ensure_ascii=False, indent=0)
    
    if os.path.exists(terrain_texture_path):
        with open(terrain_texture_path, 'r', encoding='utf-8') as f:
            terrain_texture_data = json.load(f)
        
        terrain_data = terrain_texture_data.get("texture_data", {})
        updated_textures = 0
        total_textures = len(terrain_data)
        
        for key, value in terrain_data.items():
            old_texture_path = value.get("textures", "")
            if old_texture_path in global_path_mapping:
                new_path = global_path_mapping[old_texture_path]
                terrain_data[key]["textures"] = new_path
                updated_textures += 1
            else:
                print(f"[DEBUG] No mapping found for {key}: {old_texture_path}")
        
        print(f"Cập nhật {updated_textures}/{total_textures} textures trong terrain_texture.json")
        
        terrain_texture_data['texture_data'] = terrain_data
        with open(terrain_texture_path, 'w', encoding='utf-8') as f:
            json.dump(terrain_texture_data, f, ensure_ascii=False, indent=0)
    
    # Cập nhật attachables
    attachables_dir = "staging/target/rp/attachables"
    updated_count = 0
    
    if os.path.exists(attachables_dir):
        json_files = list(glob.glob(f"{attachables_dir}/**/*.json", recursive=True))
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    attachable_data = json.load(f)
                
                desc = attachable_data.get("minecraft:attachable", {}).get("description", {})
                textures = desc.get("textures", {})
                updated = False
                
                for tex_key, tex_value in textures.items():
                    if tex_value:
                        for old_path, new_path in global_path_mapping.items():
                            if old_path in tex_value:
                                textures[tex_key] = tex_value.replace(old_path, new_path)
                                updated = True
                
                if updated:
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(attachable_data, f, ensure_ascii=False, indent=2)
                    updated_count += 1
            except:
                pass
        
        print(f"Cập nhật {updated_count} attachable files")

def random_folder_name():
    """Tạo tên random 15 ký tự chữ cái in thường và số cho thư mục"""
    return 'campfire_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

def rename_json_files():
    """Random tên tất cả file JSON trong attachables, animations, models/entity"""
    
    directories = [
        "staging/target/rp/attachables",
        "staging/target/rp/animations", 
        "staging/target/rp/models/entity",
        "staging/target/rp/render_controllers",
        "staging/target/rp/animation_controllers"
    ]
    
    # Danh sách thư mục cần tạo thư mục con trước khi xáo trộn
    dirs_need_subfolders = [
        "staging/target/rp/animations",
        "staging/target/rp/render_controllers",
        "staging/target/rp/animation_controllers"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        # Bước 1: Random tên file JSON
        json_files = list(glob.glob(f"{directory}/**/*.json", recursive=True))
        
        for json_file in json_files:
            dir_path = os.path.dirname(json_file)
            new_name = f"{random_name()}.json"
            new_path = os.path.join(dir_path, new_name)
            os.rename(json_file, new_path)
        
        # Bước 2: Random tên thư mục con (chỉ với attachables và models/entity)
        if directory in ["staging/target/rp/attachables", "staging/target/rp/models/entity"]:
            folders = []
            for root, dirs, files in os.walk(directory, topdown=False):
                for dir_name in dirs:
                    folders.append(os.path.join(root, dir_name))
            
            for old_dir_path in folders:
                new_dir_path = os.path.join(os.path.dirname(old_dir_path), random_folder_name())
                os.rename(old_dir_path, new_dir_path)
        
        # Bước 3: Xáo trộn file JSON
        # Thu thập lại tất cả file JSON sau khi rename
        json_files_after_rename = list(glob.glob(f"{directory}/**/*.json", recursive=True))
        
        if directory in dirs_need_subfolders:
            # Tạo 2-5 thư mục con ngẫu nhiên
            num_folders = random.randint(2, 5)
            created_dirs = []
            
            for _ in range(num_folders):
                folder_name = random_folder_name()
                folder_path = os.path.join(directory, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                created_dirs.append(folder_path)
            
            # Thu thập tất cả thư mục con (bao gồm cả thư mục vừa tạo và thư mục có sẵn)
            all_dirs = created_dirs.copy()
            for root, dirs, files in os.walk(directory):
                if root != directory:
                    for d in dirs:
                        dir_path = os.path.join(root, d)
                        if dir_path not in all_dirs:
                            all_dirs.append(dir_path)
            
            # Nếu không có thư mục con nào, chỉ dùng thư mục vừa tạo
            if not all_dirs:
                all_dirs = created_dirs
            
            # Xáo trộn 100% file vào các thư mục con
            for json_file in json_files_after_rename:
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
        
        else:
            # Với attachables và models/entity: xáo trộn giữa các thư mục có sẵn
            # Thu thập tất cả thư mục con
            all_dirs = []
            for root, dirs, files in os.walk(directory):
                if root != directory:
                    all_dirs.append(root)
            
            # Nếu có thư mục con, xáo trộn file
            if all_dirs:
                for json_file in json_files_after_rename:
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

def check_randomized():
    """Kiểm tra xem tất cả file JSON và thư mục đã có prefix campfire_ chưa"""
    dirs = [
        "staging/target/rp/attachables",
        "staging/target/rp/animations",
        "staging/target/rp/models/entity",
        "staging/target/rp/render_controllers",
        "staging/target/rp/animation_controllers"
    ]
    
    skip_folders = ['gui', 'campfire_item', 'item']
    
    for directory in dirs:
        if os.path.exists(directory):
            for json_file in glob.glob(f"{directory}/**/*.json", recursive=True):
                if not os.path.basename(json_file).startswith("campfire_"):
                    return False
            
            if directory in ["staging/target/rp/attachables", "staging/target/rp/models/entity"]:
                for root, dirs_list, files in os.walk(directory):
                    for dir_name in dirs_list:
                        if not dir_name.startswith("campfire_"):
                            return False
    
    # Kiểm tra textures
    textures_root = "staging/target/rp/textures"
    if os.path.exists(textures_root):
        for root, dirs_list, files in os.walk(textures_root):
            rel_root = os.path.relpath(root, textures_root)
            should_skip = any(rel_root == skip or rel_root.startswith(skip + os.sep) for skip in skip_folders)
            
            if not should_skip:
                for file in files:
                    if file in ['item_texture.json', 'terrain_texture.json']:
                        continue
                    if file.endswith('.png') and not file.startswith("campfire_"):
                        return False
                for dir_name in dirs_list:
                    if dir_name not in skip_folders and not dir_name.startswith("campfire_"):
                        return False
    
    return True

if __name__ == "__main__":
    # Reset global mapping
    global_path_mapping = {}
    
    # Thực hiện randomization
    randomize_item_textures()
    rename_json_files()
    
    # Cập nhật tất cả mapping một lần duy nhất
    update_all_mappings()
    
    if not check_randomized():
        # Reset và thử lại
        global_path_mapping = {}
        randomize_item_textures()
        rename_json_files()
        update_all_mappings()
