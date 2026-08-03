"""
Upper Body Layer Slicer for Astra Avatar Engine:
1. neck.png (isolated neck segment)
2. torso.png (hoodie body only — chest, zipper, logo, hood, waist belt — NO arms baked in)
3. upper_arm_L.png & upper_arm_R.png (shoulder to elbow sleeve fabric)
4. lower_arm_L.png & lower_arm_R.png (elbow to wrist sleeve fabric + cuff)
5. hand_L.png & hand_R.png (wrist to fingertips)

Updates sprite_manifest.json with exact joint anchors, z-indices, and parent hierarchy.
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

def slice_upper_body():
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

    # ── 1. NECK (neck.png) ──
    neck_arr = np.zeros_like(arr)
    neck_mask = (grid_y >= 212) & (grid_y <= 242) & (grid_x >= 250) & (grid_x <= 326)
    neck_arr[neck_mask] = arr[neck_mask]
    Image.fromarray(neck_arr).save(os.path.join(OUTPUT_DIR, "neck.png"))
    print("Saved neck.png")

    # ── 2. TORSO (torso.png) ──
    # Full hoodie jacket body width including waist belt (X: 195 to 380, Y: 225 to 428)
    torso_arr = np.zeros_like(arr)
    torso_mask = (grid_y >= 225) & (grid_y <= 428) & (grid_x >= 195) & (grid_x <= 380)
    
    # Exclude arm sleeve regions above Y=390 (sleeve fabric belongs to upper_arm_L and upper_arm_R)
    sleeve_L_box = (grid_y >= 235) & (grid_y <= 390) & (grid_x < 215)
    sleeve_R_box = (grid_y >= 235) & (grid_y <= 390) & (grid_x > 356)
    
    final_torso_mask = torso_mask & (~sleeve_L_box) & (~sleeve_R_box)
    torso_arr[final_torso_mask] = arr[final_torso_mask]
    Image.fromarray(torso_arr).save(os.path.join(OUTPUT_DIR, "torso.png"))
    print("Saved torso.png (clean hoodie body with waist belt)")

    # ── 3. UPPER ARM LEFT (upper_arm_L.png) ──
    u_arm_L_arr = np.zeros_like(arr)
    u_arm_L_mask = (grid_y >= 235) & (grid_y <= 392) & (grid_x >= 160) & (grid_x <= 222)
    u_arm_L_arr[u_arm_L_mask] = arr[u_arm_L_mask]
    Image.fromarray(u_arm_L_arr).save(os.path.join(OUTPUT_DIR, "upper_arm_L.png"))
    print("Saved upper_arm_L.png")

    # ── 4. UPPER ARM RIGHT (upper_arm_R.png) ──
    u_arm_R_arr = np.zeros_like(arr)
    u_arm_R_mask = (grid_y >= 235) & (grid_y <= 392) & (grid_x >= 354) & (grid_x <= 416)
    u_arm_R_arr[u_arm_R_mask] = arr[u_arm_R_mask]
    Image.fromarray(u_arm_R_arr).save(os.path.join(OUTPUT_DIR, "upper_arm_R.png"))
    print("Saved upper_arm_R.png")

    # ── 5. LOWER ARM LEFT (lower_arm_L.png) ──
    l_arm_L_arr = np.zeros_like(arr)
    l_arm_L_mask = (grid_y >= 388) & (grid_y <= 478) & (grid_x >= 160) & (grid_x <= 205)
    l_arm_L_arr[l_arm_L_mask] = arr[l_arm_L_mask]
    Image.fromarray(l_arm_L_arr).save(os.path.join(OUTPUT_DIR, "lower_arm_L.png"))
    print("Saved lower_arm_L.png")

    # ── 6. LOWER ARM RIGHT (lower_arm_R.png) ──
    l_arm_R_arr = np.zeros_like(arr)
    l_arm_R_mask = (grid_y >= 388) & (grid_y <= 478) & (grid_x >= 370) & (grid_x <= 416)
    l_arm_R_arr[l_arm_R_mask] = arr[l_arm_R_mask]
    Image.fromarray(l_arm_R_arr).save(os.path.join(OUTPUT_DIR, "lower_arm_R.png"))
    print("Saved lower_arm_R.png")

    # ── 7. HAND LEFT (hand_L.png) ──
    hand_L_arr = np.zeros_like(arr)
    hand_L_mask = (grid_y >= 475) & (grid_y <= 540) & (grid_x >= 160) & (grid_x <= 198)
    hand_L_arr[hand_L_mask] = arr[hand_L_mask]
    Image.fromarray(hand_L_arr).save(os.path.join(OUTPUT_DIR, "hand_L.png"))
    print("Saved hand_L.png")

    # ── 8. HAND RIGHT (hand_R.png) ──
    hand_R_arr = np.zeros_like(arr)
    hand_R_mask = (grid_y >= 475) & (grid_y <= 540) & (grid_x >= 376) & (grid_x <= 418)
    hand_R_arr[hand_R_mask] = arr[hand_R_mask]
    Image.fromarray(hand_R_arr).save(os.path.join(OUTPUT_DIR, "hand_R.png"))
    print("Saved hand_R.png")

    # ── 9. UPDATE MANIFEST (sprite_manifest.json) ──
    manifest_path = os.path.join(OUTPUT_DIR, "sprite_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    layers = manifest.get("layers", {})

    upper_body_layers = {
        "torso": {
            "file": "torso.png",
            "anchor": [288, 238],
            "z_index": 15,
            "parent": "root"
        },
        "neck": {
            "file": "neck.png",
            "anchor": [288, 225],
            "z_index": 18,
            "parent": "torso"
        },
        "upper_arm_L": {
            "file": "upper_arm_L.png",
            "anchor": [210, 245],
            "z_index": 25,
            "parent": "torso"
        },
        "upper_arm_R": {
            "file": "upper_arm_R.png",
            "anchor": [366, 245],
            "z_index": 25,
            "parent": "torso"
        },
        "lower_arm_L": {
            "file": "lower_arm_L.png",
            "anchor": [188, 388],
            "z_index": 35,
            "parent": "upper_arm_L"
        },
        "lower_arm_R": {
            "file": "lower_arm_R.png",
            "anchor": [388, 388],
            "z_index": 35,
            "parent": "upper_arm_R"
        },
        "hand_L": {
            "file": "hand_L.png",
            "anchor": [182, 478],
            "z_index": 45,
            "parent": "lower_arm_L"
        },
        "hand_R": {
            "file": "hand_R.png",
            "anchor": [394, 478],
            "z_index": 45,
            "parent": "lower_arm_R"
        }
    }

    layers.update(upper_body_layers)
    manifest["layers"] = layers

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Updated sprite_manifest.json with upper body layers.")

if __name__ == "__main__":
    slice_upper_body()
