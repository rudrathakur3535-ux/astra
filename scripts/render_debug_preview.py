"""
Script to generate debug rendering with anchor dots for ONLY the specified 6 layers:
- hair_back
- face_base
- eye_L, eye_R
- eyebrow_L, eyebrow_R
- mouth
- hair_front
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "avatar", "renderer", "assets")
)

def render_debug_preview():
    manifest_path = os.path.join(ASSETS_DIR, "sprite_manifest.json")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    W = manifest["canvas"]["width"]
    H = manifest["canvas"]["height"]

    # Composite Canvas (dark blue/purple preview background)
    canvas = Image.new("RGBA", (W, H), (15, 23, 42, 255))

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

    # Composite layers
    for layer_key in layer_order:
        info = manifest["layers"][layer_key]
        img_path = os.path.join(ASSETS_DIR, info["file"])
        if os.path.exists(img_path):
            layer_img = Image.open(img_path).convert("RGBA")
            canvas.alpha_composite(layer_img)

    # Draw Debug Anchor Dots
    draw = ImageDraw.Draw(canvas)

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

    for layer_key in layer_order:
        info = manifest["layers"][layer_key]
        ax, ay = info["anchor"]
        color = dot_colors.get(layer_key, (56, 189, 248, 255))

        # Pulse outer circle
        draw.ellipse([ax - 10, ay - 10, ax + 10, ay + 10], outline=color, width=2)
        # Inner solid anchor dot
        draw.ellipse([ax - 4, ay - 4, ax + 4, ay + 4], fill=color)

        # Crosshair lines
        draw.line([(ax - 14, ay), (ax + 14, ay)], fill=color, width=1)
        draw.line([(ax, ay - 14), (ax, ay + 14)], fill=color, width=1)

        # Text label
        label_str = f"{layer_key} ({ax}, {ay})"
        # Shadow offset text
        draw.text((ax + 17, ay - 5), label_str, fill=(0, 0, 0, 255))
        draw.text((ax + 16, ay - 6), label_str, fill=(255, 255, 255, 255))

    out_preview_path = os.path.join(ASSETS_DIR, "debug_6_layers_preview.png")
    canvas.save(out_preview_path)
    print(f"Saved debug 6-layer preview to {out_preview_path}")

if __name__ == "__main__":
    render_debug_preview()
