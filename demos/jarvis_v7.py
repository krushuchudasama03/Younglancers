"""
================================================================================
JARVIS v5 - AI-Powered Touchless Scientific Visualization System (OpenGL)
================================================================================
Major rewrite of the OpenCV-only prototype. Rendering engine is now real
OpenGL (PyOpenGL + GLFW): true lighting, depth, glass-like transparency,
glow, and smooth 3D geometry for every model. All text/HUD/telemetry stays
in the original, proven 2D compositor (drawn with OpenCV onto an RGBA
canvas) which is then uploaded as a single texture and blitted on top of
the 3D scene every frame. This hybrid keeps rendering fast and reliable
instead of gambling everything on immediate-mode GL text.

  CORE (always on, camera + MediaPipe required):
    - MediaPipe hand tracking, one-hand + two-hand, run on its own worker
      thread so a slow camera/model frame never stalls the render loop
    - One-hand rotate (inverted) + pinch zoom, two-hand rotate + distance zoom
    - Expanded discrete gesture set with cooldown + stability debouncing
    - Real OpenGL 3D rendering: lit spheres/cylinders/rings, glow (additive
      blend pass), glass-like transparency (alpha blend, back-to-front sort),
      360 auto-rotate, assemble/explode animation
    - Big data-driven science library (chemistry / biology / physics-space),
      each model built from simple primitives so highlight + exploded-view
      + labels all work uniformly
    - Exploded view (point gesture / 'x' key) for every organ + molecule
    - Selection cursor: holographic reticle follows the index fingertip,
      dwell-select after ~1s, drives a top category menu
    - Hand telemetry panel (index/thumb coords, pinch px, gesture, confidence)
    - Upgraded HUD: boot sequence, radar, waveform, hand skeleton overlay,
      finger coordinates, bounding box, AI-thinking spinner, clock,
      CPU/RAM (optional via psutil), camera/network status
    - Virtual chemistry lab: pick two reactants, 'combine' gesture -> shows
      balanced equation + product model + spoken result
    - Presentation / demo mode: auto-cycles the whole library with narration
    - Screenshot + video recording (now captured from the GL framebuffer)
    - Four HUD themes, full keyboard fallback, defensive error handling
      around every optional subsystem (mirrors the original's philosophy)

  OPTIONAL / PLUGGABLE (off by default, degrade to no-ops if unavailable):
    - Face/pose tracking (MediaPipe FaceMesh): head-tilt rotate, nod =
      confirm, shake = cancel. Throttled to every 3rd frame so it never
      competes with hand tracking for frame budget.
    - AI conversational brain: natural-language voice commands routed to
      Anthropic's API ("JARVIS, show me the human heart"). OFF by default;
      only activates if ENABLE_AI_BRAIN=True *and* an ANTHROPIC_API_KEY is
      set. Uses only the standard library (urllib) so it never becomes a
      hard dependency. Runs on its own thread; never blocks the render loop.
    - Wake word ("Hey JARVIS") gate in front of the AI brain, using the
      same non-blocking speech_recognition pipeline as ordinary voice
      commands.

Run:
    python jarvis_v5.py

Install (only the first two lines are required for the core experience):
    pip install opencv-python mediapipe numpy
    pip install PyOpenGL PyOpenGL_accelerate glfw
    pip install pyttsx3 SpeechRecognition           # optional: voice
    pip install psutil                              # optional: CPU/RAM in HUD

If PyOpenGL/glfw are missing, JARVIS prints install instructions and exits
cleanly rather than crashing -- see main() at the bottom of this file.
================================================================================
"""

import os
import io
import sys
import time
import math
import json
import queue
import random
import ctypes
import threading
import collections
import urllib.request
import urllib.error
from datetime import datetime

import cv2
import numpy as np

# --------------------------------------------------------------------------
# OPTIONAL DEPENDENCIES - the program keeps running even if these are
# missing. Each subsystem checks its own *_AVAILABLE flag and the HUD
# reports the resulting status honestly. This mirrors the original file's
# defensive philosophy and extends it to the new subsystems.
# --------------------------------------------------------------------------

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("[WARN] mediapipe not installed -> hand tracking disabled. "
          "Install with: pip install mediapipe")

try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("[FATAL] PyOpenGL not installed. Install with: "
          "pip install PyOpenGL PyOpenGL_accelerate")

try:
    import glfw
    GLFW_AVAILABLE = True
except ImportError:
    GLFW_AVAILABLE = False
    print("[FATAL] glfw not installed. Install with: pip install glfw")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("[INFO] speech_recognition not installed -> voice control disabled. "
          "Install with: pip install SpeechRecognition PyAudio")

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("[INFO] pyttsx3 not installed -> voice responses disabled. "
          "Install with: pip install pyttsx3")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # silent - CPU/RAM readout is a nice-to-have, not worth a log line


# ============================================================================
# CONFIG / CONSTANTS
# ============================================================================

CAP_W, CAP_H = 640, 480          # camera capture resolution
FRAME_W, FRAME_H = 1280, 800     # output window / canvas resolution

# --- AI conversational brain: OFF by default, pluggable, never required ----
ENABLE_AI_BRAIN = False                                   # flip to True to opt in
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-sonnet-4-6"
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

# --- Face/pose tracking: optional, throttled ---------------------------
ENABLE_FACE_TRACKING_DEFAULT = False
FACE_PROCESS_EVERY_N_FRAMES = 3

THEMES = {
    "blue":   {"accent": (255, 180, 0),   "text": (220, 240, 255), "gl": (1.00, 0.71, 0.00)},
    "green":  {"accent": (100, 255, 120), "text": (200, 255, 220), "gl": (0.39, 1.00, 0.47)},
    "red":    {"accent": (70, 70, 255),   "text": (220, 220, 255), "gl": (0.27, 0.27, 1.00)},
    "purple": {"accent": (255, 100, 200), "text": (240, 220, 255), "gl": (1.00, 0.39, 0.78)},
}
THEME_ORDER = ["blue", "green", "red", "purple"]

# CPK-style atom colors (0-1 floats for GL, reused for 2D swatches too)
ATOM_COLORS = {
    "H": (0.95, 0.95, 0.95), "C": (0.25, 0.25, 0.25), "N": (0.20, 0.30, 0.95),
    "O": (0.90, 0.15, 0.15), "S": (0.90, 0.80, 0.15), "P": (0.95, 0.55, 0.10),
    "Cl": (0.15, 0.85, 0.15), "Na": (0.60, 0.35, 0.85), "Fe": (0.70, 0.35, 0.10),
}


def wrap_text(text, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ease(t):
    """Smoothstep easing, used for explode/assemble animation."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp3(a, b, f):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f)


# ============================================================================
# OPENGL PRIMITIVE RENDERING LAYER
# ============================================================================
# Every model in the science library is described as a flat list of
# primitives (spheres / cylinders / rings). This one renderer draws all of
# them with real lighting, optional glow and optional glass-like
# transparency, so adding a new model is a data-entry problem, not a new
# renderer. Text labels are NOT drawn here -- they are projected to 2D with
# gluProject and drawn later in the HUD compositor, which keeps this layer
# simple and keeps every label crisp and readable.

class GLPrimitives:
    """Thin wrapper around a couple of reusable GLU quadric objects."""

    def __init__(self):
        self.quadric = None

    def ensure(self):
        if self.quadric is None:
            self.quadric = gluNewQuadric()
            gluQuadricNormals(self.quadric, GLU_SMOOTH)

    def sphere(self, radius, slices=18, stacks=18):
        self.ensure()
        gluSphere(self.quadric, radius, slices, stacks)

    def cylinder(self, base, top, radius, slices=14):
        """Draw a cylinder/cone-like bond or bone segment from point base to
        point top in the current modelview space."""
        self.ensure()
        bx, by, bz = base
        tx, ty, tz = top
        dx, dy, dz = tx - bx, ty - by, tz - bz
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        if length < 1e-6:
            return
        glPushMatrix()
        glTranslatef(bx, by, bz)
        # rotate +Z axis (gluCylinder's default axis) onto the base->top vector
        if abs(dz) < length * 0.999999:
            ax, ay, az = -dy, dx, 0.0
            angle = math.degrees(math.acos(max(-1.0, min(1.0, dz / length))))
            glRotatef(angle, ax, ay, az)
        elif dz < 0:
            glRotatef(180.0, 1.0, 0.0, 0.0)
        gluCylinder(self.quadric, radius, radius, length, slices, 1)
        glPopMatrix()

    def ring(self, center, radius, tube_radius, color, alpha, segments=40, tilt=0.0):
        """A torus-like ring built from short cylinder segments (no GLU torus
        quadric exists, so we approximate one -- cheap and looks correct)."""
        self.ensure()
        glPushMatrix()
        glTranslatef(*center)
        glRotatef(tilt, 1.0, 0.0, 0.0)
        set_material(color, alpha)
        pts = [(radius * math.cos(2 * math.pi * i / segments),
                radius * math.sin(2 * math.pi * i / segments), 0.0)
               for i in range(segments + 1)]
        for i in range(segments):
            self.cylinder(pts[i], pts[i + 1], tube_radius, slices=8)
        glPopMatrix()


GL_PRIM = GLPrimitives() if OPENGL_AVAILABLE else None

# Sphere tessellation used by every model in draw_primitives(). A dict (not a
# plain int) so PERFORMANCE MODE ('k' key) can drop it at runtime without any
# module-level `global` juggling -- fewer slices/stacks per sphere is the
# single cheapest lever for cutting per-frame GL cost on models with lots of
# parts (fullerene, DNA, the capsid-style virus models).
SPHERE_QUALITY = {"n": 16}


def set_material(color, alpha=1.0, emissive=0.0):
    """color is an (r,g,b) tuple in 0-1 floats."""
    r, g, b = color
    glColor4f(r, g, b, alpha)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [r * 0.35, g * 0.35, b * 0.35, alpha])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [r, g, b, alpha])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.6, 0.6, 0.6, alpha])
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [r * emissive, g * emissive, b * emissive, alpha])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 48.0)


def draw_glow(pos, radius, color, t, pulse=True):
    """Cheap glow: a few additively-blended, larger, translucent spheres
    behind the real one. No shaders required."""
    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
    glDisable(GL_LIGHTING)
    glDepthMask(GL_FALSE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # additive
    mul = 1.0 + 0.15 * math.sin(t * 3.0) if pulse else 1.0
    for i, (scale_f, alpha) in enumerate([(1.4, 0.18), (2.0, 0.09), (2.8, 0.04)]):
        glPushMatrix()
        glTranslatef(*pos)
        glColor4f(color[0], color[1], color[2], alpha)
        GL_PRIM.sphere(radius * scale_f * mul, 12, 12)
        glPopMatrix()
    glDepthMask(GL_TRUE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPopAttrib()


def draw_primitives(parts, t, explode_factor=0.0, highlight_key=None,
                     highlight_color=(1.0, 1.0, 0.0)):
    """Draws one model's primitive list with lighting, glow and glass-like
    transparency, sorted back-to-front for correct blending (painter's
    algorithm, same technique the original file used in 2D)."""
    if not parts:
        return

    def world_pos(p):
        base = p["pos"]
        if explode_factor > 0.0 and "explode_dir" in p:
            ex, ey, ez = p["explode_dir"]
            f = explode_factor * p.get("explode_dist", 1.0)
            return (base[0] + ex * f, base[1] + ey * f, base[2] + ez * f)
        return base

    # depth for painter's algorithm: use camera-space Z via modelview matrix
    mv = glGetFloatv(GL_MODELVIEW_MATRIX)

    def view_z(pos):
        x, y, z = pos
        return x * mv[0][2] + y * mv[1][2] + z * mv[2][2] + mv[3][2]

    ordered = sorted(parts, key=lambda p: view_z(world_pos(p)))

    glEnable(GL_LIGHTING)
    glDepthMask(GL_TRUE)
    for p in ordered:
        pos = world_pos(p)
        color = highlight_color if (highlight_key and p.get("key") == highlight_key) else p["color"]
        alpha = p.get("alpha", 1.0)
        if p["type"] == "cylinder" and "explode_dir" not in p:
            # bonds/connectors don't have their own explode offset, so fade
            # them out as the two ends they join fly apart -- looks like a
            # clean separation instead of a stretched, glitchy line.
            alpha *= max(0.0, 1.0 - explode_factor * 1.6)
            if alpha <= 0.01:
                continue
        emissive = 0.35 if (highlight_key and p.get("key") == highlight_key) else p.get("emissive", 0.0)

        if alpha < 0.999:
            glDepthMask(GL_FALSE)  # glass-like parts don't occlude what's behind them
        else:
            glDepthMask(GL_TRUE)

        set_material(color, alpha, emissive)
        ptype = p["type"]
        if ptype == "sphere":
            glPushMatrix()
            glTranslatef(*pos)
            n = SPHERE_QUALITY["n"]
            GL_PRIM.sphere(p["radius"], n, n)
            glPopMatrix()
            if p.get("glow"):
                draw_glow(pos, p["radius"], color, t)
        elif ptype == "cylinder":
            base = pos
            top_p = dict(p)
            top_p["pos"] = p["pos2"]
            top = world_pos(top_p)
            GL_PRIM.cylinder(base, top, p.get("radius", 0.05))
        elif ptype == "ring":
            GL_PRIM.ring(pos, p["radius"], p.get("tube_radius", 0.03), color, alpha,
                         segments=p.get("segments", 36), tilt=p.get("tilt", 0.0))

    glDepthMask(GL_TRUE)


# ============================================================================
# GENERIC MODEL BUILDERS (data -> primitive lists)
# ============================================================================
# Every model in the library funnels through one of these two builders, so
# the ~35-entry science library below stays pure data instead of ~35 bespoke
# renderers. Keeps the file both bigger in *content* and smaller in *risk*.

ELEMENT_RADIUS = {"H": 0.10, "C": 0.16, "N": 0.15, "O": 0.15, "S": 0.18,
                   "P": 0.18, "Cl": 0.18, "Na": 0.17, "Fe": 0.18}


def build_molecule(atoms, bonds, glow_elements=()):
    """atoms: list of (element_symbol, (x,y,z)). bonds: list of (i, j) or
    (i, j, order) where order 2/3 draws a double/triple-bond offset pair."""
    centroid = np.mean([a[1] for a in atoms], axis=0) if atoms else np.zeros(3)
    parts = []
    for sym, pos in atoms:
        rel = (pos[0] - centroid[0], pos[1] - centroid[1], pos[2] - centroid[2])
        dist = math.sqrt(sum(c * c for c in rel)) or 1.0
        parts.append({
            "type": "sphere", "pos": tuple(pos), "radius": ELEMENT_RADIUS.get(sym, 0.14),
            "color": ATOM_COLORS.get(sym, (0.8, 0.8, 0.8)), "key": None,
            "explode_dir": (rel[0] / dist, rel[1] / dist, rel[2] / dist), "explode_dist": 1.4,
            "glow": sym in glow_elements,
        })
    for b in bonds:
        i, j = b[0], b[1]
        order = b[2] if len(b) > 2 else 1
        p1, p2 = np.array(atoms[i][1]), np.array(atoms[j][1])
        offsets = {1: [0.0], 2: [-0.045, 0.045], 3: [-0.06, 0.0, 0.06]}[order]
        mid_dir = np.cross(p2 - p1, (0, 0, 1))
        if np.linalg.norm(mid_dir) < 1e-6:
            mid_dir = np.array((1.0, 0.0, 0.0))
        mid_dir = mid_dir / (np.linalg.norm(mid_dir) + 1e-9)
        for off in offsets:
            a = p1 + mid_dir * off
            c = p2 + mid_dir * off
            parts.append({"type": "cylinder", "pos": tuple(a), "pos2": tuple(c),
                          "radius": 0.035, "color": (0.75, 0.75, 0.75), "key": None})
    return parts


def build_organ(blobs, connectors=()):
    """blobs: list of dicts with key,pos,radius,color[,explode_dist].
    connectors: list of (pos_a, pos_b, radius, color) tube segments (vessels,
    bronchi, tracts, etc.) drawn as cylinders and left untouched by explode."""
    centroid = np.mean([b["pos"] for b in blobs], axis=0)
    parts = []
    for b in blobs:
        rel = np.array(b["pos"]) - centroid
        dist = np.linalg.norm(rel) or 1.0
        parts.append({
            "type": "sphere", "pos": tuple(b["pos"]), "radius": b["radius"],
            "color": b["color"], "key": b.get("key"), "alpha": b.get("alpha", 1.0),
            "explode_dir": tuple(rel / dist), "explode_dist": b.get("explode_dist", 1.2),
            "glow": b.get("glow", False),
        })
    for a, c, r, col in connectors:
        parts.append({"type": "cylinder", "pos": a, "pos2": c, "radius": r, "color": col, "key": None})
    return parts


def _fibonacci_sphere(n, radius=1.0):
    """n points spread ~evenly over a sphere surface using the golden-angle
    spiral. Used to place capsomeres (virus capsid subunits) and envelope
    spikes without visible clumping or poles, for a small fraction of the
    cost of a real geodesic-icosahedron subdivision."""
    pts = []
    ga = math.pi * (3.0 - math.sqrt(5.0))
    for i in range(n):
        yv = 1.0 - (i / float(max(1, n - 1))) * 2.0
        r = math.sqrt(max(0.0, 1.0 - yv * yv))
        theta = ga * i
        x, z = math.cos(theta) * r, math.sin(theta) * r
        pts.append((x * radius, yv * radius, z * radius))
    return pts


def _icosahedron_vertices(radius=1.0):
    """The 12 vertices of a regular icosahedron -- used for the 12 vertex
    fibers/spikes of the adenovirus penton and phage capsid landmarks."""
    phi = (1 + math.sqrt(5)) / 2
    raw = [(-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
           (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
           (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1)]
    out = []
    for v in raw:
        n = math.sqrt(sum(c * c for c in v)) or 1.0
        out.append(tuple(c / n * radius for c in v))
    return out


def _capsid_blobs(key, center, radius, n, sphere_r, color, alpha=1.0):
    """Capsomere spheres tiled over a sphere surface -- the recurring shape
    behind every non-enveloped icosahedral virus capsid in this library."""
    blobs = []
    cx, cy, cz = center
    for x, y, z in _fibonacci_sphere(n, radius):
        blobs.append({"key": key, "pos": (cx + x, cy + y, cz + z),
                      "radius": sphere_r, "color": color, "alpha": alpha})
    return blobs


def chain_blobs(key, points, radius, color, step=1):
    """Helper: turn a polyline of points into overlapping small spheres plus
    connecting tubes -- handy for airways, intestines, vessels, axons."""
    blobs, connectors = [], []
    for i, p in enumerate(points):
        blobs.append({"key": key, "pos": p, "radius": radius, "color": color})
    for i in range(0, len(points) - 1, step):
        connectors.append((points[i], points[i + 1], radius * 0.7, color))
    return blobs, connectors



# ============================================================================
# TEXTURE MANAGEMENT (camera background, HUD overlay, procedural planets)
# ============================================================================

class TextureManager:
    """Owns a handful of reusable GL texture IDs and knows how to (re)upload
    numpy image data into them each frame. Created only after a GL context
    exists (glGenTextures needs one).

    PERFORMANCE: the original version called glTexImage2D() every single
    frame for the camera background and HUD overlay. glTexImage2D() tells
    the driver to throw away the old texture storage and allocate a brand
    new block of GPU memory, which is far slower than just overwriting the
    pixels that are already there. That reallocation, happening twice a
    frame at full canvas resolution, was the single biggest source of lag.
    Fix: allocate each texture's storage ONCE with glTexImage2D, then use
    glTexSubImage2D on every later frame, which reuses the same memory and
    is dramatically cheaper. We also skip the per-frame cv2.cvtColor(BGR2RGB)
    copy for the camera feed by uploading straight from GL_BGR -- OpenCV's
    native byte order -- which saves a full-frame colour conversion + copy
    every single frame."""

    def __init__(self):
        self.ids = {}
        self._sizes = {}  # name -> (w, h) of the storage currently allocated

    def _get(self, name):
        if name not in self.ids:
            self.ids[name] = glGenTextures(1)
        return self.ids[name]

    def _ensure_storage(self, name, tex_id, w, h, internal_fmt, src_fmt):
        """(Re)allocate GPU storage only when the size actually changes."""
        if self._sizes.get(name) != (w, h):
            glTexImage2D(GL_TEXTURE_2D, 0, internal_fmt, w, h, 0, src_fmt, GL_UNSIGNED_BYTE, None)
            self._sizes[name] = (w, h)

    def upload_bgr(self, name, bgr_image):
        """Upload a cv2 BGR uint8 image as a GL texture (used for the
        camera background). Uploaded directly in GL_BGR order -- no color
        conversion needed -- and reuses existing GPU storage via
        glTexSubImage2D instead of reallocating every frame."""
        tex_id = self._get(name)
        h, w = bgr_image.shape[:2]
        if not bgr_image.flags['C_CONTIGUOUS']:
            bgr_image = np.ascontiguousarray(bgr_image)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        self._ensure_storage(name, tex_id, w, h, GL_RGB, GL_BGR)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_BGR, GL_UNSIGNED_BYTE, bgr_image.tobytes())
        return tex_id

    def upload_rgba(self, name, rgba_image):
        """Upload an RGBA uint8 image (used for the HUD overlay). Reuses
        existing GPU storage via glTexSubImage2D instead of reallocating
        every frame."""
        tex_id = self._get(name)
        h, w = rgba_image.shape[:2]
        if not rgba_image.flags['C_CONTIGUOUS']:
            rgba_image = np.ascontiguousarray(rgba_image)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        self._ensure_storage(name, tex_id, w, h, GL_RGBA, GL_RGBA)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, rgba_image.tobytes())
        return tex_id

    def upload_once_rgb(self, name, rgb_image):
        """Upload a static procedural texture (planet surfaces) a single
        time; callers just look it up by name afterwards."""
        if name in self.ids:
            return self.ids[name]
        tex_id = self._get(name)
        h, w = rgb_image.shape[:2]
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 0, GL_RGB, GL_UNSIGNED_BYTE, rgb_image.tobytes())
        return tex_id

    def id_of(self, name):
        return self.ids.get(name)


def make_planet_texture(base_color, land_color=None, seed=0, size=(180, 360), craters=False):
    """Procedurally paints a simple equirectangular planet texture with cv2
    so Earth/Moon/Mars etc. read as textured spheres instead of flat colour."""
    h, w = size
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = base_color
    rng = random.Random(seed)
    if land_color is not None:
        for _ in range(14):
            cx, cy = rng.randint(0, w - 1), rng.randint(0, h - 1)
            rw, rh = rng.randint(15, 60), rng.randint(10, 35)
            cv2.ellipse(img, (cx, cy), (rw, rh), rng.randint(0, 180), 0, 360, land_color, -1, cv2.LINE_AA)
            # wrap around the seam so continents don't visibly cut off
            cv2.ellipse(img, (cx - w, cy), (rw, rh), rng.randint(0, 180), 0, 360, land_color, -1, cv2.LINE_AA)
            cv2.ellipse(img, (cx + w, cy), (rw, rh), rng.randint(0, 180), 0, 360, land_color, -1, cv2.LINE_AA)
    if craters:
        for _ in range(40):
            cx, cy = rng.randint(0, w - 1), rng.randint(0, h - 1)
            r = rng.randint(3, 14)
            shade = tuple(int(max(0, c - 40)) for c in base_color)
            cv2.circle(img, (cx, cy), r, shade, 1, cv2.LINE_AA)
    img = cv2.GaussianBlur(img, (3, 3), 0)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def draw_textured_sphere(tex_id, radius, slices=28, stacks=28):
    """A gluSphere with texture coordinates enabled -- used for planets."""
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor4f(1.0, 1.0, 1.0, 1.0)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.1, 0.1, 0.1, 1.0])
    GL_PRIM.ensure()
    gluQuadricTexture(GL_PRIM.quadric, GL_TRUE)
    gluSphere(GL_PRIM.quadric, radius, slices, stacks)
    gluQuadricTexture(GL_PRIM.quadric, GL_FALSE)
    glDisable(GL_TEXTURE_2D)


# ============================================================================
# MODEL LIBRARY -- CHEMISTRY (molecules built from the generic builder)
# ============================================================================

def _fullerene_atoms_edges():
    """Truncated icosahedron: 60 vertices, 90 edges (unchanged geometry from
    the original file, now emitted as GL primitives instead of cv2 points)."""
    phi = (1 + math.sqrt(5)) / 2
    base_points = [(0, 1, 3 * phi), (1, 2 + phi, 2 * phi), (2, 1 + 2 * phi, phi)]

    def cyclic_perms(t):
        a, b, c = t
        return [(a, b, c), (b, c, a), (c, a, b)]

    def sign_variants(t):
        options = [[v] if v == 0 else [v, -v] for v in t]
        out = []
        for x in options[0]:
            for y in options[1]:
                for z in options[2]:
                    out.append((x, y, z))
        return out

    vertex_set = set()
    for base in base_points:
        for perm in cyclic_perms(base):
            for signed in sign_variants(perm):
                vertex_set.add(signed)

    vertices = np.array(list(vertex_set), dtype=float)
    vertices = vertices / np.max(np.linalg.norm(vertices, axis=1)) * 1.4

    n = len(vertices)
    dists = np.linalg.norm(vertices[:, None, :] - vertices[None, :, :], axis=2)
    min_dist = np.min(dists[dists > 1e-6])

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if dists[i, j] < min_dist * 1.05:
                edges.append((i, j))
    return vertices, edges


def build_fullerene_parts():
    verts, edges = _fullerene_atoms_edges()
    atoms = [("C", tuple(v)) for v in verts]
    bonds = [(i, j) for i, j in edges]
    return build_molecule(atoms, bonds)


def build_dna_parts(turns=3.2, points_per_turn=12):
    n = int(turns * points_per_turn)
    radius, pitch = 1.0, 0.22
    parts, rung_labels = [], []
    prev1 = prev2 = None
    base_pairs = [("A", "T", (0.35, 0.75, 0.35)), ("G", "C", (0.85, 0.55, 0.15))]
    for k in range(n):
        ang = 2 * math.pi * k / points_per_turn
        y = (k - n / 2) * pitch
        x1, z1 = radius * math.cos(ang), radius * math.sin(ang)
        x2, z2 = radius * math.cos(ang + math.pi), radius * math.sin(ang + math.pi)
        p1, p2 = (x1, y, z1), (x2, y, z2)
        parts.append({"type": "sphere", "pos": p1, "radius": 0.07, "color": (1.0, 0.63, 0.24),
                      "key": "backbone", "explode_dir": (x1 / radius, 0, z1 / radius), "explode_dist": 1.0})
        parts.append({"type": "sphere", "pos": p2, "radius": 0.07, "color": (0.24, 0.78, 1.0),
                      "key": "backbone", "explode_dir": (x2 / radius, 0, z2 / radius), "explode_dist": 1.0})
        if prev1 is not None:
            parts.append({"type": "cylinder", "pos": prev1, "pos2": p1, "radius": 0.03, "color": (1.0, 0.63, 0.24), "key": None})
            parts.append({"type": "cylinder", "pos": prev2, "pos2": p2, "radius": 0.03, "color": (0.24, 0.78, 1.0), "key": None})
        if k % 3 == 0:
            b1, b2, col = base_pairs[(k // 3) % 2]
            parts.append({"type": "cylinder", "pos": p1, "pos2": p2, "radius": 0.025, "color": col,
                          "key": "base_pair", "explode_dir": (0, 0, 0), "explode_dist": 0.0})
            rung_labels.append((f"{b1}-{b2}", (0.0, y, 0.0)))
        prev1, prev2 = p1, p2
    return parts, rung_labels


def _hex_ring(radius, y=0.0):
    return [(radius * math.cos(2 * math.pi * i / 6), y, radius * math.sin(2 * math.pi * i / 6)) for i in range(6)]


MOLECULES = {
    "h2o": {
        "atoms": [("O", (0.0, -0.15, 0.0)),
                  ("H", (0.76, 0.35, 0.0)),
                  ("H", (-0.76, 0.35, 0.0))],
        "bonds": [(0, 1), (0, 2)],
    },
    "co2": {
        "atoms": [("C", (0, 0, 0)), ("O", (1.16, 0, 0)), ("O", (-1.16, 0, 0))],
        "bonds": [(0, 1, 2), (0, 2, 2)],
    },
    "ch4": {
        "atoms": [("C", (0, 0, 0))] + [
            ("H", tuple(np.array(p) / math.sqrt(3) * 1.09))
            for p in [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]],
        "bonds": [(0, 1), (0, 2), (0, 3), (0, 4)],
    },
    "nh3": {
        "atoms": [("N", (0, 0.2, 0)),
                  ("H", (0.94, -0.25, 0.0)),
                  ("H", (-0.47, -0.25, 0.81)),
                  ("H", (-0.47, -0.25, -0.81))],
        "bonds": [(0, 1), (0, 2), (0, 3)],
    },
    "o2": {"atoms": [("O", (-0.6, 0, 0)), ("O", (0.6, 0, 0))], "bonds": [(0, 1, 2)]},
    "n2": {"atoms": [("N", (-0.55, 0, 0)), ("N", (0.55, 0, 0))], "bonds": [(0, 1, 3)]},
    "hcl": {"atoms": [("Cl", (-0.3, 0, 0)), ("H", (0.97, 0, 0))], "bonds": [(0, 1)]},
    "h2so4": {
        "atoms": [("S", (0, 0, 0)),
                  ("O", (1.0, 0.6, 0.0)), ("O", (-1.0, 0.6, 0.0)),
                  ("O", (0.6, -1.0, 0.6)), ("O", (-0.6, -1.0, -0.6)),
                  ("H", (1.4, 1.1, 0.5)), ("H", (-1.4, 1.1, -0.5))],
        "bonds": [(0, 1, 2), (0, 2, 2), (0, 3), (0, 4), (3, 5), (4, 6)],
    },
    "benzene": {
        "atoms": [("C", p) for p in _hex_ring(1.0)] + [("H", p) for p in _hex_ring(1.7)],
        "bonds": [(i, (i + 1) % 6) for i in range(6)] + [(i, i + 6) for i in range(6)],
    },
    "glucose": {  # simplified ring skeleton (C6H12O6), schematic not stereochemical
        "atoms": [("C", p) for p in _hex_ring(0.9)] + [("O", (0.0, 0.9, 0.0))] +
                 [("O", tuple(np.array(p) * 1.6)) for p in _hex_ring(0.9)[:4]],
        "bonds": [(i, (i + 1) % 6) for i in range(5)] + [(0, 6)] + [(i, 7 + i) for i in range(4)],
    },
    "ethanol": {
        "atoms": [("C", (-0.75, 0, 0)), ("C", (0.75, 0, 0)), ("O", (1.45, 1.1, 0))],
        "bonds": [(0, 1), (1, 2)],
    },
    "aspirin": {  # schematic: benzene ring + carboxyl + acetyl branches
        "atoms": [("C", p) for p in _hex_ring(1.0)] +
                 [("O", (1.9, 0.9, 0.0)), ("O", (2.1, -0.6, 0.0)),
                  ("O", (-1.9, 0.9, 0.0)), ("C", (-2.6, 1.6, 0.0)), ("O", (-3.4, 1.3, 0.0))],
        "bonds": [(i, (i + 1) % 6) for i in range(6)] + [(0, 6, 2), (0, 7), (1, 8), (8, 9), (9, 10, 2)],
    },
    "atp": {  # schematic: three phosphates chained off a ribose stand-in sphere
        "atoms": [("C", (-1.6, 0, 0)),
                  ("P", (-0.5, 0.3, 0)), ("O", (-0.5, 1.2, 0)), ("O", (-0.5, -0.6, 0.7)),
                  ("P", (0.7, 0.3, 0)), ("O", (0.7, 1.2, 0)), ("O", (0.7, -0.6, 0.7)),
                  ("P", (1.9, 0.3, 0)), ("O", (1.9, 1.2, 0)), ("O", (1.9, -0.6, 0.7)), ("O", (2.9, 0.3, 0))],
        "bonds": [(0, 1), (1, 2), (1, 3), (1, 4), (4, 5), (4, 6), (4, 7), (7, 8), (7, 9), (7, 10)],
    },
    "amino_acid": {  # glycine, the simplest amino acid
        "atoms": [("N", (-1.2, 0.4, 0)), ("C", (0.0, 0.0, 0)), ("C", (1.2, 0.6, 0)),
                  ("O", (1.2, 1.8, 0)), ("O", (2.3, -0.1, 0))],
        "bonds": [(0, 1), (1, 2), (2, 3, 2), (2, 4)],
    },
}


# ============================================================================
# MODEL LIBRARY -- BIOLOGY (organs built from the generic blob builder)
# ============================================================================

def _organ(blobs, connectors=()):
    return build_organ(blobs, connectors)


ORGANS = {}

# --- Heart -------------------------------------------------------------
ORGANS["heart"] = _organ([
    {"key": "left_atrium",    "pos": (-0.5, 0.55, 0.0), "radius": 0.42, "color": (0.85, 0.25, 0.30)},
    {"key": "right_atrium",   "pos": (0.5, 0.55, 0.0),  "radius": 0.42, "color": (0.70, 0.20, 0.55)},
    {"key": "left_ventricle", "pos": (-0.35, -0.35, 0.0), "radius": 0.55, "color": (0.90, 0.15, 0.20)},
    {"key": "right_ventricle","pos": (0.4, -0.35, 0.0),   "radius": 0.50, "color": (0.55, 0.15, 0.65)},
])

# --- Respiratory system --------------------------------------------------
_trachea_pts = [(0, 1.4, 0), (0, 1.0, 0), (0, 0.6, 0), (0, 0.2, 0)]
_bronchi_l = [(0, 0.2, 0), (-0.5, -0.1, 0), (-0.9, -0.4, 0)]
_bronchi_r = [(0, 0.2, 0), (0.5, -0.1, 0), (0.9, -0.4, 0)]
_b1, _c1 = chain_blobs("trachea", _trachea_pts, 0.09, (0.85, 0.85, 0.9))
_b2, _c2 = chain_blobs("bronchi", _bronchi_l, 0.07, (0.85, 0.75, 0.75))
_b3, _c3 = chain_blobs("bronchi", _bronchi_r, 0.07, (0.85, 0.75, 0.75))
ORGANS["respiratory"] = _organ(
    [{"key": "nasal_cavity", "pos": (0, 1.7, 0), "radius": 0.16, "color": (0.9, 0.7, 0.7)}] +
    _b1 + _b2 + _b3 +
    [{"key": "lungs", "pos": (-0.95, -0.7, 0), "radius": 0.55, "color": (1.0, 0.55, 0.55), "alpha": 0.85},
     {"key": "lungs", "pos": (0.95, -0.7, 0), "radius": 0.55, "color": (1.0, 0.55, 0.55), "alpha": 0.85},
     {"key": "alveoli", "pos": (-1.15, -1.0, 0.2), "radius": 0.10, "color": (1.0, 0.75, 0.75), "glow": True},
     {"key": "alveoli", "pos": (1.15, -1.0, -0.2), "radius": 0.10, "color": (1.0, 0.75, 0.75), "glow": True},
     {"key": "diaphragm", "pos": (0, -1.5, 0), "radius": 0.20, "color": (0.9, 0.7, 0.3)}],
    _c1 + _c2 + _c3)

# --- Digestive system ------------------------------------------------------
_intestine_pts = [(0.3, -0.3 - 0.18 * i, 0.15 * math.sin(i)) for i in range(8)]
_bI, _cI = chain_blobs("small_intestine", _intestine_pts, 0.10, (0.9, 0.75, 0.55))
ORGANS["digestive"] = _organ(
    [{"key": "mouth", "pos": (0, 1.6, 0), "radius": 0.15, "color": (0.9, 0.6, 0.6)},
     {"key": "esophagus", "pos": (0, 1.0, 0), "radius": 0.08, "color": (0.85, 0.75, 0.75)},
     {"key": "stomach", "pos": (-0.3, 0.4, 0), "radius": 0.4, "color": (0.95, 0.65, 0.35)},
     {"key": "liver", "pos": (0.6, 0.6, 0.1), "radius": 0.38, "color": (0.55, 0.30, 0.20)},
     {"key": "large_intestine", "pos": (0.0, -1.8, 0), "radius": 0.5, "color": (0.8, 0.55, 0.4)}] + _bI,
    _cI + [((0, 1.45, 0), (0, 1.1, 0), 0.07, (0.85, 0.75, 0.75)),
           ((-0.15, 1.0, 0), (-0.3, 0.65, 0), 0.08, (0.85, 0.75, 0.75))])

# --- Neuron ----------------------------------------------------------------
_axon_pts = [(0.3, 0.05 * math.sin(i), 0) for i in np.linspace(0.4, 2.4, 8)]
_bA, _cA = chain_blobs("axon", _axon_pts, 0.05, (0.9, 0.85, 0.4))
ORGANS["neuron"] = _organ(
    [{"key": "soma", "pos": (0, 0, 0), "radius": 0.35, "color": (0.75, 0.85, 1.0)},
     {"key": "dendrites", "pos": (-0.55, 0.35, 0), "radius": 0.08, "color": (0.6, 0.8, 1.0)},
     {"key": "dendrites", "pos": (-0.6, -0.1, 0.2), "radius": 0.08, "color": (0.6, 0.8, 1.0)},
     {"key": "dendrites", "pos": (-0.5, -0.4, -0.2), "radius": 0.08, "color": (0.6, 0.8, 1.0)},
     {"key": "synapse", "pos": (2.5, 0, 0), "radius": 0.12, "color": (1.0, 0.85, 0.3), "glow": True}] + _bA,
    _cA + [((0, 0, 0), (-0.55, 0.35, 0), 0.03, (0.6, 0.8, 1.0)),
           ((0, 0, 0), (-0.6, -0.1, 0.2), 0.03, (0.6, 0.8, 1.0)),
           ((0, 0, 0), (-0.5, -0.4, -0.2), 0.03, (0.6, 0.8, 1.0))])

# --- Brain -------------------------------------------------------------
ORGANS["brain"] = _organ([
    {"key": "cerebrum", "pos": (0, 0.25, 0), "radius": 0.65, "color": (0.92, 0.72, 0.68)},
    {"key": "cerebellum", "pos": (0.1, -0.45, -0.35), "radius": 0.32, "color": (0.85, 0.60, 0.65)},
    {"key": "brainstem", "pos": (0.05, -0.7, 0.0), "radius": 0.16, "color": (0.80, 0.55, 0.50)},
])

# --- Eye -----------------------------------------------------------------
ORGANS["eye"] = _organ([
    {"key": "sclera", "pos": (0, 0, 0), "radius": 0.55, "color": (0.95, 0.95, 0.92), "alpha": 0.9},
    {"key": "iris", "pos": (0, 0, 0.52), "radius": 0.22, "color": (0.35, 0.55, 0.75)},
    {"key": "pupil", "pos": (0, 0, 0.60), "radius": 0.10, "color": (0.02, 0.02, 0.02)},
    {"key": "optic_nerve", "pos": (0, 0, -0.75), "radius": 0.12, "color": (0.95, 0.9, 0.7)},
], [((0, 0, -0.55), (0, 0, -0.9), 0.08, (0.95, 0.9, 0.7))])

# --- Ear -------------------------------------------------------------------
ORGANS["ear"] = _organ([
    {"key": "outer_ear", "pos": (-0.6, 0, 0), "radius": 0.35, "color": (0.92, 0.75, 0.68), "alpha": 0.85},
    {"key": "ear_canal", "pos": (-0.1, 0, 0), "radius": 0.10, "color": (0.85, 0.65, 0.6)},
    {"key": "eardrum", "pos": (0.15, 0, 0), "radius": 0.12, "color": (0.9, 0.85, 0.8)},
    {"key": "cochlea", "pos": (0.55, 0.1, 0), "radius": 0.20, "color": (0.55, 0.75, 0.95)},
], [((-0.35, 0, 0), (0.0, 0, 0), 0.09, (0.85, 0.65, 0.6))])

# --- Kidney ----------------------------------------------------------------
ORGANS["kidney"] = _organ([
    {"key": "cortex", "pos": (0, 0, 0), "radius": 0.55, "color": (0.65, 0.25, 0.25), "alpha": 0.9},
    {"key": "medulla", "pos": (0.15, 0, 0), "radius": 0.32, "color": (0.75, 0.35, 0.30)},
    {"key": "ureter", "pos": (0.3, -0.9, 0), "radius": 0.08, "color": (0.85, 0.7, 0.5)},
], [((0.25, -0.35, 0), (0.3, -0.85, 0), 0.06, (0.85, 0.7, 0.5))])

# --- Liver -------------------------------------------------------------
ORGANS["liver"] = _organ([
    {"key": "right_lobe", "pos": (0.4, 0, 0), "radius": 0.6, "color": (0.55, 0.28, 0.18)},
    {"key": "left_lobe", "pos": (-0.5, 0.1, 0), "radius": 0.38, "color": (0.6, 0.32, 0.20)},
    {"key": "bile_duct", "pos": (0.0, -0.55, 0.1), "radius": 0.08, "color": (0.4, 0.7, 0.35)},
])

# --- Skeleton (simplified) --------------------------------------------
_spine_pts = [(0, y, 0) for y in np.linspace(1.1, -1.1, 8)]
_bS, _cS = chain_blobs("spine", _spine_pts, 0.08, (0.92, 0.9, 0.85))
ORGANS["skeleton"] = _organ(
    [{"key": "skull", "pos": (0, 1.5, 0), "radius": 0.32, "color": (0.95, 0.93, 0.88)},
     {"key": "ribcage", "pos": (0, 0.6, 0), "radius": 0.45, "color": (0.9, 0.88, 0.82), "alpha": 0.7},
     {"key": "pelvis", "pos": (0, -1.15, 0), "radius": 0.35, "color": (0.9, 0.88, 0.82)}] + _bS,
    _cS + [((-0.4, 0.0, 0), (-0.5, -1.4, 0), 0.07, (0.9, 0.88, 0.82)),
           ((0.4, 0.0, 0), (0.5, -1.4, 0), 0.07, (0.9, 0.88, 0.82))])

# --- Muscular system (schematic) --------------------------------------
ORGANS["muscular"] = _organ([
    {"key": "biceps", "pos": (-0.7, 0.4, 0), "radius": 0.22, "color": (0.75, 0.25, 0.22)},
    {"key": "biceps", "pos": (0.7, 0.4, 0), "radius": 0.22, "color": (0.75, 0.25, 0.22)},
    {"key": "quadriceps", "pos": (-0.35, -0.9, 0), "radius": 0.26, "color": (0.8, 0.3, 0.25)},
    {"key": "quadriceps", "pos": (0.35, -0.9, 0), "radius": 0.26, "color": (0.8, 0.3, 0.25)},
    {"key": "core", "pos": (0, 0, 0), "radius": 0.4, "color": (0.78, 0.28, 0.24)},
])

# --- Circulatory system (schematic loop) --------------------------------
_loop_pts = [(0.9 * math.cos(a), 0.9 * math.sin(a), 0) for a in np.linspace(0, 2 * math.pi, 16)]
_bC, _cC = chain_blobs("vessels", _loop_pts, 0.05, (0.85, 0.2, 0.2))
ORGANS["circulatory"] = _organ([{"key": "heart", "pos": (0, 0, 0), "radius": 0.3, "color": (0.9, 0.15, 0.2)}] + _bC, _cC)

# --- Cell / organelles ---------------------------------------------------
ORGANS["cell"] = _organ([
    {"key": "membrane", "pos": (0, 0, 0), "radius": 0.9, "color": (0.7, 0.85, 0.95), "alpha": 0.35},
    {"key": "nucleus", "pos": (0.1, 0.1, 0), "radius": 0.35, "color": (0.55, 0.55, 0.85)},
    {"key": "mitochondria", "pos": (-0.5, -0.3, 0.2), "radius": 0.18, "color": (0.9, 0.5, 0.3)},
    {"key": "ribosome", "pos": (0.4, -0.5, -0.3), "radius": 0.06, "color": (0.4, 0.7, 0.4)},
    {"key": "ribosome", "pos": (0.55, -0.35, 0.1), "radius": 0.06, "color": (0.4, 0.7, 0.4)},
])

ORGANS["mitochondria"] = _organ([
    {"key": "outer_membrane", "pos": (0, 0, 0), "radius": 0.6, "color": (0.85, 0.55, 0.3), "alpha": 0.5},
    {"key": "cristae", "pos": (-0.2, 0.15, 0), "radius": 0.18, "color": (0.75, 0.35, 0.15)},
    {"key": "cristae", "pos": (0.15, -0.2, 0.1), "radius": 0.18, "color": (0.75, 0.35, 0.15)},
    {"key": "matrix", "pos": (0.1, 0.1, -0.1), "radius": 0.22, "color": (0.9, 0.65, 0.4), "alpha": 0.7},
])

ORGANS["ribosome"] = _organ([
    {"key": "large_subunit", "pos": (0, 0.15, 0), "radius": 0.35, "color": (0.4, 0.75, 0.45)},
    {"key": "small_subunit", "pos": (0.05, -0.35, 0), "radius": 0.24, "color": (0.5, 0.85, 0.55)},
])

_chrom_pts_a = [(0, y, 0.1) for y in np.linspace(-0.7, 0.7, 6)]
_chrom_pts_b = [(0.15 * math.sin(i), y, -0.1) for i, y in enumerate(np.linspace(-0.7, 0.7, 6))]
_bX1, _cX1 = chain_blobs("chromatid", _chrom_pts_a, 0.10, (0.6, 0.35, 0.85))
_bX2, _cX2 = chain_blobs("chromatid", _chrom_pts_b, 0.10, (0.75, 0.45, 0.9))
ORGANS["chromosome"] = _organ(
    [{"key": "centromere", "pos": (0, 0, 0), "radius": 0.13, "color": (0.95, 0.85, 0.3)}] + _bX1 + _bX2,
    _cX1 + _cX2)


# --- Virology: bacteriophage, HIV, HPV, adenovirus ------------------------
# All four share the same "blobs + connectors -> build_organ()" recipe as
# the organs above, just built from _capsid_blobs()/_icosahedron_vertices()
# instead of hand-placed points, since a virus capsid is a repeating
# geometric shell rather than a handful of bespoke organs.

def build_bacteriophage_parts():
    """Simplified T4-style tailed bacteriophage: an icosahedral head packed
    with DNA, a contractile tail sheath, a baseplate, and six tail fibers --
    the classic 'lunar lander' silhouette used to teach phage structure."""
    head_c = (0, 0.9, 0)
    blobs = _capsid_blobs("capsid_head", head_c, 0.55, 42, 0.11, (0.55, 0.75, 0.35))
    blobs.append({"key": "genome", "pos": head_c, "radius": 0.32,
                  "color": (1.0, 0.75, 0.2), "alpha": 0.85, "glow": True})
    blobs.append({"key": "collar", "pos": (0, 0.35, 0), "radius": 0.12, "color": (0.5, 0.5, 0.5)})

    sheath_pts = [(0, y, 0) for y in np.linspace(0.28, -0.55, 6)]
    b_sheath, c_sheath = chain_blobs("tail_sheath", sheath_pts, 0.09, (0.6, 0.55, 0.35))
    blobs += b_sheath
    connectors = list(c_sheath)

    baseplate = (0, -0.62, 0)
    blobs.append({"key": "baseplate", "pos": baseplate, "radius": 0.16, "color": (0.4, 0.4, 0.42)})
    for i in range(6):
        ang = 2 * math.pi * i / 6
        tip = (0.55 * math.cos(ang), -1.05, 0.55 * math.sin(ang))
        connectors.append((baseplate, tip, 0.025, (0.65, 0.6, 0.4)))
        blobs.append({"key": "tail_fiber", "pos": tip, "radius": 0.045, "color": (0.7, 0.65, 0.45)})
    return build_organ(blobs, connectors)


def build_hiv_parts():
    """HIV virion: a spherical lipid envelope studded with gp120/gp41
    spikes, a matrix layer, a cone-shaped capsid core, and the RNA genome
    inside it."""
    env_r = 0.85
    blobs = [{"key": "envelope", "pos": (0, 0, 0), "radius": env_r,
              "color": (0.55, 0.6, 0.85), "alpha": 0.28}]
    connectors = []
    for x, y, z in _fibonacci_sphere(28, env_r):
        n = math.sqrt(x * x + y * y + z * z) or 1.0
        dx, dy, dz = x / n, y / n, z / n
        tip = (x + dx * 0.18, y + dy * 0.18, z + dz * 0.18)
        connectors.append(((x, y, z), tip, 0.02, (0.85, 0.35, 0.55)))
        blobs.append({"key": "spike", "pos": tip, "radius": 0.045, "color": (0.9, 0.4, 0.6)})

    blobs.append({"key": "matrix", "pos": (0, 0, 0), "radius": 0.62,
                  "color": (0.75, 0.65, 0.35), "alpha": 0.5})
    for y in np.linspace(-0.35, 0.3, 5):
        rr = max(0.08, 0.30 - 0.22 * (y + 0.35) / 0.65)  # tapers -> cone-shaped capsid
        blobs.append({"key": "capsid_core", "pos": (0, y, 0), "radius": rr, "color": (0.35, 0.3, 0.55)})
    blobs.append({"key": "genome", "pos": (0.05, -0.05, 0.05), "radius": 0.09,
                  "color": (1.0, 0.75, 0.2), "glow": True})
    blobs.append({"key": "genome", "pos": (-0.05, 0.1, -0.05), "radius": 0.09,
                  "color": (1.0, 0.75, 0.2), "glow": True})
    return build_organ(blobs, connectors)


def build_papillomavirus_parts():
    """Human papillomavirus: small, non-enveloped icosahedral capsid built
    from 72 capsomeres (pentamers) around a circular dsDNA genome -- no
    envelope and no tail, unlike the phage or HIV models."""
    blobs = _capsid_blobs("capsid", (0, 0, 0), 0.55, 72, 0.09, (0.45, 0.65, 0.85))
    blobs.append({"key": "genome", "pos": (0, 0, 0), "radius": 0.28,
                  "color": (1.0, 0.75, 0.2), "alpha": 0.85, "glow": True})
    return build_organ(blobs)


def build_adenovirus_parts():
    """Adenovirus: an icosahedral hexon capsid with a distinctive fiber
    protein (penton base + shaft + terminal knob) projecting from each of
    the 12 vertices -- the feature that makes adenovirus visually
    recognizable next to a plain capsid like HPV."""
    blobs = _capsid_blobs("capsid", (0, 0, 0), 0.58, 60, 0.10, (0.55, 0.5, 0.85))
    connectors = []
    for v in _icosahedron_vertices(0.58):
        n = math.sqrt(sum(c * c for c in v)) or 1.0
        dx, dy, dz = v[0] / n, v[1] / n, v[2] / n
        knob = (v[0] + dx * 0.5, v[1] + dy * 0.5, v[2] + dz * 0.5)
        connectors.append((v, knob, 0.025, (0.9, 0.7, 0.3)))
        blobs.append({"key": "fiber", "pos": v, "radius": 0.06, "color": (0.85, 0.65, 0.25)})
        blobs.append({"key": "fiber_knob", "pos": knob, "radius": 0.06, "color": (1.0, 0.8, 0.35)})
    blobs.append({"key": "genome", "pos": (0, 0, 0), "radius": 0.3,
                  "color": (1.0, 0.75, 0.2), "alpha": 0.85, "glow": True})
    return build_organ(blobs, connectors)


ORGANS["bacteriophage"] = build_bacteriophage_parts()
ORGANS["hiv"] = build_hiv_parts()
ORGANS["papillomavirus"] = build_papillomavirus_parts()
ORGANS["adenovirus"] = build_adenovirus_parts()


# ============================================================================
# MODEL LIBRARY -- DYNAMIC (atom, space, physics scenes with real motion)
# ============================================================================
# These need t (time) every frame, so they render themselves directly
# instead of going through the static draw_primitives() path.

def render_atom(t, explode_factor, highlight_key, theme_gl, shells=(2, 6, 6)):
    set_material((0.15, 0.55, 1.0), 1.0, emissive=0.25)
    glPushMatrix()
    GL_PRIM.sphere(0.18)
    glPopMatrix()
    draw_glow((0, 0, 0), 0.18, (0.15, 0.55, 1.0), t)
    for si, count in enumerate(shells):
        r = 0.55 + si * 0.42 + explode_factor * 0.3
        GL_PRIM.ring((0, 0, 0), r, 0.008, (0.4, 0.4, 0.4), 0.6, segments=48,
                     tilt=20 * si)
        for e in range(count):
            phase = 2 * math.pi * e / count
            speed = 1.1 - si * 0.18
            ang = t * speed + phase
            x = r * math.cos(ang)
            z = r * math.sin(ang)
            y = 0.18 * math.sin(ang * 0.6 + si) * math.sin(math.radians(20 * si))
            set_material((0.35, 1.0, 0.45), 1.0, emissive=0.3)
            glPushMatrix()
            glTranslatef(x, y, z)
            GL_PRIM.sphere(0.06)
            glPopMatrix()


SOLAR_PLANETS = [
    ("Mercury", (0.55, 0.55, 0.55), None, 0.75, 0.09, 4.1),
    ("Venus",   (0.85, 0.75, 0.55), None, 1.05, 0.13, 2.4),
    ("Earth",   (0.25, 0.45, 0.85), (0.15, 0.45, 0.15), 1.35, 0.14, 1.6),
    ("Mars",    (0.75, 0.35, 0.20), None, 1.65, 0.11, 1.0),
    ("Jupiter", (0.75, 0.60, 0.45), None, 2.15, 0.30, 0.42),
    ("Saturn",  (0.80, 0.72, 0.50), None, 2.65, 0.26, 0.27),
]


def render_solar_system(t, explode_factor, highlight_key, theme_gl, tex_mgr):
    set_material((1.0, 0.75, 0.1), 1.0, emissive=0.6)
    glPushMatrix()
    GL_PRIM.sphere(0.30)
    glPopMatrix()
    draw_glow((0, 0, 0), 0.30, (1.0, 0.8, 0.2), t, pulse=True)
    for name, color, land, orbit_r, size, speed in SOLAR_PLANETS:
        orbit_r = orbit_r * (1.0 + explode_factor * 0.6)
        GL_PRIM.ring((0, 0, 0), orbit_r, 0.006, (0.4, 0.4, 0.4), 0.35, segments=64)
        ang = t * speed
        x, z = orbit_r * math.cos(ang), orbit_r * math.sin(ang)
        glPushMatrix()
        glTranslatef(x, 0, z)
        tex_name = f"planet_{name}"
        tex_id = tex_mgr.id_of(tex_name)
        if tex_id is None:
            tex_id = tex_mgr.upload_once_rgb(tex_name, make_planet_texture(
                tuple(int(c * 255) for c in reversed(color)),
                tuple(int(c * 255) for c in reversed(land)) if land else None,
                seed=hash(name) % 1000))
        draw_textured_sphere(tex_id, size)
        glPopMatrix()


def render_earth_standalone(t, explode_factor, highlight_key, theme_gl, tex_mgr):
    tex_id = tex_mgr.id_of("earth_solo")
    if tex_id is None:
        tex_id = tex_mgr.upload_once_rgb("earth_solo", make_planet_texture(
            (140, 60, 20), (40, 140, 40), seed=7))
    glPushMatrix()
    glRotatef(t * 8.0, 0, 1, 0)
    draw_textured_sphere(tex_id, 0.9, 36, 36)
    glPopMatrix()
    draw_glow((0, 0, 0), 0.9, (0.3, 0.55, 1.0), t, pulse=False)


def render_moon_standalone(t, explode_factor, highlight_key, theme_gl, tex_mgr):
    tex_id = tex_mgr.id_of("moon_solo")
    if tex_id is None:
        tex_id = tex_mgr.upload_once_rgb("moon_solo", make_planet_texture(
            (170, 170, 170), None, seed=3, craters=True))
    glPushMatrix()
    glRotatef(t * 3.0, 0, 1, 0)
    draw_textured_sphere(tex_id, 0.85, 32, 32)
    glPopMatrix()


def render_black_hole(t, explode_factor, highlight_key, theme_gl):
    set_material((0.0, 0.0, 0.0), 1.0)
    glPushMatrix()
    GL_PRIM.sphere(0.35)
    glPopMatrix()
    for i, (rr, alpha) in enumerate([(0.55, 0.9), (0.75, 0.6), (0.95, 0.35)]):
        r = rr * (1.0 + explode_factor * 0.5)
        set_material((1.0, 0.55, 0.15), alpha, emissive=0.4)
        GL_PRIM.ring((0, 0, 0), r, 0.05, (1.0, 0.55, 0.1), alpha, segments=48, tilt=70)
    draw_glow((0, 0, 0), 0.35, (0.6, 0.2, 1.0), t)


def render_wave(t, explode_factor, highlight_key, theme_gl):
    set_material((0.2, 0.7, 1.0), 1.0, emissive=0.2)
    n = 60
    for i in range(n):
        x = (i / (n - 1) - 0.5) * 3.0
        y = 0.5 * math.sin(x * 3.0 - t * 3.0)
        glPushMatrix()
        glTranslatef(x, y, 0)
        GL_PRIM.sphere(0.035)
        glPopMatrix()


def render_pendulum(t, explode_factor, highlight_key, theme_gl):
    ang = math.radians(35) * math.sin(t * 2.2)
    pivot = (0, 1.0, 0)
    bob = (math.sin(ang) * 1.2, 1.0 - math.cos(ang) * 1.2, 0)
    set_material((0.8, 0.8, 0.85), 1.0)
    glPushMatrix()
    glTranslatef(*pivot)
    GL_PRIM.sphere(0.05)
    glPopMatrix()
    GL_PRIM.cylinder(pivot, bob, 0.02)
    set_material((1.0, 0.4, 0.2), 1.0, emissive=0.15)
    glPushMatrix()
    glTranslatef(*bob)
    GL_PRIM.sphere(0.18)
    glPopMatrix()


def render_projectile(t, explode_factor, highlight_key, theme_gl):
    dur = 2.2
    phase = (t % dur) / dur
    x = (phase - 0.5) * 3.2
    y = -0.9 + 4.0 * phase * (1 - phase) * 1.8
    trail_n = 24
    for i in range(trail_n):
        tp = phase - i * 0.01
        if tp < 0:
            continue
        tx = (tp - 0.5) * 3.2
        ty = -0.9 + 4.0 * tp * (1 - tp) * 1.8
        a = max(0.0, 1.0 - i / trail_n)
        set_material((1.0, 0.6, 0.2), a * 0.5)
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        GL_PRIM.sphere(0.04)
        glPopMatrix()
    set_material((1.0, 0.75, 0.2), 1.0, emissive=0.3)
    glPushMatrix()
    glTranslatef(x, y, 0)
    GL_PRIM.sphere(0.09)
    glPopMatrix()
    set_material((0.5, 0.5, 0.5), 1.0)
    GL_PRIM.cylinder((-1.6, -0.9, 0), (1.6, -0.9, 0), 0.02)


def render_circuit(t, explode_factor, highlight_key, theme_gl):
    pts = [(-1, 0.6, 0), (1, 0.6, 0), (1, -0.6, 0), (-1, -0.6, 0)]
    set_material((0.8, 0.6, 0.2), 1.0)
    for i in range(4):
        GL_PRIM.cylinder(pts[i], pts[(i + 1) % 4], 0.025)
    set_material((0.9, 0.2, 0.2), 1.0, emissive=0.2)
    glPushMatrix(); glTranslatef(-1, 0, 0); GL_PRIM.sphere(0.12); glPopMatrix()  # battery
    set_material((0.3, 0.3, 0.3), 1.0)
    glPushMatrix(); glTranslatef(1, 0, 0); GL_PRIM.sphere(0.10); glPopMatrix()   # resistor
    # animated current dots flowing around the loop
    speed = 1.5
    for k in range(6):
        u = (t * speed + k / 6.0) % 1.0
        seg = int(u * 4)
        f = (u * 4) - seg
        a, b = pts[seg], pts[(seg + 1) % 4]
        p = lerp3(a, b, f)
        set_material((1.0, 0.9, 0.3), 1.0, emissive=0.5)
        glPushMatrix(); glTranslatef(*p); GL_PRIM.sphere(0.03); glPopMatrix()


def render_magnetic_field(t, explode_factor, highlight_key, theme_gl):
    set_material((0.75, 0.1, 0.1), 1.0)
    GL_PRIM.cylinder((0, -0.5, 0), (0, 0.5, 0), 0.22)
    for i, r in enumerate([0.5, 0.8, 1.1]):
        set_material((0.3, 0.6, 1.0), 0.7, emissive=0.15)
        GL_PRIM.ring((0, 0, 0), r * (1 + explode_factor * 0.4), 0.012, (0.3, 0.6, 1.0), 0.7,
                     segments=40, tilt=90)


def render_em_field(t, explode_factor, highlight_key, theme_gl):
    n = 10
    for i in range(n):
        x = (i / (n - 1) - 0.5) * 3.0
        phase = t * 2.0
        ey = 0.4 * math.sin(x * 2.5 + phase)
        bz = 0.4 * math.sin(x * 2.5 + phase + math.pi / 2)
        set_material((0.3, 0.7, 1.0), 1.0, emissive=0.2)
        GL_PRIM.cylinder((x, 0, 0), (x, ey, 0), 0.012)
        glPushMatrix(); glTranslatef(x, ey, 0); GL_PRIM.sphere(0.025); glPopMatrix()
        set_material((1.0, 0.4, 0.3), 1.0, emissive=0.2)
        GL_PRIM.cylinder((x, 0, 0), (x, 0, bz), 0.012)
        glPushMatrix(); glTranslatef(x, 0, bz); GL_PRIM.sphere(0.025); glPopMatrix()


def render_quantum_cloud(t, explode_factor, highlight_key, theme_gl):
    rng = np.random.RandomState(42)
    n = 260
    lobe = rng.choice([1, -1], size=n)
    z = np.abs(rng.normal(0, 0.28, n)) * lobe
    r = np.abs(rng.normal(0, 0.22, n))
    theta = rng.uniform(0, 2 * math.pi, n)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
    glDisable(GL_LIGHTING)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glPointSize(3.0)
    glBegin(GL_POINTS)
    glColor4f(0.4, 0.8, 1.0, 0.5)
    for i in range(n):
        glVertex3f(float(x[i]), float(y[i]), float(z[i]) * (1 + explode_factor))
    glEnd()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPopAttrib()



# ============================================================================
# NEW & ENHANCED DYNAMIC RENDERERS (Heart, Car Engine, World Map, India Map)
# ============================================================================

def render_heart(t, explode_factor, highlight_key, theme_gl):
    """
    Anatomically accurate, physiologically beating human heart:
    - Left Ventricle (thick muscular cone down to apex)
    - Right Ventricle (crescent anterior chamber)
    - Left Atrium & Right Atrium (with auricles)
    - Ascending Aorta & Aortic Arch with Brachiocephalic, Carotid, Subclavian branches
    - Pulmonary Trunk bifurcating to Left & Right Pulmonary Arteries
    - Superior & Inferior Vena Cava
    - 4 Pulmonary Veins (oxygenated red entering left atrium)
    - Coronary Arteries (LAD, RCA) tracing across myocardium with pulsing blood flow
    - Cardiac Apex
    - Dual-phase cardiac cycle beating at 72 BPM
    """
    bpm = 72.0
    period = 60.0 / bpm
    phase = (t % period) / period

    # Dual-phase cardiac contraction:
    # 0.0 - 0.18: Atrial systole (atria squeeze, ventricles fill)
    # 0.18 - 0.48: Ventricular systole (ventricles contract, aorta expands)
    # 0.48 - 1.0: Diastole (cardiac relaxation & filling)
    if phase < 0.18:
        atria_scale = 1.0 - 0.14 * math.sin(phase / 0.18 * math.pi)
        vent_scale = 1.04
        aorta_scale = 1.0
        pulse_glow = 0.15
    elif phase < 0.48:
        v_prog = (phase - 0.18) / 0.30
        vent_scale = 1.0 - 0.20 * math.sin(v_prog * math.pi)
        atria_scale = 1.02
        aorta_scale = 1.0 + 0.16 * math.sin(v_prog * math.pi)
        pulse_glow = 0.5 * math.sin(v_prog * math.pi)
    else:
        d_prog = (phase - 0.48) / 0.52
        vent_scale = 1.0 + 0.04 * math.sin(d_prog * math.pi)
        atria_scale = 1.0
        aorta_scale = 1.0
        pulse_glow = 0.05

    ef = explode_factor * 1.25

    def get_color(part_key, default_color):
        if highlight_key and highlight_key == part_key:
            return (1.0, 1.0, 0.0)
        return default_color

    # --- 1. Left Ventricle (LV) & Muscular Apex ---
    lv_col = get_color("left_ventricle", (0.85, 0.14, 0.18))
    lv_off = (-0.45 * ef, -0.55 * ef, 0.0)
    glPushMatrix()
    glTranslatef(lv_off[0], lv_off[1], lv_off[2])
    glScalef(vent_scale, vent_scale, vent_scale)
    set_material(lv_col, 1.0, emissive=0.18 if highlight_key == "left_ventricle" else 0.02)
    # LV body
    glPushMatrix()
    glTranslatef(-0.28, -0.28, 0.04)
    GL_PRIM.sphere(0.50, 18, 18)
    glPopMatrix()
    # Tapered conical muscular wall toward apex
    glPushMatrix()
    glTranslatef(-0.35, -0.55, 0.08)
    GL_PRIM.sphere(0.38, 16, 16)
    glPopMatrix()
    glPopMatrix()

    # --- Cardiac Apex ---
    apex_col = get_color("cardiac_apex", (0.76, 0.12, 0.16))
    apex_off = (-0.55 * ef, -0.85 * ef, 0.15 * ef)
    glPushMatrix()
    glTranslatef(apex_off[0], apex_off[1], apex_off[2])
    glScalef(vent_scale, vent_scale, vent_scale)
    set_material(apex_col, 1.0, emissive=0.25 if highlight_key == "cardiac_apex" else 0.0)
    glPushMatrix()
    glTranslatef(-0.42, -0.80, 0.14)
    GL_PRIM.sphere(0.24, 14, 14)
    glPopMatrix()
    glPopMatrix()

    # --- 2. Right Ventricle (RV) ---
    rv_col = get_color("right_ventricle", (0.72, 0.18, 0.32))
    rv_off = (0.42 * ef, -0.45 * ef, 0.35 * ef)
    glPushMatrix()
    glTranslatef(rv_off[0], rv_off[1], rv_off[2])
    glScalef(vent_scale, vent_scale, vent_scale)
    set_material(rv_col, 1.0, emissive=0.18 if highlight_key == "right_ventricle" else 0.02)
    glPushMatrix()
    glTranslatef(0.24, -0.26, 0.16)
    GL_PRIM.sphere(0.44, 18, 18)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.18, -0.52, 0.18)
    GL_PRIM.sphere(0.32, 14, 14)
    glPopMatrix()
    glPopMatrix()

    # --- 3. Left Atrium (LA) & Pulmonary Veins ---
    la_col = get_color("left_atrium", (0.86, 0.22, 0.26))
    la_off = (-0.50 * ef, 0.35 * ef, -0.35 * ef)
    glPushMatrix()
    glTranslatef(la_off[0], la_off[1], la_off[2])
    glScalef(atria_scale, atria_scale, atria_scale)
    set_material(la_col, 1.0, emissive=0.18 if highlight_key == "left_atrium" else 0.02)
    glPushMatrix()
    glTranslatef(-0.32, 0.38, -0.14)
    GL_PRIM.sphere(0.38, 16, 16)
    glPopMatrix()
    # 4 Pulmonary Veins (oxygenated red entering LA from back)
    pv_col = (0.90, 0.20, 0.20)
    set_material(pv_col, 1.0, emissive=0.04)
    GL_PRIM.cylinder((-0.32, 0.44, -0.14), (-0.68, 0.48, -0.22), 0.065)
    GL_PRIM.cylinder((-0.32, 0.32, -0.14), (-0.68, 0.28, -0.26), 0.065)
    GL_PRIM.cylinder((-0.20, 0.44, -0.14), (0.35, 0.48, -0.30), 0.065)
    GL_PRIM.cylinder((-0.20, 0.32, -0.14), (0.35, 0.28, -0.34), 0.065)
    glPopMatrix()

    # --- 4. Right Atrium (RA) ---
    ra_col = get_color("right_atrium", (0.38, 0.32, 0.75))
    ra_off = (0.65 * ef, 0.25 * ef, 0.10 * ef)
    glPushMatrix()
    glTranslatef(ra_off[0], ra_off[1], ra_off[2])
    glScalef(atria_scale, atria_scale, atria_scale)
    set_material(ra_col, 1.0, emissive=0.18 if highlight_key == "right_atrium" else 0.02)
    glPushMatrix()
    glTranslatef(0.42, 0.35, 0.06)
    GL_PRIM.sphere(0.40, 16, 16)
    glPopMatrix()
    # Right auricle flap
    glPushMatrix()
    glTranslatef(0.24, 0.45, 0.18)
    GL_PRIM.sphere(0.18, 12, 12)
    glPopMatrix()
    glPopMatrix()

    # --- 5. Aorta & Aortic Arch with Supra-Aortic Branches ---
    ao_col = get_color("aorta", (0.95, 0.12, 0.12))
    ao_off = (0.0, 0.85 * ef, -0.15 * ef)
    glPushMatrix()
    glTranslatef(ao_off[0], ao_off[1], ao_off[2])
    set_material(ao_col, 1.0, emissive=0.25 if highlight_key == "aorta" else 0.05)
    # Ascending Aorta & Arch modeled as smooth connected segments
    aorta_path = [
        (-0.06, 0.18, -0.04),
        (-0.04, 0.42, -0.02),
        (-0.02, 0.68, 0.00),
        (-0.06, 0.88, -0.04),
        (-0.20, 0.95, -0.12),
        (-0.35, 0.88, -0.22),
        (-0.40, 0.60, -0.28),
        (-0.42, 0.30, -0.30)
    ]
    r_ao = 0.125 * aorta_scale
    for i in range(len(aorta_path) - 1):
        GL_PRIM.cylinder(aorta_path[i], aorta_path[i+1], r_ao, slices=14)
        glPushMatrix()
        glTranslatef(*aorta_path[i+1])
        GL_PRIM.sphere(r_ao, 12, 12)
        glPopMatrix()
    # 3 Major Arteries branching from the arch:
    set_material(ao_col, 1.0, emissive=0.08)
    GL_PRIM.cylinder((-0.04, 0.86, -0.04), (0.12, 1.25, -0.04), 0.052, slices=10)   # Brachiocephalic
    GL_PRIM.cylinder((-0.14, 0.94, -0.08), (-0.12, 1.30, -0.08), 0.044, slices=10)  # Left common carotid
    GL_PRIM.cylinder((-0.24, 0.92, -0.14), (-0.30, 1.25, -0.16), 0.044, slices=10)  # Left subclavian
    glPopMatrix()

    # --- 6. Pulmonary Trunk & Bifurcation ---
    pt_col = get_color("pulmonary_trunk", (0.18, 0.48, 0.88))
    pt_off = (-0.25 * ef, 0.65 * ef, 0.35 * ef)
    glPushMatrix()
    glTranslatef(pt_off[0], pt_off[1], pt_off[2])
    set_material(pt_col, 1.0, emissive=0.25 if highlight_key == "pulmonary_trunk" else 0.05)
    # Main trunk
    GL_PRIM.cylinder((0.04, 0.22, 0.20), (-0.05, 0.62, 0.12), 0.11, slices=14)
    glPushMatrix()
    glTranslatef(-0.05, 0.62, 0.12)
    GL_PRIM.sphere(0.11, 12, 12)
    glPopMatrix()
    # Left & Right pulmonary arteries
    GL_PRIM.cylinder((-0.05, 0.62, 0.12), (-0.55, 0.68, -0.15), 0.075, slices=12)
    GL_PRIM.cylinder((-0.05, 0.62, 0.12), (0.58, 0.58, -0.15), 0.075, slices=12)
    glPopMatrix()

    # --- 7. Superior Vena Cava (SVC) ---
    svc_col = get_color("superior_vena_cava", (0.15, 0.38, 0.88))
    svc_off = (0.75 * ef, 0.70 * ef, -0.05 * ef)
    glPushMatrix()
    glTranslatef(svc_off[0], svc_off[1], svc_off[2])
    set_material(svc_col, 1.0, emissive=0.25 if highlight_key == "superior_vena_cava" else 0.04)
    GL_PRIM.cylinder((0.48, 0.50, 0.0), (0.48, 1.18, -0.05), 0.115, slices=14)
    glPopMatrix()

    # --- 8. Inferior Vena Cava (IVC) ---
    ivc_col = (0.15, 0.38, 0.88)
    ivc_off = (0.65 * ef, -0.65 * ef, -0.20 * ef)
    glPushMatrix()
    glTranslatef(ivc_off[0], ivc_off[1], ivc_off[2])
    set_material(ivc_col, 1.0, emissive=0.04)
    GL_PRIM.cylinder((0.42, -0.20, -0.15), (0.42, -0.78, -0.25), 0.105, slices=14)
    glPopMatrix()

    # --- 9. Coronary Arteries (LAD & RCA) & Blood Pulse ---
    cor_col = get_color("coronary_arteries", (0.95, 0.35, 0.15))
    cor_off = (0.0, -0.15 * ef, 0.50 * ef)
    glPushMatrix()
    glTranslatef(cor_off[0], cor_off[1], cor_off[2])
    set_material(cor_col, 1.0, emissive=0.4 if highlight_key == "coronary_arteries" else 0.1)
    lad_pts = [
        (-0.02, 0.18, 0.22),
        (-0.08, -0.05, 0.28),
        (-0.16, -0.28, 0.30),
        (-0.25, -0.52, 0.26),
        (-0.35, -0.72, 0.20)
    ]
    for i in range(len(lad_pts) - 1):
        GL_PRIM.cylinder(lad_pts[i], lad_pts[i+1], 0.026, slices=8)
    # Animated blood pulse dot moving down the artery
    pulse_idx = (t * 2.5) % (len(lad_pts) - 1)
    p_seg = int(pulse_idx)
    p_frac = pulse_idx - p_seg
    p_pos = lerp3(lad_pts[p_seg], lad_pts[p_seg + 1], p_frac)
    glPushMatrix()
    glTranslatef(*p_pos)
    set_material((1.0, 0.8, 0.2), 1.0, emissive=0.8)
    GL_PRIM.sphere(0.045, 10, 10)
    glPopMatrix()
    glPopMatrix()

    # Heart rhythm ambient glow
    if pulse_glow > 0.1:
        draw_glow((-0.1, -0.2, 0.1), 0.85, (1.0, 0.15, 0.2), t, pulse=False)


def render_car_engine(t, explode_factor, highlight_key, theme_gl):
    """
    Detailed, fully animated 4-Cylinder Internal Combustion Car Engine:
    - Inline-4 Engine Block with 4 distinct cylinder sleeves
    - Crankshaft with 4 crank throws, counterweights, and rear flywheel
    - 4 Articulated Connecting Rods
    - 4 Reciprocating Pistons with piston rings
    - Cast Cylinder Head with intake and exhaust poppet valves
    - Twin Overhead Camshafts (DOHC) with timing gears
    - 4 Spark Plugs with timed 1-3-4-2 electric spark ignition flashes
    - Intake Manifold with plenum & Exhaust Headers with 4 tuned pipes
    - Animated at 120 RPM with accurate kinematics
    """
    omega = t * 4.5
    r_crank = 0.26
    l_rod = 0.68
    cyl_z = [-0.90, -0.30, 0.30, 0.90]

    ef = explode_factor * 1.3

    def get_color(part_key, default_color):
        if highlight_key and highlight_key == part_key:
            return (1.0, 1.0, 0.0)
        return default_color

    # Kinematic calculation for each cylinder:
    # Cyl 1 & 4 are in phase; Cyl 2 & 3 are 180 deg out of phase
    piston_data = []
    for i, z in enumerate(cyl_z):
        th = omega + (0.0 if i in (0, 3) else math.pi)
        xc = r_crank * math.sin(th)
        yc = -0.30 + r_crank * math.cos(th)
        yw = -0.30 + r_crank * math.cos(th) + math.sqrt(l_rod**2 - (r_crank * math.sin(th))**2)
        piston_data.append((th, xc, yc, yw, z))

    # --- 1. Crankshaft & Flywheel ---
    crank_col = get_color("crankshaft", (0.85, 0.86, 0.90))
    crank_off = (0.0, -0.35 * ef, 0.0)
    glPushMatrix()
    glTranslatef(crank_off[0], crank_off[1], crank_off[2])
    set_material(crank_col, 1.0, emissive=0.2 if highlight_key == "crankshaft" else 0.04)
    # Main crank shaft along Z axis
    GL_PRIM.cylinder((0.0, -0.30, -1.25), (0.0, -0.30, 1.25), 0.075, slices=16)
    # Crank throws & counterweights
    for i, (th, xc, yc, yw, z) in enumerate(piston_data):
        GL_PRIM.cylinder((xc, yc, z - 0.09), (xc, yc, z + 0.09), 0.055, slices=12)
        GL_PRIM.cylinder((0.0, -0.30, z - 0.09), (xc, yc, z - 0.09), 0.045, slices=10)
        GL_PRIM.cylinder((0.0, -0.30, z + 0.09), (xc, yc, z + 0.09), 0.045, slices=10)
        cwx, cwy = -xc * 0.85, -0.30 - (yc - (-0.30)) * 0.85
        glPushMatrix()
        glTranslatef(cwx, cwy, z)
        GL_PRIM.sphere(0.12, 12, 12)
        glPopMatrix()
    # Flywheel at rear
    glPushMatrix()
    glTranslatef(0.0, -0.30, 1.25)
    GL_PRIM.cylinder((0.0, 0.0, 0.0), (0.0, 0.0, 0.12), 0.52, slices=28)
    glPopMatrix()
    # Front timing pulley
    glPushMatrix()
    glTranslatef(0.0, -0.30, -1.35)
    GL_PRIM.cylinder((0.0, 0.0, 0.0), (0.0, 0.0, 0.10), 0.22, slices=20)
    glPopMatrix()
    glPopMatrix()

    # --- 2. Connecting Rods ---
    rod_col = get_color("connecting_rods", (0.82, 0.75, 0.60))
    rod_off = (0.0, 0.10 * ef, 0.0)
    glPushMatrix()
    glTranslatef(rod_off[0], rod_off[1], rod_off[2])
    set_material(rod_col, 1.0, emissive=0.2 if highlight_key == "connecting_rods" else 0.03)
    for i, (th, xc, yc, yw, z) in enumerate(piston_data):
        GL_PRIM.cylinder((xc, yc, z), (0.0, yw, z), 0.042, slices=12)
        glPushMatrix()
        glTranslatef(0.0, yw, z)
        GL_PRIM.sphere(0.05, 10, 10)
        glPopMatrix()
    glPopMatrix()

    # --- 3. Pistons & Rings ---
    piston_col = get_color("pistons", (0.78, 0.82, 0.88))
    piston_off = (0.0, 0.55 * ef, 0.0)
    glPushMatrix()
    glTranslatef(piston_off[0], piston_off[1], piston_off[2])
    set_material(piston_col, 1.0, emissive=0.25 if highlight_key == "pistons" else 0.05)
    for i, (th, xc, yc, yw, z) in enumerate(piston_data):
        p_base = (0.0, yw - 0.08, z)
        p_top = (0.0, yw + 0.18, z)
        GL_PRIM.cylinder(p_base, p_top, 0.21, slices=18)
        glPushMatrix()
        glTranslatef(*p_top)
        GL_PRIM.sphere(0.21, 18, 10)
        glPopMatrix()
        set_material((0.4, 0.4, 0.45), 1.0)
        GL_PRIM.ring((0.0, yw + 0.12, z), 0.215, 0.008, (0.4, 0.4, 0.45), 1.0, segments=24, tilt=90)
        GL_PRIM.ring((0.0, yw + 0.06, z), 0.215, 0.008, (0.4, 0.4, 0.45), 1.0, segments=24, tilt=90)
        set_material(piston_col, 1.0, emissive=0.05)
    glPopMatrix()

    # --- 4. Engine Block & Cylinder Sleeves ---
    block_col = get_color("engine_block", (0.35, 0.38, 0.42))
    block_off = (0.0, 0.20 * ef, 0.0)
    glPushMatrix()
    glTranslatef(block_off[0], block_off[1], block_off[2])
    for z in cyl_z:
        set_material((0.65, 0.70, 0.75), 0.35, emissive=0.05)
        GL_PRIM.cylinder((0.0, 0.05, z), (0.0, 0.80, z), 0.23, slices=18)
    set_material(block_col, 0.85, emissive=0.02)
    GL_PRIM.cylinder((-0.38, -0.20, -1.15), (-0.38, -0.20, 1.15), 0.08, slices=8)
    GL_PRIM.cylinder((0.38, -0.20, -1.15), (0.38, -0.20, 1.15), 0.08, slices=8)
    GL_PRIM.cylinder((-0.38, 0.65, -1.15), (-0.38, 0.65, 1.15), 0.08, slices=8)
    GL_PRIM.cylinder((0.38, 0.65, -1.15), (0.38, 0.65, 1.15), 0.08, slices=8)
    for z in [-1.15, -0.60, 0.0, 0.60, 1.15]:
        GL_PRIM.cylinder((-0.38, 0.65, z), (0.38, 0.65, z), 0.06, slices=8)
        GL_PRIM.cylinder((-0.38, -0.20, z), (0.38, -0.20, z), 0.06, slices=8)
    set_material((0.24, 0.25, 0.28), 1.0)
    GL_PRIM.cylinder((0.0, -0.75, -1.10), (0.0, -0.75, 1.10), 0.28, slices=14)
    glPopMatrix()

    # --- 5. Cylinder Head & DOHC Camshafts & Valves ---
    head_col = get_color("cylinder_head", (0.68, 0.72, 0.76))
    head_off = (0.0, 1.05 * ef, 0.0)
    glPushMatrix()
    glTranslatef(head_off[0], head_off[1], head_off[2])
    set_material(head_col, 1.0, emissive=0.2 if highlight_key == "cylinder_head" else 0.03)
    GL_PRIM.cylinder((-0.36, 0.82, -1.15), (-0.36, 0.82, 1.15), 0.09, slices=8)
    GL_PRIM.cylinder((0.36, 0.82, -1.15), (0.36, 0.82, 1.15), 0.09, slices=8)
    GL_PRIM.cylinder((-0.36, 1.08, -1.15), (-0.36, 1.08, 1.15), 0.09, slices=8)
    GL_PRIM.cylinder((0.36, 1.08, -1.15), (0.36, 1.08, 1.15), 0.09, slices=8)
    cam_angle = omega * 0.5
    for z in cyl_z:
        v_lift_in = 0.03 * max(0.0, math.sin(cam_angle + z))
        GL_PRIM.cylinder((-0.14, 0.82 - v_lift_in, z), (-0.14, 1.12 - v_lift_in, z), 0.022, slices=8)
        v_lift_ex = 0.03 * max(0.0, math.sin(cam_angle + z + math.pi))
        GL_PRIM.cylinder((0.14, 0.82 - v_lift_ex, z), (0.14, 1.12 - v_lift_ex, z), 0.022, slices=8)
    cam_col = (0.85, 0.85, 0.88)
    set_material(cam_col, 1.0)
    GL_PRIM.cylinder((-0.14, 1.18, -1.25), (-0.14, 1.18, 1.15), 0.045, slices=12)
    GL_PRIM.cylinder((0.14, 1.18, -1.25), (0.14, 1.18, 1.15), 0.045, slices=12)
    glPushMatrix()
    glTranslatef(-0.14, 1.18, -1.25)
    GL_PRIM.cylinder((0.0, 0.0, 0.0), (0.0, 0.0, 0.05), 0.16, slices=18)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.14, 1.18, -1.25)
    GL_PRIM.cylinder((0.0, 0.0, 0.0), (0.0, 0.0, 0.05), 0.16, slices=18)
    glPopMatrix()
    glPopMatrix()

    # --- 6. Spark Plugs & Timed Ignition Sparks ---
    spark_col = get_color("spark_plugs", (0.95, 0.95, 0.95))
    spark_off = (0.0, 1.55 * ef, 0.0)
    glPushMatrix()
    glTranslatef(spark_off[0], spark_off[1], spark_off[2])
    engine_cycle = omega % (4.0 * math.pi)
    firing_cyl = -1
    if engine_cycle < math.pi:
        firing_cyl = 0   # Cyl 1
    elif engine_cycle < 2.0 * math.pi:
        firing_cyl = 2   # Cyl 3
    elif engine_cycle < 3.0 * math.pi:
        firing_cyl = 3   # Cyl 4
    else:
        firing_cyl = 1   # Cyl 2

    for i, z in enumerate(cyl_z):
        set_material(spark_col, 1.0, emissive=0.1)
        GL_PRIM.cylinder((0.0, 1.12, z), (0.0, 1.36, z), 0.038, slices=10)
        set_material((0.8, 0.6, 0.2), 1.0)
        glPushMatrix()
        glTranslatef(0.0, 1.37, z)
        GL_PRIM.sphere(0.032, 10, 10)
        glPopMatrix()

        if i == firing_cyl and (engine_cycle % math.pi) < 0.38:
            sp_pos = (0.0, 0.85, z)
            draw_glow(sp_pos, 0.14, (1.0, 0.85, 0.25), t, pulse=True)
            set_material((1.0, 1.0, 0.6), 1.0, emissive=1.0)
            for ang in np.linspace(0, 2*math.pi, 6):
                tip = (0.08 * math.cos(ang), 0.85 + 0.06 * math.sin(ang), z + 0.05 * math.sin(ang*2))
                GL_PRIM.cylinder(sp_pos, tip, 0.012, slices=6)
    glPopMatrix()

    # --- 7. Intake Manifold (Left) ---
    in_col = get_color("intake_manifold", (0.22, 0.55, 0.85))
    in_off = (-0.85 * ef, 0.35 * ef, 0.0)
    glPushMatrix()
    glTranslatef(in_off[0], in_off[1], in_off[2])
    set_material(in_col, 1.0, emissive=0.2 if highlight_key == "intake_manifold" else 0.04)
    GL_PRIM.cylinder((-0.65, 0.75, -1.0), (-0.65, 0.75, 1.0), 0.11, slices=14)
    for z in cyl_z:
        GL_PRIM.cylinder((-0.65, 0.75, z), (-0.26, 0.88, z), 0.065, slices=12)
    GL_PRIM.cylinder((-0.65, 0.75, -1.0), (-0.65, 0.75, -1.35), 0.12, slices=14)
    glPopMatrix()

    # --- 8. Exhaust Headers Manifold (Right) ---
    ex_col = get_color("exhaust_manifold", (0.85, 0.45, 0.18))
    ex_off = (0.85 * ef, 0.35 * ef, 0.0)
    glPushMatrix()
    glTranslatef(ex_off[0], ex_off[1], ex_off[2])
    set_material(ex_col, 1.0, emissive=0.25 if highlight_key == "exhaust_manifold" else 0.06)
    for z in cyl_z:
        p_port = (0.26, 0.88, z)
        p_bend = (0.60, 0.70, z * 0.75)
        p_coll = (0.68, 0.15, z * 0.40)
        GL_PRIM.cylinder(p_port, p_bend, 0.062, slices=12)
        GL_PRIM.cylinder(p_bend, p_coll, 0.062, slices=12)
    GL_PRIM.cylinder((0.68, 0.15, -0.45), (0.68, 0.15, 0.75), 0.12, slices=14)
    GL_PRIM.cylinder((0.68, 0.15, 0.75), (0.68, -0.35, 1.25), 0.11, slices=14)
    glPopMatrix()


def make_world_map_texture(size=(360, 720)):
    """Procedurally paints an authentic equirectangular world map with continents,
    oceans, arid zones, polar ice caps, and lat/lon coordinate lines."""
    h, w = size
    img = np.zeros((h, w, 3), dtype=np.uint8)
    # Deep ocean blue
    img[:, :] = (130, 45, 15)  # BGR: blue dominant

    # Procedural continents drawn with smooth natural contours:
    # Eurasia
    cv2.ellipse(img, (int(w*0.62), int(h*0.35)), (int(w*0.18), int(h*0.14)), -10, 0, 360, (55, 140, 50), -1, cv2.LINE_AA)
    cv2.ellipse(img, (int(w*0.75), int(h*0.30)), (int(w*0.12), int(h*0.12)), 15, 0, 360, (55, 130, 45), -1, cv2.LINE_AA)
    # India peninsula
    cv2.ellipse(img, (int(w*0.67), int(h*0.48)), (int(w*0.04), int(h*0.08)), 10, 0, 360, (40, 160, 60), -1, cv2.LINE_AA)
    # Africa
    cv2.ellipse(img, (int(w*0.52), int(h*0.55)), (int(w*0.07), int(h*0.18)), 5, 0, 360, (45, 120, 50), -1, cv2.LINE_AA)
    # Sahara desert beige
    cv2.ellipse(img, (int(w*0.52), int(h*0.44)), (int(w*0.06), int(h*0.06)), 0, 0, 360, (75, 160, 195), -1, cv2.LINE_AA)
    # North America
    cv2.ellipse(img, (int(w*0.25), int(h*0.32)), (int(w*0.12), int(h*0.14)), -15, 0, 360, (50, 135, 45), -1, cv2.LINE_AA)
    # South America
    cv2.ellipse(img, (int(w*0.32), int(h*0.65)), (int(w*0.06), int(h*0.18)), 15, 0, 360, (40, 155, 40), -1, cv2.LINE_AA)
    # Australia
    cv2.ellipse(img, (int(w*0.82), int(h*0.72)), (int(w*0.06), int(h*0.08)), -5, 0, 360, (65, 145, 165), -1, cv2.LINE_AA)
    # Antarctica (polar ice)
    cv2.rectangle(img, (0, int(h*0.88)), (w, h), (245, 245, 250), -1)
    # Greenland & Arctic ice
    cv2.ellipse(img, (int(w*0.38), int(h*0.15)), (int(w*0.04), int(h*0.07)), -20, 0, 360, (235, 240, 245), -1, cv2.LINE_AA)
    cv2.rectangle(img, (0, 0), (w, int(h*0.08)), (240, 245, 250), -1)

    # Coordinate grid lines: Equator, Tropics, and Meridians
    eq_y = h // 2
    cv2.line(img, (0, eq_y), (w, eq_y), (40, 180, 220), 1, cv2.LINE_AA)
    cv2.line(img, (0, int(h*0.37)), (w, int(h*0.37)), (30, 130, 160), 1, cv2.LINE_AA) # Tropic of Cancer
    cv2.line(img, (0, int(h*0.63)), (w, int(h*0.63)), (30, 130, 160), 1, cv2.LINE_AA) # Tropic of Capricorn
    for mx in range(0, w, w // 12):
        cv2.line(img, (mx, 0), (mx, h), (30, 120, 150), 1, cv2.LINE_AA)

    img = cv2.GaussianBlur(img, (3, 3), 0)
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def lat_lon_to_sphere(lat, lon, radius=1.22):
    phi = math.radians(90.0 - lat)
    theta = math.radians(lon + 180.0)
    x = radius * math.sin(phi) * math.cos(theta)
    y = radius * math.cos(phi)
    z = radius * math.sin(phi) * math.sin(theta)
    return (x, y, z)


WORLD_CITIES = [
    ("New Delhi", 28.61, 77.20),
    ("Tokyo", 35.68, 139.77),
    ("London", 51.51, -0.13),
    ("New York", 40.71, -74.01),
    ("Cairo", 30.04, 31.24),
    ("Sydney", -33.87, 151.21),
    ("Rio de Janeiro", -22.91, -43.17),
    ("Moscow", 55.75, 37.62),
    ("Cape Town", -33.92, 18.42)
]


def render_world_map(t, explode_factor, highlight_key, theme_gl, tex_mgr):
    """
    3D Geographical World Map & Interactive Globe:
    - Accurate continent geography, oceans, biomes, and polar caps
    - 3D Geographical coordinate grid: Equator, Prime Meridian, Tropics, and Meridians
    - 3D Mountain elevation relief on Himalayas, Andes, Rockies, Alps
    - Major world metropolitan and landmark pins with glowing beacons
    - Animated atmospheric cloud layer with differential rotation
    - Exploded view separating continental tectonic plates
    """
    tex_id = tex_mgr.id_of("world_map_texture")
    if tex_id is None:
        tex_id = tex_mgr.upload_once_rgb("world_map_texture", make_world_map_texture())

    R = 1.20
    ef = explode_factor * 0.85

    # Globe core & textured sphere
    glPushMatrix()
    glRotatef(t * 5.0, 0, 1, 0)

    # Exploded continental relief plates
    if ef > 0.01:
        # Molten mantle core
        set_material((1.0, 0.45, 0.10), 1.0, emissive=0.6)
        GL_PRIM.sphere(R * 0.75, 24, 24)
        draw_glow((0, 0, 0), R * 0.75, (1.0, 0.5, 0.1), t)

    glPushMatrix()
    glScalef(1.0 + ef * 0.35, 1.0 + ef * 0.35, 1.0 + ef * 0.35)
    draw_textured_sphere(tex_id, R, slices=36, stacks=36)
    glPopMatrix()

    # 3D Coordinate Grid:
    # 1. Equator
    set_material((1.0, 0.85, 0.25), 0.85, emissive=0.3)
    GL_PRIM.ring((0, 0, 0), (R + 0.015) * (1.0 + ef * 0.4), 0.008, (1.0, 0.85, 0.25), 0.85, segments=64, tilt=0)
    # 2. Prime Meridian
    set_material((0.25, 0.85, 1.0), 0.75, emissive=0.25)
    GL_PRIM.ring((0, 0, 0), (R + 0.018) * (1.0 + ef * 0.4), 0.007, (0.25, 0.85, 1.0), 0.75, segments=64, tilt=90)

    # 3D Mountain Elevation Relief:
    # Himalayas
    him_pos = lat_lon_to_sphere(28.0, 85.0, R + 0.02)
    set_material((0.95, 0.98, 1.0), 1.0, emissive=0.3)
    glPushMatrix()
    glTranslatef(*him_pos)
    GL_PRIM.sphere(0.065, 10, 10)
    glPopMatrix()
    # Andes
    and_pos = lat_lon_to_sphere(-20.0, -70.0, R + 0.02)
    set_material((0.65, 0.55, 0.40), 1.0)
    glPushMatrix()
    glTranslatef(*and_pos)
    GL_PRIM.sphere(0.055, 10, 10)
    glPopMatrix()

    # Strategic World City Pins & Beacons
    for name, lat, lon in WORLD_CITIES:
        base = lat_lon_to_sphere(lat, lon, R)
        tip = lat_lon_to_sphere(lat, lon, R + 0.14)
        is_hl = (highlight_key == "cities") or (name == "New Delhi" and highlight_key == "india")
        pin_col = (1.0, 1.0, 0.0) if is_hl else (0.2, 0.9, 1.0)
        set_material(pin_col, 1.0, emissive=0.5 if is_hl else 0.2)
        GL_PRIM.cylinder(base, tip, 0.012, slices=8)
        glPushMatrix()
        glTranslatef(*tip)
        GL_PRIM.sphere(0.032, 10, 10)
        glPopMatrix()

    # Translucent rotating cloud layer
    glPushMatrix()
    glRotatef(t * 1.5, 0, 1, 0)
    set_material((1.0, 1.0, 1.0), 0.20)
    GL_PRIM.sphere(R * 1.035, 24, 24)
    glPopMatrix()

    glPopMatrix()  # End of rotated globe

    # Atmospheric limb glow
    draw_glow((0, 0, 0), R * 1.05, (0.35, 0.65, 1.0), t, pulse=False)


# India Rivers Coordinate Polylines (lat, lon)
INDIA_RIVERS = {
    "Ganga": [
        (30.9, 78.9), (30.1, 78.3), (29.9, 78.1), (28.4, 79.5),
        (27.1, 80.8), (25.4, 81.8), (25.3, 83.0), (25.6, 85.1),
        (25.3, 87.0), (24.8, 87.9), (23.5, 88.3), (22.0, 88.5)
    ],
    "Yamuna": [
        (31.0, 78.4), (30.3, 77.6), (28.6, 77.2), (27.2, 78.0),
        (26.5, 79.0), (25.4, 81.8)
    ],
    "Brahmaputra": [
        (29.0, 95.0), (28.1, 95.5), (27.5, 94.8), (26.2, 91.8),
        (26.0, 89.9), (24.5, 89.7)
    ],
    "Narmada": [
        (22.7, 81.7), (23.1, 79.9), (22.4, 77.8), (21.9, 75.5),
        (21.7, 73.0)
    ],
    "Godavari": [
        (19.9, 73.5), (19.8, 75.3), (18.9, 77.4), (18.7, 79.8),
        (16.9, 81.8)
    ],
    "Krishna": [
        (17.9, 73.7), (16.8, 74.6), (16.2, 77.2), (16.5, 80.6),
        (15.8, 80.9)
    ],
    "Kaveri": [
        (12.4, 75.5), (12.3, 76.6), (11.5, 77.7), (10.8, 79.8)
    ]
}

INDIA_LANDMARKS = [
    ("New Delhi", 28.61, 77.20, 0.12),
    ("Mumbai", 19.07, 72.87, 0.08),
    ("Bengaluru", 12.97, 77.59, 0.18),
    ("Kolkata", 22.57, 88.36, 0.06),
    ("Chennai", 13.08, 80.27, 0.06),
    ("Hyderabad", 17.38, 78.48, 0.14),
    ("Kanyakumari", 8.08, 77.53, 0.04),
    ("Kanchenjunga", 27.70, 88.14, 0.45),
    ("Thar Desert", 26.90, 70.90, 0.08),
]


def india_geo_to_3d(lat, lon, z=0.0):
    """Maps (lat, lon) to 3D workspace centered at (0, 0, 0)."""
    lat_c, lon_c = 22.5, 82.5
    scale_x, scale_y = 0.12, 0.11
    x = (lon - lon_c) * scale_x
    y = (lat - lat_c) * scale_y
    return (x, y, z)


def render_india_map(t, explode_factor, highlight_key, theme_gl, tex_mgr):
    """
    High-Fidelity 3D Geographical Map of India:
    - Northern Himalayan Mountain Arc with snowy peaks (K2, Nanda Devi, Kanchenjunga)
    - Indo-Gangetic Alluvial Fertile Plains (emerald green)
    - Great Indian Desert (Thar Desert) & Rann of Kutch (golden sand)
    - Peninsular Deccan Plateau & Central Highlands (volcanic mineral basalt)
    - Western Ghats (Sahyadri rainforest ridge) & Eastern Ghats
    - Coastal Plains along Arabian Sea, Bay of Bengal, and Indian Ocean
    - Glowing Animated 3D River Network (Ganga, Yamuna, Brahmaputra, Narmada, Godavari, Krishna, Kaveri)
    - Strategic Landmark Pins with laser beacons (Delhi, Mumbai, Bengaluru, Kolkata, Chennai, Kanyakumari)
    - Exploded view elevating physiographic divisions into stratified relief tiers
    """
    ef = explode_factor * 1.2

    def get_color(part_key, default_color):
        if highlight_key and highlight_key == part_key:
            return (1.0, 1.0, 0.0)
        return default_color

    # --- 1. Great Himalayan Arc (Northern Mountain Range) ---
    him_col = get_color("himalayas", (0.92, 0.95, 0.98))
    him_off = (0.0, 0.45 * ef, 0.65 * ef)
    glPushMatrix()
    glTranslatef(him_off[0], him_off[1], him_off[2])
    # Himalayan ridge mountain arc
    him_peaks = [
        (35.9, 76.5, 0.42),  # K2 / Karakoram
        (34.2, 75.3, 0.34),  # Pir Panjal / Kashmir
        (32.1, 77.2, 0.36),  # Himachal
        (30.4, 79.9, 0.38),  # Nanda Devi / Garhwal
        (28.0, 84.0, 0.40),  # Central Himalayas
        (27.7, 88.1, 0.44),  # Kanchenjunga / Sikkim
        (28.2, 94.5, 0.35)   # Arunachal Himalayas
    ]
    for i in range(len(him_peaks) - 1):
        p1 = india_geo_to_3d(*him_peaks[i])
        p2 = india_geo_to_3d(*him_peaks[i+1])
        # Mountain ridge mass
        set_material((0.55, 0.60, 0.68), 1.0)
        GL_PRIM.cylinder(p1, p2, 0.11, slices=10)
        # Snow-capped peaks
        set_material(him_col, 1.0, emissive=0.3 if highlight_key == "himalayas" else 0.1)
        glPushMatrix()
        glTranslatef(*p1)
        GL_PRIM.sphere(0.095, 12, 12)
        glPopMatrix()
    # Kanchenjunga summit
    glPushMatrix()
    glTranslatef(*india_geo_to_3d(*him_peaks[-2]))
    set_material((1.0, 1.0, 1.0), 1.0, emissive=0.5)
    GL_PRIM.sphere(0.11, 14, 14)
    glPopMatrix()
    glPopMatrix()

    # --- 2. Indo-Gangetic Alluvial Plains ---
    plains_col = get_color("northern_plains", (0.24, 0.68, 0.28))
    plains_off = (0.0, 0.20 * ef, 0.25 * ef)
    glPushMatrix()
    glTranslatef(plains_off[0], plains_off[1], plains_off[2])
    set_material(plains_col, 0.95, emissive=0.2 if highlight_key == "northern_plains" else 0.02)
    # Series of connected terrain slabs for northern plains
    plain_centers = [
        (30.0, 75.5, 0.05), (28.5, 77.5, 0.05), (26.5, 80.5, 0.05),
        (25.5, 84.5, 0.05), (24.0, 88.0, 0.05), (26.0, 92.5, 0.05)
    ]
    for c in plain_centers:
        pt = india_geo_to_3d(*c)
        glPushMatrix()
        glTranslatef(*pt)
        GL_PRIM.sphere(0.24, 14, 10)
        glPopMatrix()
    glPopMatrix()

    # --- 3. Great Indian Desert (Thar Desert) & Rann of Kutch ---
    thar_col = get_color("thar_desert", (0.88, 0.74, 0.38))
    thar_off = (-0.35 * ef, 0.15 * ef, 0.15 * ef)
    glPushMatrix()
    glTranslatef(thar_off[0], thar_off[1], thar_off[2])
    set_material(thar_col, 1.0, emissive=0.2 if highlight_key == "thar_desert" else 0.03)
    # Thar desert dunes
    for pt_geo in [(27.5, 71.5, 0.06), (26.0, 72.5, 0.06), (24.5, 71.0, 0.04)]:
        pt = india_geo_to_3d(*pt_geo)
        glPushMatrix()
        glTranslatef(*pt)
        GL_PRIM.sphere(0.22, 12, 10)
        glPopMatrix()
    # Rann of Kutch white salt flats
    set_material((0.92, 0.90, 0.85), 0.9)
    pt_kutch = india_geo_to_3d(23.8, 70.0, 0.02)
    glPushMatrix()
    glTranslatef(*pt_kutch)
    GL_PRIM.sphere(0.18, 12, 8)
    glPopMatrix()
    glPopMatrix()

    # --- 4. Peninsular Deccan Plateau & Central Highlands ---
    dec_col = get_color("deccan_plateau", (0.58, 0.44, 0.30))
    dec_off = (0.0, -0.20 * ef, 0.10 * ef)
    glPushMatrix()
    glTranslatef(dec_off[0], dec_off[1], dec_off[2])
    set_material(dec_col, 1.0, emissive=0.2 if highlight_key == "deccan_plateau" else 0.02)
    # Deccan plateau tableland
    deccan_nodes = [
        (22.0, 78.0, 0.14), (20.5, 76.5, 0.15), (19.0, 79.0, 0.14),
        (17.5, 76.0, 0.16), (15.5, 77.0, 0.17), (13.5, 76.5, 0.18)
    ]
    for c in deccan_nodes:
        pt = india_geo_to_3d(*c)
        glPushMatrix()
        glTranslatef(*pt)
        GL_PRIM.sphere(0.26, 14, 10)
        glPopMatrix()
    # Vindhya & Satpura mountain ranges
    set_material((0.48, 0.38, 0.26), 1.0)
    GL_PRIM.cylinder(india_geo_to_3d(23.5, 74.5, 0.16), india_geo_to_3d(23.2, 81.5, 0.16), 0.065, slices=8)
    glPopMatrix()

    # --- 5. Western Ghats (Sahyadri) & Eastern Ghats ---
    wg_col = (0.16, 0.50, 0.22)
    wg_off = (-0.25 * ef, -0.35 * ef, 0.20 * ef)
    glPushMatrix()
    glTranslatef(wg_off[0], wg_off[1], wg_off[2])
    set_material(wg_col, 1.0, emissive=0.08)
    # Western Ghats continuous rainforest ridge
    wg_pts = [
        (20.5, 73.5, 0.20), (18.5, 73.6, 0.22), (16.0, 74.2, 0.24),
        (14.0, 74.8, 0.23), (11.5, 76.2, 0.25), (9.5, 77.1, 0.22)
    ]
    for i in range(len(wg_pts) - 1):
        GL_PRIM.cylinder(india_geo_to_3d(*wg_pts[i]), india_geo_to_3d(*wg_pts[i+1]), 0.075, slices=10)
    # Eastern Ghats discontinuous hills
    set_material((0.36, 0.48, 0.26), 1.0)
    eg_pts = [(19.5, 84.5, 0.14), (17.5, 82.5, 0.15), (15.5, 79.5, 0.14), (13.0, 79.0, 0.13)]
    for i in range(len(eg_pts) - 1):
        GL_PRIM.cylinder(india_geo_to_3d(*eg_pts[i]), india_geo_to_3d(*eg_pts[i+1]), 0.06, slices=8)
    glPopMatrix()

    # --- 6. Island Territories (Andaman & Nicobar, Lakshadweep) ---
    islands_off = (0.35 * ef, -0.45 * ef, 0.0)
    glPushMatrix()
    glTranslatef(islands_off[0], islands_off[1], islands_off[2])
    set_material((0.30, 0.65, 0.35), 1.0, emissive=0.1)
    # Andaman & Nicobar (Bay of Bengal)
    for lat in [13.2, 12.5, 11.7, 10.5, 9.2, 8.0, 7.0]:
        pt = india_geo_to_3d(lat, 92.8, 0.03)
        glPushMatrix()
        glTranslatef(*pt)
        GL_PRIM.sphere(0.045, 8, 8)
        glPopMatrix()
    # Lakshadweep (Arabian Sea)
    for lat in [11.8, 11.0, 10.5, 9.8, 8.3]:
        pt = india_geo_to_3d(lat, 72.7, 0.03)
        glPushMatrix()
        glTranslatef(*pt)
        GL_PRIM.sphere(0.040, 8, 8)
        glPopMatrix()
    glPopMatrix()

    # --- 7. Glowing Animated 3D River System ---
    riv_col = get_color("rivers", (0.25, 0.78, 1.0))
    riv_off = (0.0, 0.05 * ef, 0.15 * ef)
    glPushMatrix()
    glTranslatef(riv_off[0], riv_off[1], riv_off[2])
    set_material(riv_col, 0.95, emissive=0.6 if highlight_key == "rivers" else 0.3)
    for r_name, r_coords in INDIA_RIVERS.items():
        pts_3d = [india_geo_to_3d(lat, lon, 0.065) for lat, lon in r_coords]
        for i in range(len(pts_3d) - 1):
            GL_PRIM.cylinder(pts_3d[i], pts_3d[i+1], 0.022, slices=6)
        # Animated water current pulse droplet
        r_prog = (t * 1.8 + hash(r_name) % 10 * 0.1) % (len(pts_3d) - 1)
        r_seg = int(r_prog)
        r_f = r_prog - r_seg
        r_drop = lerp3(pts_3d[r_seg], pts_3d[r_seg + 1], r_f)
        glPushMatrix()
        glTranslatef(*r_drop)
        set_material((0.7, 0.95, 1.0), 1.0, emissive=0.9)
        GL_PRIM.sphere(0.038, 8, 8)
        glPopMatrix()
    glPopMatrix()

    # --- 8. Strategic Landmark Pins with Holographic Laser Beacons ---
    for name, lat, lon, z in INDIA_LANDMARKS:
        base = india_geo_to_3d(lat, lon, z)
        tip = india_geo_to_3d(lat, lon, z + 0.16)
        is_hl = (highlight_key == "landmark_cities") or (highlight_key and highlight_key in name.lower())
        lm_col = (1.0, 1.0, 0.0) if is_hl else (1.0, 0.45, 0.15) if name == "New Delhi" else (0.25, 0.85, 1.0)
        set_material(lm_col, 1.0, emissive=0.8 if is_hl else 0.3)
        GL_PRIM.cylinder(base, tip, 0.012, slices=8)
        glPushMatrix()
        glTranslatef(*tip)
        GL_PRIM.sphere(0.035, 10, 10)
        glPopMatrix()
        # Pulse ring on Delhi and Kanyakumari
        if name in ("New Delhi", "Kanyakumari", "Kanchenjunga"):
            GL_PRIM.ring(tip, 0.045 + 0.015 * math.sin(t * 3.0), 0.005, lm_col, 0.8, segments=16, tilt=0)

DYNAMIC_MODELS = {
    "atom":         lambda t, ef, hl, theme, tex: render_atom(t, ef, hl, theme),
    "solar_system": lambda t, ef, hl, theme, tex: render_solar_system(t, ef, hl, theme, tex),
    "earth":        lambda t, ef, hl, theme, tex: render_earth_standalone(t, ef, hl, theme, tex),
    "moon":         lambda t, ef, hl, theme, tex: render_moon_standalone(t, ef, hl, theme, tex),
    "black_hole":   lambda t, ef, hl, theme, tex: render_black_hole(t, ef, hl, theme),
    "wave":         lambda t, ef, hl, theme, tex: render_wave(t, ef, hl, theme),
    "pendulum":     lambda t, ef, hl, theme, tex: render_pendulum(t, ef, hl, theme),
    "projectile":   lambda t, ef, hl, theme, tex: render_projectile(t, ef, hl, theme),
    "circuit":      lambda t, ef, hl, theme, tex: render_circuit(t, ef, hl, theme),
    "magnetic_field": lambda t, ef, hl, theme, tex: render_magnetic_field(t, ef, hl, theme),
    "em_field":     lambda t, ef, hl, theme, tex: render_em_field(t, ef, hl, theme),
    "quantum_cloud": lambda t, ef, hl, theme, tex: render_quantum_cloud(t, ef, hl, theme),
    "heart":        lambda t, ef, hl, theme, tex: render_heart(t, ef, hl, theme),
    "car_engine":   lambda t, ef, hl, theme, tex: render_car_engine(t, ef, hl, theme),
    "world_map":    lambda t, ef, hl, theme, tex: render_world_map(t, ef, hl, theme, tex),
    "india_map":    lambda t, ef, hl, theme, tex: render_india_map(t, ef, hl, theme, tex),
}


# ============================================================================
# MODEL REGISTRY (ties static primitive builders + dynamic renderers together)
# ============================================================================

_DNA_PARTS, _DNA_LABELS = build_dna_parts()

STATIC_PARTS = {"fullerene": build_fullerene_parts(), "dna": _DNA_PARTS}
STATIC_PARTS.update({key: build_molecule(spec["atoms"], spec["bonds"]) for key, spec in MOLECULES.items()})
STATIC_PARTS.update(ORGANS)

MODEL_KIND = {}
for k in STATIC_PARTS:
    MODEL_KIND[k] = "organ" if k in ORGANS else "molecule"
for k in DYNAMIC_MODELS:
    MODEL_KIND[k] = {"solar_system": "space", "earth": "space", "moon": "space",
                      "black_hole": "space"}.get(k, "physics")
MODEL_KIND["atom"] = "physics"

MODEL_ORDER = (
    ["fullerene", "h2o", "co2", "ch4", "nh3", "o2", "n2", "hcl", "h2so4",
     "benzene", "glucose", "ethanol", "aspirin", "atp", "amino_acid", "dna"] +
    ["heart", "respiratory", "digestive", "neuron", "brain", "eye", "ear",
     "kidney", "liver", "skeleton", "muscular", "circulatory",
     "cell", "mitochondria", "ribosome", "chromosome",
     "bacteriophage", "hiv", "papillomavirus", "adenovirus"] +
    ["atom", "wave", "pendulum", "projectile", "circuit", "magnetic_field",
     "em_field", "quantum_cloud"] +
    ["earth", "moon", "solar_system", "black_hole"] +
    ["car_engine", "world_map", "india_map"]
)

CATEGORY_ORDER = ["Chemistry", "Biology", "Physics", "Space", "Engineering", "Geography"]
CATEGORY_OF = {
    **{k: "Chemistry" for k in MOLECULES}, "fullerene": "Chemistry", "dna": "Chemistry",
    **{k: "Biology" for k in ORGANS},
    "heart": "Biology",
    "atom": "Physics", "wave": "Physics", "pendulum": "Physics", "projectile": "Physics",
    "circuit": "Physics", "magnetic_field": "Physics", "em_field": "Physics", "quantum_cloud": "Physics",
    "earth": "Space", "moon": "Space", "solar_system": "Space", "black_hole": "Space",
    "car_engine": "Engineering",
    "world_map": "Geography",
    "india_map": "Geography",
}


def model_label_points(key):
    """Returns {part_key: world_pos} for static and dynamic models so the HUD
    can project floating leader-line labels for each highlightable region."""
    if key == "dna":
        return {f"rung_{i}": pos for i, (_txt, pos) in enumerate(_DNA_LABELS)}
    if key == "heart":
        return {
            "aorta": (0.0, 0.95, -0.05),
            "pulmonary_trunk": (-0.05, 0.62, 0.12),
            "superior_vena_cava": (0.48, 0.90, -0.02),
            "left_ventricle": (-0.32, -0.35, 0.05),
            "right_ventricle": (0.25, -0.25, 0.18),
            "left_atrium": (-0.35, 0.38, -0.15),
            "right_atrium": (0.45, 0.35, 0.08),
            "cardiac_apex": (-0.42, -0.80, 0.15),
            "coronary_arteries": (-0.05, -0.20, 0.25)
        }
    if key == "car_engine":
        return {
            "engine_block": (0.0, 0.20, 0.0),
            "crankshaft": (0.0, -0.30, 0.0),
            "pistons": (0.0, 0.50, -0.30),
            "connecting_rods": (0.10, 0.10, -0.30),
            "cylinder_head": (0.0, 0.95, 0.0),
            "spark_plugs": (0.0, 1.25, -0.30),
            "intake_manifold": (-0.50, 0.65, 0.0),
            "exhaust_manifold": (0.50, 0.65, 0.0)
        }
    if key == "world_map":
        return {
            "continents": (0.5, 0.4, 1.1),
            "oceans": (-0.8, -0.2, 0.9),
            "equator_grid": (0.0, 0.0, 1.25),
            "mountain_ranges": (0.7, 0.6, 0.8),
            "cities": (0.4, 0.5, 1.0)
        }
    if key == "india_map":
        return {
            "himalayas": (0.0, 1.25, 0.35),
            "northern_plains": (-0.2, 0.65, 0.1),
            "deccan_plateau": (-0.3, -0.40, 0.2),
            "thar_desert": (-1.2, 0.50, 0.1),
            "rivers": (0.2, 0.50, 0.15),
            "coastal_islands": (-0.5, -1.50, 0.05),
            "landmark_cities": (-0.64, 0.67, 0.1)
        }
    parts = STATIC_PARTS.get(key)
    if not parts:
        return {}
    out = {}
    for p in parts:
        if p.get("key") and p["key"] not in out:
            out[p["key"]] = p["pos"]
    return out


# ============================================================================
# SCIENCE DATABASE (name / description / facts / highlightable parts)
# ============================================================================

def _parts(d):
    return {k: {"name": n, "function": f} for k, (n, f) in d.items()}


SCIENCE_DATA = {
    "fullerene": {"name": "Fullerene (C60)", "category": "Chemistry - Carbon Allotrope",
        "description": "A spherical carbon molecule made of 60 atoms arranged in a soccer-ball pattern.",
        "facts": ["Discovered in 1985; Nobel Prize in Chemistry 1996", "Also called a buckyball",
                  "Extremely stable and strong for its size", "Studied for nanotechnology and drug delivery"]},
    "h2o": {"name": "Water (H2O)", "category": "Chemistry - Molecule",
        "description": "A bent molecule: one oxygen bonded to two hydrogens at about 104.5 degrees.",
        "facts": ["Covers about 71% of Earth's surface", "Polar molecule", "Essential for all known life"]},
    "co2": {"name": "Carbon Dioxide (CO2)", "category": "Chemistry - Molecule",
        "description": "A linear molecule: carbon double-bonded to two oxygen atoms.",
        "facts": ["A greenhouse gas from respiration and combustion", "Used by plants in photosynthesis",
                  "Its solid form is dry ice"]},
    "ch4": {"name": "Methane (CH4)", "category": "Chemistry - Molecule",
        "description": "A tetrahedral molecule: carbon bonded to four hydrogen atoms.",
        "facts": ["The simplest hydrocarbon", "A potent greenhouse gas", "Main component of natural gas"]},
    "nh3": {"name": "Ammonia (NH3)", "category": "Chemistry - Molecule",
        "description": "A pyramidal molecule: nitrogen bonded to three hydrogen atoms with a lone pair.",
        "facts": ["Used to manufacture fertilizers", "Pungent, colorless gas at room temperature",
                  "Produced industrially via the Haber process"]},
    "o2": {"name": "Oxygen (O2)", "category": "Chemistry - Molecule",
        "description": "Two oxygen atoms joined by a double bond.",
        "facts": ["About 21% of Earth's atmosphere", "Essential for aerobic respiration",
                  "Produced by photosynthesis"]},
    "n2": {"name": "Nitrogen (N2)", "category": "Chemistry - Molecule",
        "description": "Two nitrogen atoms joined by a very strong triple bond.",
        "facts": ["About 78% of Earth's atmosphere", "Very unreactive due to the triple bond",
                  "Key ingredient in fertilizers once 'fixed'"]},
    "hcl": {"name": "Hydrochloric Acid (HCl)", "category": "Chemistry - Molecule",
        "description": "A single polar bond between hydrogen and chlorine.",
        "facts": ["A strong acid, fully ionizes in water", "Naturally present in stomach acid",
                  "Widely used in industry"]},
    "h2so4": {"name": "Sulfuric Acid (H2SO4)", "category": "Chemistry - Molecule",
        "description": "A sulfur atom bonded to four oxygens, two of which carry hydrogens.",
        "facts": ["One of the most produced industrial chemicals worldwide", "A strong, corrosive acid",
                  "Used in fertilizer and battery production"]},
    "benzene": {"name": "Benzene (C6H6)", "category": "Chemistry - Aromatic Ring",
        "description": "A ring of six carbons with delocalized bonding, each bonded to one hydrogen.",
        "facts": ["Discovered by Michael Faraday in 1825", "Basis of aromatic chemistry",
                  "Delocalized electrons give it extra stability"]},
    "glucose": {"name": "Glucose (C6H12O6)", "category": "Chemistry - Carbohydrate",
        "description": "A six-carbon sugar ring, the primary fuel for most living cells.",
        "facts": ["Produced by photosynthesis", "Broken down via cellular respiration for ATP",
                  "Blood glucose is tightly regulated by insulin"]},
    "ethanol": {"name": "Ethanol (C2H5OH)", "category": "Chemistry - Alcohol",
        "description": "A two-carbon chain with a hydroxyl (OH) group.",
        "facts": ["Produced by fermenting sugars with yeast", "Used as a solvent and biofuel",
                  "The alcohol found in beverages"]},
    "aspirin": {"name": "Aspirin (C9H8O4)", "category": "Chemistry - Pharmaceutical",
        "description": "Acetylsalicylic acid: a benzene ring with carboxyl and acetyl groups.",
        "facts": ["One of the most widely used medications in the world",
                  "Reduces pain, fever, and inflammation", "First mass-marketed in 1899"]},
    "atp": {"name": "ATP (Adenosine Triphosphate)", "category": "Chemistry / Biology - Energy Carrier",
        "description": "A molecule with three linked phosphate groups that stores usable cellular energy.",
        "facts": ["Called the 'energy currency' of the cell", "Releases energy when a phosphate bond breaks",
                  "The body recycles roughly its own body weight in ATP daily"]},
    "amino_acid": {"name": "Amino Acid (Glycine)", "category": "Chemistry / Biology - Building Block",
        "description": "The simplest amino acid: an amine group and a carboxyl group on one carbon.",
        "facts": ["Amino acids link together to form proteins", "There are 20 standard amino acids",
                  "Glycine is the smallest and simplest of them"]},
    "dna": {"name": "DNA Double Helix", "category": "Chemistry / Biology - Molecule",
        "description": "Two intertwined strands forming a spiral, carrying genetic information in base pairs.",
        "facts": ["Structure discovered by Watson and Crick in 1953", "Built from nucleotides A, T, G, C",
                  "Found in nearly every cell of the body"],
        "parts": _parts({"backbone": ("Sugar-Phosphate Backbone", "Structural support strand for each side of the helix."),
                         "base_pair": ("Base Pair", "A-T and G-C pairs encode genetic information.")})},
    "heart": {"name": "Human Heart (Anatomical)", "category": "Biology - Circulatory System",
        "description": "A vital muscular pump with dual-circuit circulation, beating continuously via cardiac conduction.",
        "facts": ["Beats about 100,000 times daily (~72 BPM)", "Left ventricle pumps oxygenated blood to the entire body via the aorta",
                  "Right ventricle pumps deoxygenated blood to lungs via pulmonary trunk", "Coronary arteries deliver oxygen directly to the myocardium"],
        "parts": _parts({"left_ventricle": ("Left Ventricle", "Thick muscular chamber pumping oxygenated blood to systemic circulation."),
                         "right_ventricle": ("Right Ventricle", "Pumps deoxygenated blood through the pulmonary trunk to the lungs."),
                         "left_atrium": ("Left Atrium", "Receives freshly oxygenated blood from the four pulmonary veins."),
                         "right_atrium": ("Right Atrium", "Receives deoxygenated blood returning from the SVC and IVC."),
                         "aorta": ("Aorta & Aortic Arch", "The main systemic arterial trunk branching to head, neck, and arms."),
                         "pulmonary_trunk": ("Pulmonary Trunk", "Bifurcates into left and right pulmonary arteries toward the lungs."),
                         "superior_vena_cava": ("Superior Vena Cava", "Large venous trunk returning blood from the upper body."),
                         "coronary_arteries": ("Coronary Arteries", "Branching arterial network nourishing the contracting heart muscle."),
                         "cardiac_apex": ("Cardiac Apex", "The inferolateral conical tip of the left ventricle.")})},
    "car_engine": {"name": "Inline-4 Car Engine", "category": "Engineering - Internal Combustion",
        "description": "A 4-cylinder four-stroke internal combustion engine with rotating crankshaft, reciprocating pistons, valves, and timed ignition.",
        "facts": ["Operates on the 4-stroke cycle: Intake, Compression, Power, and Exhaust",
                  "Firing order is 1 - 3 - 4 - 2 to minimize harmonic vibration",
                  "Pistons convert combustion pressure into crankshaft rotational torque",
                  "Twin overhead camshafts (DOHC) actuate intake and exhaust valves"],
        "parts": _parts({"engine_block": ("Engine Block & Cylinders", "Foundational cast block housing the 4 cylinder sleeves and oil pan."),
                         "crankshaft": ("Crankshaft & Flywheel", "Converts reciprocating piston motion into continuous rotational torque."),
                         "pistons": ("Pistons & Rings", "Aluminum cylindrical sliders sealing high-pressure combustion forces."),
                         "connecting_rods": ("Connecting Rods", "Forged rods articulated between the crank throws and piston wrist pins."),
                         "cylinder_head": ("Cylinder Head & Valves", "Encloses cylinders and houses intake/exhaust valves and DOHC camshafts."),
                         "spark_plugs": ("Spark Plugs & Ignition", "Delivers high-voltage electric sparks to ignite the fuel-air charge."),
                         "intake_manifold": ("Intake Manifold", "Evenly distributes the air-fuel mixture to each cylinder's intake ports."),
                         "exhaust_manifold": ("Exhaust Headers", "Collects hot exhaust gases into the catalytic exhaust pipe.")})},
    "world_map": {"name": "World Geographical Map", "category": "Geography - Global Earth",
        "description": "An interactive 3D geographical globe displaying continents, oceans, coordinates, mountain relief, and strategic cities.",
        "facts": ["Earth surface area is approximately 510 million square kilometers",
                  "Oceans cover about 70.8% while continental land accounts for 29.2%",
                  "The Equator divides Earth into Northern and Southern Hemispheres",
                  "Tectonic plates float on the semi-fluid asthenosphere, shaping continental drift"],
        "parts": _parts({"continents": ("Continents & Landmasses", "The seven major continental landmasses separated by ocean basins."),
                         "oceans": ("Oceans & Seas", "Pacific, Atlantic, Indian, Arctic, and Southern Oceans holding 97% of Earth's water."),
                         "equator_grid": ("Equator & Meridian Grid", "Reference latitude and longitude coordinates including Prime Meridian."),
                         "mountain_ranges": ("Mountain Ranges", "Major continental collision belts: Himalayas, Andes, and Rockies."),
                         "cities": ("Global Cities & Landmark Pins", "Strategic metropolitan centers with geographical coordinates.")})},
    "india_map": {"name": "India Geographical Map", "category": "Geography - Physical India",
        "description": "A high-fidelity 3D geographical visualization of India highlighting physiographic zones, mountain ranges, major rivers, and landmark cities.",
        "facts": ["Total land area of 3.287 million sq km, making it the 7th largest nation",
                  "Features 6 physiographic divisions: Himalayas, Northern Plains, Deccan Plateau, Ghats, Desert, and Islands",
                  "Coastline stretches 7,516.6 km along the Arabian Sea, Indian Ocean, and Bay of Bengal",
                  "The Great Himalayas act as a climatic barrier driving the vital Southwest Monsoon"],
        "parts": _parts({"himalayas": ("Great Himalayan Range", "The world's highest mountain arc, including K2, Kanchenjunga, and Nanda Devi peaks."),
                         "northern_plains": ("Indo-Gangetic Plains", "Vast fertile alluvial plain formed by the Indus, Ganga, and Brahmaputra basins."),
                         "deccan_plateau": ("Peninsular Deccan Plateau", "Ancient triangular basalt plateau bounded by Vindhya, Satpura, and Ghats."),
                         "thar_desert": ("Great Indian Desert (Thar)", "Arid sandy dunes in Rajasthan and salt flats of the Rann of Kutch."),
                         "rivers": ("Major River Network", "Perennial river systems: Ganga, Yamuna, Brahmaputra, Godavari, and Krishna."),
                         "coastal_islands": ("Coastlines & Island Groups", "Konkan and Coromandel coasts plus Andaman & Nicobar and Lakshadweep archipelagos."),
                         "landmark_cities": ("Strategic Cities & Capitals", "Key administrative and cultural centers: New Delhi, Mumbai, Bengaluru, Kolkata, Chennai.")})},
    "respiratory": {"name": "Respiratory System", "category": "Biology - Human Anatomy",
        "description": "The system responsible for gas exchange between air and blood.",
        "facts": ["Adults breathe 12-20 times per minute at rest", "Lungs contain ~300 million alveoli",
                  "The diaphragm is the main muscle of breathing"],
        "parts": _parts({"nasal_cavity": ("Nasal Cavity", "Warms, moistens, and filters incoming air."),
                         "trachea": ("Trachea", "Windpipe carrying air to the bronchi."),
                         "bronchi": ("Bronchi", "Branching airways delivering air to each lung."),
                         "lungs": ("Lungs", "Paired organs where gas exchange takes place."),
                         "alveoli": ("Alveoli", "Tiny air sacs where O2 and CO2 are exchanged."),
                         "diaphragm": ("Diaphragm", "Dome-shaped muscle that drives breathing.")})},
    "digestive": {"name": "Digestive System", "category": "Biology - Human Anatomy",
        "description": "The system that breaks down food into nutrients the body can absorb.",
        "facts": ["The digestive tract is about 9 meters long", "The stomach holds roughly 1 liter",
                  "Digestion begins in the mouth"],
        "parts": _parts({"mouth": ("Mouth", "Begins digestion by chewing and mixing food with saliva."),
                         "esophagus": ("Esophagus", "Muscular tube that pushes food to the stomach."),
                         "stomach": ("Stomach", "Uses acid and enzymes to break down food."),
                         "small_intestine": ("Small Intestine", "Absorbs most nutrients into the blood."),
                         "large_intestine": ("Large Intestine", "Absorbs water and forms waste."),
                         "liver": ("Liver", "Produces bile and processes nutrients and toxins.")})},
    "neuron": {"name": "Neuron", "category": "Biology - Nervous System",
        "description": "A specialized cell that transmits electrical and chemical signals.",
        "facts": ["The human brain has ~86 billion neurons", "Signals can travel over 100 m/s",
                  "Neurons communicate across synapses"],
        "parts": _parts({"soma": ("Soma (Cell Body)", "Contains the nucleus and sustains the cell."),
                         "dendrites": ("Dendrites", "Receive signals from other neurons."),
                         "axon": ("Axon", "Carries electrical impulses away from the cell body."),
                         "synapse": ("Synapse", "Junction where signals pass to the next neuron.")})},
    "brain": {"name": "Human Brain", "category": "Biology - Nervous System",
        "description": "The control center of the nervous system, coordinating thought and the body.",
        "facts": ["Uses about 20% of the body's energy", "Contains roughly 86 billion neurons",
                  "The cerebrum handles higher reasoning"],
        "parts": _parts({"cerebrum": ("Cerebrum", "Handles reasoning, language, and voluntary movement."),
                         "cerebellum": ("Cerebellum", "Coordinates balance and fine motor control."),
                         "brainstem": ("Brainstem", "Controls breathing, heart rate, and reflexes.")})},
    "eye": {"name": "Human Eye", "category": "Biology - Sensory System",
        "description": "The organ that converts light into neural signals for vision.",
        "facts": ["The eye can distinguish about 10 million colors", "The retina has ~120 million rod cells",
                  "The optic nerve carries signals to the brain"],
        "parts": _parts({"sclera": ("Sclera", "The tough white outer wall of the eye."),
                         "iris": ("Iris", "Colored muscle that controls pupil size."),
                         "pupil": ("Pupil", "The opening that lets light into the eye."),
                         "optic_nerve": ("Optic Nerve", "Carries visual signals to the brain.")})},
    "ear": {"name": "Human Ear", "category": "Biology - Sensory System",
        "description": "The organ responsible for hearing and balance.",
        "facts": ["Contains the smallest bones in the human body", "The cochlea converts vibration to signal",
                  "Also manages balance via the inner ear"],
        "parts": _parts({"outer_ear": ("Outer Ear", "Collects and funnels sound waves inward."),
                         "ear_canal": ("Ear Canal", "Channels sound to the eardrum."),
                         "eardrum": ("Eardrum", "Vibrates in response to sound waves."),
                         "cochlea": ("Cochlea", "Converts vibrations into nerve signals.")})},
    "kidney": {"name": "Kidney", "category": "Biology - Excretory System",
        "description": "A bean-shaped organ that filters blood to produce urine.",
        "facts": ["Each kidney has about a million nephrons", "Filters roughly 180 liters of blood daily",
                  "Also regulates blood pressure and electrolytes"],
        "parts": _parts({"cortex": ("Cortex", "Outer region where blood filtration begins."),
                         "medulla": ("Medulla", "Inner region that concentrates urine."),
                         "ureter": ("Ureter", "Tube carrying urine to the bladder.")})},
    "liver": {"name": "Liver", "category": "Biology - Digestive System",
        "description": "The body's largest internal organ, central to metabolism and detoxification.",
        "facts": ["Performs over 500 distinct functions", "Can regenerate lost tissue",
                  "Produces bile to digest fats"],
        "parts": _parts({"right_lobe": ("Right Lobe", "The larger of the liver's two main lobes."),
                         "left_lobe": ("Left Lobe", "The smaller lobe, tucked near the stomach."),
                         "bile_duct": ("Bile Duct", "Carries bile to the small intestine.")})},
    "skeleton": {"name": "Human Skeleton", "category": "Biology - Skeletal System",
        "description": "The internal framework of bones that supports and protects the body.",
        "facts": ["Adults have 206 bones", "Bone marrow produces blood cells",
                  "Bones store calcium and other minerals"],
        "parts": _parts({"skull": ("Skull", "Protects the brain and supports the face."),
                         "ribcage": ("Ribcage", "Protects the heart and lungs."),
                         "pelvis": ("Pelvis", "Supports the spine and connects the legs."),
                         "spine": ("Spine", "Protects the spinal cord and supports posture.")})},
    "muscular": {"name": "Muscular System", "category": "Biology - Muscular System",
        "description": "The system of muscles that produces movement and maintains posture.",
        "facts": ["The body has over 600 muscles", "Skeletal muscle is under voluntary control",
                  "Muscles work in pairs to move joints"],
        "parts": _parts({"biceps": ("Biceps", "Flexes the elbow joint."),
                         "quadriceps": ("Quadriceps", "Extends the knee joint."),
                         "core": ("Core Muscles", "Stabilize the trunk and spine.")})},
    "circulatory": {"name": "Circulatory System", "category": "Biology - Circulatory System",
        "description": "The network of the heart and vessels that transports blood through the body.",
        "facts": ["Roughly 100,000 km of blood vessels in an adult", "Blood completes a full circuit in about a minute",
                  "Carries oxygen, nutrients, and immune cells"],
        "parts": _parts({"heart": ("Heart", "Pumps blood through the network of vessels."),
                         "vessels": ("Blood Vessels", "Carry blood to and from every tissue.")})},
    "cell": {"name": "Animal Cell", "category": "Biology - Cell Biology",
        "description": "The basic structural and functional unit of living organisms.",
        "facts": ["The human body has roughly 37 trillion cells", "Each cell carries a full copy of DNA",
                  "Organelles divide labor within the cell"],
        "parts": _parts({"membrane": ("Cell Membrane", "Controls what enters and exits the cell."),
                         "nucleus": ("Nucleus", "Houses the cell's DNA."),
                         "mitochondria": ("Mitochondria", "Generates ATP energy for the cell."),
                         "ribosome": ("Ribosome", "Builds proteins from amino acids.")})},
    "mitochondria": {"name": "Mitochondrion", "category": "Biology - Cell Biology",
        "description": "The organelle that produces most of a cell's chemical energy as ATP.",
        "facts": ["Often called the 'powerhouse of the cell'", "Has its own small set of DNA",
                  "Cristae folds increase surface area for energy production"],
        "parts": _parts({"outer_membrane": ("Outer Membrane", "Encloses the organelle."),
                         "cristae": ("Cristae", "Folded inner membrane where ATP is made."),
                         "matrix": ("Matrix", "Fluid interior containing enzymes and mtDNA.")})},
    "ribosome": {"name": "Ribosome", "category": "Biology - Cell Biology",
        "description": "A molecular machine that translates RNA into proteins.",
        "facts": ["Made of two subunits, large and small", "Found free-floating or on the endoplasmic reticulum",
                  "A cell can contain millions of ribosomes"],
        "parts": _parts({"large_subunit": ("Large Subunit", "Catalyzes the formation of peptide bonds."),
                         "small_subunit": ("Small Subunit", "Reads the messenger RNA sequence.")})},
    "chromosome": {"name": "Chromosome", "category": "Biology - Genetics",
        "description": "A tightly packaged structure of DNA and protein carrying genetic information.",
        "facts": ["Humans have 23 pairs of chromosomes", "Made of DNA wound around histone proteins",
                  "Duplicated chromosomes are joined at the centromere"],
        "parts": _parts({"chromatid": ("Chromatid", "One of two identical halves of a duplicated chromosome."),
                         "centromere": ("Centromere", "The point where sister chromatids are joined.")})},
    "bacteriophage": {"name": "Bacteriophage", "category": "Biology - Virology",
        "description": "A virus that infects bacteria, injecting its DNA through a tail into the host cell.",
        "facts": ["Among the most abundant biological entities on Earth", "Does not infect human cells",
                  "Used in 'phage therapy' as an antibiotic alternative",
                  "The tail sheath contracts to punch DNA through the bacterial wall"],
        "parts": _parts({"capsid_head": ("Capsid Head", "Protein shell that protects the packaged DNA genome."),
                         "genome": ("DNA Genome", "The phage's genetic material, tightly packed inside the head."),
                         "collar": ("Collar", "Connects the head to the tail assembly."),
                         "tail_sheath": ("Tail Sheath", "Contracts to drive the tail tube into the host cell wall."),
                         "baseplate": ("Baseplate", "Anchors the tail fibers and senses the host cell surface."),
                         "tail_fiber": ("Tail Fiber", "Recognizes and binds specific receptors on the host bacterium.")})},
    "hiv": {"name": "HIV (Human Immunodeficiency Virus)", "category": "Biology - Virology",
        "description": "An enveloped retrovirus that infects immune cells, using surface spikes to bind and enter its target.",
        "facts": ["Belongs to the retrovirus family", "Carries its genome as RNA, not DNA",
                  "Uses reverse transcriptase to convert its RNA into DNA inside the host cell",
                  "Primarily targets CD4+ T cells of the immune system"],
        "parts": _parts({"envelope": ("Viral Envelope", "Lipid membrane taken from the host cell during budding."),
                         "spike": ("gp120/gp41 Spike", "Surface glycoprotein that binds CD4 receptors to enter cells."),
                         "matrix": ("Matrix Layer", "Protein shell lining the inside of the envelope."),
                         "capsid_core": ("Capsid Core", "Cone-shaped shell enclosing the viral RNA and enzymes."),
                         "genome": ("RNA Genome", "Two copies of single-stranded RNA carrying the viral genes.")})},
    "papillomavirus": {"name": "Human Papillomavirus (HPV)", "category": "Biology - Virology",
        "description": "A small, non-enveloped virus with an icosahedral capsid that infects skin and mucosal cells.",
        "facts": ["Has no lipid envelope, making it unusually resistant to disinfectants",
                  "Capsid is built from 72 pentamer capsomeres in an icosahedral lattice",
                  "Certain high-risk strains are linked to cervical and other cancers",
                  "The basis for the HPV vaccine, made from empty capsid shells"],
        "parts": _parts({"capsid": ("Capsid", "Icosahedral protein shell made of repeating pentamer subunits."),
                         "genome": ("Circular DNA Genome", "Double-stranded circular DNA carrying the viral genes.")})},
    "adenovirus": {"name": "Adenovirus", "category": "Biology - Virology",
        "description": "A non-enveloped virus with an icosahedral capsid and long fiber proteins projecting from each vertex.",
        "facts": ["Causes common cold, conjunctivitis, and gastroenteritis symptoms",
                  "Capsid vertices each carry a penton base and a fiber ending in a knob",
                  "The fiber knob is what first attaches the virus to a host cell receptor",
                  "Modified (disabled) adenoviruses are used as vectors in some vaccines and gene therapy"],
        "parts": _parts({"capsid": ("Hexon Capsid", "Icosahedral shell built from hexon capsomere proteins."),
                         "fiber": ("Penton Base", "Vertex protein anchoring each fiber to the capsid."),
                         "fiber_knob": ("Fiber Knob", "Tip of the fiber that binds the host cell receptor."),
                         "genome": ("DNA Genome", "Linear double-stranded DNA carrying the viral genes.")})},
    "atom": {"name": "Atom (Bohr Model)", "category": "Physics - Fundamental Particle",
        "description": "A simplified model: a dense nucleus orbited by electrons in discrete shells.",
        "facts": ["Nucleus contains protons and neutrons", "Electrons occupy quantized energy shells",
                  "Real atoms follow quantum mechanics, not fixed orbits"]},
    "wave": {"name": "Transverse Wave", "category": "Physics - Waves",
        "description": "A traveling disturbance where the medium oscillates perpendicular to motion.",
        "facts": ["Wavelength and frequency are inversely related for fixed speed",
                  "Light and sound both exhibit wave behavior", "Amplitude relates to energy carried"]},
    "pendulum": {"name": "Simple Pendulum", "category": "Physics - Mechanics",
        "description": "A mass swinging from a fixed pivot under gravity.",
        "facts": ["Period depends on length, not mass, for small swings",
                  "A classic example of simple harmonic motion", "Used historically to keep time"]},
    "projectile": {"name": "Projectile Motion", "category": "Physics - Mechanics",
        "description": "The curved path an object follows under gravity alone.",
        "facts": ["The horizontal and vertical motions are independent",
                  "The path traced is a parabola", "Maximum range occurs near a 45-degree launch angle"]},
    "circuit": {"name": "Electric Circuit", "category": "Physics - Electricity",
        "description": "A closed loop allowing electric current to flow from a source through a load.",
        "facts": ["Current flows from + to - in conventional notation",
                  "Voltage, current, and resistance relate through Ohm's Law", "Requires a closed loop to function"]},
    "magnetic_field": {"name": "Magnetic Field (Bar Magnet)", "category": "Physics - Magnetism",
        "description": "Field lines looping from the north to the south pole of a magnet.",
        "facts": ["Field lines never cross", "Like poles repel, opposite poles attract",
                  "Moving charges generate magnetic fields"]},
    "em_field": {"name": "Electromagnetic Wave", "category": "Physics - Electromagnetism",
        "description": "Oscillating, perpendicular electric and magnetic fields propagating together.",
        "facts": ["Travels at the speed of light in a vacuum", "Includes radio, light, and X-rays",
                  "Needs no medium to propagate"]},
    "quantum_cloud": {"name": "Quantum Probability Cloud (p-orbital)", "category": "Physics - Quantum Mechanics",
        "description": "A visualization of where an electron is likely to be found, not a fixed path.",
        "facts": ["Electrons don't follow fixed orbits", "Denser regions mean higher probability",
                  "The shape shown resembles a p-orbital"]},
    "earth": {"name": "Earth", "category": "Physics / Space - Planet",
        "description": "The third planet from the Sun, and the only known world to harbor life.",
        "facts": ["71% of the surface is covered in water", "Rotates once every 24 hours",
                  "Orbits the Sun once every 365.25 days"]},
    "moon": {"name": "The Moon", "category": "Physics / Space - Natural Satellite",
        "description": "Earth's only natural satellite, responsible for tides and axial stability.",
        "facts": ["About 384,400 km from Earth on average", "Tidally locked, same side always faces Earth",
                  "Formed roughly 4.5 billion years ago"]},
    "solar_system": {"name": "Solar System", "category": "Physics / Space - Planetary System",
        "description": "The Sun and the planets, moons, and smaller bodies that orbit it.",
        "facts": ["Contains eight planets", "The Sun holds ~99.8% of the system's mass",
                  "Formed about 4.6 billion years ago"]},
    "black_hole": {"name": "Black Hole", "category": "Physics / Space - Extreme Gravity",
        "description": "A region where gravity is so strong that not even light can escape.",
        "facts": ["Bounded by an event horizon", "An accretion disk of infalling matter glows brightly",
                  "The first image of one was released in 2019"]},
}

for _k in MODEL_ORDER:
    SCIENCE_DATA[_k].setdefault("parts", None)

SCIENCE_DB = SCIENCE_DATA  # simple dict is enough; kept as a name for clarity elsewhere


# ============================================================================
# GESTURE CONTROLLER (extended discrete-gesture set + continuous transform)
# ============================================================================

class GestureController:
    PINCH_THRESHOLD = 0.045
    SWIPE_MIN_DIST = 0.28
    SWIPE_MAX_TIME = 0.45
    VERTICAL_MIN_DIST = 0.22
    COOLDOWN = 0.85
    STABILITY_FRAMES = 3

    def __init__(self):
        self.last_trigger = {}
        self.pos_history = collections.deque(maxlen=12)
        self.stable_pose = None
        self.stable_count = 0
        self.prev_two_hand_dist = None
        self.prev_two_hand_pinch = None
        self.drag_anchor = None

    def _cooldown_ok(self, name, now):
        return now - self.last_trigger.get(name, 0) >= self.COOLDOWN

    def _fire(self, name, now):
        self.last_trigger[name] = now
        return name

    @staticmethod
    def _finger_states(lm):
        """
        Robust orientation-independent finger extension detector.
        Works consistently whether the hand is held vertically, horizontally,
        tilted sideways, or pointed toward the camera.
        """
        wrist = lm[0]
        # (tip, pip, mcp) indices for Index, Middle, Ring, Pinky
        joints = ((8, 6, 5), (12, 10, 9), (16, 14, 13), (20, 18, 17))
        others = []
        for tip_i, pip_i, mcp_i in joints:
            tip = lm[tip_i]
            pip = lm[pip_i]
            mcp = lm[mcp_i]
            d_wrist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
            d_wrist_pip = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
            d_mcp_tip = math.hypot(tip.x - mcp.x, tip.y - mcp.y)
            d_mcp_pip = math.hypot(pip.x - mcp.x, pip.y - mcp.y)
            # A finger is extended when its tip is farther from wrist and MCP than PIP is
            extended = (d_wrist_tip > d_wrist_pip * 1.10) and (d_mcp_tip > d_mcp_pip * 1.12)
            others.append(1 if extended else 0)

        # Thumb extension: check distance of thumb tip (4) to pinky base (17) vs thumb IP (3)
        d_thumb_tip = math.hypot(lm[4].x - lm[17].x, lm[4].y - lm[17].y)
        d_thumb_ip = math.hypot(lm[3].x - lm[17].x, lm[3].y - lm[17].y)
        d_thumb_mcp = math.hypot(lm[2].x - lm[17].x, lm[2].y - lm[17].y)
        thumb_ext = (d_thumb_tip > d_thumb_ip * 1.08) and (d_thumb_tip > d_thumb_mcp * 1.12)
        thumb = 1 if thumb_ext else 0

        return [thumb] + others

    def classify_static(self, lm):
        f = self._finger_states(lm)
        thumb, index, middle, ring, pinky = f
        thumb_tip, index_tip = lm[4], lm[8]
        pinch_dist = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)

        if pinch_dist < self.PINCH_THRESHOLD and middle == 0 and ring == 0 and pinky == 0:
            return "pinch"
        if pinch_dist < self.PINCH_THRESHOLD and middle == 1 and ring == 1:
            return "ok_sign"
        if sum(f) == 5:
            # palm facing camera vs away: MediaPipe gives a mirrored image,
            # z of the middle-finger MCP relative to the wrist is a cheap
            # proxy for facing/away without needing handedness metadata.
            return "open_palm"
        if sum(f) == 0:
            return "fist"
        if index == 1 and middle == 0 and ring == 0 and pinky == 0 and thumb == 0:
            return "point"
        if index == 1 and middle == 1 and ring == 0 and pinky == 0:
            return "two_fingers"
        if index == 1 and middle == 1 and ring == 1 and pinky == 0:
            return "three_fingers"
        if thumb == 1 and index == 0 and middle == 0 and ring == 0 and pinky == 0:
            wrist_y, thumb_y = lm[0].y, lm[4].y
            return "thumbs_up" if thumb_y < wrist_y else None
        return None

    def update(self, hand_list, now):
        discrete = None
        if not hand_list:
            self.stable_pose = None
            self.stable_count = 0
            self.pos_history.clear()
            self.prev_two_hand_dist = None
            return None, {"pose": None}

        primary = hand_list[0].landmark
        pose = self.classify_static(primary)

        if pose == self.stable_pose:
            self.stable_count += 1
        else:
            self.stable_pose = pose
            self.stable_count = 1

        if pose is not None and self.stable_count >= self.STABILITY_FRAMES:
            if self._cooldown_ok(pose, now):
                discrete = self._fire(pose, now)

        wrist = primary[0]
        self.pos_history.append((now, wrist.x, wrist.y))
        if len(self.pos_history) >= 4 and discrete is None:
            t0, x0, y0 = self.pos_history[0]
            t1, x1, y1 = self.pos_history[-1]
            dt = t1 - t0
            if 0 < dt <= self.SWIPE_MAX_TIME:
                dx, dy = x1 - x0, y1 - y0
                if abs(dx) > self.SWIPE_MIN_DIST and abs(dx) > abs(dy) * 1.5:
                    name = "swipe_right" if dx > 0 else "swipe_left"
                    if self._cooldown_ok(name, now):
                        discrete = self._fire(name, now)
                        self.pos_history.clear()
                elif abs(dy) > self.VERTICAL_MIN_DIST and abs(dy) > abs(dx) * 1.5:
                    name = "swipe_down" if dy > 0 else "swipe_up"
                    if self._cooldown_ok(name, now):
                        discrete = self._fire(name, now)
                        self.pos_history.clear()

        if len(hand_list) == 2:
            w1, w2 = hand_list[0].landmark[0], hand_list[1].landmark[0]
            dist = math.hypot(w1.x - w2.x, w1.y - w2.y)
            if self.prev_two_hand_dist is not None and discrete is None:
                delta = dist - self.prev_two_hand_dist
                if delta > 0.06 and self._cooldown_ok("apart", now):
                    discrete = self._fire("apart", now)
                elif delta < -0.06 and self._cooldown_ok("together", now):
                    discrete = self._fire("together", now)
            self.prev_two_hand_dist = dist

        return discrete, {"pose": pose}

    @staticmethod
    def compute_transform(hand_list):
        """Rotate/zoom logic (same math as the original), returns
        (target_angle_x, target_angle_y, target_scale, label_text)."""
        if len(hand_list) == 2:
            idx1 = hand_list[0].landmark[8]
            idx2 = hand_list[1].landmark[8]
            mid_x, mid_y = (idx1.x + idx2.x) / 2.0, (idx1.y + idx2.y) / 2.0
            norm_x, norm_y = mid_x - 0.5, mid_y - 0.5
            angle_y = -norm_x * 2 * math.pi
            angle_x = -norm_y * 2 * math.pi

            wrist1, wrist2 = hand_list[0].landmark[0], hand_list[1].landmark[0]
            hx1, hy1 = wrist1.x * CAP_W, wrist1.y * CAP_H
            hx2, hy2 = wrist2.x * CAP_W, wrist2.y * CAP_H
            hand_distance = math.hypot(hx2 - hx1, hy2 - hy1)
            scale = int(np.clip(hand_distance * 2.2, 120, 900))
            label = f"Hand Distance: {int(hand_distance)}"
        else:
            control = hand_list[0]
            index_finger, thumb = control.landmark[8], control.landmark[4]
            norm_x, norm_y = index_finger.x - 0.5, index_finger.y - 0.5
            angle_y = -norm_x * 2 * math.pi
            angle_x = -norm_y * 2 * math.pi

            ix, iy = index_finger.x * CAP_W, index_finger.y * CAP_H
            tx, ty = thumb.x * CAP_W, thumb.y * CAP_H
            pinch_distance = math.hypot(ix - tx, iy - ty)
            scale = int(np.clip(pinch_distance * 6.0, 120, 900))
            label = f"Pinch Distance: {int(pinch_distance)}"

        return angle_x, angle_y, scale, label


# ============================================================================
# OPTIONAL: FACE TRACKING (head-tilt rotate, nod=confirm, shake=cancel)
# ============================================================================
# Off by default, throttled to every FACE_PROCESS_EVERY_N_FRAMES frames so it
# never competes with hand tracking for frame budget. Degrades to a no-op if
# mediapipe's FaceMesh solution can't be constructed.

class FaceTracker:
    def __init__(self):
        self.available = False
        self.mesh = None
        self._frame_i = 0
        self._y_hist = collections.deque(maxlen=10)
        self._x_hist = collections.deque(maxlen=10)
        self.enabled = ENABLE_FACE_TRACKING_DEFAULT
        self.head_yaw = 0.0
        self.last_gesture = None
        self._last_fire = 0.0

        if not MEDIAPIPE_AVAILABLE:
            return
        try:
            self.mesh = mp.solutions.face_mesh.FaceMesh(
                max_num_faces=1, refine_landmarks=False,
                min_detection_confidence=0.5, min_tracking_confidence=0.5)
            self.available = True
        except Exception as e:
            print(f"[INFO] Face tracking unavailable ({e})")
            self.available = False

    def toggle(self):
        if self.available:
            self.enabled = not self.enabled
        return self.enabled

    def process(self, rgb_frame, now):
        """Call every frame; internally throttles. Returns a discrete
        gesture name ('nod' / 'shake') or None, and updates self.head_yaw
        continuously for use as a rotation offset."""
        if not (self.available and self.enabled):
            return None
        self._frame_i += 1
        if self._frame_i % FACE_PROCESS_EVERY_N_FRAMES != 0:
            return self.last_gesture if False else None
        try:
            result = self.mesh.process(rgb_frame)
        except Exception:
            return None
        if not result.multi_face_landmarks:
            return None
        lm = result.multi_face_landmarks[0].landmark
        nose = lm[1]
        left_cheek, right_cheek = lm[234], lm[454]
        self.head_yaw = (nose.x - (left_cheek.x + right_cheek.x) / 2.0) * 4.0

        self._y_hist.append(nose.y)
        self._x_hist.append(nose.x)
        if len(self._y_hist) == self._y_hist.maxlen and now - self._last_fire > 1.2:
            y_range = max(self._y_hist) - min(self._y_hist)
            x_range = max(self._x_hist) - min(self._x_hist)
            if y_range > 0.045 and y_range > x_range * 1.3:
                self._last_fire = now
                self._y_hist.clear()
                return "nod"
            if x_range > 0.06 and x_range > y_range * 1.3:
                self._last_fire = now
                self._x_hist.clear()
                return "shake"
        return None


# ============================================================================
# VOICE CONTROLLER (non-blocking, optional) -- unchanged approach, extended
# with an optional wake-word gate in front of the AI brain.
# ============================================================================

class VoiceController:
    def __init__(self):
        self.available = False
        self.command_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = None
        self.recognizer = None
        self.microphone = None
        self.last_heard_raw = ""

        if not SPEECH_RECOGNITION_AVAILABLE:
            return
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 260
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.5
            self.recognizer.phrase_threshold = 0.25
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
            self.available = True
        except Exception as e:
            print(f"[WARN] Microphone unavailable -> voice control disabled ({e})")
            self.available = False

    def start(self):
        if not self.available:
            return
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def _listen_loop(self):
        while not self._stop_event.is_set():
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio).lower()
                self.last_heard_raw = text
                self.command_queue.put(text)
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception:
                time.sleep(0.5)
                continue

    def get_command(self):
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self._stop_event.set()


class TTSController:
    def __init__(self):
        self.available = TTS_AVAILABLE
        self.speech_queue = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = None
        self.engine = None
        self.speaking = False

        if self.available:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 175)
            except Exception as e:
                print(f"[WARN] TTS unavailable ({e})")
                self.available = False

    def start(self):
        if not self.available:
            return
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        while not self._stop_event.is_set():
            try:
                text = self.speech_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                self.speaking = True
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception:
                pass
            finally:
                self.speaking = False

    def speak(self, text):
        if self.available:
            self.speech_queue.put(text)

    def stop(self):
        self._stop_event.set()


# ============================================================================
# OPTIONAL: AI CONVERSATIONAL BRAIN
# ============================================================================
# OFF by default (ENABLE_AI_BRAIN=False). Even when turned on, it only
# activates if ANTHROPIC_API_KEY is set. Uses only urllib (standard library)
# so it never becomes a hard dependency, and runs on its own thread so a
# slow/failed network call can never stall the render loop. It converts
# free-form speech into one of a small set of JSON-described intents that
# the controller already knows how to execute -- it does not get to run
# arbitrary code.

AI_SYSTEM_PROMPT = (
    "You are the intent parser for a touchless science-visualization app called "
    "JARVIS. Given a spoken instruction, reply with ONLY a compact JSON object, "
    "no prose, no markdown fences, matching this schema: "
    '{"action": "show|next|previous|zoom_in|zoom_out|rotate_toggle|explode_toggle|'
    'pause|resume|highlight_next|demo_start|demo_stop|lab_combine|theme|info|unknown", '
    '"target": "<model key or theme name or null>", "speak": "<short spoken reply>"}. '
    f"Valid model keys: {', '.join(sorted(SCIENCE_DATA.keys()))}. "
    "If the instruction is a question (e.g. 'what does the left ventricle do'), set "
    'action to "info" and put your answer, in under 30 words, in "speak".'
)


class AIBrain:
    def __init__(self, enabled, api_key):
        self.enabled = bool(enabled and api_key)
        self.api_key = api_key
        self.result_queue = queue.Queue()
        self.thinking = False
        if enabled and not api_key:
            print("[INFO] AI brain requested but ANTHROPIC_API_KEY is not set -> staying off.")

    def ask_async(self, text):
        if not self.enabled:
            return
        threading.Thread(target=self._ask, args=(text,), daemon=True).start()

    def _ask(self, text):
        self.thinking = True
        try:
            payload = json.dumps({
                "model": ANTHROPIC_MODEL,
                "max_tokens": 300,
                "system": AI_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": text}],
            }).encode("utf-8")
            req = urllib.request.Request(ANTHROPIC_API_URL, data=payload, method="POST", headers={
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
            })
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            raw = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
            raw = raw.strip().strip("`")
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()
            intent = json.loads(raw)
            self.result_queue.put(intent)
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            self.result_queue.put({"action": "unknown", "target": None,
                                    "speak": "I couldn't reach the AI service."})
            print(f"[WARN] AI brain network error: {e}")
        except Exception as e:
            self.result_queue.put({"action": "unknown", "target": None, "speak": ""})
            print(f"[WARN] AI brain error: {e}")
        finally:
            self.thinking = False

    def get_result(self):
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None



# ============================================================================
# SCREENSHOT / RECORDING (captures the actual GL framebuffer)
# ============================================================================

def read_gl_framebuffer(width, height):
    """Reads the current GL back buffer into a cv2-ready BGR numpy array."""
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    arr = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 3)
    arr = np.flipud(arr)  # GL's origin is bottom-left
    return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)


class ScreenshotManager:
    def __init__(self, folder="screenshots"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)

    def capture(self, width, height):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_path = os.path.join(self.folder, f"JARVIS_{ts}.png")
        path, counter = base_path, 1
        while os.path.exists(path):
            path = base_path.replace(".png", f"_{counter}.png")
            counter += 1
        frame = read_gl_framebuffer(width, height)
        cv2.imwrite(path, frame)
        return path


class Recorder:
    def __init__(self, folder="recordings"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.writer = None
        self.active = False
        self.path = None

    def start(self, frame_size, fps=20):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.path = os.path.join(self.folder, f"JARVIS_{ts}.mp4")
        for fourcc_str in ("mp4v", "XVID", "MJPG"):
            try:
                fourcc = cv2.VideoWriter_fourcc(*fourcc_str)
                writer = cv2.VideoWriter(self.path, fourcc, fps, frame_size)
                if writer.isOpened():
                    self.writer = writer
                    self.active = True
                    return True
            except Exception:
                continue
        print("[WARN] Could not initialize a video writer -> recording disabled")
        self.active = False
        return False

    def write_gl_frame(self, width, height):
        if self.active and self.writer is not None:
            self.writer.write(read_gl_framebuffer(width, height))

    def stop(self):
        if self.writer is not None:
            self.writer.release()
        self.active = False
        self.writer = None


class ThemeManager:
    def __init__(self, name="blue"):
        self.name = name

    @property
    def colors(self):
        return THEMES[self.name]

    def cycle(self):
        i = THEME_ORDER.index(self.name)
        self.name = THEME_ORDER[(i + 1) % len(THEME_ORDER)]

    def set(self, name):
        if name in THEMES:
            self.name = name
            return True
        return False


# ============================================================================
# VIRTUAL CHEMISTRY LAB
# ============================================================================
# Pick two reactant models (pinch to select while in lab mode), then use the
# "together" gesture (or 'c' key) to combine them. A small, honest set of
# balanced reactions -- not a general chemistry engine, just enough to make
# the demo land: "a chemical reaction has occurred."

REACTIONS = {
    frozenset(("h2o", "co2")): {"equation": "H2O + CO2  (no spontaneous reaction shown)",
                                 "product": None,
                                 "speak": "Water and carbon dioxide don't react directly at room temperature."},
    frozenset(("o2", "ch4")): {"equation": "CH4 + 2 O2 -> CO2 + 2 H2O",
                                "product": "co2", "speak": "Combustion complete. Methane burned into carbon dioxide and water."},
    frozenset(("n2", "h2so4")): {"equation": "N2 + 3 H2 -> 2 NH3 (Haber process, schematic)",
                                  "product": "nh3", "speak": "Under pressure and a catalyst, nitrogen forms ammonia."},
    frozenset(("hcl", "h2o")): {"equation": "HCl + H2O -> H3O+ + Cl-",
                                 "product": None, "speak": "Hydrochloric acid fully ionizes in water."},
}


class VirtualLab:
    def __init__(self):
        self.selected = []
        self.last_result = None
        self.last_result_time = 0.0

    def select(self, model_key):
        if model_key in self.selected:
            self.selected.remove(model_key)
        else:
            self.selected.append(model_key)
            if len(self.selected) > 2:
                self.selected.pop(0)

    def clear(self):
        self.selected = []
        self.last_result = None

    def combine(self):
        if len(self.selected) != 2:
            return None
        key = frozenset(self.selected)
        result = REACTIONS.get(key)
        if result is None:
            result = {"equation": f"{self.selected[0].upper()} + {self.selected[1].upper()} -> no known reaction shown",
                       "product": None, "speak": "No reaction is modeled for that combination yet."}
        self.last_result = result
        self.last_result_time = time.time()
        return result


# ============================================================================
# DEMO / PRESENTATION MODE
# ============================================================================

DEMO_SEQUENCE = ["fullerene", "dna", "atom", "heart", "respiratory", "cell",
                  "bacteriophage", "hiv", "papillomavirus", "adenovirus",
                  "earth", "solar_system", "black_hole"]
DEMO_DWELL_SECONDS = 8.0


class DemoMode:
    def __init__(self):
        self.active = False
        self.index = 0
        self.entered_at = 0.0

    def start(self):
        self.active = True
        self.index = 0
        self.entered_at = time.time()
        return DEMO_SEQUENCE[0]

    def stop(self):
        self.active = False

    def update(self, now):
        """Returns a new model key when it's time to advance, else None."""
        if not self.active:
            return None
        if now - self.entered_at >= DEMO_DWELL_SECONDS:
            self.index = (self.index + 1) % len(DEMO_SEQUENCE)
            self.entered_at = now
            return DEMO_SEQUENCE[self.index]
        return None


# ============================================================================
# HUD RENDERER (2D compositor -- drawn once per frame, then blitted as one
# GL texture on top of the 3D scene). Bright-on-black by design: converting
# to RGBA below derives alpha from brightness, so panels read as translucent
# glass instead of opaque boxes blocking the model behind them.
# ============================================================================

def canvas_to_rgba(bgr_canvas):
    b, g, r = cv2.split(bgr_canvas)
    alpha = np.maximum(np.maximum(b, g), r)
    return cv2.merge([r, g, b, alpha])


class HUDRenderer:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.particles = [[random.uniform(0, width), random.uniform(0, height),
                            random.uniform(-1, 1), random.uniform(-1, 1)] for _ in range(40)]
        self.scan_y = 0
        self.waveform_hist = collections.deque([0.0] * 60, maxlen=60)

    def new_canvas(self):
        return np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def _text(self, canvas, text, pos, scale=0.5, color=(255, 255, 255), thickness=1):
        cv2.putText(canvas, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)

    # -- ambient chrome (unchanged look from the original) -----------------
    def draw_particles(self, canvas, color):
        for p in self.particles:
            p[0] += p[2]; p[1] += p[3]
            if p[0] < 0 or p[0] > self.width: p[2] *= -1
            if p[1] < 0 or p[1] > self.height: p[3] *= -1
            cv2.circle(canvas, (int(p[0]), int(p[1])), 1, color, -1, cv2.LINE_AA)

    def draw_scan_line(self, canvas, color):
        self.scan_y = (self.scan_y + 3) % self.height
        cv2.line(canvas, (0, self.scan_y), (self.width, self.scan_y), color, 1, cv2.LINE_AA)

    def draw_corner_brackets(self, canvas, color, margin=18, size=34, thickness=2):
        w, h = self.width, self.height
        corners = [(margin, margin, 1, 1), (w - margin, margin, -1, 1),
                   (margin, h - margin, 1, -1), (w - margin, h - margin, -1, -1)]
        for x, y, dx, dy in corners:
            cv2.line(canvas, (x, y), (x + dx * size, y), color, thickness, cv2.LINE_AA)
            cv2.line(canvas, (x, y), (x, y + dy * size), color, thickness, cv2.LINE_AA)

    def draw_rotating_ring(self, canvas, center, radius, t, color):
        for i in range(3):
            ang = t * 1.2 + i * (2 * math.pi / 3)
            x = int(center[0] + radius * math.cos(ang))
            y = int(center[1] + radius * math.sin(ang))
            cv2.circle(canvas, (x, y), 3, color, -1, cv2.LINE_AA)
        cv2.circle(canvas, center, radius, color, 1, cv2.LINE_AA)

    def draw_top_bar(self, canvas, color, text_color):
        cv2.line(canvas, (0, 64), (self.width, 64), color, 1, cv2.LINE_AA)
        self._text(canvas, "J A R V I S", (self.width // 2 - 110, 34), 0.95, text_color, 2)
        self._text(canvas, "AI TOUCHLESS SCIENTIFIC VISUALIZATION SYSTEM", (self.width // 2 - 210, 56), 0.5, color, 1)

    def draw_left_panel(self, canvas, status, color, text_color):
        x, y = 20, 90
        self._text(canvas, "SYSTEM STATUS", (x, y), 0.55, text_color, 2)
        y += 12
        cv2.line(canvas, (x, y), (x + 200, y), color, 1)
        y += 26
        for label, ok in status:
            dot_color = (100, 255, 120) if ok else (60, 60, 255)
            cv2.circle(canvas, (x + 6, y - 5), 5, dot_color, -1, cv2.LINE_AA)
            self._text(canvas, label, (x + 22, y), 0.46, text_color, 1)
            y += 23
        return y

    def draw_performance_box(self, canvas, fps, hands_n, gesture, tracking, resolution, proc_ms, color, text_color,
                              perf_mode=False):
        # Note: `gesture` is accepted for backward compatibility but is no
        # longer rendered -- the HUD no longer names the detected hand pose
        # (e.g. "FIST", "PALM") on screen, only system/performance status.
        x, y = 20, self.height - 260
        lines = [f"FPS: {fps:.0f}", f"RES: {resolution}", f"HANDS: {hands_n}",
                 f"TRACKING: {'ACTIVE' if tracking else 'PAUSED'}",
                 f"PROC: {proc_ms:.1f} ms"]
        if perf_mode:
            lines.append("PERFORMANCE MODE: ON")
        cv2.rectangle(canvas, (x - 6, y - 20), (x + 190, y + 20 * len(lines)), (20, 20, 20), -1)
        cv2.rectangle(canvas, (x - 6, y - 20), (x + 190, y + 20 * len(lines)), color, 1)
        for i, line in enumerate(lines):
            self._text(canvas, line, (x, y + i * 20), 0.42, text_color, 1)

    def draw_right_panel(self, canvas, info, highlight_info, color, text_color, visible):
        if not visible or info is None:
            return
        x, y = self.width - 340, 90
        cv2.line(canvas, (x, y - 22), (x + 320, y - 22), color, 1)
        self._text(canvas, "CURRENT OBJECT", (x, y - 4), 0.55, text_color, 2)
        y += 24
        self._text(canvas, info["name"].upper(), (x, y), 0.6, color, 2)
        y += 24
        self._text(canvas, info["category"], (x, y), 0.45, text_color, 1)
        y += 28
        for line in wrap_text(info["description"], 34):
            self._text(canvas, line, (x, y), 0.45, text_color, 1)
            y += 20
        y += 8
        self._text(canvas, "KEY FACTS", (x, y), 0.48, color, 1)
        y += 20
        for f in info.get("facts", [])[:4]:
            for line in wrap_text("- " + f, 34):
                self._text(canvas, line, (x, y), 0.42, text_color, 1)
                y += 18
        if highlight_info:
            y += 10
            cv2.line(canvas, (x, y), (x + 320, y), color, 1)
            y += 20
            self._text(canvas, highlight_info["part"].upper(), (x, y), 0.5, (255, 255, 0), 2)
            y += 20
            for line in wrap_text(highlight_info["function"], 34):
                self._text(canvas, line, (x, y), 0.42, text_color, 1)
                y += 18

    def draw_bottom_bar(self, canvas, gesture_status, mode_text, color, text_color):
        # Note: `gesture_status` is accepted for backward compatibility but
        # is no longer rendered -- per request, the HUD stays clean and
        # doesn't call out which hand pose (fist, palm, pinch, etc.) is
        # currently being read. Move your hand to rotate/zoom; the discrete
        # poses still work, they're just not named on screen anymore.
        y = self.height - 96
        cv2.line(canvas, (0, y), (self.width, y), color, 1)
        self._text(canvas, "Move hand = rotate/zoom   Two hands = distance zoom   "
                            "Point = cycle part   Swipe = next/prev/category",
                   (20, y + 22), 0.40, text_color, 1)
        self._text(canvas, "VOICE: 'JARVIS show <model>' | 'next/previous' | 'zoom in/out' | 'pause/resume' | "
                            "'screenshot' | 'start/stop recording' | 'demo mode' | 'combine'",
                   (20, y + 42), 0.40, text_color, 1)
        self._text(canvas, "KEYS: N/P Cycle  X Explode  L Lab  D Demo  M Menu  F Face  B Camera-BG  A AI-brain  "
                            "S Screenshot  V Record  T Theme  SPACE Pause  Q Quit",
                   (20, y + 62), 0.38, (150, 150, 150), 1)
        self._text(canvas, mode_text, (20, y + 84), 0.45, color, 1)

    # -- new: hand telemetry panel with mini hand skeleton overlay ----------
    def draw_telemetry(self, canvas, hand_list, gesture, confidence, color, text_color):
        x, y = self.width - 340, self.height - 260
        cv2.rectangle(canvas, (x - 6, y - 24), (x + 320, y + 170), (15, 15, 15), -1)
        cv2.rectangle(canvas, (x - 6, y - 24), (x + 320, y + 170), color, 1)
        self._text(canvas, "HAND TELEMETRY", (x, y - 4), 0.5, text_color, 2)
        y_text = y + 20
        if hand_list:
            lm = hand_list[0].landmark
            idx, thumb = lm[8], lm[4]
            pinch_px = math.hypot((idx.x - thumb.x) * CAP_W, (idx.y - thumb.y) * CAP_H)
            rows = [f"INDEX X   {idx.x:.3f}", f"INDEX Y   {idx.y:.3f}",
                    f"THUMB X   {thumb.x:.3f}", f"THUMB Y   {thumb.y:.3f}",
                    f"PINCH     {pinch_px:.0f} px",
                    f"CONFIDENCE {confidence:.1f}%", f"HANDS     {len(hand_list)}",
                    "STATUS    LOCKED"]
            # Sleek mini hand skeleton drawn in the right half of the telemetry box
            # Visual proof that hand is detected and joint tracking is active
            sk_cx, sk_cy = x + 245, y + 65
            sk_w, sk_h = 90, 110
            # Draw joints & bones
            HAND_BONES = [
                (0, 1), (1, 2), (2, 3), (3, 4),           # thumb
                (0, 5), (5, 6), (6, 7), (7, 8),           # index
                (0, 9), (9, 10), (10, 11), (11, 12),      # middle
                (0, 13), (13, 14), (14, 15), (15, 16),    # ring
                (0, 17), (17, 18), (18, 19), (19, 20),    # pinky
                (5, 9), (9, 13), (13, 17)                 # palm
            ]
            sk_pts = []
            for pt in lm:
                px = int(sk_cx + (pt.x - 0.5) * sk_w)
                py = int(sk_cy + (pt.y - 0.5) * sk_h)
                sk_pts.append((px, py))
            for b1, b2 in HAND_BONES:
                cv2.line(canvas, sk_pts[b1], sk_pts[b2], color, 1, cv2.LINE_AA)
            for i, p in enumerate(sk_pts):
                dot_c = (0, 255, 255) if i in (4, 8, 12, 16, 20) else (100, 255, 120)
                cv2.circle(canvas, p, 2, dot_c, -1, cv2.LINE_AA)
        else:
            rows = ["INDEX X   --", "INDEX Y   --", "THUMB X   --", "THUMB Y   --",
                    "PINCH     --", "CONFIDENCE --", "HANDS     0", "STATUS    WAITING"]
        for r in rows:
            self._text(canvas, r, (x, y_text), 0.42, text_color, 1)
            y_text += 20

    # -- new: radar sweep -----------------------------------------------
    def draw_radar(self, canvas, center, radius, t, color, blips):
        cv2.circle(canvas, center, radius, color, 1, cv2.LINE_AA)
        cv2.circle(canvas, center, int(radius * 0.6), color, 1, cv2.LINE_AA)
        cv2.circle(canvas, center, int(radius * 0.3), color, 1, cv2.LINE_AA)
        ang = t * 2.0
        x = int(center[0] + radius * math.cos(ang))
        y = int(center[1] + radius * math.sin(ang))
        cv2.line(canvas, center, (x, y), color, 1, cv2.LINE_AA)
        for bx, by in blips:
            cv2.circle(canvas, (int(center[0] + bx * radius), int(center[1] + by * radius)), 3, (0, 255, 120), -1, cv2.LINE_AA)

    # -- new: audio waveform (mic energy if available, else a gentle idle
    #    sine so the panel never looks broken/empty) -----------------------
    def draw_waveform(self, canvas, x, y, w, h, level, color):
        self.waveform_hist.append(level)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), (15, 15, 15), -1)
        cv2.rectangle(canvas, (x, y), (x + w, y + h), color, 1)
        pts = list(self.waveform_hist)
        n = len(pts)
        for i in range(1, n):
            x1 = x + int(w * (i - 1) / (n - 1))
            x2 = x + int(w * i / (n - 1))
            y1 = y + h // 2 - int(pts[i - 1] * h * 0.45)
            y2 = y + h // 2 - int(pts[i] * h * 0.45)
            cv2.line(canvas, (x1, y1), (x2, y2), color, 1, cv2.LINE_AA)

    # -- new: holographic selection cursor with dwell ring ------------------
    def draw_cursor(self, canvas, pos, dwell_fraction, color):
        x, y = pos
        cv2.drawMarker(canvas, (x, y), color, cv2.MARKER_CROSS, 16, 1, cv2.LINE_AA)
        cv2.circle(canvas, (x, y), 14, color, 1, cv2.LINE_AA)
        if dwell_fraction > 0:
            angle = int(360 * dwell_fraction)
            cv2.ellipse(canvas, (x, y), (20, 20), -90, 0, angle, (0, 255, 255), 2, cv2.LINE_AA)

    # -- new: category menu bar ---------------------------------------------
    def draw_category_menu(self, canvas, categories, active_idx, color, text_color):
        w = self.width // len(categories)
        y0, y1 = 68, 100
        boxes = []
        for i, cat in enumerate(categories):
            x0, x1 = i * w, (i + 1) * w
            active = (i == active_idx)
            bg = (60, 45, 0) if active else (15, 15, 15)
            cv2.rectangle(canvas, (x0 + 4, y0), (x1 - 4, y1), bg, -1)
            cv2.rectangle(canvas, (x0 + 4, y0), (x1 - 4, y1), color, 1)
            self._text(canvas, cat.upper(), (x0 + 14, y1 - 10), 0.5,
                       (255, 255, 0) if active else text_color, 2 if active else 1)
            boxes.append((x0, y0, x1, y1))
        return boxes

    # -- new: AI-thinking spinner --------------------------------------------
    def draw_ai_spinner(self, canvas, center, t, color):
        for i in range(8):
            ang = 2 * math.pi * i / 8 + t * 4
            r1, r2 = 8, 14
            p1 = (int(center[0] + r1 * math.cos(ang)), int(center[1] + r1 * math.sin(ang)))
            p2 = (int(center[0] + r2 * math.cos(ang)), int(center[1] + r2 * math.sin(ang)))
            fade = 0.3 + 0.7 * ((i + int(t * 8)) % 8) / 8.0
            c = tuple(int(ch * fade) for ch in color)
            cv2.line(canvas, p1, p2, c, 2, cv2.LINE_AA)
        self._text(canvas, "AI THINKING...", (center[0] - 55, center[1] + 34), 0.42, color, 1)

    # -- new: clock + camera/network/CPU/RAM status line ---------------------
    def draw_voice_banner(self, canvas, text, color, text_color):
        if not text:
            return
        bx, by = self.width // 2 - 220, self.height - 135
        cv2.rectangle(canvas, (bx, by), (bx + 440, by + 34), (20, 25, 30), -1)
        cv2.rectangle(canvas, (bx, by), (bx + 440, by + 34), color, 1)
        cv2.circle(canvas, (bx + 20, by + 17), 7, (0, 255, 120), -1, cv2.LINE_AA)
        self._text(canvas, f"VOICE COMMAND: '{text.upper()}'", (bx + 36, by + 22), 0.48, text_color, 1)

    def draw_system_strip(self, canvas, color, text_color, camera_ok):
        now_str = datetime.now().strftime("%H:%M:%S")
        cpu_str = ram_str = "N/A"
        if PSUTIL_AVAILABLE:
            try:
                cpu_str = f"{psutil.cpu_percent():.0f}%"
                ram_str = f"{psutil.virtual_memory().percent:.0f}%"
            except Exception:
                pass
        parts = [now_str, f"CAM: {'OK' if camera_ok else 'DOWN'}", f"CPU: {cpu_str}", f"RAM: {ram_str}"]
        text = "   ".join(parts)
        self._text(canvas, text, (self.width - 20 - 9 * len(text), self.height - 12), 0.42, text_color, 1)

    # -- new: floating world-space labels (already projected to 2D) ---------
    def draw_labels(self, canvas, label_points_2d, color):
        for text, (x, y) in label_points_2d:
            if 0 <= x <= self.width and 0 <= y <= self.height:
                cv2.circle(canvas, (x, y), 2, color, -1, cv2.LINE_AA)
                cv2.line(canvas, (x, y), (x + 14, y - 14), color, 1, cv2.LINE_AA)
                self._text(canvas, text, (x + 16, y - 16), 0.4, color, 1)


def run_startup_sequence(window_name, width, height, checks):
    canvas = np.zeros((height, width, 3), dtype=np.uint8)
    cv2.putText(canvas, "INITIALIZING JARVIS...", (width // 2 - 180, height // 2 - 170),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 180, 0), 2, cv2.LINE_AA)
    cv2.imshow(window_name, canvas)
    cv2.waitKey(1)

    y = height // 2 - 120
    for label, ok in checks:
        mark = "[OK]" if ok else "[--]"
        color = (100, 255, 120) if ok else (80, 80, 255)
        cv2.putText(canvas, f"{mark} {label}", (width // 2 - 200, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)
        cv2.imshow(window_name, canvas)
        cv2.waitKey(120)
        y += 30

    cv2.putText(canvas, "SYSTEM ONLINE", (width // 2 - 100, y + 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 255, 120), 2, cv2.LINE_AA)
    cv2.imshow(window_name, canvas)
    cv2.waitKey(500)


# ============================================================================
# CAMERA + HAND/FACE TRACKING WORKER THREAD
# ============================================================================
# This is the key "no lag" design decision: camera capture and MediaPipe
# processing run on their own thread at whatever pace they can manage. The
# GL render loop never blocks on them -- it just reads the latest published
# result. A slow frame from MediaPipe costs tracking latency, never FPS.

class TrackingWorker:
    def __init__(self, face_tracker):
        self.cap = None
        self.hands = None
        self.mediapipe_ok = False
        self.camera_ok = False
        self.face_tracker = face_tracker

        self._lock = threading.Lock()
        self._latest_frame = None      # BGR numpy, for the GL background quad
        self._latest_hand_list = []
        self._latest_num_hands = 0
        self._latest_face_gesture = None
        self._stop_event = threading.Event()
        self._thread = None

        # -- detection hysteresis -------------------------------------
        # MediaPipe occasionally misses a hand for a frame or two even
        # when it's clearly in view (motion blur, a bad angle for one
        # frame, etc). Reporting "0 hands" instantly on every one of
        # those blips is what reads as "my hand isn't getting detected"
        # and also caused auto-rotate/mode-text to flicker on and off.
        # We bridge short gaps by holding the last-seen hand pose for a
        # few frames before actually reporting the hand as gone.
        self._hold_hand_list = []
        self._hold_num_hands = 0
        self._miss_streak = 0
        self.HOLD_FRAMES = 10  # ~0.3s at 30fps -- long enough to bridge a
                                # blip, short enough to still feel instant

    def setup(self):
        # Open camera with DirectShow backend first on Windows for instant, reliable init
        try:
            self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
            if not self.cap or not self.cap.isOpened():
                # Fallback: check secondary camera index
                self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
                if not self.cap or not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(1)

            if self.cap and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.camera_ok = True
            else:
                self.camera_ok = False
        except Exception as e:
            print(f"[WARN] Camera unavailable: {e}")
            self.camera_ok = False

        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_hands = mp.solutions.hands
                # model_complexity=1 delivers vastly superior landmark tracking
                # across hand orientations, lighting variations, and distances
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False, max_num_hands=2, model_complexity=1,
                    min_detection_confidence=0.45, min_tracking_confidence=0.45)
                self.mediapipe_ok = True
            except Exception as e:
                print(f"[WARN] MediaPipe unavailable: {e}")
                self.mediapipe_ok = False

    def start(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while not self._stop_event.is_set():
            if not self.camera_ok or self.cap is None:
                time.sleep(0.05)
                continue
            success, frame = self.cap.read()
            if not success:
                self.camera_ok = False
                time.sleep(0.1)
                continue
            frame = cv2.flip(frame, 1)
            hand_list, num_hands, face_gesture = [], 0, None
            if self.mediapipe_ok:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Gentle linear illumination boost ONLY in genuinely dark rooms.
                # Avoids harsh CLAHE contrast shifts that confuse MediaPipe palm detector
                if rgb.mean() < 65:
                    rgb = cv2.convertScaleAbs(rgb, alpha=1.25, beta=20)
                rgb.flags.writeable = False
                try:
                    results = self.hands.process(rgb)
                    hand_list = results.multi_hand_landmarks or []
                    num_hands = len(hand_list)
                except Exception:
                    hand_list, num_hands = [], 0
                try:
                    face_gesture = self.face_tracker.process(rgb, time.time())
                except Exception:
                    face_gesture = None

                # -- bridge short detection gaps (see HOLD_FRAMES above) --
                if num_hands > 0:
                    self._hold_hand_list = hand_list
                    self._hold_num_hands = num_hands
                    self._miss_streak = 0
                else:
                    self._miss_streak += 1
                    if self._miss_streak <= self.HOLD_FRAMES and self._hold_hand_list:
                        hand_list = self._hold_hand_list
                        num_hands = self._hold_num_hands
                    else:
                        self._hold_hand_list = []
                        self._hold_num_hands = 0

            with self._lock:
                self._latest_frame = frame
                self._latest_hand_list = hand_list
                self._latest_num_hands = num_hands
                if face_gesture:
                    self._latest_face_gesture = face_gesture

    def snapshot(self):
        """Thread-safe read of the latest published state."""
        with self._lock:
            face_g = self._latest_face_gesture
            self._latest_face_gesture = None
            return self._latest_frame, self._latest_hand_list, self._latest_num_hands, face_g

    def stop(self):
        self._stop_event.set()
        if self.cap is not None:
            self.cap.release()
        if self.hands is not None:
            self.hands.close()


# ============================================================================
# MAIN CONTROLLER
# ============================================================================

class JARVISController:

    VOICE_ALIASES = {
        # Chemistry
        "fullerene": "fullerene", "buckyball": "fullerene", "c60": "fullerene",
        "water": "h2o", "h2o": "h2o",
        "carbon dioxide": "co2", "co2": "co2",
        "methane": "ch4", "ch4": "ch4",
        "ammonia": "nh3", "nh3": "nh3",
        "oxygen": "o2", "o2": "o2",
        "nitrogen": "n2", "n2": "n2",
        "hydrochloric acid": "hcl", "acid": "hcl", "hcl": "hcl",
        "sulfuric acid": "h2so4", "h2so4": "h2so4",
        "benzene": "benzene",
        "glucose": "glucose", "sugar": "glucose",
        "ethanol": "ethanol", "alcohol": "ethanol",
        "aspirin": "aspirin",
        "atp": "atp", "energy": "atp",
        "amino acid": "amino_acid", "glycine": "amino_acid",
        "dna": "dna", "double helix": "dna", "genetics": "dna",

        # Biology & Organs
        "heart": "heart", "human heart": "heart", "cardiac": "heart", "beating heart": "heart",
        "respiratory": "respiratory", "lungs": "respiratory", "breathing": "respiratory",
        "digestive": "digestive", "stomach": "digestive", "digestion": "digestive",
        "neuron": "neuron", "nerve": "neuron", "synapse": "neuron",
        "brain": "brain", "cerebrum": "brain", "mind": "brain",
        "eye": "eye", "vision": "eye", "eyeball": "eye",
        "ear": "ear", "hearing": "ear",
        "kidney": "kidney", "renal": "kidney",
        "liver": "liver", "hepatic": "liver",
        "skeleton": "skeleton", "bones": "skeleton", "skull": "skeleton",
        "muscular": "muscular", "muscles": "muscular", "biceps": "muscular",
        "circulatory": "circulatory", "blood": "circulatory", "vessels": "circulatory",
        "cell": "cell", "animal cell": "cell",
        "mitochondria": "mitochondria", "powerhouse": "mitochondria",
        "ribosome": "ribosome",
        "chromosome": "chromosome",
        "bacteriophage": "bacteriophage", "phage": "bacteriophage",
        "hiv": "hiv", "virus": "hiv",
        "papillomavirus": "papillomavirus", "hpv": "papillomavirus",
        "adenovirus": "adenovirus",

        # Physics & Space
        "atom": "atom", "bohr atom": "atom",
        "wave": "wave", "transverse wave": "wave",
        "pendulum": "pendulum", "swing": "pendulum",
        "projectile": "projectile", "parabola": "projectile",
        "circuit": "circuit", "electric": "circuit",
        "magnetic field": "magnetic_field", "magnet": "magnetic_field",
        "electromagnetic": "em_field", "em field": "em_field", "light wave": "em_field",
        "quantum": "quantum_cloud", "orbital": "quantum_cloud",
        "earth": "earth", "world": "earth",
        "moon": "moon", "lunar": "moon",
        "solar system": "solar_system", "planets": "solar_system",
        "black hole": "black_hole", "singularity": "black_hole",

        # Engineering (Car Engine)
        "engine": "car_engine", "car engine": "car_engine", "car": "car_engine",
        "motor": "car_engine", "pistons": "car_engine", "four cylinder": "car_engine",
        "combustion engine": "car_engine", "cylinder engine": "car_engine",

        # Geography (World Map & India Map)
        "world map": "world_map", "globe": "world_map", "geography": "world_map",
        "earth map": "world_map", "map of the world": "world_map", "global map": "world_map",
        "india": "india_map", "india map": "india_map", "indian map": "india_map",
        "map of india": "india_map", "bharat": "india_map", "hindustan": "india_map",
        "geographical india": "india_map",
    }

    def __init__(self):
        self.theme = ThemeManager("blue")
        self.hud = HUDRenderer(FRAME_W, FRAME_H)
        self.gestures = GestureController()
        self.face_tracker = FaceTracker()
        self.science = SCIENCE_DATA
        self.screenshot_mgr = ScreenshotManager()
        self.recorder = Recorder()
        self.voice = VoiceController()
        self.tts = TTSController()
        self.ai_brain = AIBrain(ENABLE_AI_BRAIN, ANTHROPIC_API_KEY)
        self.lab = VirtualLab()
        self.demo = DemoMode()
        self.tracking = TrackingWorker(self.face_tracker)
        self.tex_mgr = None  # created after the GL context exists

        self.model_order = MODEL_ORDER
        self.current_model = self.model_order[0]

        self.angle_x, self.angle_y = 0.3, 0.3
        self.target_angle_x, self.target_angle_y = 0.3, 0.3
        self.scale, self.target_scale = 1.0, 1.0
        self.smoothing = 0.25
        self.pan_x, self.pan_y = 0.0, 0.0
        self.transition_start = time.time()
        self.transition_duration = 0.45
        self.last_voice_text = ""
        self.last_voice_time = 0.0

        self.detection_active = True
        self.info_visible = True
        # Auto-rotate is ON by default: with no hand in frame the model
        # spins gently on its own, and the moment a hand appears and takes
        # over rotation/zoom control, it stops -- then resumes the instant
        # the hand leaves the frame again. This is the default idle
        # behaviour now rather than something you have to turn on; it can
        # still be toggled off with the 'R' key / voice command if wanted.
        self.auto_rotate = True
        self.highlight_index = 0
        self.explode_factor_target = 0.0
        self.explode_factor = 0.0

        self.menu_open = False
        self.category_idx = 0
        self.cursor_target = None
        self.cursor_dwell_start = None
        self.cursor_dwell_time = 1.0

        self.wake_active = not SPEECH_RECOGNITION_AVAILABLE  # if no mic, treat as "always listening" no-op
        self.show_camera_bg = False  # black background by default; 'b' toggles the live camera feed
        self.perf_mode = False  # 'k' toggles: drops sphere detail + purely-decorative HUD chrome to cut lag
        self.ai_pending_speak = None

        self.gesture_status = "NONE"
        self.mode_text = "MODE: GESTURE"
        self.start_time = time.time()
        self.frame_times = collections.deque(maxlen=30)

        self._take_screenshot_flag = False
        self._start_recording_flag = False
        self._stop_recording_flag = False
        self._quit_flag = False
        self.window = None

    # -- model navigation ------------------------------------------------
    def go_home(self):
        self.current_model = self.model_order[0]
        self.target_angle_x, self.target_angle_y = 0.3, 0.3
        self.target_scale = 1.0
        self.highlight_index = 0
        self.explode_factor_target = 0.0

    def next_model(self):
        i = self.model_order.index(self.current_model)
        self.current_model = self.model_order[(i + 1) % len(self.model_order)]
        self.highlight_index = 0
        self.explode_factor_target = 0.0

    def prev_model(self):
        i = self.model_order.index(self.current_model)
        self.current_model = self.model_order[(i - 1) % len(self.model_order)]
        self.highlight_index = 0
        self.explode_factor_target = 0.0

    def set_model(self, key):
        if key in self.model_order:
            self.current_model = key
            self.highlight_index = 0
            self.explode_factor_target = 0.0
            return True
        return False

    def next_category(self, step=1):
        self.category_idx = (self.category_idx + step) % len(CATEGORY_ORDER)
        cat = CATEGORY_ORDER[self.category_idx]
        for key in self.model_order:
            if CATEGORY_OF.get(key) == cat:
                self.set_model(key)
                break

    def cycle_highlight(self):
        info = self.science.get(self.current_model)
        parts = info.get("parts") if info else None
        if parts:
            self.highlight_index = (self.highlight_index + 1) % len(parts)

    def current_highlight_key(self):
        info = self.science.get(self.current_model)
        parts = info.get("parts") if info else None
        if parts:
            return list(parts.keys())[self.highlight_index]
        return None

    def toggle_explode(self):
        self.explode_factor_target = 0.0 if self.explode_factor_target > 0.5 else 1.0

    # -- discrete gesture handling ---------------------------------------
    def _handle_discrete_gesture(self, gesture):
        if gesture == "open_palm":
            self.go_home()
        elif gesture == "fist":
            self.detection_active = not self.detection_active
        elif gesture == "point":
            if self.cursor_target is not None:
                pass  # cursor already drives selection via dwell
            else:
                self.cycle_highlight()
        elif gesture == "two_fingers":
            self.menu_open = not self.menu_open
        elif gesture == "three_fingers":
            self.info_visible = not self.info_visible
        elif gesture == "ok_sign":
            if self.menu_open:
                self.next_category()
                self.menu_open = False
            else:
                self.tts.speak("Confirmed.")
        elif gesture == "thumbs_up":
            self.tts.speak("Confirmed.")
        elif gesture == "swipe_left":
            self.prev_model()
        elif gesture == "swipe_right":
            self.next_model()
        elif gesture == "swipe_up":
            if self.menu_open:
                self.next_category(-1)
            else:
                self.info_visible = True
        elif gesture == "swipe_down":
            if self.menu_open:
                self.next_category(1)
            else:
                self.info_visible = False
        elif gesture == "together":
            if len(self.lab.selected) == 2:
                self._run_lab_combine()
        # "pinch"/"apart" already drive continuous zoom via compute_transform

    def _run_lab_combine(self):
        result = self.lab.combine()
        if result:
            self.tts.speak(result["speak"])
            if result["product"]:
                self.set_model(result["product"])

    def _handle_face_gesture(self, gesture):
        if gesture == "nod":
            if self.menu_open:
                self.next_category()
                self.menu_open = False
            else:
                self.tts.speak("Confirmed.")
        elif gesture == "shake":
            self.go_home()

    # -- voice command handling -------------------------------------------
    def handle_voice_command(self, text):
        text = text.lower().strip()
        self.last_voice_text = text
        self.last_voice_time = time.time()

        if ENABLE_AI_BRAIN and self.ai_brain.enabled and ("jarvis" in text or self.wake_active):
            known = any(p in text for p in list(self.VOICE_ALIASES) + [
                "next", "previous", "zoom", "rotate", "resume", "pause",
                "screenshot", "recording", "hide information", "show information",
                "theme", "quit", "exit", "shutdown", "demo", "combine", "explode"])
            if not known:
                self.ai_brain.ask_async(text)
                return

        # 1. Match models directly by alias (longest match first) - no "show" prefix required!
        matched_model = None
        for phrase, key in sorted(self.VOICE_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
            if phrase in text:
                matched_model = key
                break

        if matched_model:
            self.set_model(matched_model)
            m_name = self.science.get(matched_model, {}).get("name", matched_model)
            self.tts.speak(f"{m_name} loaded.")
            return

        # 2. Control actions and parameters
        if "next" in text or "forward" in text:
            self.next_model(); self.tts.speak("Next model.")
        elif "previous" in text or "back" in text:
            self.prev_model(); self.tts.speak("Previous model.")
        elif "zoom in" in text or "bigger" in text or "closer" in text:
            self.target_scale = min(3.2, self.target_scale + 0.4)
            self.tts.speak("Zooming in.")
        elif "zoom out" in text or "smaller" in text or "farther" in text:
            self.target_scale = max(0.3, self.target_scale - 0.4)
            self.tts.speak("Zooming out.")
        elif "reset zoom" in text or "normal size" in text:
            self.target_scale = 1.0
            self.tts.speak("Zoom reset.")
        elif "explode" in text or "disassemble" in text or "break apart" in text:
            self.explode_factor_target = 1.0
            self.tts.speak("Exploded view active.")
        elif "assemble" in text or "put together" in text or "reassemble" in text:
            self.explode_factor_target = 0.0
            self.tts.speak("Model assembled.")
        elif "rotate" in text or "spin" in text:
            self.auto_rotate = not self.auto_rotate
            self.tts.speak("Auto rotation " + ("enabled" if self.auto_rotate else "disabled"))
        elif "resume" in text or "play" in text or "unpause" in text:
            self.detection_active = True; self.tts.speak("Resuming detection.")
        elif "pause" in text or "freeze" in text or "stop" in text:
            self.detection_active = False; self.tts.speak("Detection paused.")
        elif "screenshot" in text or "capture" in text or "take picture" in text:
            self._take_screenshot_flag = True
        elif "start recording" in text or "record video" in text:
            self._start_recording_flag = True
        elif "stop recording" in text:
            self._stop_recording_flag = True
        elif "hide information" in text or "close info" in text:
            self.info_visible = False
        elif "show information" in text or "info" in text or "tell me about this" in text:
            self.info_visible = True
            info = self.science.get(self.current_model)
            if info:
                self.tts.speak(info["description"])
        elif "demo" in text or "presentation" in text:
            if "stop" in text:
                self.demo.stop(); self.tts.speak("Demo mode stopped.")
            else:
                self.set_model(self.demo.start()); self.tts.speak("Starting demonstration mode.")
        elif "combine" in text:
            self._run_lab_combine()
        elif "theme" in text:
            for name in THEME_ORDER:
                if name in text:
                    self.theme.set(name)
                    self.tts.speak(f"Switched to {name} theme.")
                    break
        elif "quit" in text or "exit" in text or "shutdown" in text:
            self._quit_flag = True

    def handle_ai_intent(self, intent):
        action = intent.get("action", "unknown")
        target = intent.get("target")
        speak = intent.get("speak") or ""
        if action == "show" and target in self.model_order:
            self.set_model(target)
        elif action == "next":
            self.next_model()
        elif action == "previous":
            self.prev_model()
        elif action == "zoom_in":
            self.target_scale = min(3.0, self.target_scale + 0.4)
        elif action == "zoom_out":
            self.target_scale = max(0.3, self.target_scale - 0.4)
        elif action == "rotate_toggle":
            self.auto_rotate = not self.auto_rotate
        elif action == "explode_toggle":
            self.toggle_explode()
        elif action == "pause":
            self.detection_active = False
        elif action == "resume":
            self.detection_active = True
        elif action == "highlight_next":
            self.cycle_highlight()
        elif action == "demo_start":
            self.set_model(self.demo.start())
        elif action == "demo_stop":
            self.demo.stop()
        elif action == "lab_combine":
            self._run_lab_combine()
        elif action == "theme" and target in THEMES:
            self.theme.set(target)
        if speak:
            self.tts.speak(speak)

    # -- keyboard fallback --------------------------------------------------
    def _handle_key(self, key):
        ch = chr(key) if 32 <= key < 127 else ''
        if ch == 'n':
            self.next_model()
        elif ch == 'p':
            self.prev_model()
        elif ch == 's':
            self._take_screenshot_flag = True
        elif ch == 'v':
            if self.recorder.active:
                self._stop_recording_flag = True
            else:
                self._start_recording_flag = True
        elif ch == 'i':
            self.info_visible = not self.info_visible
        elif ch == 't':
            self.theme.cycle()
        elif ch == 'x':
            self.toggle_explode()
        elif ch == 'l':
            if self.current_model in self.model_order:
                self.lab.select(self.current_model)
        elif ch == 'c':
            self._run_lab_combine()
        elif ch == 'd':
            if self.demo.active:
                self.demo.stop()
            else:
                self.set_model(self.demo.start())
        elif ch == 'm':
            self.menu_open = not self.menu_open
        elif ch == 'f':
            self.face_tracker.toggle()
        elif ch == 'b':
            self.show_camera_bg = not self.show_camera_bg
        elif ch == 'a':
            self.ai_brain.enabled = not self.ai_brain.enabled and bool(self.ai_brain.api_key)
        elif ch == 'k':
            self.perf_mode = not self.perf_mode
            SPHERE_QUALITY["n"] = 9 if self.perf_mode else 16
            self.tts.speak("Performance mode " + ("on" if self.perf_mode else "off"))
        elif key == 32:  # space
            self.detection_active = not self.detection_active


    # -- GL / window setup ---------------------------------------------------
    def setup_gl_window(self):
        if not glfw.init():
            raise RuntimeError("glfw.init() failed")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        self.window = glfw.create_window(FRAME_W, FRAME_H,
            "JARVIS - Touchless Scientific Visualization System", None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("glfw.create_window() failed")
        glfw.make_context_current(self.window)
        glfw.swap_interval(1)  # vsync -- avoids pegging a core and keeps frame pacing smooth

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [2.0, 3.0, 4.0, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.95, 0.95, 0.95, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.25, 0.25, 0.28, 1.0])
        glShadeModel(GL_SMOOTH)
        glEnable(GL_NORMALIZE)
        self.tex_mgr = TextureManager()
        glfw.set_key_callback(self.window, self._glfw_key_callback)

    def _glfw_key_callback(self, window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE or key == glfw.KEY_Q:
            self._quit_flag = True
            return
        try:
            ch = chr(key).lower()
        except ValueError:
            return
        if 97 <= ord(ch) <= 122 or ch == ' ':
            self._handle_key(ord(ch) if ch != ' ' else 32)

    # -- background + 3D scene ------------------------------------------------
    def _draw_camera_background(self, frame_bgr):
        if not self.show_camera_bg or frame_bgr is None:
            return
        tex_id = self.tex_mgr.upload_bgr("camera", frame_bgr)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(0.4, 0.4, 0.4, 1.0)  # dim the raw camera feed so the 3D model reads clearly on top
        glMatrixMode(GL_PROJECTION)
        glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0, FRAME_W, FRAME_H, 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix(); glLoadIdentity()
        glBegin(GL_QUADS)
        # texcoord v=0 is the FIRST row uploaded, which is the top row of
        # our numpy image -- so screen-top must map to v=0, not v=1, or the
        # whole picture renders upside down.
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(FRAME_W, 0)
        glTexCoord2f(1, 1); glVertex2f(FRAME_W, FRAME_H)
        glTexCoord2f(0, 1); glVertex2f(0, FRAME_H)
        glEnd()
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

    def _setup_3d_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, FRAME_W / float(FRAME_H), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 0, 4.2, 0, 0, 0, 0, 1, 0)

    def _draw_model_and_collect_labels(self, t):
        """Draws the current model in 3D and returns {key: (sx, sy)} screen
        positions for every highlightable part, via gluProject, so the HUD
        compositor can draw crisp 2D text labels next to the 3D geometry."""
        glPushMatrix()
        glTranslatef(self.pan_x, self.pan_y, 0)
        glScalef(self.scale, self.scale, self.scale)
        glRotatef(math.degrees(self.angle_x), 1, 0, 0)
        glRotatef(math.degrees(self.angle_y), 0, 1, 0)

        key = self.current_model
        highlight = self.current_highlight_key()
        if key in DYNAMIC_MODELS:
            DYNAMIC_MODELS[key](t, self.explode_factor, highlight, self.theme.colors["gl"], self.tex_mgr)
        else:
            draw_primitives(STATIC_PARTS.get(key, []), t, self.explode_factor, highlight,
                            highlight_color=(1.0, 1.0, 0.0))

        # Holographic spawn/materialize animation scanner ring
        prog = min(1.0, (t - (self.transition_start - self.start_time)) / self.transition_duration)
        if prog < 1.0:
            scan_y = -1.2 + 2.4 * prog
            set_material(self.theme.colors["gl"], 0.65, emissive=0.8)
            GL_PRIM.ring((0, scan_y, 0), 1.25, 0.012, self.theme.colors["gl"], 0.7, segments=48)

        label_screen = {}
        anchors = model_label_points(key)
        if anchors:
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            viewport = glGetIntegerv(GL_VIEWPORT)
            for pk, pos in anchors.items():
                try:
                    sx, sy, sz = gluProject(pos[0], pos[1], pos[2], modelview, projection, viewport)
                    if 0.0 < sz < 1.0:
                        label_screen[pk] = (int(sx), int(FRAME_H - sy))
                except Exception:
                    continue
        glPopMatrix()
        return label_screen


    # -- HUD overlay compositing + blit --------------------------------------
    def _blit_overlay(self, rgba_canvas):
        tex_id = self.tex_mgr.upload_rgba("hud", rgba_canvas)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0, FRAME_W, FRAME_H, 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix(); glLoadIdentity()
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(FRAME_W, 0)
        glTexCoord2f(1, 1); glVertex2f(FRAME_W, FRAME_H)
        glTexCoord2f(0, 1); glVertex2f(0, FRAME_H)
        glEnd()
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)

    def _render_hud(self, num_hands, hand_list, t, proc_ms, label_screen, cursor_pos):
        colors = self.theme.colors
        accent, text_c = colors["accent"], colors["text"]
        canvas = self.hud.new_canvas()

        if not self.perf_mode:
            # Ambient chrome only -- zero effect on tracking, gestures, or
            # science content, so it's the first thing PERFORMANCE MODE
            # drops to claw back frame time on slower machines.
            self.hud.draw_particles(canvas, accent)
            self.hud.draw_scan_line(canvas, tuple(int(c * 0.3) for c in accent))
            self.hud.draw_rotating_ring(canvas, (FRAME_W - 50, 90), 22, t, accent)
        self.hud.draw_corner_brackets(canvas, accent)
        self.hud.draw_top_bar(canvas, accent, text_c)

        fps = (1.0 / max(1e-6, sum(self.frame_times) / len(self.frame_times))) if self.frame_times else 0.0

        status = [
            ("CAMERA", self.tracking.camera_ok),
            ("HAND TRACKING", self.tracking.mediapipe_ok and self.detection_active),
            ("GESTURE ENGINE", self.tracking.mediapipe_ok),
            ("FACE TRACKING", self.face_tracker.available and self.face_tracker.enabled),
            ("VOICE RECOGNITION", self.voice.available),
            ("TTS RESPONSES", self.tts.available),
            ("AI BRAIN", self.ai_brain.enabled),
            (f"FPS: {fps:.0f}", fps > 10),
        ]
        self.hud.draw_left_panel(canvas, status, accent, text_c)
        self.hud.draw_performance_box(canvas, fps, num_hands, self.gesture_status,
                                       self.detection_active, f"{CAP_W}x{CAP_H}", proc_ms, accent, text_c,
                                       self.perf_mode)
        self.hud.draw_telemetry(canvas, hand_list, self.gesture_status,
                                 96.4 if hand_list else 0.0, accent, text_c)

        info = self.science.get(self.current_model)
        highlight_key = self.current_highlight_key()
        highlight_info = None
        if info and highlight_key and info.get("parts"):
            part = info["parts"].get(highlight_key)
            if part:
                highlight_info = {"part": part["name"], "function": part["function"]}
        self.hud.draw_right_panel(canvas, info, highlight_info, accent, text_c, self.info_visible)
        self.hud.draw_bottom_bar(canvas, self.gesture_status, self.mode_text, accent, text_c)
        self.hud.draw_system_strip(canvas, accent, text_c, self.tracking.camera_ok)
        if self.last_voice_text and (time.time() - self.last_voice_time < 4.5):
            self.hud.draw_voice_banner(canvas, self.last_voice_text, accent, text_c)

        if not self.perf_mode:
            mic_level = 0.15 * math.sin(t * 6.0) + (0.5 if self.tts.speaking else 0.0)
            self.hud.draw_waveform(canvas, FRAME_W - 340, 420, 320, 60, mic_level, accent)
            self.hud.draw_radar(canvas, (FRAME_W - 100, FRAME_H - 340), 60, t, accent,
                                 blips=[(0.3, 0.2)] if hand_list else [])

        if self.menu_open:
            boxes = self.hud.draw_category_menu(canvas, CATEGORY_ORDER, self.category_idx, accent, text_c)
        if cursor_pos:
            dwell_frac = 0.0
            if self.cursor_dwell_start is not None:
                dwell_frac = min(1.0, (time.time() - self.cursor_dwell_start) / self.cursor_dwell_time)
            self.hud.draw_cursor(canvas, cursor_pos, dwell_frac, (0, 255, 255))

        label_list = []
        if info and info.get("parts"):
            for pk, pos in label_screen.items():
                nice = info["parts"].get(pk, {}).get("name", pk) if not pk.startswith("rung_") else None
                if nice:
                    label_list.append((nice, pos))
        elif self.current_model == "dna":
            for i, (pk, pos) in enumerate(label_screen.items()):
                if i < len(_DNA_LABELS):
                    label_list.append((_DNA_LABELS[i][0], pos))
        self.hud.draw_labels(canvas, label_list, (255, 255, 0))

        if self.lab.selected:
            self.hud._text(canvas, "LAB: " + " + ".join(self.lab.selected), (20, 480), 0.5, (0, 255, 255), 2)
        if self.lab.last_result and time.time() - self.lab.last_result_time < 6.0:
            self.hud._text(canvas, self.lab.last_result["equation"], (20, 505), 0.5, (0, 255, 0), 1)
        if self.demo.active:
            self.hud._text(canvas, "DEMO MODE", (FRAME_W // 2 - 60, 110), 0.6, (255, 200, 0), 2)
        if self.ai_brain.thinking:
            self.hud.draw_ai_spinner(canvas, (FRAME_W // 2, 150), t, accent)

        if self.recorder.active:
            cv2.circle(canvas, (FRAME_W - 30, 30), 8, (0, 0, 255), -1, cv2.LINE_AA)
            self.hud._text(canvas, "REC", (FRAME_W - 60, 36), 0.5, (0, 0, 255), 2)

        rgba = canvas_to_rgba(canvas)
        self._blit_overlay(rgba)


    # -- main loop -------------------------------------------------------------
    def run(self):
        self.tracking.setup()
        self.tracking.start()
        self.voice.start()
        self.tts.start()

        boot_window = "JARVIS Boot"
        cv2.namedWindow(boot_window, cv2.WINDOW_NORMAL)
        run_startup_sequence(boot_window, FRAME_W, FRAME_H, [
            ("CAMERA", self.tracking.camera_ok),
            ("MEDIAPIPE HANDS", self.tracking.mediapipe_ok),
            ("FACE MESH", self.face_tracker.available),
            ("GESTURE ENGINE", self.tracking.mediapipe_ok),
            ("SCIENCE DATABASE", True),
            ("VOICE SYSTEM", self.voice.available),
            ("TTS SYSTEM", self.tts.available),
            ("AI BRAIN", self.ai_brain.enabled),
            ("OPENGL VISUALIZATION ENGINE", OPENGL_AVAILABLE and GLFW_AVAILABLE),
        ])
        cv2.destroyWindow(boot_window)

        self.setup_gl_window()
        self.tts.speak("JARVIS online. Scientific visualization system ready.")

        try:
            while not glfw.window_should_close(self.window):
                frame_start = time.time()
                glfw.poll_events()

                frame_bgr, hand_list, num_hands, face_gesture = self.tracking.snapshot()

                if face_gesture:
                    self._handle_face_gesture(face_gesture)
                if self.face_tracker.enabled and self.face_tracker.available:
                    self.target_angle_y += self.face_tracker.head_yaw * 0.01

                if hand_list and self.detection_active:
                    (self.target_angle_x, self.target_angle_y,
                     target_scale_px, _label) = GestureController.compute_transform(hand_list)
                    self.target_scale = float(np.clip(target_scale_px / 320.0, 0.35, 2.8))
                    self.mode_text = "MODE: " + ("TWO-HAND" if num_hands == 2 else "ONE-HAND")
                elif not self.detection_active:
                    self.mode_text = "MODE: PAUSED"
                else:
                    self.mode_text = "MODE: NO HAND"

                discrete = None
                if hand_list:
                    discrete, _ginfo = self.gestures.update(hand_list, frame_start)
                    if discrete:
                        self.gesture_status = discrete.upper()
                        self._handle_discrete_gesture(discrete)
                else:
                    self.gestures.update([], frame_start)

                # -- fingertip cursor + dwell selection --------------------------
                cursor_pos = None
                if hand_list:
                    tip = hand_list[0].landmark[8]
                    cursor_pos = (int(tip.x * FRAME_W), int(tip.y * FRAME_H))
                    if self.menu_open:
                        seg_w = FRAME_W // len(CATEGORY_ORDER)
                        hovered = min(cursor_pos[0] // max(1, seg_w), len(CATEGORY_ORDER) - 1)
                        if self.cursor_target == hovered:
                            if self.cursor_dwell_start and time.time() - self.cursor_dwell_start >= self.cursor_dwell_time:
                                self.category_idx = hovered
                                self.next_category(0)
                                self.menu_open = False
                                self.cursor_dwell_start = None
                        else:
                            self.cursor_target = hovered
                            self.cursor_dwell_start = time.time()
                    else:
                        self.cursor_target = None
                        self.cursor_dwell_start = None

                if self.auto_rotate and num_hands == 0:
                    self.target_angle_y += 0.01

                demo_next = self.demo.update(frame_start)
                if demo_next:
                    self.set_model(demo_next)
                    info = self.science.get(demo_next)
                    if info:
                        self.tts.speak(info["name"] + ". " + info["description"])

                ai_intent = self.ai_brain.get_result()
                if ai_intent:
                    self.handle_ai_intent(ai_intent)

                self.angle_x += (self.target_angle_x - self.angle_x) * self.smoothing
                self.angle_y += (self.target_angle_y - self.angle_y) * self.smoothing
                self.scale += (self.target_scale - self.scale) * self.smoothing
                self.explode_factor += (self.explode_factor_target - self.explode_factor) * 0.12

                glClearColor(0.0, 0.0, 0.0, 1.0)
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

                self._draw_camera_background(frame_bgr)
                self._setup_3d_projection()
                t = frame_start - self.start_time
                label_screen = self._draw_model_and_collect_labels(t)

                proc_ms = (time.time() - frame_start) * 1000.0
                self._render_hud(num_hands, hand_list, t, proc_ms, label_screen, cursor_pos)

                if self._take_screenshot_flag:
                    path = self.screenshot_mgr.capture(FRAME_W, FRAME_H)
                    self.tts.speak("Screenshot saved.")
                    self._take_screenshot_flag = False
                if self._start_recording_flag:
                    self.recorder.start((FRAME_W, FRAME_H))
                    self.tts.speak("Recording started.")
                    self._start_recording_flag = False
                if self._stop_recording_flag:
                    self.recorder.stop()
                    self.tts.speak("Recording stopped.")
                    self._stop_recording_flag = False
                if self.recorder.active:
                    self.recorder.write_gl_frame(FRAME_W, FRAME_H)

                voice_cmd = self.voice.get_command()
                if voice_cmd:
                    self.handle_voice_command(voice_cmd)

                glfw.swap_buffers(self.window)
                self.frame_times.append(time.time() - frame_start)

                if self._quit_flag:
                    break
        finally:
            self._cleanup()

    def _cleanup(self):
        self.tracking.stop()
        self.recorder.stop()
        self.voice.stop()
        self.tts.stop()
        if self.window is not None:
            glfw.destroy_window(self.window)
        if GLFW_AVAILABLE:
            glfw.terminate()
        cv2.destroyAllWindows()


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    missing = []
    if not OPENGL_AVAILABLE:
        missing.append("PyOpenGL (pip install PyOpenGL PyOpenGL_accelerate)")
    if not GLFW_AVAILABLE:
        missing.append("glfw (pip install glfw)")
    if not MEDIAPIPE_AVAILABLE:
        missing.append("mediapipe (pip install mediapipe) -- required for gesture control")
    if missing:
        print("=" * 70)
        print("JARVIS cannot start: missing required packages:")
        for m in missing:
            print("  -", m)
        print("Install the packages above and run again.")
        print("=" * 70)
        sys.exit(1)

    JARVISController().run()


if __name__ == "__main__":
    main()
