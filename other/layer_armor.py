import os
import re
import yaml
import random
import string

def remove_ia_generated_armors():
    folder_path = "pack/assets/minecraft/optifine/cit/ia_generated_armors"
    
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Đã xóa file: {file_path}")
        print(f"Đã xóa tất cả các file trong: {folder_path}")
    else:
        os.makedirs(folder_path, exist_ok=True)
        print(f"Đã tạo thư mục: {folder_path}")

def generate_random_name():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

def process_armor_items():
    contents_folder = "pack/contents"
    storage_folder = "pack/storage"
    
    print(f"Kiểm tra thư mục contents: {os.path.exists(contents_folder)}")
    print(f"Kiểm tra thư mục storage: {os.path.exists(storage_folder)}")
    
    if not os.path.exists(contents_folder):
        print(f"Thư mục không tồn tại: {contents_folder}")
        return
    
    if not os.path.exists(storage_folder):
        print(f"Thư mục không tồn tại: {storage_folder}")
        return
    
    yml_path = "pack/storage/items_ids_cache.yml"
    
    print(f"Kiểm tra file yml: {os.path.exists(yml_path)}")
    
    if not os.path.exists(yml_path):
        print(f"File không tồn tại: {yml_path}")
        return
    
    with open(yml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"Đã đọc file yml, kích thước: {len(content)} bytes")
    
    # In ra 500 ký tự đầu để xem format
    print("=== 500 ký tự đầu của file ===")
    print(content[:500])
    print("=== Kết thúc preview ===")
    
    # Tìm một ví dụ helmet để test
    helmet_sample = content[content.find("helmet"):content.find("helmet")+100] if "helmet" in content else "Không tìm thấy helmet"
    print(f"=== Mẫu helmet: {helmet_sample} ===")
    
    # Pattern mới cho format: namespace:item_name: số
    # Ví dụ: plny_luminite_set:luminite_sethelmet: 10017
    armor_patterns = [
        r'(\S+?):([\w]+helmet):\s*(\d+)',
        r'(\S+?):([\w]+chestplate):\s*(\d+)',
        r'(\S+?):([\w]+leggings):\s*(\d+)',
        r'(\S+?):([\w]+boots):\s*(\d+)'
    ]
    
    armor_items = []
    for pattern in armor_patterns:
        matches = re.findall(pattern, content)
        armor_items.extend(matches)
    
    print(f"Tìm thấy {len(armor_items)} armor items")
    
    cit_folder = "pack/assets/minecraft/optifine/cit/ia_generated_armors"
    os.makedirs(cit_folder, exist_ok=True)
    
    # Quét đệ quy tất cả file yml trong contents
    yml_files = []
    for root, dirs, files in os.walk(contents_folder):
        for file in files:
            if file.endswith('.yml'):
                yml_files.append(os.path.join(root, file))
    
    print(f"\nTìm thấy {len(yml_files)} file yml trong {contents_folder} (đệ quy):")
    for yml_file in yml_files[:5]:  # In ra 5 file đầu
        print(f"  - {yml_file}")
    
    # Đọc thử 1 file yml để xem cấu trúc
    if yml_files:
        sample_yml = yml_files[0]
        print(f"\n=== Cấu trúc file mẫu: {os.path.basename(sample_yml)} ===")
        try:
            with open(sample_yml, 'r', encoding='utf-8') as f:
                sample_data = yaml.safe_load(f)
            print(f"Keys: {list(sample_data.keys()) if sample_data else 'None'}")
            if sample_data and 'items' in sample_data:
                items_list = list(sample_data['items'].keys())[:5]
                print(f"Items (5 đầu): {items_list}")
        except Exception as e:
            print(f"Lỗi đọc file mẫu: {e}")
        print("=== Kết thúc cấu trúc file mẫu ===\n")
    
    for namespace, item_name, custom_model_data in armor_items:
        file_name = f"{namespace}_{item_name}"
        
        print(f"\n--- Xử lý: {file_name} ---")
        
        found_layers = False
        random_name = None
        
        for yml_file_path in yml_files:
                
                try:
                    with open(yml_file_path, 'r', encoding='utf-8') as f:
                        yml_data = yaml.safe_load(f)
                    
                    if yml_data and 'info' in yml_data and 'items' in yml_data:
                        if item_name in yml_data['items']:
                            print(f"Tìm thấy '{item_name}' trong file: {yml_file_path}")
                            
                            if 'armors_rendering' in yml_data:
                                print(f"  Có armors_rendering")
                                for armor_key, armor_data in yml_data['armors_rendering'].items():
                                    if 'layer_1' in armor_data and 'layer_2' in armor_data:
                                        layer_1 = armor_data['layer_1']
                                        layer_2 = armor_data['layer_2']
                                        
                                        print(f"  Tìm thấy layers: {layer_1}, {layer_2}")
                                        
                                        layer_1_name = layer_1.split('/')[-1]
                                        layer_2_name = layer_2.split('/')[-1]
                                        
                                        random_name = generate_random_name()
                                        
                                        new_layer_1 = f"{random_name}_1"
                                        new_layer_2 = f"{random_name}_2"
                                        
                                        layer_1_file = os.path.join(cit_folder, f"{new_layer_1}.png")
                                        layer_2_file = os.path.join(cit_folder, f"{new_layer_2}.png")
                                        
                                        with open(layer_1_file, 'w', encoding='utf-8') as f:
                                            f.write("")
                                        with open(layer_2_file, 'w', encoding='utf-8') as f:
                                            f.write("")
                                        
                                        print(f"  Layer 1: {layer_1_name} -> {new_layer_1}.png")
                                        print(f"  Layer 2: {layer_2_name} -> {new_layer_2}.png")
                                        
                                        found_layers = True
                                        break
                            
                            if not found_layers and 'equipments' in yml_data:
                                print(f"  Có equipments")
                                for equip_key, equip_data in yml_data['equipments'].items():
                                    if 'layer_1' in equip_data and 'layer_2' in equip_data:
                                        layer_1 = equip_data['layer_1']
                                        layer_2 = equip_data['layer_2']
                                        
                                        print(f"  Tìm thấy layers: {layer_1}, {layer_2}")
                                        
                                        layer_1_name = layer_1.split('/')[-1]
                                        layer_2_name = layer_2.split('/')[-1]
                                        
                                        random_name = generate_random_name()
                                        
                                        new_layer_1 = f"{random_name}_1"
                                        new_layer_2 = f"{random_name}_2"
                                        
                                        layer_1_file = os.path.join(cit_folder, f"{new_layer_1}.png")
                                        layer_2_file = os.path.join(cit_folder, f"{new_layer_2}.png")
                                        
                                        with open(layer_1_file, 'w', encoding='utf-8') as f:
                                            f.write("")
                                        with open(layer_2_file, 'w', encoding='utf-8') as f:
                                            f.write("")
                                        
                                        print(f"  Layer 1: {layer_1_name} -> {new_layer_1}.png")
                                        print(f"  Layer 2: {layer_2_name} -> {new_layer_2}.png")
                                        
                                        found_layers = True
                                        break
                            
                            if found_layers:
                                break
                except Exception as e:
                    print(f"  Lỗi khi đọc {yml_file}: {e}")
                    pass
        
        if found_layers and random_name:
            properties_file = os.path.join(cit_folder, f"{file_name}.properties")
            
            with open(properties_file, 'w', encoding='utf-8') as f:
                f.write(f"texture.leather_layer_1={random_name}_1.png\n")
                f.write(f"texture.leather_layer_2={random_name}_2.png\n")
            
            print(f"Đã tạo file: {properties_file}")
        else:
            print(f"  Không tìm thấy layers cho {item_name}")

if __name__ == "__main__":
    remove_ia_generated_armors()
    process_armor_items()
