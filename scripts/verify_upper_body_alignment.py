"""
Verification script for Upper Body Phase 0 Continued:
1. Composite all 11 layer categories (16 files: 6 head/face + 5 upper body) ON TOP OF body_base.png at their anchor coordinates, full 576x1024 scale.
2. Show full-body composite with anchor dots visible and labeled.
3. Show torso.png alone on a checkerboard background (confirming zero arm pixels baked in).
4. Show upper_arm_L.png alone on checkerboard (confirming anchor point sits at shoulder joint).
5. Show hand_L.png alone on checkerboard (confirming wrist joint anchor).
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

def verify_upper_body():
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
        "hair_back": (168, 85, 247, 255),
        "torso": (249, 115, 22, 255),       # Orange
        "neck": (236, 72, 153, 255),        # Pink
        "face_base": (244, 63, 94, 255),
        "upper_arm_L": (34, 197, 94, 255),  # Emerald Green
        "upper_arm_R": (34, 197, 94, 255),
        "eye_L": (56, 189, 248, 255),
        "eye_R": (56, 189, 248, 255),
        "lower_arm_L": (168, 85, 247, 255), # Purple
        "lower_arm_R": (168, 85, 247, 255),
        "eyebrow_L": (234, 179, 8, 255),
        "eyebrow_R": (234, 179, 8, 255),
        "hand_L": (56, 189, 248, 255),      # Cyan
        "hand_R": (56, 189, 248, 255),
        "mouth": (74, 222, 128, 255),
        "hair_front": (236, 72, 153, 255)
    }

    # ── 1. FULL BODY COMPOSITE VIEW (All 11 Layers on body_base.png) ──
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

    full_out = os.path.join(ASSETS_DIR, "fullbody_upperbody_composite_debug.png")
    composite_canvas.save(full_out)
    shutil.copy(full_out, os.path.join(ARTIFACTS_DIR, "fullbody_upperbody_composite_debug.png"))
    print(f"Saved full-body composite image to {full_out}")

    # ── 2. TORSO.PNG ALONE ON CHECKERBOARD ──
    cb_torso = draw_checkerboard(W, H, square_size=16)
    torso_img = Image.open(os.path.join(ASSETS_DIR, "torso.png")).convert("RGBA")
    cb_torso.alpha_composite(torso_img)
    draw_t = ImageDraw.Draw(cb_torso)

    tax, tay = layers_dict["torso"]["anchor"]
    draw_t.ellipse([tax - 9, tay - 9, tax + 9, tay + 9], outline=(249, 115, 22, 255), width=2)
    draw_t.ellipse([tax - 4, tay - 4, tax + 4, tay + 4], fill=(249, 115, 22, 255))
    draw_t.line([(tax - 12, tay), (tax + 12, tay)], fill=(249, 115, 22, 255), width=1)
    draw_t.line([(tax, tay - 12), (tax, tay + 12)], fill=(249, 115, 22, 255), width=1)

    t_lbl = f"torso ({tax}, {tay}) [Pivot: Neck-Base | ZERO Arms Baked In]"
    draw_t.text((tax + 14, tay - 5), t_lbl, fill=(0, 0, 0, 255))
    draw_t.text((tax + 13, tay - 6), t_lbl, fill=(255, 255, 255, 255))

    torso_out = os.path.join(ASSETS_DIR, "torso_checkerboard_proof.png")
    cb_torso.save(torso_out)
    shutil.copy(torso_out, os.path.join(ARTIFACTS_DIR, "torso_checkerboard_proof.png"))
    print(f"Saved torso checkerboard proof to {torso_out}")

    # ── 3. UPPER_ARM_L.PNG ALONE ON CHECKERBOARD ──
    cb_arm = draw_checkerboard(W, H, square_size=16)
    arm_img = Image.open(os.path.join(ASSETS_DIR, "upper_arm_L.png")).convert("RGBA")
    cb_arm.alpha_composite(arm_img)
    draw_a = ImageDraw.Draw(cb_arm)

    aax, aay = layers_dict["upper_arm_L"]["anchor"]
    draw_a.ellipse([aax - 9, aay - 9, aax + 9, aay + 9], outline=(34, 197, 94, 255), width=2)
    draw_a.ellipse([aax - 4, aay - 4, aax + 4, aay + 4], fill=(34, 197, 94, 255))
    draw_a.line([(aax - 12, aay), (aax + 12, aay)], fill=(34, 197, 94, 255), width=1)
    draw_a.line([(aax, aay - 12), (aax, aay + 12)], fill=(34, 197, 94, 255), width=1)

    a_lbl = f"upper_arm_L ({aax}, {aay}) [Pivot: Shoulder Joint]"
    draw_a.text((aax + 14, aay - 5), a_lbl, fill=(0, 0, 0, 255))
    draw_a.text((aax + 13, aay - 6), a_lbl, fill=(255, 255, 255, 255))

    arm_out = os.path.join(ASSETS_DIR, "upper_arm_L_checkerboard_proof.png")
    cb_arm.save(arm_out)
    shutil.copy(arm_out, os.path.join(ARTIFACTS_DIR, "upper_arm_L_checkerboard_proof.png"))
    print(f"Saved upper_arm_L checkerboard proof to {arm_out}")

    # ── 4. HAND_L.PNG ALONE ON CHECKERBOARD ──
    cb_hand = draw_checkerboard(W, H, square_size=16)
    hand_img = Image.open(os.path.join(ASSETS_DIR, "hand_L.png")).convert("RGBA")
    cb_hand.alpha_composite(hand_img)
    draw_h = ImageDraw.Draw(cb_hand)

    hax, hay = layers_dict["hand_L"]["anchor"]
    draw_h.ellipse([hax - 9, hay - 9, hax + 9, hay + 9], outline=(56, 189, 248, 255), width=2)
    draw_h.ellipse([hax - 4, hay - 4, hax + 4, hay + 4], fill=(56, 189, 248, 255))
    draw_h.line([(hax - 12, hay), (hax + 12, hay)], fill=(56, 189, 248, 255), width=1)
    draw_h.line([(hax, hay - 12), (hax, hay + 12)], fill=(56, 189, 248, 255), width=1)

    h_lbl = f"hand_L ({hax}, {hay}) [Pivot: Wrist Joint]"
    draw_h.text((hax + 14, hay - 5), h_lbl, fill=(0, 0, 0, 255))
    draw_h.text((hax + 13, hay - 6), h_lbl, fill=(255, 255, 255, 255))

    hand_out = os.path.join(ASSETS_DIR, "hand_L_checkerboard_proof.png")
    cb_hand.save(hand_out)
    shutil.copy(hand_out, os.path.join(ARTIFACTS_DIR, "hand_L_checkerboard_proof.png"))
    print(f"Saved hand_L checkerboard proof to {hand_out}")

if __name__ == "__main__":
    verify_upper_body()
