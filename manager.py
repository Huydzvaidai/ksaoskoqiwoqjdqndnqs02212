import zipfile, os, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")

all_items_enabled = os.getenv("ALL_ITEMS_CONVERSION") == "true"
all_items_non_offhand_enabled = os.getenv("ALL_ITEMS_NON_OFFHAND_CONVERSION") == "true"

# Function to run conversion tasks
def run_task(task_func):
    try:
        task_func()
    except Exception as e:
        pass

# Define all conversion tasks as functions
def task_item():
    if os.getenv("ITEM_CONVERSION") == "true" or all_items_enabled:
        import item

def task_item_non_offhand():
    if os.getenv("ITEM_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled:
        import item_non_offhand

def task_layer_armor():
    subprocess.run(["python", "other/layer_armor.py"], capture_output=True, text=True)

def task_armor():
    if os.getenv("ARMOR_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled:
        import armor

def task_font():
    if os.getenv("FONT_CONVERSION") == "true":
        import font

def task_bow():
    if os.getenv("BOW_CONVERSION") == "true" or all_items_enabled:
        import bow

def task_bow_non_offhand():
    if os.getenv("BOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled:
        import bow_non_offhand

def task_crossbow():
    if os.getenv("CROSSBOW_CONVERSION") == "true" or all_items_enabled:
        import crossbow

def task_crossbow_non_offhand():
    if os.getenv("CROSSBOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled:
        import crossbow_non_offhand

def task_shield():
    if os.getenv("SHIELD_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled:
        import shield

def task_blocks():
    if os.getenv("BLOCK_CONVERSION") == "true":
        import blocks

def task_sound():
    if os.getenv("SOUND_CONVERSION") == "true":
        import sound

# Run main conversions in parallel (max 2 workers for 2 CPU)
tasks = [
    task_layer_armor,
    task_item,
    task_item_non_offhand,
    task_armor,
    task_font,
    task_bow,
    task_bow_non_offhand,
    task_crossbow,
    task_crossbow_non_offhand,
    task_shield,
    task_blocks,
    task_sound
]

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(run_task, task) for task in tasks]
    for future in as_completed(futures):
        future.result()

# Animation 2D (must run after main conversions)
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

# Post-processing tasks in parallel
def post_gui():
    if os.getenv("GUI_CONVERSION") == "true":
        subprocess.run(["python", "other/gui.py"], capture_output=True, text=True)

def post_remove():
    subprocess.run(["python", "other/remove.py"], capture_output=True, text=True)

def post_auto_sprites():
    subprocess.run(["python", "other/auto_sprites.py"], capture_output=True, text=True)

def post_mappings():
    if os.getenv("ITEM_MODEL") == "true":
        import sys
        sys.path.insert(0, 'other')
        import mappings

def post_icon_gen():
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

post_tasks = [post_gui, post_remove, post_auto_sprites, post_mappings, post_icon_gen]

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(run_task, task) for task in post_tasks]
    for future in as_completed(futures):
        future.result()

# OTHER_CONVERSION tasks in parallel
try:
    other_conversion = os.getenv("OTHER_CONVERSION", "")
    other_tasks = []
    
    if "turn on all" in other_conversion.lower() or "Turn on all" in other_conversion:
        other_tasks = [
            lambda: subprocess.run(["python", "other/animations_clear.py"], capture_output=True, text=True),
            lambda: subprocess.run(["python", "other/group_resolve.py"], capture_output=True, text=True),
            lambda: subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True),
            lambda: subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True),
            lambda: subprocess.run(["python", "other/directory_confusion.py"], capture_output=True, text=True),
            lambda: subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
        ]
    else:
        if "clear animation folders" in other_conversion.lower():
            other_tasks.append(lambda: subprocess.run(["python", "other/animations_clear.py"], capture_output=True, text=True))
        if "resolve groups" in other_conversion.lower():
            other_tasks.append(lambda: subprocess.run(["python", "other/group_resolve.py"], capture_output=True, text=True))
        if "merge json models" in other_conversion.lower():
            other_tasks.append(lambda: subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True))
        if "directory confusion" in other_conversion.lower():
            other_tasks.append(lambda: subprocess.run(["python", "other/directory_confusion.py"], capture_output=True, text=True))
        if "random name json" in other_conversion.lower():
            other_tasks.append(lambda: subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True))
        if "attachable dupe" in other_conversion.lower():
            other_tasks.append(lambda: subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True))
    
    if other_tasks:
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run_task, task) for task in other_tasks]
            for future in as_completed(futures):
                future.result()
except Exception as e: 
    pass


