"""
Sprite Generator Script for Astra Avatar Engine.
Generates placeholder RGBA PNG sprite layers for Astra's body, outfits, expressions,
gestures, eyes, and mouth visemes, along with sprite_manifest.json.

Run this script to populate app/avatar/renderer/assets/ with working placeholder graphics
that can later be replaced with final art assets from design sheets.
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

# Define output assets directory
OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "avatar", "renderer", "assets")
)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Standard sprite dimensions (512x640 canvas)
WIDTH, HEIGHT = 512, 640


def create_body_base():
    """Generates body base silhouette (head, torso, hair baseline)."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Hair silhouette (Dark Purple / Indigo)
    draw.ellipse([140, 60, 372, 340], fill=(45, 27, 78, 255))  # Top hair volume
    draw.polygon([(140, 180), (100, 480), (180, 480)], fill=(45, 27, 78, 255))  # Left hair strand
    draw.polygon([(372, 180), (412, 480), (332, 480)], fill=(45, 27, 78, 255))  # Right hair strand

    # Head / Skin (Warm Pale Peach)
    draw.ellipse([176, 110, 336, 300], fill=(255, 224, 204, 255))

    # Neck
    draw.rectangle([236, 280, 276, 330], fill=(245, 210, 190, 255))

    # Shoulders / Torso Base
    draw.polygon([(150, 420), (236, 330), (276, 330), (362, 420), (380, 640), (132, 640)], fill=(30, 30, 45, 255))

    img.save(os.path.join(OUTPUT_DIR, "body_base.png"))
    print("Generated body_base.png")


def create_outfits():
    """Generates 6 outfit mode color overlays."""
    outfit_colors = {
        "focus": (56, 189, 248, 220),         # Tech Cyan / Blue
        "relax": (168, 85, 247, 220),         # Purple Soft
        "creative": (244, 63, 94, 220),       # Vibrant Rose
        "travel": (34, 197, 94, 220),         # Emerald Green
        "night": (30, 41, 59, 235),           # Deep Slate/Night
        "presentation": (234, 179, 8, 220),  # Gold / Formal Accent
    }

    for outfit_name, color in outfit_colors.items():
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Jacket / Collar Overlay
        draw.polygon([(160, 410), (236, 330), (276, 330), (352, 410), (370, 640), (142, 640)], fill=color)

        # Draw collar accent lines
        draw.line([(236, 330), (220, 420)], fill=(255, 255, 255, 180), width=3)
        draw.line([(276, 330), (292, 420)], fill=(255, 255, 255, 180), width=3)

        img.save(os.path.join(OUTPUT_DIR, f"outfit_{outfit_name}.png"))
        print(f"Generated outfit_{outfit_name}.png")


def create_expressions():
    """Generates 24 facial expression overlay graphics."""
    emotions = [
        "neutral", "happy", "smile", "excited", "laughing", "blush", "thinking", "curious",
        "serious", "focused", "confident", "determined", "surprised", "shocked",
        "worried", "sad", "angry", "disappointed", "tired", "sleepy", "relaxed",
        "proud", "playful", "greeting", "confused", "shy"
    ]

    for emo in emotions:
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Eyebrows
        if emo in ("angry", "determined", "serious"):
            draw.line([(200, 160), (240, 175)], fill=(60, 40, 30, 255), width=4)
            draw.line([(312, 160), (272, 175)], fill=(60, 40, 30, 255), width=4)
        elif emo in ("surprised", "shocked", "curious"):
            draw.arc([200, 145, 240, 165], start=180, end=360, fill=(60, 40, 30, 255), width=4)
            draw.arc([272, 145, 312, 165], start=180, end=360, fill=(60, 40, 30, 255), width=4)
        elif emo in ("sad", "worried", "disappointed"):
            draw.line([(200, 175), (240, 160)], fill=(60, 40, 30, 255), width=4)
            draw.line([(312, 175), (272, 160)], fill=(60, 40, 30, 255), width=4)
        else:
            # Neutral / arched eyebrows
            draw.arc([200, 155, 240, 170], start=180, end=360, fill=(60, 40, 30, 255), width=3)
            draw.arc([272, 155, 312, 170], start=180, end=360, fill=(60, 40, 30, 255), width=3)

        # Blush / Cheek highlights
        if emo in ("happy", "smile", "excited", "shy", "playful", "greeting"):
            draw.ellipse([185, 220, 225, 240], fill=(255, 120, 140, 120))
            draw.ellipse([287, 220, 327, 240], fill=(255, 120, 140, 120))

        # Sweat drop for worried / confused
        if emo in ("worried", "confused", "shy"):
            draw.ellipse([325, 145, 335, 160], fill=(100, 200, 255, 200))

        img.save(os.path.join(OUTPUT_DIR, f"expr_{emo}.png"))

    print(f"Generated {len(emotions)} expression sprites.")


def create_eye_sprites():
    """Generates eye base, pupil, and blink frames."""
    # Eyes base (Eye whites + eyelashes)
    img_base = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_base = ImageDraw.Draw(img_base)
    # Left eye white
    draw_base.ellipse([200, 175, 244, 215], fill=(255, 255, 255, 255))
    draw_base.arc([198, 172, 246, 217], start=180, end=360, fill=(20, 20, 35, 255), width=4)
    # Right eye white
    draw_base.ellipse([268, 175, 312, 215], fill=(255, 255, 255, 255))
    draw_base.arc([266, 172, 314, 217], start=180, end=360, fill=(20, 20, 35, 255), width=4)
    img_base.save(os.path.join(OUTPUT_DIR, "eyes_base.png"))

    # Pupil sprite (Violet / Amethyst iris with highlight)
    img_pupil = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_pupil = ImageDraw.Draw(img_pupil)
    # Left pupil
    draw_pupil.ellipse([213, 183, 231, 207], fill=(138, 43, 226, 255))
    draw_pupil.ellipse([217, 186, 227, 202], fill=(40, 10, 70, 255))
    draw_pupil.ellipse([223, 186, 228, 192], fill=(255, 255, 255, 230))  # Catchlight
    # Right pupil
    draw_pupil.ellipse([281, 183, 299, 207], fill=(138, 43, 226, 255))
    draw_pupil.ellipse([285, 186, 295, 202], fill=(40, 10, 70, 255))
    draw_pupil.ellipse([291, 186, 296, 192], fill=(255, 255, 255, 230))  # Catchlight
    img_pupil.save(os.path.join(OUTPUT_DIR, "eye_pupil.png"))

    # Blink frames
    # Blink 1 (half closed)
    img_b1 = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_b1 = ImageDraw.Draw(img_b1)
    draw_b1.rectangle([196, 175, 248, 198], fill=(255, 224, 204, 255))
    draw_b1.arc([198, 172, 246, 217], start=180, end=360, fill=(20, 20, 35, 255), width=4)
    draw_b1.rectangle([264, 175, 316, 198], fill=(255, 224, 204, 255))
    draw_b1.arc([266, 172, 314, 217], start=180, end=360, fill=(20, 20, 35, 255), width=4)
    img_b1.save(os.path.join(OUTPUT_DIR, "blink_1.png"))

    # Blink closed
    img_closed = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw_closed = ImageDraw.Draw(img_closed)
    draw_closed.rectangle([195, 175, 249, 216], fill=(255, 224, 204, 255))
    draw_closed.arc([198, 185, 246, 205], start=0, end=180, fill=(20, 20, 35, 255), width=4)
    draw_closed.rectangle([263, 175, 317, 216], fill=(255, 224, 204, 255))
    draw_closed.arc([266, 185, 314, 205], start=0, end=180, fill=(20, 20, 35, 255), width=4)
    img_closed.save(os.path.join(OUTPUT_DIR, "blink_closed.png"))

    print("Generated eye sprites and blink frames.")


def create_mouth_visemes():
    """Generates mouth viseme frames for lip-sync animation."""
    visemes = {
        "mouth_closed": (0, 0),
        "mouth_slightly_open": (12, 8),
        "mouth_open": (20, 16),
        "mouth_wide": (28, 24),
    }

    for v_name, (w_extra, h_extra) in visemes.items():
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = 256, 250
        rx = 18 + w_extra
        ry = 4 + h_extra

        if ry <= 4:
            # Closed mouth line
            draw.arc([cx - rx, cy - 6, cx + rx, cy + 6], start=0, end=180, fill=(180, 60, 60, 255), width=3)
        else:
            # Open mouth oval with dark interior and tongue
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(120, 30, 40, 255))
            draw.arc([cx - rx, cy - ry, cx + rx, cy + ry], start=0, end=360, fill=(180, 60, 60, 255), width=2)
            # Tongue curve inside
            draw.chord([cx - (rx - 4), cy, cx + (rx - 4), cy + ry], start=0, end=180, fill=(230, 100, 120, 255))

        img.save(os.path.join(OUTPUT_DIR, f"{v_name}.png"))

    print("Generated mouth viseme frames.")


def create_gesture_arms():
    """Generates 12 hand gesture arm overlay sprites."""
    gestures = [
        "wave", "point", "explain", "present", "welcome", "ok_sign",
        "thumbs_up", "victory", "typing", "thinking", "none"
    ]

    for g_name in gestures:
        img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if g_name == "wave":
            # Right arm raised waving
            draw.polygon([(340, 380), (430, 260), (455, 275), (365, 395)], fill=(255, 224, 204, 255))
            draw.ellipse([420, 230, 465, 270], fill=(255, 224, 204, 255))  # Hand
        elif g_name == "point":
            # Right arm pointing forward
            draw.polygon([(340, 390), (440, 340), (450, 360), (350, 410)], fill=(255, 224, 204, 255))
            draw.ellipse([435, 335, 470, 365], fill=(255, 224, 204, 255))  # Hand
        elif g_name in ("explain", "present", "welcome"):
            # Both arms open outward
            draw.polygon([(160, 390), (70, 360), (80, 380), (170, 410)], fill=(255, 224, 204, 255))
            draw.polygon([(350, 390), (440, 360), (430, 380), (340, 410)], fill=(255, 224, 204, 255))
        elif g_name == "thinking":
            # Left arm up to chin
            draw.polygon([(160, 390), (220, 290), (240, 300), (180, 410)], fill=(255, 224, 204, 255))
            draw.ellipse([215, 270, 245, 300], fill=(255, 224, 204, 255))

        img.save(os.path.join(OUTPUT_DIR, f"gesture_{g_name}.png"))

    print("Generated gesture arm overlay sprites.")


def generate_manifest():
    """Generates sprite_manifest.json mapping for the animation engine."""
    emotions = [
        "neutral", "happy", "smile", "excited", "laughing", "blush", "thinking", "curious",
        "serious", "focused", "confident", "determined", "surprised", "shocked",
        "worried", "sad", "angry", "disappointed", "tired", "sleepy", "relaxed",
        "proud", "playful", "greeting", "confused", "shy"
    ]
    outfits = ["focus", "relax", "creative", "travel", "night", "presentation"]
    gestures = [
        "wave", "point", "explain", "present", "welcome", "ok_sign",
        "thumbs_up", "victory", "typing", "thinking", "stop", "none"
    ]

    manifest = {
        "canvas": {"width": WIDTH, "height": HEIGHT},
        "body": {"base": "body_base.png", "anchor": [0.5, 1.0]},
        "outfits": {o: f"outfit_{o}.png" for o in outfits},
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

    print(f"Generated sprite_manifest.json at {manifest_path}")


if __name__ == "__main__":
    print("Generating Astra Avatar placeholder sprite assets...")
    create_body_base()
    create_outfits()
    create_expressions()
    create_eye_sprites()
    create_mouth_visemes()
    create_gesture_arms()
    generate_manifest()
    print("All sprite assets successfully generated!")
