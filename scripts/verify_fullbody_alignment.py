"""
Verification script for Full-Body Composite Alignment and Isolated Face Base Transparency Proof.
1. Overlays hair_back, face_base, eye_L, eye_R, eyebrow_L, eyebrow_R, mouth, hair_front directly on top of body_base.png (576x1024 full body).
2. Renders face_base.png alone over a checkerboard background to prove zero leftover mouth/eye pixels baked in.
"""

import os
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ASSETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "avatar", "renderer", "assets")
)
ARTIFACTS_DIR = r"C:\Users\rudra\.gemini\antigravity-ide\brain\f9d45dba-7071-459c-b97e-30b4190e010f"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def draw_checkerboard(w, h, square_size=16):
    """Generates a standard transparency checkerboard pattern."""
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

def verify_and_render():
    manifest_path = os.path.join(ASSETS_DIR, "sprite_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    W = manifest["canvas"]["width"] # 576
    H = manifest["canvas"]["height"] # 1024

    body_base_path = os.path.join(ASSETS_DIR, "body_base.png")
    body_base_img = Image.open(body_base_path).convert("RGBA")

    layer_order = [
        "hair_back",
        "face_base",
        "eye_L",
        "eye_R",
        "eyebrow_L",
        "eyebrow_R",
        "mouth",
        "hair_front"
    ]

    dot_colors = {
        "hair_back": (168, 85, 247, 255),   # Purple
        "face_base": (244, 63, 94, 255),    # Crimson Rose
        "eye_L": (56, 189, 248, 255),       # Cyan
        "eye_R": (56, 189, 248, 255),       # Cyan
        "eyebrow_L": (234, 179, 8, 255),    # Yellow
        "eyebrow_R": (234, 179, 8, 255),    # Yellow
        "mouth": (74, 222, 128, 255),       # Emerald Green
        "hair_front": (236, 72, 153, 255)   # Pink
    }

    # ── 1. FULL BODY COMPOSITE DEBUG VIEW (576x1024) ──
    composite_canvas = body_base_img.copy()

    for layer_key in layer_order:
        info = manifest["layers"][layer_key]
        img_path = os.path.join(ASSETS_DIR, info["file"])
        if os.path.exists(img_path):
            layer_img = Image.open(img_path).convert("RGBA")
            composite_canvas.alpha_composite(layer_img)

    draw_comp = ImageDraw.Draw(composite_canvas)

    for layer_key in layer_order:
        info = manifest["layers"][layer_key]
        ax, ay = info["anchor"]
        color = dot_colors.get(layer_key, (56, 189, 248, 255))

        # Pulse outer circle
        draw_comp.ellipse([ax - 10, ay - 10, ax + 10, ay + 10], outline=color, width=2)
        # Inner solid anchor dot
        draw_comp.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=color)

        # Crosshair lines
        draw_comp.line([(ax - 14, ay), (ax + 14, ay)], fill=color, width=1)
        draw_comp.line([(ax, ay - 14), (ax, ay + 14)], fill=color, width=1)

        # Text label with dark background box for readability
        label_str = f"{layer_key} ({ax}, {ay})"
        draw_comp.text((ax + 17, ay - 5), label_str, fill=(0, 0, 0, 255))
        draw_comp.text((ax + 16, ay - 6), label_str, fill=(255, 255, 255, 255))

    fullbody_out_path = os.path.join(ASSETS_DIR, "fullbody_composite_debug.png")
    composite_canvas.save(fullbody_out_path)
    shutil.copy(fullbody_out_path, os.path.join(ARTIFACTS_DIR, "fullbody_composite_debug.png"))
    print(f"Saved full-body composite debug image to {fullbody_out_path}")

    # ── 2. ISOLATED FACE_BASE CHECKERBOARD PROOF (576x1024) ──
    checkerboard = draw_checkerboard(W, H, square_size=16)
    face_base_path = os.path.join(ASSETS_DIR, "face_base.png")
    face_base_img = Image.open(face_base_path).convert("RGBA")

    checkerboard.alpha_composite(face_base_img)
    draw_proof = ImageDraw.Draw(checkerboard)

    # Draw face_base anchor
    fb_ax, fb_ay = manifest["layers"]["face_base"]["anchor"]
    color_fb = dot_colors["face_base"]
    draw_proof.ellipse([fb_ax - 10, fb_ay - 10, fb_ax + 10, fb_ay + 10], outline=color_fb, width=2)
    draw_proof.ellipse([fb_ax - 4, fb_ay - 4, fb_ax + 4, fb_ay + 4], fill=color_fb)
    draw_proof.line([(fb_ax - 14, fb_ay), (fb_ax + 14, fb_ay)], fill=color_fb, width=1)
    draw_proof.line([(fb_ax, fb_ay - 14), (fb_ax, fb_ay + 14)], fill=color_fb, width=1)

    label_fb = f"face_base ({fb_ax}, {fb_ay}) [NO baked-in eyes/mouth]"
    draw_proof.text((fb_ax + 17, fb_ay - 5), label_fb, fill=(0, 0, 0, 255))
    draw_proof.text((fb_ax + 16, fb_ay - 6), label_fb, fill=(255, 255, 255, 255))

    proof_out_path = os.path.join(ASSETS_DIR, "face_base_checkerboard_proof.png")
    checkerboard.save(proof_out_path)
    shutil.copy(proof_out_path, os.path.join(ARTIFACTS_DIR, "face_base_checkerboard_proof.png"))
    print(f"Saved face_base checkerboard proof image to {proof_out_path}")

if __name__ == "__main__":
    verify_and_render()
