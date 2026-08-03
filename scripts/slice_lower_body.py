"""
Refined Lower Body Layer Slicer for Astra Avatar Engine (Phase 0 Final Chunk):
1. hip.png (pelvis/waist segment — full width pants belt & hip area, ZERO legs/hands baked in)
2. leg_L.png & leg_R.png (thigh through ankle, pants fabric, ZERO shoes/hands baked in)
3. shoe_L.png & shoe_R.png (footwear only)

Updates sprite_manifest.json with all 16 layer categories (21 entries/files total).
"""

import os
import json
import numpy as np
from PIL import Image

SOURCE_IMAGE_PATH = r"C:\Users\rudra\OneDrive\Desktop\astra\app\avatar\renderer\assets\body_base.png"
OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "avatar", "renderer", "assets")
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def slice_lower_body():
    print(f"Loading base illustration from: {SOURCE_IMAGE_PATH}")
    src_raw = Image.open(SOURCE_IMAGE_PATH).convert("RGBA")
    W, H = src_raw.size  # (576, 1024)

    # Background removal -> RGBA
    arr_raw = np.array(src_raw)
    r, g, b, a = arr_raw[:, :, 0], arr_raw[:, :, 1], arr_raw[:, :, 2], arr_raw[:, :, 3]
    is_white = (r >= 238) & (g >= 238) & (b >= 238)
    arr_raw[is_white, 3] = 0
    char_rgba = Image.fromarray(arr_raw)
    arr = np.array(char_rgba)
    grid_y, grid_x = np.ogrid[:H, :W]

    # Hand pixels removal mask for lower body layers
    is_hand_L = (grid_x < 195) & (grid_y >= 470) & (grid_y <= 540)
    is_hand_R = (grid_x > 380) & (grid_y >= 470) & (grid_y <= 540)

    # ── 1. HIP (hip.png) ──
    # Full pelvis/waist segment width (Y: 410 to 525, X: 190 to 386)
    hip_arr = np.zeros_like(arr)
    hip_mask = (grid_y >= 410) & (grid_y <= 525) & (grid_x >= 190) & (grid_x <= 386) & (~is_hand_L) & (~is_hand_R)
    hip_arr[hip_mask] = arr[hip_mask]
    Image.fromarray(hip_arr).save(os.path.join(OUTPUT_DIR, "hip.png"))
    print("Saved hip.png (full width pelvis/waist segment)")

    # ── 2. LEG LEFT (leg_L.png) ──
    leg_L_arr = np.zeros_like(arr)
    leg_L_mask = (grid_y >= 515) & (grid_y <= 808) & (grid_x >= 185) & (grid_x <= 285) & (~is_hand_L)
    leg_L_arr[leg_L_mask] = arr[leg_L_mask]
    Image.fromarray(leg_L_arr).save(os.path.join(OUTPUT_DIR, "leg_L.png"))
    print("Saved leg_L.png (clean pants fabric)")

    # ── 3. LEG RIGHT (leg_R.png) ──
    leg_R_arr = np.zeros_like(arr)
    leg_R_mask = (grid_y >= 515) & (grid_y <= 808) & (grid_x >= 285) & (grid_x <= 390) & (~is_hand_R)
    leg_R_arr[leg_R_mask] = arr[leg_R_mask]
    Image.fromarray(leg_R_arr).save(os.path.join(OUTPUT_DIR, "leg_R.png"))
    print("Saved leg_R.png (clean pants fabric)")

    # ── 4. SHOE LEFT (shoe_L.png) ──
    shoe_L_arr = np.zeros_like(arr)
    shoe_L_mask = (grid_y >= 808) & (grid_y <= 960) & (grid_x >= 160) & (grid_x <= 275)
    shoe_L_arr[shoe_L_mask] = arr[shoe_L_mask]
    Image.fromarray(shoe_L_arr).save(os.path.join(OUTPUT_DIR, "shoe_L.png"))
    print("Saved shoe_L.png")

    # ── 5. SHOE RIGHT (shoe_R.png) ──
    shoe_R_arr = np.zeros_like(arr)
    shoe_R_mask = (grid_y >= 808) & (grid_y <= 965) & (grid_x >= 305) & (grid_x <= 415)
    shoe_R_arr[shoe_R_mask] = arr[shoe_R_mask]
    Image.fromarray(shoe_R_arr).save(os.path.join(OUTPUT_DIR, "shoe_R.png"))
    print("Saved shoe_R.png")

    # ── 6. UPDATE MANIFEST (sprite_manifest.json) ──
    manifest_path = os.path.join(OUTPUT_DIR, "sprite_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    layers = manifest.get("layers", {})

    lower_body_layers = {
        "hip": {
            "file": "hip.png",
            "anchor": [288, 420],
            "z_index": 5,
            "parent": "torso"
        },
        "leg_L": {
            "file": "leg_L.png",
            "anchor": [242, 520],
            "z_index": 8,
            "parent": "hip"
        },
        "leg_R": {
            "file": "leg_R.png",
            "anchor": [334, 520],
            "z_index": 8,
            "parent": "hip"
        },
        "shoe_L": {
            "file": "shoe_L.png",
            "anchor": [228, 808],
            "z_index": 62,
            "parent": "leg_L"
        },
        "shoe_R": {
            "file": "shoe_R.png",
            "anchor": [348, 810],
            "z_index": 62,
            "parent": "leg_R"
        }
    }

    layers.update(lower_body_layers)
    manifest["layers"] = layers

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Updated sprite_manifest.json with lower body layers.")

if __name__ == "__main__":
    slice_lower_body()
