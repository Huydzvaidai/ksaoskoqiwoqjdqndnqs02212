#!/usr/bin/env python3
"""
Java to Bedrock Resource Pack Converter
Fast Python implementation replacing converter.sh
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
import uuid
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
import urllib.request

# Color codes
class Colors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[36m'
    GRAY = '\033[37m'
    CLOSE = '\033[0m'

def status_message(msg_type: str, message: str):
    """Print colored status messages"""
    if msg_type == "completion":
        print(f"{Colors.GREEN}[+] {Colors.GRAY}{message}{Colors.CLOSE}")
    elif msg_type == "process":
        print(f"{Colors.YELLOW}[•] {Colors.GRAY}{message}{Colors.CLOSE}")
    elif msg_type == "critical":
        print(f"{Colors.RED}[X] {Colors.GRAY}{message}{Colors.CLOSE}")
    elif msg_type == "error":
        print(f"{Colors.RED}[ERROR] {Colors.GRAY}{message}{Colors.CLOSE}")
    elif msg_type == "info":
        print(f"{Colors.BLUE}{message}{Colors.CLOSE}")
    else:
        print(f"{Colors.GRAY}{message}{Colors.CLOSE}")

def load_json(filepath: str) -> Optional[dict]:
    """Load JSON file safely"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_json(filepath: str, data: dict, compact: bool = True):
    """Save JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        if compact:
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
        else:
            json.dump(data, f, indent=2, ensure_ascii=False)

def download_file(url: str, output: str):
    """Download file with progress"""
    status_message("process", f"Downloading {os.path.basename(output)}...")
    try:
        urllib.request.urlretrieve(url, output)
        status_message("completion", f"Downloaded {os.path.basename(output)}")
    except Exception as e:
        status_message("error", f"Failed to download: {e}")
        raise

def extract_zip(zip_path: str, extract_to: str = "."):
    """Extract zip file"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def create_zip(source_dir: str, output_path: str):
    """Create zip file from directory"""
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if file.startswith('.'):
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

def generate_uuid() -> str:
    """Generate UUID"""
    return str(uuid.uuid4())

def md5_hash(text: str, length: int = 7) -> str:
    """Generate MD5 hash"""
    return hashlib.md5(text.encode()).hexdigest()[:length]

class Converter:
    def __init__(self, args):
        self.args = args
        self.config = {}
        self.scratch_dir = Path("scratch_files")
        self.target_rp = Path("target/rp")
        self.target_bp = Path("target/bp")
        
    def run(self):
        """Main conversion process"""
        try:
            # Step 1: Setup
            self.setup()
            
            # Step 2: Extract input pack
            self.extract_input_pack()
            
            # Step 3: Check if valid pack
            if not self.check_valid_pack():
                return
            
            # Step 4: Download mappings
            self.download_mappings()
            
            # Step 5: Generate initial config
            self.generate_initial_config()
            
            # Step 6: Setup directories
            self.setup_directories()
            
            # Step 7: Download fallback resources
            if self.args.fallback_pack != 'none':
                self.download_fallback_resources()
            
            # Step 8: Process models
            self.process_models()
            
            # Step 9: Run manager.py
            self.run_manager()
            
            # Step 10: Package output
            self.package_output()
            
            status_message("completion", "Conversion complete!")
            
        except Exception as e:
            status_message("error", f"Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def setup(self):
        """Setup directories"""
        self.scratch_dir.mkdir(exist_ok=True)
        status_message("completion", "Setup complete")
    
    def extract_input_pack(self):
        """Extract input resource pack"""
        status_message("process", "Decompressing input pack")
        extract_zip(self.args.input_pack)
        
        # Remove potion.json if exists
        potion_path = Path("assets/minecraft/models/item/potion.json")
        if potion_path.exists():
            potion_path.unlink()
            status_message("completion", "Removed potion.json from processing")
        
        status_message("completion", "Input pack decompressed")
    
    def check_valid_pack(self) -> bool:
        """Check if pack.mcmeta exists"""
        if not Path("pack.mcmeta").exists():
            status_message("error", "Invalid resource pack! pack.mcmeta not found")
            return False
        return True
    
    def download_mappings(self):
        """Download Geyser mappings"""
        status_message("process", "Downloading Geyser item mappings")
        
        mappings_url = "https://raw.githubusercontent.com/GeyserMC/mappings/master/items.json"
        texture_url = "https://raw.githubusercontent.com/Kas-tle/java2bedrockMappings/main/item_texture.json"
        
        download_file(mappings_url, str(self.scratch_dir / "item_mappings.json"))
        download_file(texture_url, str(self.scratch_dir / "item_texture.json"))
    
    def generate_initial_config(self):
        """Generate initial config.json from item models"""
        status_message("process", "Generating initial predicate config")
        
        item_models_dir = Path("assets/minecraft/models/item")
        if not item_models_dir.exists():
            status_message("error", "Item models directory not found")
            return
        
        # Load mappings
        item_texture = load_json(str(self.scratch_dir / "item_texture.json")) or {}
        item_mappings = load_json(str(self.scratch_dir / "item_mappings.json")) or {}
        
        # Build max damage lookup
        max_damage = {}
        for key, value in item_mappings.items():
            if isinstance(value, dict) and 'max_damage' in value:
                item_name = key.split(':')[1] if ':' in key else key
                max_damage[item_name] = value['max_damage']
        
        config = {}
        counter = 1
        
        # Process all item models
        for json_file in item_models_dir.glob('*.json'):
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
                ns = model.split(':')[0] if ':' in model else 'minecraft'
                model_clean = model.split(':')[1] if ':' in model else model
                model_parts = model_clean.split('/')
                model_file = model_parts[-1]
                model_dir = '/'.join(model_parts[:-1]) if len(model_parts) > 1 else ''
                
                geyser_id = f"campfire_{counter}"
                
                # Generate hashes
                predicate_str = f"{item_name}_c{nbt.get('CustomModelData', '')}_d{nbt.get('Damage', '')}_u{nbt.get('Unbreakable', '')}"
                path_str = f"./assets/{ns}/models/{model_clean}.json"
                entry_hash = md5_hash(predicate_str)
                path_hash = md5_hash(path_str)
                
                entry = {
                    "item": item_name,
                    "bedrock_icon": bedrock_icon,
                    "nbt": nbt,
                    "path": path_str,
                    "namespace": ns,
                    "model_path": model_dir,
                    "model_name": model_file,
                    "generated": False,
                    "geyserID": geyser_id,
                    "path_hash": f"campfire_{entry_hash}",
                    "geometry": f"campfiregeo_{path_hash}"
                }
                
                config[geyser_id] = entry
                counter += 1
        
        # Filter out entries without existing files
        valid_config = {}
        for gid, entry in config.items():
            if Path(entry['path']).exists():
                valid_config[gid] = entry
        
        self.config = valid_config
        save_json("config.json", valid_config, compact=False)
        
        status_message("completion", f"Initial config generated with {len(valid_config)} entries")
    
    def setup_directories(self):
        """Create initial directory structure"""
        status_message("process", "Generating initial directory structure")
        
        dirs = [
            self.target_rp / "models/entity",
            self.target_rp / "textures",
            self.target_rp / "textures/layer_armor",
            self.target_rp / "attachables",
            self.target_rp / "animations",
            self.target_bp / "blocks",
            self.target_bp / "items"
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        # Copy pack icon
        if Path("pack.png").exists():
            shutil.copy("pack.png", self.target_rp / "pack_icon.png")
            shutil.copy("pack.png", self.target_bp / "pack_icon.png")
        
        # Generate UUIDs
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        uuid3 = generate_uuid()
        uuid4 = generate_uuid()
        
        # Get pack description
        pack_meta = load_json("pack.mcmeta") or {}
        pack_desc = "§fPack create by §a§lKaito §rDiscord §a@_jaysonmalon"
        
        # Generate RP manifest
        rp_manifest = {
            "format_version": 2,
            "header": {
                "description": "Made By Kaito",
                "name": pack_desc,
                "uuid": uuid1,
                "version": [3, 0, 0],
                "min_engine_version": [1, 21, 0]
            },
            "modules": [{
                "description": "Made By Kaito",
                "type": "resources",
                "uuid": uuid2,
                "version": [3, 0, 0]
            }]
        }
        save_json(str(self.target_rp / "manifest.json"), rp_manifest)
        
        # Generate BP manifest
        bp_manifest = {
            "format_version": 2,
            "header": {
                "description": "Adds 3D items for use with a Geyser proxy",
                "name": pack_desc,
                "uuid": uuid3,
                "version": [1, 0, 0],
                "min_engine_version": [1, 18, 3]
            },
            "modules": [{
                "description": "Adds 3D items for use with a Geyser proxy",
                "type": "data",
                "uuid": uuid4,
                "version": [1, 0, 0]
            }],
            "dependencies": [{
                "uuid": uuid1,
                "version": [1, 0, 0]
            }]
        }
        save_json(str(self.target_bp / "manifest.json"), bp_manifest)
        
        # Generate texture definitions
        terrain_texture = {
            "resource_pack_name": "geyser_custom",
            "texture_name": "atlas.terrain",
            "texture_data": {}
        }
        save_json(str(self.target_rp / "textures/terrain_texture.json"), terrain_texture)
        
        item_texture = {
            "resource_pack_name": "geyser_custom",
            "texture_name": "atlas.items",
            "texture_data": {}
        }
        save_json(str(self.target_rp / "textures/item_texture.json"), item_texture)
        
        # Generate disabling animation
        disable_anim = {
            "format_version": "1.8.0",
            "animations": {
                "animation.campfire.disable": {
                    "loop": True,
                    "override_previous_animation": True,
                    "bones": {
                        "campfire": {
                            "scale": 0
                        }
                    }
                }
            }
        }
        save_json(str(self.target_rp / "animations/animation.campfire.disable.json"), disable_anim)
        
        status_message("completion", "Directory structure created")
    
    def download_fallback_resources(self):
        """Download and merge fallback resources"""
        status_message("process", "Downloading fallback resources")
        
        version = self.args.default_asset_version or "1.21"
        url = f"https://github.com/InventivetalentDev/minecraft-assets/zipball/refs/tags/{version}"
        
        download_file(url, "default_assets.zip")
        
        # Extract
        extract_zip("default_assets.zip", "defaultassetholding")
        
        # Find root folder
        root_folders = list(Path("defaultassetholding").iterdir())
        if root_folders:
            root_folder = root_folders[0]
            
            # Copy textures and models
            src_textures = root_folder / "assets/minecraft/textures"
            src_models = root_folder / "assets/minecraft/models"
            
            dst_textures = Path("assets/minecraft/textures")
            dst_models = Path("assets/minecraft/models")
            
            if src_textures.exists():
                dst_textures.mkdir(parents=True, exist_ok=True)
                for item in src_textures.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(src_textures)
                        dst_file = dst_textures / rel_path
                        if not dst_file.exists():
                            dst_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dst_file)
            
            if src_models.exists():
                dst_models.mkdir(parents=True, exist_ok=True)
                for item in src_models.rglob('*'):
                    if item.is_file():
                        rel_path = item.relative_to(src_models)
                        dst_file = dst_models / rel_path
                        if not dst_file.exists():
                            dst_file.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dst_file)
        
        # Cleanup
        shutil.rmtree("defaultassetholding", ignore_errors=True)
        
        status_message("completion", "Fallback resources merged")
    
    def process_models(self):
        """Process parented models using fast Python processor"""
        status_message("process", "Processing parented models")
        
        # Generate pa.csv
        pa_csv = []
        for gid, entry in self.config.items():
            if 'parent' in entry or not Path(entry['path']).exists():
                continue
            
            data = load_json(entry['path'])
            if data and 'parent' in data:
                pa_csv.append(','.join([
                    entry['path'],
                    gid,
                    data['parent'],
                    entry['namespace'],
                    entry['model_path'],
                    entry['model_name'],
                    entry['path_hash']
                ]))
        
        if pa_csv:
            pa_csv_path = self.scratch_dir / "pa.csv"
            with open(pa_csv_path, 'w') as f:
                f.write('\n'.join(pa_csv))
            
            # Run fast processor
            result = subprocess.run([
                sys.executable,
                "tools/fast_model_processor.py",
                "process",
                str(pa_csv_path)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                status_message("completion", "Models processed successfully")
            else:
                status_message("error", f"Model processing failed: {result.stderr}")
        
        # Update config with generated models
        generated_csv = self.scratch_dir / "generated.csv"
        if generated_csv.exists():
            with open(generated_csv, 'r') as f:
                generated_ids = set(line.strip() for line in f)
            
            for gid in generated_ids:
                if gid in self.config:
                    self.config[gid]['generated'] = True
            
            save_json("config.json", self.config, compact=False)
        
        # Update item_texture.json with icons
        icons_csv = self.scratch_dir / "icons.csv"
        if icons_csv.exists():
            item_texture_path = self.target_rp / "textures/item_texture.json"
            item_texture = load_json(str(item_texture_path)) or {"texture_data": {}}
            
            with open(icons_csv, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        path_hash, texture_path = parts
                        item_texture['texture_data'][path_hash] = {
                            "textures": texture_path.replace('//', '/')
                        }
            
            save_json(str(item_texture_path), item_texture)
        
        # Delete unsuitable models from config
        deleted_csv = self.scratch_dir / "deleted.csv"
        if deleted_csv.exists():
            with open(deleted_csv, 'r') as f:
                deleted_ids = set(line.strip() for line in f)
            
            for gid in deleted_ids:
                self.config.pop(gid, None)
            
            save_json("config.json", self.config, compact=False)
    
    def run_manager(self):
        """Run manager.py for conversion"""
        status_message("process", "Running conversion manager")
        
        result = subprocess.run([sys.executable, "manager.py"], capture_output=True, text=True)
        
        if result.returncode != 0:
            status_message("error", f"Manager failed: {result.stderr}")
    
    def package_output(self):
        """Package output packs"""
        status_message("process", "Compressing output packs")
        
        # Create packaged directory
        packaged_dir = Path("target/packaged")
        packaged_dir.mkdir(parents=True, exist_ok=True)
        
        # Create RP pack
        create_zip(str(self.target_rp), str(packaged_dir / "geyser_resources_preview.mcpack"))
        
        # Create BP pack
        create_zip(str(self.target_bp), str(packaged_dir / "geyser_behaviors_preview.mcpack"))
        
        # Create addon
        create_zip(str(packaged_dir), "target/packaged/geyser_addon.mcaddon")
        
        # Create final bedrock pack
        create_zip(str(self.target_rp), "bedrock.mcpack")
        
        status_message("completion", "Output packs created")

def main():
    parser = argparse.ArgumentParser(description='Java to Bedrock Resource Pack Converter')
    parser.add_argument('input_pack', help='Input Java resource pack (zip file)')
    parser.add_argument('-w', '--warn', default='true', help='Show warning message')
    parser.add_argument('-m', '--merge_input', default='null', help='Existing bedrock pack to merge')
    parser.add_argument('-a', '--attachable_material', default='entity_alphatest_one_sided', help='Attachable material')
    parser.add_argument('-b', '--block_material', default='alpha_test', help='Block material')
    parser.add_argument('-f', '--fallback_pack', default='null', help='Fallback pack URL')
    parser.add_argument('-v', '--default_asset_version', default='1.21', help='Default asset version')
    parser.add_argument('-r', '--rename_model_files', default='false', help='Rename model files')
    parser.add_argument('-s', '--save_scratch', default='false', help='Save scratch files')
    parser.add_argument('-u', '--disable_ulimit', default='false', help='Disable ulimit')
    
    args = parser.parse_args()
    
    # Check if input pack exists
    if not os.path.exists(args.input_pack):
        status_message("error", f"Input pack {args.input_pack} not found")
        sys.exit(1)
    
    # Show warning
    if args.warn != 'false':
        print(f"{Colors.RED}")
        print("=" * 79)
        print(" " * 20 + "# <!> # W A R N I N G # <!> #")
        print("=" * 79)
        print("This script has been provided as is. If your resource pack does not")
        print("entirely conform the vanilla resource specification, there is a")
        print("strong possibility this script will fail.")
        print("=" * 79)
        print(f"{Colors.CLOSE}")
        input("Press Enter to continue or Ctrl+C to exit...")
    
    # Run converter
    converter = Converter(args)
    converter.run()

if __name__ == "__main__":
    main()
