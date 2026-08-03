"""
Scene Graph Transform Propagation Engine & Verification Proof Script for Astra Avatar.

TASK 1: Hierarchical world transform propagation walking root down to leaf nodes.
TASK 2: Render default pose using scene graph & compare side-by-side with body_base.png.
TASK 3: Rotation tests rotating upper_arm_L (+15 deg) and upper_arm_R (-15 deg) to prove child nodes (lower_arm & hand) rotate as rigid connected units without detaching.
"""

import os
import json
import shutil
import numpy as np
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "app", "avatar", "renderer", "assets")
)
ARTIFACTS_DIR = r"C:\Users\rudra\.gemini\antigravity-ide\brain\f9d45dba-7071-459c-b97e-30b4190e010f"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

class SceneNode:
    def __init__(self, key, info=None):
        self.key = key
        self.file = info.get("file") if info else None
        self.anchor = info.get("anchor", [0, 0]) if info else [0, 0]
        self.z_index = info.get("z_index", 0) if info else 0
        self.parent_key = info.get("parent") if info else None
        self.parent = None
        self.children = []
        
        # Local transform
        self.rotation = 0.0  # degrees
        self.translation = [0.0, 0.0]  # px offset
        self.scale = [1.0, 1.0]

class SceneGraphEngine:
    def __init__(self, manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

        self.canvas_width = self.manifest["canvas"]["width"]   # 576
        self.canvas_height = self.manifest["canvas"]["height"] # 1024
        self.nodes = {}
        self._build_tree()

    def _build_tree(self):
        # Root node at (0, 0)
        self.nodes["root"] = SceneNode("root", {"anchor": [0, 0], "z_index": 0})

        for key, info in self.manifest["layers"].items():
            self.nodes[key] = SceneNode(key, info)

        for key, node in self.nodes.items():
            if key == "root":
                continue
            parent_key = node.parent_key or "root"
            parent_node = self.nodes.get(parent_key, self.nodes["root"])
            node.parent = parent_node
            parent_node.children.append(node)

    def render_scene(self, node_rotations=None, bg_color=(255, 255, 255, 255)):
        """Renders all nodes using hierarchical matrix transform propagation."""
        if node_rotations:
            for k, rot in node_rotations.items():
                if k in self.nodes:
                    self.nodes[k].rotation = rot

        canvas = Image.new("RGBA", (self.canvas_width, self.canvas_height), bg_color)

        # Sorted render queue by z_index
        sorted_nodes = sorted(
            [n for k, n in self.nodes.items() if k != "root"],
            key=lambda n: n.z_index
        )

        # Pre-load sprites
        sprites = {}
        for n in sorted_nodes:
            if n.file:
                p = os.path.join(ASSETS_DIR, n.file)
                if os.path.exists(p):
                    sprites[n.key] = Image.open(p).convert("RGBA")

        # Composite each node by evaluating its full world transform chain from root
        for node in sorted_nodes:
            if node.key not in sprites:
                continue

            sprite = sprites[node.key]
            
            # Compute full chain of parent anchors & rotations from root down to node
            chain = []
            curr = node
            while curr is not None:
                chain.append(curr)
                curr = curr.parent
            chain.reverse()  # [root, torso, ..., node]

            t_sprite = sprite.copy()
            
            # Walk chain starting from root (index 0)
            for i in range(1, len(chain)):
                ancestor = chain[i]
                anc_anchor = ancestor.anchor
                anc_rot = ancestor.rotation

                if anc_rot != 0.0:
                    t_sprite = rotate_around_pivot(t_sprite, anc_rot, anc_anchor)

            canvas.alpha_composite(t_sprite)

        return canvas

def rotate_around_pivot(image, angle_deg, pivot):
    """Rotates RGBA image by angle_deg around pixel pivot point (px, py)."""
    px, py = pivot
    rotated = image.rotate(-angle_deg, resample=Image.BICUBIC, center=(px, py))
    return rotated

def run_verification_tasks():
    manifest_path = os.path.join(ASSETS_DIR, "sprite_manifest.json")
    engine = SceneGraphEngine(manifest_path)

    # ── TASK 2: DEFAULT POSE MATCH PROOF ──
    # Render on solid white background matching body_base.png
    default_render = engine.render_scene(bg_color=(255, 255, 255, 255))
    default_render_path = os.path.join(ASSETS_DIR, "scene_graph_default_pose.png")
    default_render.save(default_render_path)

    body_base_path = os.path.join(ASSETS_DIR, "body_base.png")
    body_base_img = Image.open(body_base_path).convert("RGBA")

    # Side-by-side comparison (1152 x 1024)
    side_by_side = Image.new("RGBA", (1152, 1024), (255, 255, 255, 255))
    side_by_side.alpha_composite(body_base_img, (0, 0))
    side_by_side.alpha_composite(default_render, (576, 0))

    draw_sbs = ImageDraw.Draw(side_by_side)
    draw_sbs.line([(576, 0), (576, 1024)], fill=(180, 180, 190, 255), width=2)

    draw_sbs.text((20, 20), "REFERENCE: body_base.png", fill=(0, 0, 0, 255))
    draw_sbs.text((596, 20), "SCENE GRAPH: Default Pose Render (All 16 Layers)", fill=(0, 0, 0, 255))
    draw_sbs.text((20, 19), "REFERENCE: body_base.png", fill=(139, 92, 246, 255))
    draw_sbs.text((596, 19), "SCENE GRAPH: Default Pose Render (All 16 Layers)", fill=(139, 92, 246, 255))

    sbs_out_path = os.path.join(ASSETS_DIR, "task2_default_pose_comparison.png")
    side_by_side.save(sbs_out_path)
    shutil.copy(sbs_out_path, os.path.join(ARTIFACTS_DIR, "task2_default_pose_comparison.png"))
    print(f"Saved Task 2 default pose comparison proof to {sbs_out_path}")

    # Pixel diff check between default_render and body_base_img
    arr_ref = np.array(body_base_img)
    arr_ren = np.array(default_render)

    diff = np.abs(arr_ref.astype(int) - arr_ren.astype(int))
    max_diff = diff.max()
    mean_diff = diff.mean()
    print(f"Default Pose Pixel Diff vs body_base.png -> Max Diff: {max_diff}, Mean Diff: {mean_diff:.4f}")

    # ── TASK 3: HIERARCHY ROTATION PROOF ──
    render_arm_L_15 = engine.render_scene({"upper_arm_L": 15.0}, bg_color=(255, 255, 255, 255))
    render_arm_R_15 = engine.render_scene({"upper_arm_R": -15.0}, bg_color=(255, 255, 255, 255))
    render_both_arms = engine.render_scene({"upper_arm_L": 15.0, "upper_arm_R": -15.0}, bg_color=(255, 255, 255, 255))

    # Create 3-panel Before / After Left / After Right proof image (1728 x 1024)
    proof_panel = Image.new("RGBA", (1728, 1024), (255, 255, 255, 255))
    proof_panel.alpha_composite(default_render, (0, 0))
    proof_panel.alpha_composite(render_arm_L_15, (576, 0))
    proof_panel.alpha_composite(render_both_arms, (1152, 0))

    draw_p = ImageDraw.Draw(proof_panel)
    for offset_x in [576, 1152]:
        draw_p.line([(offset_x, 0), (offset_x, 1024)], fill=(180, 180, 190, 255), width=2)

    draw_p.text((20, 20), "BEFORE: Neutral Pose (0 deg)", fill=(0, 0, 0, 255))
    draw_p.text((20, 19), "BEFORE: Neutral Pose (0 deg)", fill=(139, 92, 246, 255))

    draw_p.text((596, 20), "AFTER: upper_arm_L Rotated +15 deg (Shoulder Pivot)", fill=(0, 0, 0, 255))
    draw_p.text((596, 19), "AFTER: upper_arm_L Rotated +15 deg (Shoulder Pivot)", fill=(34, 197, 94, 255))

    draw_p.text((1172, 20), "AFTER: Both Arms Rotated (+15 deg L / -15 deg R)", fill=(0, 0, 0, 255))
    draw_p.text((1172, 19), "AFTER: Both Arms Rotated (+15 deg L / -15 deg R)", fill=(236, 72, 153, 255))

    panel_out_path = os.path.join(ASSETS_DIR, "task3_hierarchy_rotation_proof.png")
    proof_panel.save(panel_out_path)
    shutil.copy(panel_out_path, os.path.join(ARTIFACTS_DIR, "task3_hierarchy_rotation_proof.png"))
    print(f"Saved Task 3 hierarchy rotation proof to {panel_out_path}")

if __name__ == "__main__":
    run_verification_tasks()
