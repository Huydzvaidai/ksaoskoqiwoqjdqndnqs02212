#!/usr/bin/env python3
import json
import os
import sys
import shutil
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional

def load_json(filepath: str) -> Optional[dict]:
    """Load JSON file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_json(filepath: str, data: dict):
    """Save JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, separators=(',', ':'))

def resolve_namespace(path: str) -> str:
    """Extract namespace from path"""
    return path.split(':')[0] if ':' in path else 'minecraft'

def resolve_model_path(parent: str, namespace: str = 'minecraft') -> str:
    """Convert model reference to file path"""
    ns = resolve_namespace(parent)
    model = parent.split(':')[1] if ':' in parent else parent
    return f"./assets/{ns}/models/{model}.json"

def resolve_texture_path(texture: str, namespace: str = 'minecraft') -> str:
    """Convert texture reference to file path"""
    ns = resolve_namespace(texture)
    tex = texture.split(':')[1] if ':' in texture else texture
    return f"./assets/{ns}/textures/{tex}.png"

def resolve_parental_chain(file_path: str, max_depth: int = 20) -> Tuple[Optional[dict], Optional[dict], Optional[dict], str]:
    """Resolve parental chain to get elements, textures, display"""
    elements = None
    textures = None
    display = None
    element_parent = file_path
    current_file = file_path
    depth = 0
    
    while depth < max_depth:
        data = load_json(current_file)
        if not data:
            break
        
        # Get missing properties
        if elements is None and 'elements' in data:
            elements = data['elements']
            element_parent = current_file
        
        if textures is None and 'textures' in data:
            textures = data['textures']
        
        if display is None and 'display' in data:
            display = data['display']
        
        # Check if we have everything
        if elements is not None and textures is not None and display is not None:
            break
        
        # Get parent
        parent = data.get('parent')
        if not parent:
            break
        
        # Check for generated model
        if parent == 'builtin/generated' or parent == 'minecraft:builtin/generated':
            break
        
        current_file = resolve_model_path(parent)
        depth += 1
    
    return elements, textures, display, element_parent

def process_single_model(args: Tuple[str, str, str, str, str, str, str]) -> Tuple[str, str, Optional[str], Optional[str]]:
    """Process a single model file
    Returns: (gid, status, icon_entry, error)
    status: 'success', 'generated', 'deleted'
    """
    file_path, gid, parental, namespace, model_path, model_name, path_hash = args
    
    try:
        # Load current file
        current_data = load_json(file_path)
        if not current_data:
            return gid, 'deleted', None, f"Failed to load {file_path}"
        
        # Get initial properties
        elements = current_data.get('elements')
        textures = current_data.get('textures')
        display = current_data.get('display')
        
        # If missing properties, resolve parental chain
        if elements is None or textures is None or display is None:
            p_elements, p_textures, p_display, element_parent = resolve_parental_chain(file_path)
            
            if elements is None:
                elements = p_elements
            if textures is None:
                textures = p_textures
            if display is None:
                display = p_display
        
        # Check if this is a 2D generated model
        parent = current_data.get('parent', '')
        is_generated = parent in ['builtin/generated', 'minecraft:builtin/generated']
        
        # Handle 2D generated models
        if is_generated and textures and elements is None:
            # Get first texture
            texture_0 = None
            if isinstance(textures, dict):
                first_key = list(textures.keys())[0] if textures else None
                if first_key:
                    texture_ref = textures[first_key]
                    texture_0 = resolve_texture_path(texture_ref, namespace)
            
            if texture_0 and os.path.exists(texture_0):
                # Save 2D model
                resolved = {'textures': textures}
                if display:
                    resolved['display'] = display
                save_json(file_path, resolved)
                
                # Copy texture to target
                target_dir = f"./target/rp/textures/{namespace}/{model_path}"
                os.makedirs(target_dir, exist_ok=True)
                
                target_file = f"{target_dir}/{model_name}.png"
                shutil.copy2(texture_0, target_file)
                
                # Create icon entry
                icon_path = f"textures/{namespace}/{model_path}/{model_name}".replace('//', '/')
                icon_entry = f"{path_hash},{icon_path}"
                
                return gid, 'generated', icon_entry, None
            else:
                return gid, 'deleted', None, f"Texture not found for 2D model {gid}"
        
        # Handle 3D models
        if elements is not None and textures is not None:
            resolved = {
                'textures': textures,
                'elements': elements
            }
            if display is not None:
                resolved['display'] = display
            
            save_json(file_path, resolved)
            return gid, 'success', None, None
        
        # No valid data
        return gid, 'deleted', None, f"No valid data for {gid}"
    
    except Exception as e:
        return gid, 'deleted', None, str(e)

def process_models_parallel(csv_file: str, workers: int = None) -> Dict[str, str]:
    """Process all models in parallel
    Returns dict of gid -> status ('success', 'generated', 'deleted')
    """
    if workers is None:
        workers = max(1, os.cpu_count() - 1)
    
    # Read CSV
    tasks = []
    with open(csv_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 7:
                tasks.append(tuple(parts))
    
    total = len(tasks)
    results = {}
    icons = []
    generated = []
    deleted = []
    completed = 0
    
    print(f"Processing {total} models with {workers} workers...")
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_single_model, task): task for task in tasks}
        
        for future in as_completed(futures):
            gid, status, icon_entry, error = future.result()
            results[gid] = status
            completed += 1
            
            # Collect outputs
            if status == 'generated':
                generated.append(gid)
                if icon_entry:
                    icons.append(icon_entry)
            elif status == 'deleted':
                deleted.append(gid)
            
            if completed % 10 == 0 or completed == total:
                progress = (completed * 100) // total
                print(f"\rProgress: {completed}/{total} ({progress}%)", end='', flush=True)
            
            if error:
                print(f"\n[WARNING] {gid}: {error}", file=sys.stderr)
    
    print("\nProcessing complete!")
    
    # Write output files
    scratch_dir = os.path.dirname(csv_file)
    
    if icons:
        with open(f"{scratch_dir}/icons.csv", 'w') as f:
            f.write('\n'.join(icons))
        print(f"Created icons.csv with {len(icons)} entries")
    
    if generated:
        with open(f"{scratch_dir}/generated.csv", 'w') as f:
            f.write('\n'.join(generated))
        print(f"Created generated.csv with {len(generated)} entries")
    
    if deleted:
        with open(f"{scratch_dir}/deleted.csv", 'w') as f:
            f.write('\n'.join(deleted))
        print(f"Created deleted.csv with {len(deleted)} entries")
    
    # Create count.csv for progress tracking
    with open(f"{scratch_dir}/count.csv", 'w') as f:
        f.write('\n' * total)
    
    success_count = sum(1 for v in results.values() if v in ['success', 'generated'])
    print(f"\nResults: {success_count} successful, {len(deleted)} deleted")
    
    return results

def generate_initial_config(item_models_dir: str, item_texture_file: str, item_mappings_file: str, output_file: str):
    """Generate initial config.json from item models"""
    print("Generating initial config...")
    
    # Load mappings
    item_texture = load_json(item_texture_file) or {}
    item_mappings = load_json(item_mappings_file) or {}
    
    # Build max damage lookup
    max_damage = {}
    for key, value in item_mappings.items():
        if isinstance(value, dict) and 'max_damage' in value:
            item_name = key.split(':')[1] if ':' in key else key
            max_damage[item_name] = value['max_damage']
    
    config = {}
    counter = 1
    
    # Process all item models
    for json_file in Path(item_models_dir).glob('*.json'):
        if json_file.name == 'potion.json':
            continue
        
        item_name = json_file.stem
        data = load_json(str(json_file))
        
        if not data or 'overrides' not in data:
            continue
        
        for override in data['overrides']:
            predicate = override.get('predicate', {})
            model = override.get('model', '')
            
            # Check if has custom_model_data or damage
            if not any(k in predicate for k in ['custom_model_data', 'damage', 'damaged']):
                continue
            
            # Build NBT
            nbt = {}
            
            if 'damage' in predicate:
                max_dur = max_damage.get(item_name, 1)
                nbt['Damage'] = int(predicate['damage'] * max_dur + 0.5)
            
            if 'damaged' in predicate and predicate['damaged'] == 0:
                nbt['Unbreakable'] = True
            
            if 'custom_model_data' in predicate:
                nbt['CustomModelData'] = predicate['custom_model_data']
            
            # Get bedrock icon
            bedrock_icon = item_texture.get(item_name, {"icon": "camera", "frame": 0})
            
            # Parse model path
            ns = resolve_namespace(model)
            model_clean = model.split(':')[1] if ':' in model else model
            model_parts = model_clean.split('/')
            model_file = model_parts[-1]
            model_dir = '/'.join(model_parts[:-1]) if len(model_parts) > 1 else ''
            
            geyser_id = f"campfire_{counter}"
            
            entry = {
                "item": item_name,
                "bedrock_icon": bedrock_icon,
                "nbt": nbt,
                "path": f"./assets/{ns}/models/{model_clean}.json",
                "namespace": ns,
                "model_path": model_dir,
                "model_name": model_file,
                "generated": False,
                "geyserID": geyser_id
            }
            
            config[geyser_id] = entry
            counter += 1
    
    # Save config
    save_json(output_file, config)
    print(f"Generated config with {len(config)} entries")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fast_model_processor.py process <csv_file> [workers]")
        print("  python fast_model_processor.py generate <item_models_dir> <item_texture> <item_mappings> <output>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "process":
        csv_file = sys.argv[2]
        workers = int(sys.argv[3]) if len(sys.argv) > 3 else None
        results = process_models_parallel(csv_file, workers)
        
        success_count = sum(1 for v in results.values() if v in ['success', 'generated'])
        print(f"\nSuccessfully processed: {success_count}/{len(results)}")
        
        sys.exit(0)
    
    elif command == "generate":
        if len(sys.argv) < 6:
            print("Error: generate requires 4 arguments")
            sys.exit(1)
        
        item_models_dir = sys.argv[2]
        item_texture = sys.argv[3]
        item_mappings = sys.argv[4]
        output = sys.argv[5]
        
        generate_initial_config(item_models_dir, item_texture, item_mappings, output)
        sys.exit(0)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
