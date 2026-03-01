import os
import random
import string
import glob
import shutil

def create_nested_structure(base_dir, depth=3):
    """Tạo cấu trúc thư mục lồng nhau phức tạp"""
    current = base_dir
    for _ in range(random.randint(1, depth)):
        current = os.path.join(current, ''.join(random.choices(string.ascii_lowercase + string.digits, k=20)))
        os.makedirs(current, exist_ok=True)
    return current

def confuse_directory():
    """Xáo trộn file và tạo thư mục rỗng"""
    directories = [
        "staging/target/rp/attachables",
        "staging/target/rp/animations",
        "staging/target/rp/models/entity",
        "staging/target/rp/render_controllers",
        "staging/target/rp/animation_controllers"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        json_files = list(glob.glob(f"{directory}/**/*.json", recursive=True))
        if not json_files:
            continue
        
        # Xáo trộn file vào thư mục lồng nhau
        for json_file in json_files:
            if random.random() < 0.6:
                target_dir = create_nested_structure(directory, depth=random.randint(2, 4))
                new_path = os.path.join(target_dir, os.path.basename(json_file))
                if not os.path.exists(new_path):
                    shutil.move(json_file, new_path)
        
        # Tạo thư mục rỗng
        for _ in range(random.randint(5, 10)):
            create_nested_structure(directory, depth=random.randint(1, 4))

if __name__ == "__main__":
    confuse_directory()
