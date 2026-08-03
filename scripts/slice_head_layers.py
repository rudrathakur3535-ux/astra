"""
Clean Head Layer Slicer for Astra Avatar Engine:
1. hair_back.png (complete rear hair volume, dark black + purple highlights)
2. face_base.png (clean face skin base, ZERO baked-in eyes/mouth/eyebrows, clean RGBA alpha)
3. eye_L.png & eye_R.png
4. eyebrow_L.png & eyebrow_R.png
5. mouth.png
6. hair_front.png (front hair bangs overlaying forehead & temples)
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

def slice_head_layers():
    print(f"Loading source character illustration from: {SOURCE_IMAGE_PATH}")
    src_img = Image.open(SOURCE_IMAGE_PATH).convert("RGBA")
    W, H = src_img.size  # (576, 1024)

    # Clean Background Removal (white canvas background -> alpha=0)
    arr_raw = np.array(src_img)
    r, g, b, a = arr_raw[:, :, 0], arr_raw[:, :, 1], arr_raw[:, :, 2], arr_raw[:, :, 3]
    is_white_bg = (r >= 235) & (g >= 235) & (b >= 235)
    arr_raw[is_white_bg, 3] = 0
    char_img = Image.fromarray(arr_raw)
    arr = np.array(char_img)

    grid_y, grid_x = np.ogrid[:H, :W]

    # Skin pixel identification
    head_hair_box = (grid_y <= 242) & (grid_x >= 180) & (grid_x <= 396) & (arr[:, :, 3] > 0)
    is_skin = (arr[:, :, 0] >= 160) & (arr[:, :, 1] >= 110) & (arr[:, :, 2] >= 90) & (arr[:, :, 0] >= arr[:, :, 1] + 8) & (arr[:, :, 3] > 0)
    is_hair = head_hair_box & (~is_skin)

    # ── 1. HAIR BACK (hair_back.png) ──
    hair_back_arr = np.zeros_like(arr)
    hair_back_arr[is_hair] = arr[is_hair]
    Image.fromarray(hair_back_arr).save(os.path.join(OUTPUT_DIR, "hair_back.png"))
    print("Saved hair_back.png (complete top/rear hair volume)")

    # ── 2. FACE BASE (face_base.png) ──
    face_base_arr = np.zeros_like(arr)
    head_box = (grid_y >= 80) & (grid_y <= 222) & (grid_x >= 224) & (grid_x <= 352) & (arr[:, :, 3] > 0)
    face_base_arr[head_box & is_skin] = arr[head_box & is_skin]

    # Feature inpainting regions
    eye_L = (grid_y >= 134) & (grid_y <= 165) & (grid_x >= 232) & (grid_x <= 266)
    eye_R = (grid_y >= 130) & (grid_y <= 162) & (grid_x >= 318) & (grid_x <= 350)
    eb_L = (grid_y >= 114) & (grid_y <= 130) & (grid_x >= 228) & (grid_x <= 254)
    eb_R = (grid_y >= 110) & (grid_y <= 126) & (grid_x >= 324) & (grid_x <= 348)
    mth = (grid_y >= 196) & (grid_y <= 214) & (grid_x >= 274) & (grid_x <= 302)

    features = eye_L | eye_R | eb_L | eb_R | mth
    for y in range(80, 223):
        for x in range(224, 353):
            if features[y, x] and head_box[y, x]:
                face_base_arr[y, x] = [251, 221, 200, 255]

    Image.fromarray(face_base_arr).save(os.path.join(OUTPUT_DIR, "face_base.png"))
    print("Saved face_base.png (clean face skin base)")

    # ── 3. EYES (eye_L.png, eye_R.png) ──
    eye_L_arr = np.zeros_like(arr)
    eye_L_mask = (grid_y >= 136) & (grid_y <= 164) & (grid_x >= 234) & (grid_x <= 264)
    eye_L_arr[eye_L_mask] = arr[eye_L_mask]
    Image.fromarray(eye_L_arr).save(os.path.join(OUTPUT_DIR, "eye_L.png"))
    print("Saved eye_L.png")

    eye_R_arr = np.zeros_like(arr)
    eye_R_mask = (grid_y >= 132) & (grid_y <= 160) & (grid_x >= 320) & (grid_x <= 348)
    eye_R_arr[eye_R_mask] = arr[eye_R_mask]
    Image.fromarray(eye_R_arr).save(os.path.join(OUTPUT_DIR, "eye_R.png"))
    print("Saved eye_R.png")

    # ── 4. EYEBROWS (eyebrow_L.png, eyebrow_R.png) ──
    eb_L_arr = np.zeros_like(arr)
    eb_L_mask = (grid_y >= 115) & (grid_y <= 130) & (grid_x >= 228) & (grid_x <= 252)
    eb_L_arr[eb_L_mask] = arr[eb_L_mask]
    Image.fromarray(eb_L_arr).save(os.path.join(OUTPUT_DIR, "eyebrow_L.png"))
    print("Saved eyebrow_L.png")

    eb_R_arr = np.zeros_like(arr)
    eb_R_mask = (grid_y >= 112) & (grid_y <= 126) & (grid_x >= 325) & (grid_x <= 348)
    eb_R_arr[eb_R_mask] = arr[eb_R_mask]
    Image.fromarray(eb_R_arr).save(os.path.join(OUTPUT_DIR, "eyebrow_R.png"))
    print("Saved eyebrow_R.png")

    # ── 5. MOUTH (mouth.png) ──
    mouth_arr = np.zeros_like(arr)
    mouth_mask = (grid_y >= 198) & (grid_y <= 214) & (grid_x >= 275) & (grid_x <= 301)
    mouth_arr[mouth_mask] = arr[mouth_mask]
    Image.fromarray(mouth_arr).save(os.path.join(OUTPUT_DIR, "mouth.png"))
    print("Saved mouth.png")

    # ── 6. HAIR FRONT (hair_front.png) ──
    hair_front_arr = np.zeros_like(arr)
    hair_front_mask = (grid_y <= 180) & (grid_x >= 200) & (grid_x <= 376) & is_hair
    hair_front_arr[hair_front_mask] = arr[hair_front_mask]
    Image.fromarray(hair_front_arr).save(os.path.join(OUTPUT_DIR, "hair_front.png"))
    print("Saved hair_front.png")

if __name__ == "__main__":
    slice_head_layers()
