import zipfile, os, subprocess

with zipfile.ZipFile("staging/input_pack.zip", "r") as file:
    file.extractall("pack/")

all_items_enabled = os.getenv("ALL_ITEMS_CONVERSION") == "true"
all_items_non_offhand_enabled = os.getenv("ALL_ITEMS_NON_OFFHAND_CONVERSION") == "true"

try:
    if os.getenv("ITEM_CONVERSION") == "true" or all_items_enabled: 
        import item
except Exception as e: pass
try:
    if os.getenv("ITEM_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled: 
        import item_non_offhand
except Exception as e: pass
try:
    if os.getenv("ARMOR_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled: 
        import armor
except Exception as e: pass
try:
    if os.getenv("FONT_CONVERSION") == "true": import font
except Exception as e: pass
try:
    if os.getenv("BOW_CONVERSION") == "true" or all_items_enabled: import bow
except Exception as e: pass
try:
    if os.getenv("BOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled: 
        import bow_non_offhand
except Exception as e: pass
try:
    if os.getenv("CROSSBOW_CONVERSION") == "true" or all_items_enabled: 
        import crossbow
except Exception as e: pass
try:
    if os.getenv("CROSSBOW_NON_OFFHAND_CONVERSION") == "true" or all_items_non_offhand_enabled: 
        import crossbow_non_offhand
except Exception as e: pass
try:
    if os.getenv("SHIELD_CONVERSION") == "true" or all_items_enabled or all_items_non_offhand_enabled: import shield
except Exception as e: pass
try:
    if os.getenv("BLOCK_CONVERSION") == "true": import blocks
except Exception as e: pass
try:
    if os.getenv("SOUND_CONVERSION") == "true": import sound
except Exception as e: pass
try:
    if os.getenv("ANIMATION_2D_CONVERSION") == "true":
        result = subprocess.run(["python", "animations/anim_2d.py"], capture_output=True, text=True)
        print("=== ANIMATION_2D_CONVERSION Output ===")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        print(f"Return code: {result.returncode}")
except Exception as e: 
    print(f"Error running anim_2d.py: {e}")
    pass
try:
    if os.getenv("GUI_CONVERSION") == "true":
        result = subprocess.run(["python", "other/gui.py"], capture_output=True, text=True)
except Exception as e: 
    pass
try:
    result = subprocess.run(["python", "other/remove.py"], capture_output=True, text=True)
except Exception as e: 
    pass
try:
    result = subprocess.run(["python", "other/auto_sprites.py"], capture_output=True, text=True)
except Exception as e: pass

try:
    if os.getenv("ITEM_MODEL") == "true":
        import sys
        sys.path.insert(0, 'other')
        import mappings
except Exception as e: pass

try:
    result = subprocess.run(["python", "other/resize_armor.py"], capture_output=True, text=True)
except Exception as e: 
    pass

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

try:
    other_conversion = os.getenv("OTHER_CONVERSION", "")
    if "turn on all" in other_conversion.lower() or "Turn on all" in other_conversion:
        result1 = subprocess.run(["python", "other/animations_clear.py"], capture_output=True, text=True)
        result2 = subprocess.run(["python", "other/group_resolve.py"], capture_output=True, text=True)
        result3 = subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True)
        result4 = subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True)
        result5 = subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
    else:
        if "clear animation folders" in other_conversion.lower() or "Clear animation folders" in other_conversion:
            result = subprocess.run(["python", "other/animations_clear.py"], capture_output=True, text=True)
        if "resolve groups" in other_conversion.lower() or "Resolve groups" in other_conversion:
            result = subprocess.run(["python", "other/group_resolve.py"], capture_output=True, text=True)
        if "merge json models" in other_conversion.lower() or "Merge json models" in other_conversion:
            result = subprocess.run(["python", "other/merge_models.py"], capture_output=True, text=True)
        if "random name json" in other_conversion.lower() or "Random name json" in other_conversion:
            result = subprocess.run(["python", "other/random_name.py"], capture_output=True, text=True)
        if "attachable dupe" in other_conversion.lower() or "Attachable dupe" in other_conversion:
            result = subprocess.run(["python", "other/attachables_dupe.py"], capture_output=True, text=True)
except Exception as e: 
    pass


