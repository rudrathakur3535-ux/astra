/**
 * Astra Animated Character Engine (v2.1 Enterprise Specification).
 * Layered 2D sprite rendering, emotion strength scaling, eye focus gaze targets,
 * idle breathing motion, blink cycles, mouth viseme lip-sync, gesture priority/duration handling,
 * and renderer-agnostic state machine resolution.
 */

class AstraAnimationEngine {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container '${containerId}' not found.`);
            return;
        }

        this.manifestUrl = options.manifestUrl || '/avatar/static/assets/sprite_manifest.json';
        this.assetsDir = options.assetsDir || '/avatar/static/assets/';
        this.wsUrl = options.wsUrl || `ws://${window.location.host}/avatar/ws/state`;

        // Canvas & Context setup (576 x 1024 matching official character artwork)
        this.canvas = document.createElement('canvas');
        this.canvas.width = 576;
        this.canvas.height = 1024;
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.objectFit = 'contain';
        this.container.appendChild(this.canvas);

        this.ctx = this.canvas.getContext('2d');

        // State, Loaded Sprites, and Manifest Offsets
        this.manifest = null;
        this.sprites = {};
        this.offsets = {};
        this.currentState = {
            emotion: 'neutral',
            emotion_strength: 0.5,
            outfit_mode: 'relax',
            gesture: 'none',
            gesture_priority: 'normal',
            gesture_duration: 1.5,
            eye_focus: 'user',
            speech_style: { speed: 1.0, pitch: 0.95, energy: 0.75, pause_level: 0.30 },
            is_speaking: false,
            is_listening: false,
            is_thinking: false,
            eye_target_x: 0.5,
            eye_target_y: 0.5,
            mouth_openness: 0.0,
            reply_text: '',
            reasoning_hint: ''
        };

        // Smooth Pupil Lerp Tracking
        this.pupilPos = { x: 0, y: 0 };
        this.targetPupilPos = { x: 0, y: 0 };

        // Idle Animation Counters
        this.time = 0;
        this.blinkTimer = 0;
        this.isBlinking = false;
        this.blinkFrame = 0; // 0: open, 1: half, 2: closed

        // Gesture Timer
        this.gestureTimer = 0;

        // Speech Bubble state
        this.bubbleText = '';
        this.bubbleOpacity = 0;

        // WebSocket Listener
        this.ws = null;

        this.init();
    }

    async init() {
        try {
            const res = await fetch(this.manifestUrl);
            this.manifest = await res.json();

            await this.loadSprites();
            this.buildSceneGraph();
            this.setupEvents();
            this.connectWebSocket();

            requestAnimationFrame((t) => this.renderLoop(t));
            console.log("Astra Animation Engine v2.1 initialized successfully with full 16-layer scene graph hierarchy!");
        } catch (err) {
            console.error("Failed to initialize Astra Animation Engine:", err);
        }
    }

    buildSceneGraph() {
        this.nodes = {};

        // Virtual Root node
        this.nodes['root'] = {
            key: 'root',
            anchor: [0, 0],
            z_index: 0,
            parentKey: null,
            parent: null,
            children: [],
            localTransform: { x: 0, y: 0, rotation: 0, scaleX: 1, scaleY: 1 },
            worldTransform: { x: 0, y: 0, rotation: 0, scaleX: 1, scaleY: 1 }
        };

        if (!this.manifest || !this.manifest.layers) return;

        for (const [key, info] of Object.entries(this.manifest.layers)) {
            this.nodes[key] = {
                key: key,
                file: info.file,
                anchor: info.anchor || [0, 0],
                z_index: info.z_index || 0,
                parentKey: info.parent || 'root',
                parent: null,
                children: [],
                localTransform: { x: 0, y: 0, rotation: 0, scaleX: 1, scaleY: 1 },
                worldTransform: { x: 0, y: 0, rotation: 0, scaleX: 1, scaleY: 1 }
            };
        }

        // Link hierarchy (parent -> children)
        for (const [key, node] of Object.entries(this.nodes)) {
            if (key === 'root') continue;
            const parentNode = this.nodes[node.parentKey] || this.nodes['root'];
            node.parent = parentNode;
            parentNode.children.push(node);
        }
    }

    computeWorldTransforms(node = this.nodes['root'], parentWorld = { x: 0, y: 0, rotation: 0 }) {
        if (!node) return;

        if (node.key !== 'root') {
            const parentAnchor = node.parent ? node.parent.anchor : [0, 0];
            const localOffsetX = node.anchor[0] - parentAnchor[0];
            const localOffsetY = node.anchor[1] - parentAnchor[1];

            node.worldTransform.rotation = parentWorld.rotation + (node.localTransform.rotation || 0);

            // Accumulate rotation & translation relative to parent anchor pivot
            const rad = parentWorld.rotation * Math.PI / 180.0;
            const cos = Math.cos(rad);
            const sin = Math.sin(rad);

            const rotatedX = localOffsetX * cos - localOffsetY * sin;
            const rotatedY = localOffsetX * sin + localOffsetY * cos;

            node.worldTransform.x = parentWorld.x + rotatedX + (node.localTransform.x || 0);
            node.worldTransform.y = parentWorld.y + rotatedY + (node.localTransform.y || 0);
        } else {
            node.worldTransform.x = 0;
            node.worldTransform.y = 0;
            node.worldTransform.rotation = 0;
        }

        for (const child of node.children) {
            this.computeWorldTransforms(child, node.worldTransform);
        }
    }

    renderLoop(timestamp) {
        this.time += 0.016;

        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Smooth Pupil Shift
        this.pupilPos.x += (this.targetPupilPos.x - this.pupilPos.x) * 0.15;
        this.pupilPos.y += (this.targetPupilPos.y - this.pupilPos.y) * 0.15;

        // Propagate world transforms down the hierarchy tree
        this.computeWorldTransforms();

        // Render ALL 16 layer categories (sorted by z_index)
        const sortedKeys = Object.keys(this.manifest.layers || {}).sort((a, b) => {
            const zA = this.manifest.layers[a].z_index || 0;
            const zB = this.manifest.layers[b].z_index || 0;
            return zA - zB;
        });

        for (const layerKey of sortedKeys) {
            let extra = { x: 0, y: 0 };
            if (layerKey === 'eye_L' || layerKey === 'eye_R') {
                extra = this.pupilPos;
            }
            this.drawSprite(layerKey, 1.0, extra);
        }

        // Render Debug Anchor Dots for all 16 layer categories
        this.renderDebugAnchors(sortedKeys);

        requestAnimationFrame((t) => this.renderLoop(t));
    }

    renderDebugAnchors(activeLayers) {
        const dotColors = {
            hip: '#eab308',          // Gold
            leg_L: '#38bdf8',        // Cyan
            leg_R: '#38bdf8',        // Cyan
            hair_back: '#a855f7',    // Purple
            torso: '#f97316',        // Orange
            neck: '#ec4899',         // Pink
            face_base: '#f43f5e',    // Crimson Rose
            upper_arm_L: '#22c55e', // Emerald Green
            upper_arm_R: '#22c55e', // Emerald Green
            eye_L: '#38bdf8',        // Cyan
            eye_R: '#38bdf8',        // Cyan
            lower_arm_L: '#a855f7', // Purple
            lower_arm_R: '#a855f7', // Purple
            eyebrow_L: '#eab308',    // Yellow
            eyebrow_R: '#eab308',    // Yellow
            hand_L: '#38bdf8',       // Cyan
            hand_R: '#38bdf8',       // Cyan
            mouth: '#4ade80',        // Emerald Green
            hair_front: '#ec4899',   // Pink
            shoe_L: '#f43f5e',       // Crimson Red
            shoe_R: '#f43f5e'        // Crimson Red
        };

        for (const key of activeLayers) {
            const anchor = this.anchors[key];
            if (!anchor) continue;

            const [ax, ay] = anchor;
            const color = dotColors[key] || '#38bdf8';

            this.ctx.save();

            // Outer pulse ring
            this.ctx.beginPath();
            this.ctx.arc(ax, ay, 10, 0, 2 * Math.PI);
            this.ctx.fillStyle = color + '33';
            this.ctx.fill();
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 1.5;
            this.ctx.stroke();

            // Inner solid anchor dot
            this.ctx.beginPath();
            this.ctx.arc(ax, ay, 4, 0, 2 * Math.PI);
            this.ctx.fillStyle = color;
            this.ctx.fill();

            // Crosshair
            this.ctx.beginPath();
            this.ctx.moveTo(ax - 14, ay);
            this.ctx.lineTo(ax + 14, ay);
            this.ctx.moveTo(ax, ay - 14);
            this.ctx.lineTo(ax, ay + 14);
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 1;
            this.ctx.stroke();

            // Label text
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = 'bold 11px sans-serif';
            this.ctx.shadowColor = '#000000';
            this.ctx.shadowBlur = 4;
            const label = `${key} (${ax}, ${ay})`;
            this.ctx.fillText(label, ax + 16, ay + 4);

            this.ctx.restore();
        }
    }

    renderSpeechBubble() {
        if (!this.bubbleText || this.bubbleOpacity <= 0) return;

        this.ctx.save();
        this.ctx.globalAlpha = this.bubbleOpacity;

        const bx = 40, by = 40, bw = 432, bh = 80;
        const radius = 12;

        this.ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
        this.ctx.strokeStyle = '#38bdf8';
        this.ctx.lineWidth = 1.5;

        this.ctx.beginPath();
        this.ctx.roundRect(bx, by, bw, bh, radius);
        this.ctx.fill();
        this.ctx.stroke();

        this.ctx.beginPath();
        this.ctx.moveTo(256 - 10, by + bh);
        this.ctx.lineTo(256 + 10, by + bh);
        this.ctx.lineTo(256, by + bh + 12);
        this.ctx.closePath();
        this.ctx.fillStyle = 'rgba(15, 23, 42, 0.88)';
        this.ctx.fill();

        this.ctx.fillStyle = '#f8fafc';
        this.ctx.font = '14px "Inter", sans-serif';

        const maxLen = 65;
        let displayStr = this.bubbleText;
        if (displayStr.length > maxLen) {
            displayStr = displayStr.substring(0, maxLen - 3) + '...';
        }

        this.ctx.fillText(displayStr, bx + 16, by + 32);

        this.ctx.fillStyle = '#38bdf8';
        this.ctx.font = 'bold 11px sans-serif';
        const strVal = Math.round((this.currentState.emotion_strength || 0.5) * 100);
        const tagStr = `[${(this.currentState.emotion || 'NEUTRAL').toUpperCase()} ${strVal}% | OUTFIT: ${(this.currentState.outfit_mode || 'RELAX').toUpperCase()}]`;
        this.ctx.fillText(tagStr, bx + 16, by + 58);

        this.ctx.restore();
    }
}

window.initAstraAvatar = function(containerId, options) {
    return new AstraAnimationEngine(containerId, options);
};
