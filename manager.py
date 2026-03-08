import zipfile, os, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")

all_items_enabled = os.getenv("ALL_ITEMS_CONVERSION") == "true"
all_items_non_offhand_enabled = os.getenv("ALL_ITEMS_NON_OFFHAND_CONVERSION") == "true"

# Run layer_armor.py first (needed by armor conversion)
try:
    result = subprocess.run(["python", "other/layer_armor.py"], capture_output=True, text=True)
except Exception as e: 
    pass

# Define tasks that can run in parallel
parallel_tasks = []

def run_item_conversion():
    if os.getenv("ITEM_CONVERSION") == "true" or all_items_enabled:
        import item

def run_item_non_offhand():
    if os.getenv("ITEM_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled:
        import item_non_offhand

def run_armor_conversion():
    if os.getenv("ARMOR_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled:
        import armor

def run_font_conversion():
    if os.getenv("FONT_CONVERSION") == "true":
        import font

def run_bow_conversion():
    if os.getenv("BOW_CONVERSION") == "true" or all_items_enabled:
        import bow

def run_bow_non_offhand():
    if os.getenv("BOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled:
        import bow_non_offhand

def run_crossbow_conversion():
    if os.getenv("CROSSBOW_CONVERSION") == "true" or all_items_enabled:
        import crossbow

def run_crossbow_non_offhand():
    if os.getenv("CROSSBOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled:
        import crossbow_non_offhand

def run_shield_conversion():
    if os.getenv("SHIELD_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled:
        import shield

def run_block_conversion():
    if os.getenv("BLOCK_CONVERSION") == "true":
        import blocks

def run_sound_conversion():
    if os.getenv("SOUND_CONVERSION") == "true":
        import sound

# Execute conversions in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    
    try:
        futures.append(executor.submit(run_item_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_item_non_offhand))
    except: pass
    
    try:
        futures.append(executor.submit(run_armor_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_font_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_bow_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_bow_non_offhand))
    except: pass
    
    try:
        futures.append(executor.submit(run_crossbow_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_crossbow_non_offhand))
    except: pass
    
    try:
        futures.append(executor.submit(run_shield_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_block_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_sound_conversion))
    except: pass
    
    # Wait for all tasks to complete
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            pass

# Sequential tasks that must run after conversions
try:
    if os.getenv("ANIMATION_2D_CONVERSION") == "true":
        print("=== Starting ANIMATION_2D_CONVERSION ===")
        import sys
        sys.path.insert(0, 'animations')
        import anim_2d
        print("=== Finished ANIMATION_2D_CONVERSION ===")
except Exception as e: 
    print(f"Error in anim_2d: {e}")
    pass

# Run post-processing tasks in parallel
post_processing_tasks = []

def run_gui_conversion():
    if os.getenv("GUI_CONVERSION") == "true":
        subprocess.run(["python", "other/gui.py"], capture_output=True, text=True)

def run_remove():
    subprocess.run(["python", "other/remove.py"], capture_output=True, text=True)

def run_auto_sprites():
    subprocess.run(["python", "other/auto_sprites.py"], capture_output=True, text=True)

def run_item_model():
    if os.getenv("ITEM_MODEL") == "true":
        import sys
        sys.path.insert(0, 'other')
        import mappings

def run_generate_simple():
    result = subprocess.run(
        ["node", "tools/generate-simple.js"],
        cwd=".",
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        import shutil
        icon_source = "tools/generated_icons"
        targets = [
            "staging/target/rp/textures",
            "bedrock/textures"
        ]
        for target in targets:
            if os.path.exists(icon_source):
                for root, dirs, files in os.walk(icon_source):
                    for file in files:
                        if file.endswith('.png'):
                            src_path = os.path.join(root, file)
                            rel_path = os.path.relpath(src_path, icon_source)
                            dst_path = os.path.join(target, rel_path)
                            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                            shutil.copy2(src_path, dst_path)

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    
    try:
        futures.append(executor.submit(run_gui_conversion))
    except: pass
    
    try:
        futures.append(executor.submit(run_remove))
    except: pass
    
    try:
        futures.append(executor.submit(run_auto_sprites))
    except: pass
    
    try:
        futures.append(executor.submit(run_item_model))
    except: pass
    
    try:
        futures.append(executor.submit(run_generate_simple))
    except: pass
    
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            pass


# Run other conversion tasks
try:
    other_conversion = os.getenv("OTHER_CONVERSION", "")
    
    def run_animations_clear():
        subprocess.run(["python", "other/animations_clear.py"], capture_output=True, text=True)
    
    def run_group_resolve():
        subprocess.run(["python", "other/group_resolve.py"], capture_output=True, text=True)
    
    def run_merge_models():
        subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True)
    
    def run_attachables_dupe():
        subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True)
    
    def run_directory_confusion():
        subprocess.run(["python", "other/directory_confusion.py"], capture_output=True, text=True)
    
    def run_random_name():
        subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
    
    if "turn on all" in other_conversion.lower() or "Turn on all" in other_conversion:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(run_animations_clear),
                executor.submit(run_group_resolve),
                executor.submit(run_merge_models),
                executor.submit(run_attachables_dupe),
                executor.submit(run_directory_confusion),
                executor.submit(run_random_name)
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except: pass
    else:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            
            if "clear animation folders" in other_conversion.lower() or "Clear animation folders" in other_conversion:
                futures.append(executor.submit(run_animations_clear))
            if "resolve groups" in other_conversion.lower() or "Resolve groups" in other_conversion:
                futures.append(executor.submit(run_group_resolve))
            if "merge json models" in other_conversion.lower() or "Merge json models" in other_conversion:
                futures.append(executor.submit(run_merge_models))
            if "directory confusion" in other_conversion.lower() or "Directory Confusion" in other_conversion:
                futures.append(executor.submit(run_directory_confusion))
            if "random name json" in other_conversion.lower() or "Random name json" in other_conversion:
                futures.append(executor.submit(run_random_name))
            if "attachable dupe" in other_conversion.lower() or "Attachable dupe" in other_conversion:
                futures.append(executor.submit(run_attachables_dupe))
            
            for future in as_completed(futures):
                try:
                    future.result()
                except: pass
except Exception as e: 
    pass


