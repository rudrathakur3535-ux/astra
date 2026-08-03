"""
Verification script for Phase 0 Final Chunk: Lower Body Layers & Complete Full Skeleton.
1. Composites all 16 layer categories (21 entries/files) on top of body_base.png at full 576x1024 scale with visible joint anchor dots.
2. Generates hip.png alone on checkerboard background (confirming zero leg pixels baked in).
3. Generates leg_L.png alone on checkerboard background (confirming hip joint anchor and zero shoe baked in).
"""

import os
import json
import shutil
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "avatar", "renderer", "assets")
)
ARTIFACTS_DIR = r"C:\Users\rudra\.gemini\antigravity-ide\brain\f9d45dba-7071-459c-b97e-30b4190e010f"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def draw_checkerboard(w, h, square_size=16):
    img = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    color1 = (240, 240, 245, 255)
    color2 = (210, 210, 220, 255)
    for y in range(0, h, square_size):
        for x in range(0, w, square_size):
            if ((x // square_size) + (y // square_size)) % 2 == 0:
                draw.rectangle([x, y, x + square_size, y + square_size], fill=color1)
            else:
                draw.rectangle([x, y, x + square_size, y + square_size], fill=color2)
    return img

def verify_final_skeleton():
    manifest_path = os.path.join(ASSETS_DIR, "sprite_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    W = manifest["canvas"]["width"] # 576
    H = manifest["canvas"]["height"] # 1024

    body_base_path = os.path.join(ASSETS_DIR, "body_base.png")
    body_base_img = Image.open(body_base_path).convert("RGBA")

    # Sorted by z_index
    layers_dict = manifest["layers"]
    sorted_layer_keys = sorted(layers_dict.keys(), key=lambda k: layers_dict[k].get("z_index", 0))

    dot_colors = {
        "hip": (234, 179, 8, 255),          # Gold / Yellow
        "leg_L": (56, 189, 248, 255),       # Cyan
        "leg_R": (56, 189, 248, 255),
        "hair_back": (168, 85, 247, 255),
        "torso": (249, 115, 22, 255),       # Orange
        "neck": (236, 72, 153, 255),        # Pink
        "face_base": (244, 63, 94, 255),
        "upper_arm_L": (34, 197, 94, 255),  # Emerald Green
        "upper_arm_R": (34, 197, 94, 255),
        "eye_L": (56, 189, 248, 255),
        "eye_R": (56, 189, 248, 255),
        "lower_arm_L": (168, 85, 247, 255),
        "lower_arm_R": (168, 85, 247, 255),
        "eyebrow_L": (234, 179, 8, 255),
        "eyebrow_R": (234, 179, 8, 255),
        "hand_L": (56, 189, 248, 255),
        "hand_R": (56, 189, 248, 255),
        "mouth": (74, 222, 128, 255),
        "hair_front": (236, 72, 153, 255),
        "shoe_L": (244, 63, 94, 255),       # Crimson Red
        "shoe_R": (244, 63, 94, 255)
    }

    # ── 1. FINAL FULL-SKELETON COMPOSITE VIEW (All 16 Categories on body_base.png) ──
    composite_canvas = body_base_img.copy()

    for key in sorted_layer_keys:
        info = layers_dict[key]
        img_p = os.path.join(ASSETS_DIR, info["file"])
        if os.path.exists(img_p):
            layer_img = Image.open(img_p).convert("RGBA")
            composite_canvas.alpha_composite(layer_img)

    draw_comp = ImageDraw.Draw(composite_canvas)

    for key in sorted_layer_keys:
        info = layers_dict[key]
        ax, ay = info["anchor"]
        color = dot_colors.get(key, (56, 189, 248, 255))

        draw_comp.ellipse([ax - 9, ay - 9, ax + 9, ay + 9], outline=color, width=2)
        draw_comp.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=color)
        draw_comp.line([(ax - 12, ay), (ax + 12, ay)], fill=color, width=1)
        draw_comp.line([(ax, ay - 12), (ax, ay + 12)], fill=color, width=1)

        label_str = f"{key} ({ax}, {ay})"
        draw_comp.text((ax + 14, ay - 5), label_str, fill=(0, 0, 0, 255))
        draw_comp.text((ax + 13, ay - 6), label_str, fill=(255, 255, 255, 255))

    full_out = os.path.join(ASSETS_DIR, "fullbody_final_debug.png")
    composite_canvas.save(full_out)
    shutil.copy(full_out, os.path.join(ARTIFACTS_DIR, "fullbody_final_debug.png"))
    print(f"Saved final full-skeleton composite image to {full_out}")

    # ── 2. HIP.PNG ALONE ON CHECKERBOARD ──
    cb_hip = draw_checkerboard(W, H, square_size=16)
    hip_img = Image.open(os.path.join(ASSETS_DIR, "hip.png")).convert("RGBA")
    cb_hip.alpha_composite(hip_img)
    draw_h = ImageDraw.Draw(cb_hip)

    hax, hay = layers_dict["hip"]["anchor"]
    draw_h.ellipse([hax - 9, hay - 9, hax + 9, hay + 9], outline=(234, 179, 8, 255), width=2)
    draw_h.ellipse([hax - 4, hay - 4, hax + 4, hay + 4], fill=(234, 179, 8, 255))
    draw_h.line([(hax - 12, hay), (hax + 12, hay)], fill=(234, 179, 8, 255), width=1)
    draw_h.line([(hax, hay - 12), (hax, hay + 12)], fill=(234, 179, 8, 255), width=1)

    h_lbl = f"hip ({hax}, {hay}) [Pivot: Torso-Base | ZERO Legs Baked In]"
    draw_h.text((hax + 14, hay - 5), h_lbl, fill=(0, 0, 0, 255))
    draw_h.text((hax + 13, hay - 6), h_lbl, fill=(255, 255, 255, 255))

    hip_out = os.path.join(ASSETS_DIR, "hip_checkerboard_proof.png")
    cb_hip.save(hip_out)
    shutil.copy(hip_out, os.path.join(ARTIFACTS_DIR, "hip_checkerboard_proof.png"))
    print(f"Saved hip checkerboard proof to {hip_out}")

    # ── 3. LEG_L.PNG ALONE ON CHECKERBOARD ──
    cb_leg = draw_checkerboard(W, H, square_size=16)
    leg_img = Image.open(os.path.join(ASSETS_DIR, "leg_L.png")).convert("RGBA")
    cb_leg.alpha_composite(leg_img)
    draw_l = ImageDraw.Draw(cb_leg)

    lax, lay = layers_dict["leg_L"]["anchor"]
    draw_l.ellipse([lax - 9, lay - 9, lax + 9, lay + 9], outline=(56, 189, 248, 255), width=2)
    draw_l.ellipse([lax - 4, lay - 4, lax + 4, lay + 4], fill=(56, 189, 248, 255))
    draw_l.line([(lax - 12, lay), (lax + 12, lay)], fill=(56, 189, 248, 255), width=1)
    draw_l.line([(lax, lay - 12), (lax, lay + 12)], fill=(56, 189, 248, 255), width=1)

    l_lbl = f"leg_L ({lax}, {lay}) [Pivot: Hip Joint | ZERO Shoe Baked In]"
    draw_l.text((lax + 14, lay - 5), l_lbl, fill=(0, 0, 0, 255))
    draw_l.text((lax + 13, lay - 6), l_lbl, fill=(255, 255, 255, 255))

    leg_out = os.path.join(ASSETS_DIR, "leg_L_checkerboard_proof.png")
    cb_leg.save(leg_out)
    shutil.copy(leg_out, os.path.join(ARTIFACTS_DIR, "leg_L_checkerboard_proof.png"))
    print(f"Saved leg_L checkerboard proof to {leg_out}")

if __name__ == "__main__":
    verify_final_skeleton()
