import zipfile, os, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")

all_items_enabled = os.getenv("ALL_ITEMS_CONVERSION") == "true"
all_items_non_offhand_enabled = os.getenv("ALL_ITEMS_NON_OFFHAND_CONVERSION") == "true"

# Parallel conversion tasks
def run_conversion_task(task_name, condition, import_name=None, script_path=None):
    try:
        if condition:
            if import_name:
                __import__(import_name)
            elif script_path:
                subprocess.run(["python", script_path], capture_output=True, text=True)
    except Exception as e:
        pass

# Define conversion tasks
conversion_tasks = [
    ("layer_armor", True, None, "other/layer_armor.py"),
    ("item", os.getenv("ITEM_CONVERSION") == "true" or all_items_enabled, "item", None),
    ("item_non_offhand", os.getenv("ITEM_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled, "item_non_offhand", None),
    ("armor", os.getenv("ARMOR_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled, "armor", None),
    ("font", os.getenv("FONT_CONVERSION") == "true", "font", None),
    ("bow", os.getenv("BOW_CONVERSION") == "true" or all_items_enabled, "bow", None),
    ("bow_non_offhand", os.getenv("BOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled, "bow_non_offhand", None),
    ("crossbow", os.getenv("CROSSBOW_CONVERSION") == "true" or all_items_enabled, "crossbow", None),
    ("crossbow_non_offhand", os.getenv("CROSSBOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled, "crossbow_non_offhand", None),
    ("shield", os.getenv("SHIELD_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled, "shield", None),
    ("blocks", os.getenv("BLOCK_CONVERSION") == "true", "blocks", None),
    ("sound", os.getenv("SOUND_CONVERSION") == "true", "sound", None),
]

# Run conversions in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for task_name, condition, import_name, script_path in conversion_tasks:
        if condition:
            future = executor.submit(run_conversion_task, task_name, condition, import_name, script_path)
            futures.append(future)
    
    for future in as_completed(futures):
        future.result()
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

# Parallel post-processing tasks
def run_post_task(script_path):
    try:
        subprocess.run(["python", script_path], capture_output=True, text=True)
    except Exception as e:
        pass

def run_mappings():
    try:
        if os.getenv("ITEM_MODEL") == "true":
            import sys
            sys.path.insert(0, 'other')
            import mappings
    except Exception as e:
        pass

def run_icon_generator():
    try:
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
    except Exception as e:
        pass

post_tasks = [
    "other/gui.py" if os.getenv("GUI_CONVERSION") == "true" else None,
    "other/remove.py",
    "other/auto_sprites.py",
]

# Run post-processing, mappings, and icon generation in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = []
    
    # Post tasks
    for task in post_tasks:
        if task:
            futures.append(executor.submit(run_post_task, task))
    
    # Mappings
    futures.append(executor.submit(run_mappings))
    
    # Icon generator
    futures.append(executor.submit(run_icon_generator))
    
    for future in as_completed(futures):
        future.result()

# Parallel OTHER_CONVERSION tasks
try:
    other_conversion = os.getenv("OTHER_CONVERSION", "")
    other_tasks = []
    
    if "turn on all" in other_conversion.lower() or "Turn on all" in other_conversion:
        other_tasks = [
            "other/animations_clear.py",
            "other/group_resolve.py",
            "other/merge_models.py",
            "other/attachables_dupe.py",
            "other/directory_confusion.py",
            "other/random_name.py"
        ]
    else:
        if "clear animation folders" in other_conversion.lower():
            other_tasks.append("other/animations_clear.py")
        if "resolve groups" in other_conversion.lower():
            other_tasks.append("other/group_resolve.py")
        if "merge json models" in other_conversion.lower():
            other_tasks.append("other/merge_models.py")
        if "directory confusion" in other_conversion.lower():
            other_tasks.append("other/directory_confusion.py")
        if "random name json" in other_conversion.lower():
            other_tasks.append("other/random_name.py")
        if "attachable dupe" in other_conversion.lower():
            other_tasks.append("other/attachables_dupe.py")
    
    if other_tasks:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(run_post_task, task) for task in other_tasks]
            for future in as_completed(futures):
                future.result()
except Exception as e: 
    pass


