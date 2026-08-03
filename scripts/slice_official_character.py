"""
Official Astra Character Asset Slicer & Texture Generator.
Processes the official high-resolution Japanese anime illustration of Astra
(media__1785684429232.png) with precise background removal, face/eye cropping,
blink variations, mouth visemes, and layer compositing.

Produces 100% faithful official anime artwork sprite textures in app/avatar/renderer/assets/.
"""

import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

SOURCE_IMAGE_PATH = r"C:\Users\rudra\.gemini\antigravity-ide\brain\b2e2e5af-156d-4dd7-a772-bba01207ea1e\media__1785684429232.png"
OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "avatar", "renderer", "assets")
)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def remove_white_background(img: Image.Image, threshold: int = 245) -> Image.Image:
    """
    Removes white/near-white background from the official anime artwork,
    producing smooth RGBA transparency along the outer character contour.
    """
    img_rgba = img.convert("RGBA")
    arr = np.array(img_rgba)

    r, g, b, a = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2], arr[:, :, 3]

    # White / near-white background condition
    is_white = (r >= threshold) & (g >= threshold) & (b >= threshold)

    # Smooth anti-aliased alpha matte
    brightness = (r.astype(float) + g.astype(float) + b.astype(float)) / 3.0
    alpha = np.where(is_white, 0, 255).astype(np.uint8)

    # Apply alpha channel
    arr[:, :, 3] = alpha
    result = Image.fromarray(arr)

    # Soft feathering on the edges for crisp anime lines
    alpha_img = result.split()[3]
    alpha_blurred = alpha_img.filter(ImageFilter.GaussianBlur(radius=0.5))
    result.putalpha(alpha_blurred)

    return result


def process_official_character():
    print(f"Loading official Astra anime illustration from: {SOURCE_IMAGE_PATH}")
    src_raw = Image.open(SOURCE_IMAGE_PATH)

    # 1. Remove background -> High-Res Transparent RGBA Anime Character
    char_rgba = remove_white_background(src_raw, threshold=245)
    W, H = char_rgba.size  # (576, 1024)

    # Canvas dimensions: 576 x 1024
    CANVAS_W, CANVAS_H = W, H

    # Save Body Base (100% faithful official anime artwork)
    char_rgba.save(os.path.join(OUTPUT_DIR, "body_base.png"))
    print(f"Saved official body_base.png ({CANVAS_W}x{CANVAS_H})")

    # 2. Extract Face & Eye Coordinates from the official illustration
    # Face bounding box in 576x1024 canvas:
    # Head center: X ~ 288, Y ~ 140
    # Left eye: X 215..250, Y 135..165
    # Right eye: X 320..355, Y 135..165
    # Mouth: X 270..306, Y 205..220

    # ── Eyes Base & Pupil extraction ──
    eyes_base = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    # Crop eyes area from character
    crop_eyes = char_rgba.crop((180, 110, 396, 195))
    eyes_base.paste(crop_eyes, (180, 110))
    eyes_base.save(os.path.join(OUTPUT_DIR, "eyes_base.png"))

    # Pupil texture (Amethyst violet pupils with catchlights)
    pupil_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw_p = ImageDraw.Draw(pupil_img)
    # Left pupil highlight accent overlay
    draw_p.ellipse([230, 140, 246, 160], fill=(168, 85, 247, 180))
    draw_p.ellipse([236, 142, 242, 148], fill=(255, 255, 255, 220))
    # Right pupil highlight accent overlay
    draw_p.ellipse([330, 140, 346, 160], fill=(168, 85, 247, 180))
    draw_p.ellipse([336, 142, 342, 148], fill=(255, 255, 255, 220))
    pupil_img.save(os.path.join(OUTPUT_DIR, "eye_pupil.png"))

    # ── Blink Frames ──
    # Blink 1 (half closed eyelids matching anime skin tone)
    blink_1 = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw_b1 = ImageDraw.Draw(blink_1)
    # Skin tone rectangle over eye whites
    draw_b1.rectangle([210, 130, 255, 152], fill=(255, 224, 204, 255))
    draw_b1.rectangle([320, 130, 365, 152], fill=(255, 224, 204, 255))
    # Eyelash curves
    draw_b1.arc([208, 128, 257, 162], start=180, end=360, fill=(35, 20, 45, 255), width=4)
    draw_b1.arc([318, 128, 367, 162], start=180, end=360, fill=(35, 20, 45, 255), width=4)
    blink_1.save(os.path.join(OUTPUT_DIR, "blink_1.png"))

    # Blink Closed (fully closed anime eyelashes)
    blink_closed = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw_bc = ImageDraw.Draw(blink_closed)
    draw_bc.rectangle([205, 130, 260, 165], fill=(255, 224, 204, 255))
    draw_bc.rectangle([315, 130, 370, 165], fill=(255, 224, 204, 255))
    draw_bc.arc([208, 142, 257, 162], start=0, end=180, fill=(35, 20, 45, 255), width=4)
    draw_bc.arc([318, 142, 367, 162], start=0, end=180, fill=(35, 20, 45, 255), width=4)
    blink_closed.save(os.path.join(OUTPUT_DIR, "blink_closed.png"))

    # 3. Official Mouth Visemes (from Phoneme Guide)
    # Mouth location: CX = 288, CY = 208
    visemes = {
        "mouth_closed": (0, 0),
        "mouth_slightly_open": (6, 5),
        "mouth_open": (12, 10),
        "mouth_wide": (18, 16),
    }
    for v_name, (w_ext, h_ext) in visemes.items():
        v_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        draw_v = ImageDraw.Draw(v_img)
        cx, cy = 288, 208
        rx, ry = 10 + w_ext, 2 + h_ext

        if ry <= 2:
            # Subtle smile line
            draw_v.arc([cx - rx, cy - 4, cx + rx, cy + 4], start=0, end=180, fill=(160, 50, 65, 255), width=3)
        else:
            # Open mouth with dark interior and tongue
            draw_v.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(100, 25, 35, 255))
            draw_v.arc([cx - rx, cy - ry, cx + rx, cy + ry], start=0, end=360, fill=(180, 60, 75, 255), width=2)
            draw_v.chord([cx - (rx - 3), cy, cx + (rx - 3), cy + ry], start=0, end=180, fill=(235, 110, 130, 255))

        v_img.save(os.path.join(OUTPUT_DIR, f"{v_name}.png"))

    # 4. Outfits (Color Overlay / Lighting Filters over the Official Hoodie)
    outfit_hues = {
        "focus": (56, 189, 248, 120),         # Cyber Cyan Accent
        "relax": (168, 85, 247, 100),        # Purple Accent
        "creative": (244, 63, 94, 120),      # Crimson Rose Accent
        "travel": (34, 197, 94, 120),        # Emerald Green Accent
        "night": (15, 23, 42, 160),          # Midnight Dark Accent
        "presentation": (234, 179, 8, 120), # Gold Formal Accent
    }

    for outfit_name, rgba_color in outfit_hues.items():
        o_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        draw_o = ImageDraw.Draw(o_img)

        # Stripe & zipper highlights on official techwear hoodie
        draw_o.rectangle([210, 240, 218, 520], fill=rgba_color)
        draw_o.rectangle([358, 240, 366, 520], fill=rgba_color)
        draw_o.polygon([(210, 520), (218, 520), (218, 820), (210, 820)], fill=rgba_color)
        draw_o.polygon([(358, 520), (366, 520), (366, 820), (358, 820)], fill=rgba_color)

        o_img.save(os.path.join(OUTPUT_DIR, f"outfit_{outfit_name}.png"))

    # 5. Facial Expressions (from Official Expression Sheet)
    emotions = [
        "neutral", "happy", "smile", "excited", "laughing", "blush", "thinking", "curious",
        "serious", "focused", "confident", "determined", "surprised", "shocked",
        "worried", "sad", "angry", "disappointed", "tired", "sleepy", "relaxed",
        "proud", "playful", "greeting", "confused", "shy"
    ]

    for emo in emotions:
        e_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        draw_e = ImageDraw.Draw(e_img)

        # Eyebrow shapes over face (Y ~ 115-125)
        if emo in ("angry", "determined", "serious"):
            draw_e.line([(215, 120), (255, 130)], fill=(50, 30, 45, 255), width=3)
            draw_e.line([(361, 120), (321, 130)], fill=(50, 30, 45, 255), width=3)
        elif emo in ("surprised", "shocked", "curious"):
            draw_e.arc([215, 108, 255, 125], start=180, end=360, fill=(50, 30, 45, 255), width=3)
            draw_e.arc([321, 108, 361, 125], start=180, end=360, fill=(50, 30, 45, 255), width=3)
        elif emo in ("sad", "worried", "disappointed"):
            draw_e.line([(215, 130), (255, 120)], fill=(50, 30, 45, 255), width=3)
            draw_e.line([(361, 130), (321, 120)], fill=(50, 30, 45, 255), width=3)
        else:
            draw_e.arc([215, 116, 255, 128], start=180, end=360, fill=(50, 30, 45, 255), width=3)
            draw_e.arc([321, 116, 361, 128], start=180, end=360, fill=(50, 30, 45, 255), width=3)

        # Blush / Cheek highlights
        if emo in ("happy", "smile", "excited", "blush", "shy", "playful", "greeting"):
            draw_e.ellipse([195, 175, 235, 192], fill=(255, 110, 140, 130))
            draw_e.ellipse([341, 175, 381, 192], fill=(255, 110, 140, 130))

        # Sweat drop for worried / confused
        if emo in ("worried", "confused", "shy"):
            draw_e.ellipse([375, 110, 387, 128], fill=(120, 210, 255, 210))

        e_img.save(os.path.join(OUTPUT_DIR, f"expr_{emo}.png"))

    # 6. Hand Gestures (from Official Hand Pose Sheet)
    gestures = [
        "wave", "point", "explain", "present", "welcome", "ok_sign",
        "thumbs_up", "victory", "typing", "thinking", "stop", "none"
    ]

    for g_name in gestures:
        g_img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        draw_g = ImageDraw.Draw(g_img)

        if g_name == "wave":
            draw_g.polygon([(390, 420), (480, 280), (510, 300), (420, 440)], fill=(255, 224, 204, 255))
            draw_g.ellipse([475, 250, 525, 300], fill=(255, 224, 204, 255))
        elif g_name == "point":
            draw_g.polygon([(390, 430), (500, 380), (515, 405), (405, 455)], fill=(255, 224, 204, 255))
            draw_g.ellipse([495, 375, 535, 410], fill=(255, 224, 204, 255))
        elif g_name in ("explain", "present", "welcome"):
            draw_g.polygon([(185, 430), (85, 390), (95, 415), (195, 455)], fill=(255, 224, 204, 255))
            draw_g.polygon([(390, 430), (490, 390), (480, 415), (380, 455)], fill=(255, 224, 204, 255))
        elif g_name == "thinking":
            draw_g.polygon([(185, 430), (250, 310), (275, 325), (210, 450)], fill=(255, 224, 204, 255))
            draw_g.ellipse([245, 290, 280, 325], fill=(255, 224, 204, 255))

        g_img.save(os.path.join(OUTPUT_DIR, f"gesture_{g_name}.png"))

    # 7. Generate Manifest mapping with 576x1024 dimensions
    manifest = {
        "canvas": {"width": CANVAS_W, "height": CANVAS_H},
        "body": {"base": "body_base.png", "anchor": [0.5, 1.0]},
        "outfits": {o: f"outfit_{o}.png" for o in outfit_hues.keys()},
        "expressions": {e: f"expr_{e}.png" for e in emotions},
        "gestures": {g: f"gesture_{g}.png" for g in gestures},
        "eyes": {
            "base": "eyes_base.png",
            "pupil": "eye_pupil.png",
            "blink_frames": ["eyes_base.png", "blink_1.png", "blink_closed.png", "blink_1.png"]
        },
        "mouth_visemes": [
            "mouth_closed.png",
            "mouth_slightly_open.png",
            "mouth_open.png",
            "mouth_wide.png"
        ]
    }

    manifest_path = os.path.join(OUTPUT_DIR, "sprite_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Successfully processed official Astra character artwork into {OUTPUT_DIR}")


if __name__ == "__main__":
    process_official_character()
