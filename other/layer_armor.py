import os
import re
import yaml
import random
import string
import shutil

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
    
    # Pattern mới cho format: namespace:item_name: số
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
    
    print(f"\nTìm thấy {len(yml_files)} file yml trong {contents_folder} (đệ quy)")
    
    # Dictionary để lưu mapping layer_name -> random_name (tránh trùng lặp)
    layer_mapping = {}
    
    for namespace, item_name, custom_model_data in armor_items:
        file_name = f"{namespace}_{item_name}"
        
        found_layers = False
        random_name = None
        layer_1_original = None
        layer_2_original = None
        
        for yml_file_path in yml_files:
            try:
                with open(yml_file_path, 'r', encoding='utf-8') as f:
                    yml_data = yaml.safe_load(f)
                
                if yml_data and 'info' in yml_data and 'items' in yml_data:
                    if item_name in yml_data['items']:
                        
                        if 'armors_rendering' in yml_data:
                            for armor_key, armor_data in yml_data['armors_rendering'].items():
                                if 'layer_1' in armor_data and 'layer_2' in armor_data:
                                    layer_1_original = armor_data['layer_1']
                                    layer_2_original = armor_data['layer_2']
                                    found_layers = True
                                    break
                        
                        if not found_layers and 'equipments' in yml_data:
                            for equip_key, equip_data in yml_data['equipments'].items():
                                if 'layer_1' in equip_data and 'layer_2' in equip_data:
                                    layer_1_original = equip_data['layer_1']
                                    layer_2_original = equip_data['layer_2']
                                    found_layers = True
                                    break
                        
                        if found_layers:
                            break
            except Exception as e:
                pass
        
        if found_layers and layer_1_original and layer_2_original:
            layer_1_name = layer_1_original.split('/')[-1]
            layer_2_name = layer_2_original.split('/')[-1]
            
            # Kiểm tra xem layer này đã được xử lý chưa
            if layer_1_name not in layer_mapping:
                random_name = generate_random_name()
                layer_mapping[layer_1_name] = f"{random_name}_1"
                layer_mapping[layer_2_name] = f"{random_name}_2"
                
                # Tìm và copy file ảnh gốc
                layer_1_src = f"pack/{layer_1_original}.png"
                layer_2_src = f"pack/{layer_2_original}.png"
                
                layer_1_dst = os.path.join(cit_folder, f"{random_name}_1.png")
                layer_2_dst = os.path.join(cit_folder, f"{random_name}_2.png")
                
                if os.path.exists(layer_1_src):
                    shutil.copy2(layer_1_src, layer_1_dst)
                    print(f"Copy: {layer_1_src} -> {layer_1_dst}")
                
                if os.path.exists(layer_2_src):
                    shutil.copy2(layer_2_src, layer_2_dst)
                    print(f"Copy: {layer_2_src} -> {layer_2_dst}")
            else:
                random_name = layer_mapping[layer_1_name].replace("_1", "")
            
            # Tạo file .properties
            properties_file = os.path.join(cit_folder, f"{file_name}.properties")
            
            with open(properties_file, 'w', encoding='utf-8') as f:
                f.write(f"texture.leather_layer_1={random_name}_1.png\n")
                f.write(f"texture.leather_layer_2={random_name}_2.png\n")
            
            print(f"Đã tạo: {properties_file}")

if __name__ == "__main__":
    remove_ia_generated_armors()
    process_armor_items()
