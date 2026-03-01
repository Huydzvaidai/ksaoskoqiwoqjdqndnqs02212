import os
import random
import glob
import shutil

def confuse_directory():
    """Xáo trộn file vào thư mục con ngẫu nhiên"""
    directories = [
        "staging/target/rp/attachables"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        json_files = list(glob.glob(f"{directory}/**/*.json", recursive=True))
        if not json_files:
            continue
        
        # Thu thập tất cả thư mục con hiện có
        existing_dirs = []
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                existing_dirs.append(os.path.join(root, d))
        
        # Nếu không có thư mục con, bỏ qua
        if not existing_dirs:
            continue
        
        # Xáo trộn file vào các thư mục con ngẫu nhiên
        for json_file in json_files:
            if random.random() < 0.6:
                target_dir = random.choice(existing_dirs)
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
    confuse_directory()
