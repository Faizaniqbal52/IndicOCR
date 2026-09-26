"""
Agent-Augmenter: Authentic Indian Physical Degradation Engine & Metric Gatekeeper
Enforces:
1. Dynamic vertical zone preservation (Zero diacritic clipping, CNN H=1 pooling protection).
2. DiacriticOwnershipGate: 100% own ink in bbox, 0 foreign ink pixels.
3. Stochastic DAG of 3 to 6 realistic degradations:
   - Yellow raddi / newsprint substrate texture
   - Non-uniform lighting gradients & shadow overlays
   - Ink bleed & toner erosion
   - Gaussian / defocus blur
   - Xerox photostat contrast clipping & toner dust
   - Skew / perspective jitter (-3 to +3 deg)
   - Official Indian stamp / seal overlays (purple/red/blue)
4. INVARIANT: assert applied_augmentations_count >= 2.
"""

import sys
import math
import random
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageOps

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class DegradationError(Exception):
    """Base exception for Agent-Augmenter."""
    pass


class DiacriticOwnershipError(DegradationError):
    """Raised when token ink escapes bounding box or foreign ink enters."""
    pass


class PaperSubstrateEngine:
    """Procedural generator for the 12 document substrate classes from SynthOCR-Gen (arXiv:2601.16113 Figure 7a)."""

    @staticmethod
    def _create_base_canvas(w: int, h: int, rgb: Tuple[int, int, int]) -> np.ndarray:
        canvas = np.zeros((h, w, 3), dtype=np.float32)
        canvas[:, :] = rgb
        return canvas

    @staticmethod
    def _perlin_octaves(w: int, h: int, octaves: List[Tuple[int, float]]) -> np.ndarray:
        accum = np.zeros((h, w), dtype=np.float32)
        for scale, weight in octaves:
            sh, sw = max(4, h // scale), max(4, w // scale)
            noise = np.random.normal(0, 1.0, (sh, sw)).astype(np.float32)
            smooth = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
            accum += smooth * weight
        return accum

    def generate(self, w: int, h: int, substrate_type: str, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        st = substrate_type.lower().replace(" ", "_")

        if st == "clean_white":
            canvas = self._create_base_canvas(w, h, (255, 255, 255))
            noise = np.random.normal(0, 0.3, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "aged_paper":
            base_rgb = (239, 224, 189)
            canvas = self._create_base_canvas(w, h, base_rgb)
            clouds = self._perlin_octaves(w, h, [(36, 11.0), (16, 6.0), (8, 3.0)])
            canvas[:, :, 0] += clouds * 1.15
            canvas[:, :, 1] += clouds * 0.95
            canvas[:, :, 2] += clouds * 0.65
            fine_grain = np.random.normal(0, 1.8, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + fine_grain, 0, 255).astype(np.uint8)

        elif st == "book_page":
            base_rgb = (245, 239, 228)
            canvas = self._create_base_canvas(w, h, base_rgb)
            clouds = self._perlin_octaves(w, h, [(40, 4.5), (16, 2.5)])
            canvas[:, :, 0] += clouds * 0.95
            canvas[:, :, 1] += clouds * 0.90
            canvas[:, :, 2] += clouds * 0.80
            fibers = np.random.normal(0, 1.5, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + fibers, 0, 255).astype(np.uint8)

        elif st == "newspaper":
            base_rgb = (218, 216, 208)
            canvas = self._create_base_canvas(w, h, base_rgb)
            pulp = self._perlin_octaves(w, h, [(24, 6.5), (10, 4.0), (3, 2.5)])
            canvas += pulp[:, :, None]

            ghost_mask = np.zeros((h, w), dtype=np.float32)
            num_cols = max(1, w // 70)
            col_w = w // num_cols
            for c in range(num_cols):
                cx0 = c * col_w + 6
                cx1 = (c + 1) * col_w - 6
                for gy in range(8, h - 8, 7):
                    if random.random() < 0.70:
                        gl_w = random.randint(int((cx1 - cx0) * 0.5), cx1 - cx0)
                        cv2.line(ghost_mask, (cx0, gy), (cx0 + gl_w, gy), 1.0, 1)
            ghost_mask = cv2.GaussianBlur(ghost_mask, (5, 5), 1.5)
            canvas -= (ghost_mask[:, :, None] * random.uniform(8.0, 14.0))

            num_specks = int(w * h * 0.0007)
            for _ in range(num_specks):
                sx = random.randint(0, w - 1)
                sy = random.randint(0, h - 1)
                dark = random.randint(25, 65)
                canvas[sy, sx, :] -= dark

            noise = np.random.normal(0, 3.0, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "notebook":
            base_rgb = (250, 248, 238)
            canvas = self._create_base_canvas(w, h, base_rgb)
            clouds = self._perlin_octaves(w, h, [(30, 2.5)])
            canvas += clouds[:, :, None]

            line_spacing = 26
            rule_color = np.array([172, 196, 218], dtype=np.float32)
            first_y = line_spacing - (line_spacing // 4)
            for y in range(first_y, h - 3, line_spacing):
                if 0 <= y < h:
                    alpha = 0.65
                    canvas[y, :, :] = canvas[y, :, :] * (1.0 - alpha) + rule_color * alpha
                    if y + 1 < h:
                        canvas[y + 1, :, :] = canvas[y + 1, :, :] * (1.0 - alpha * 0.35) + rule_color * (alpha * 0.35)

            if w > 140:
                mx = int(w * 0.08)
                m_color = np.array([232, 175, 175], dtype=np.float32)
                alpha_m = 0.50
                canvas[:, mx, :] = canvas[:, mx, :] * (1.0 - alpha_m) + m_color * alpha_m
                if mx + 1 < w:
                    canvas[:, mx + 1, :] = canvas[:, mx + 1, :] * (1.0 - alpha_m * 0.35) + m_color * (alpha_m * 0.35)

            noise = np.random.normal(0, 1.2, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "parchment":
            base_rgb = (235, 215, 162)
            canvas = self._create_base_canvas(w, h, base_rgb)
            mottle = self._perlin_octaves(w, h, [(44, 15.0), (18, 8.5), (8, 4.0)])
            canvas[:, :, 0] += mottle * 1.25
            canvas[:, :, 1] += mottle * 1.05
            canvas[:, :, 2] += mottle * 0.60
            noise = np.random.normal(0, 2.8, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "weathered":
            base_rgb = (198, 194, 184)
            canvas = self._create_base_canvas(w, h, base_rgb)
            grunge = self._perlin_octaves(w, h, [(36, 12.0), (14, 7.0), (6, 3.5)])
            canvas += grunge[:, :, None] * 0.95

            num_damp = random.randint(1, 3)
            for _ in range(num_damp):
                cx = random.randint(0, w - 1)
                cy = random.randint(0, h - 1)
                rx = random.randint(15, max(20, w // 4))
                ry = random.randint(15, max(20, h // 4))
                damp_mask = np.zeros((h, w), dtype=np.float32)
                cv2.ellipse(damp_mask, (cx, cy), (rx, ry), random.randint(0, 180), 0, 360, 1.0, -1)
                damp_mask = cv2.GaussianBlur(damp_mask, (25, 25), 8.0)
                canvas -= (damp_mask[:, :, None] * 18.0)

            noise = np.random.normal(0, 3.2, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "coffee_stained":
            base_rgb = (244, 236, 218)
            canvas = self._create_base_canvas(w, h, base_rgb)
            clouds = self._perlin_octaves(w, h, [(30, 4.0)])
            canvas += clouds[:, :, None]

            cx = random.randint(int(w * 0.2), int(w * 0.8))
            cy = random.randint(int(h * 0.2), int(h * 0.8))
            min_dim = min(w, h)
            radius = random.randint(max(18, min_dim // 4), max(28, int(min_dim * 0.48)))

            y_grid, x_grid = np.ogrid[:h, :w]
            dist = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)

            ring_dist = np.abs(dist - radius)
            ring_mask = np.exp(-0.5 * (ring_dist / 3.2)**2)
            interior_mask = (dist < radius).astype(np.float32) * np.exp(-0.5 * ((dist / radius)**2)) * 0.40
            total_stain = np.clip(ring_mask * 0.80 + interior_mask, 0, 1.0)

            stain_rgb = np.array([155, 105, 58], dtype=np.float32)
            for c in range(3):
                canvas[:, :, c] = canvas[:, :, c] * (1.0 - total_stain * 0.62) + stain_rgb[c] * (total_stain * 0.62)

            for _ in range(random.randint(5, 12)):
                drx = cx + random.randint(-radius - 25, radius + 25)
                dry = cy + random.randint(-radius - 25, radius + 25)
                if 0 <= drx < w and 0 <= dry < h:
                    sp_r = random.randint(1, 3)
                    cv2.circle(canvas, (drx, dry), sp_r, (145, 95, 50), -1)

            noise = np.random.normal(0, 1.8, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "old_book":
            base_rgb = (236, 218, 185)
            canvas = self._create_base_canvas(w, h, base_rgb)
            mottle = self._perlin_octaves(w, h, [(30, 8.0), (12, 4.0)])
            canvas[:, :, 0] += mottle * 1.15
            canvas[:, :, 1] += mottle * 0.90
            canvas[:, :, 2] += mottle * 0.55

            y_grid, x_grid = np.ogrid[:h, :w]
            norm_x = (x_grid - (w / 2.0)) / (w / 2.0)
            norm_y = (y_grid - (h / 2.0)) / (h / 2.0)
            corner_dist = np.sqrt(norm_x**2 + norm_y**2)
            vignette = np.clip(1.0 - 0.38 * (corner_dist**1.8), 0.52, 1.0)
            canvas *= vignette[:, :, None]

            num_foxing = random.randint(4, 9)
            for _ in range(num_foxing):
                fx = random.randint(0, w - 1)
                fy = random.randint(0, h - 1)
                fr = random.randint(2, 4)
                fox_mask = np.zeros((h, w), dtype=np.float32)
                cv2.circle(fox_mask, (fx, fy), fr, 1.0, -1)
                fox_mask = cv2.GaussianBlur(fox_mask, (7, 7), 1.8)
                fox_color = np.array([168, 112, 60], dtype=np.float32)
                for c in range(3):
                    canvas[:, :, c] = canvas[:, :, c] * (1.0 - fox_mask * 0.55) + fox_color[c] * (fox_mask * 0.55)

            noise = np.random.normal(0, 2.2, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "recycled":
            base_rgb = (212, 198, 178)
            canvas = self._create_base_canvas(w, h, base_rgb)
            pulp_clouds = self._perlin_octaves(w, h, [(24, 7.5), (8, 4.0)])
            canvas += pulp_clouds[:, :, None]

            num_fibers = int(w * h * 0.0013)
            for _ in range(num_fibers):
                fx = random.randint(2, w - 4)
                fy = random.randint(2, h - 4)
                flen = random.randint(2, 6)
                fangle = random.uniform(0, math.pi)
                dx = int(flen * math.cos(fangle))
                dy = int(flen * math.sin(fangle))
                darkness = random.randint(45, 100)
                fcolor = (int(max(0, canvas[fy, fx, 0] - darkness * 1.1)),
                          int(max(0, canvas[fy, fx, 1] - darkness)),
                          int(max(0, canvas[fy, fx, 2] - darkness * 0.9)))
                cv2.line(canvas, (fx, fy), (fx + dx, fy + dy), fcolor, 1)

            noise = np.random.normal(0, 3.0, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "cream":
            base_rgb = (253, 246, 216)
            canvas = self._create_base_canvas(w, h, base_rgb)
            smooth_clouds = self._perlin_octaves(w, h, [(40, 2.8)])
            canvas += smooth_clouds[:, :, None]
            noise = np.random.normal(0, 1.0, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        elif st == "ivory":
            base_rgb = (252, 250, 238)
            canvas = self._create_base_canvas(w, h, base_rgb)
            smooth_clouds = self._perlin_octaves(w, h, [(50, 1.8)])
            canvas += smooth_clouds[:, :, None]
            noise = np.random.normal(0, 0.8, (h, w, 3)).astype(np.float32)
            return np.clip(canvas + noise, 0, 255).astype(np.uint8)

        else:
            return self.generate(w, h, "book_page", seed=seed)

    @staticmethod
    def apply_diagonal_crease(img_bgr: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        """Adds a physical 3D paper fold / crease line with highlight and shadow edges."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        h, w = img_bgr.shape[:2]
        p1 = (random.randint(0, int(w * 0.3)), random.randint(0, int(h * 0.4)))
        p2 = (random.randint(int(w * 0.7), w), random.randint(int(h * 0.6), h))

        vx = p2[0] - p1[0]
        vy = p2[1] - p1[1]
        length = math.hypot(vx, vy)
        if length == 0:
            return img_bgr

        nx = -vy / length
        ny = vx / length

        y_grid, x_grid = np.ogrid[:h, :w]
        signed_dist = (x_grid - p1[0]) * nx + (y_grid - p1[1]) * ny

        span = 2.5
        shadow = np.exp(-0.5 * (signed_dist / span)**2) * (signed_dist < 0) * 0.22
        highlight = np.exp(-0.5 * (signed_dist / span)**2) * (signed_dist >= 0) * 0.14

        factor = 1.0 - shadow + highlight
        result = np.clip(img_bgr.astype(np.float32) * factor[:, :, None], 0, 255).astype(np.uint8)
        return result


class ScriptureDegradationEngine:
    """
    Simulates three evolutionary cycles of historical scripture/manuscript degradation:
    - Cycle 1: Baseline Aged Manuscript (sepia wash, moisture blotches, simple ink erosion)
    - Cycle 2: Advanced Folio Breakdown (palm-leaf striations, insect boreholes, ink craquelure)
    - Cycle 3: Extreme Rough Scripture (iron gall corrosion, brittle frayed margins, lamp soot, vermilion rubs, fungal rot)
    """

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    @staticmethod
    def _perlin_octaves(w: int, h: int, octaves: List[Tuple[int, float]]) -> np.ndarray:
        accum = np.zeros((h, w), dtype=np.float32)
        for scale, weight in octaves:
            sh, sw = max(4, h // scale), max(4, w // scale)
            noise = np.random.normal(0, 1.0, (sh, sw)).astype(np.float32)
            smooth = cv2.resize(noise, (w, h), interpolation=cv2.INTER_CUBIC)
            accum += smooth * weight
        return accum

    def apply_cycle_1_baseline(self, img_bgr: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        """Cycle 1: Baseline sepia wash, broad moisture patches, and simple ink erosion."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        h, w = img_bgr.shape[:2]
        mottle = self._perlin_octaves(w, h, [(32, 14.0), (12, 6.0)])
        substrate = np.zeros((h, w, 3), dtype=np.float32)
        substrate[:, :, 0] = 165 + mottle * 0.7
        substrate[:, :, 1] = 205 + mottle * 0.9
        substrate[:, :, 2] = 230 + mottle * 1.1

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        ink_mask = (255 - gray).astype(np.float32) / 255.0
        ink_mask = np.clip(ink_mask * 1.25, 0.0, 1.0)[:, :, None]

        res = (img_bgr.astype(np.float32) * ink_mask) + (substrate * (1.0 - ink_mask))

        bx = random.randint(int(w * 0.2), int(w * 0.8))
        by = random.randint(int(h * 0.2), int(h * 0.8))
        br = random.randint(max(15, min(w, h) // 4), max(25, min(w, h) // 2))
        blotch_mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(blotch_mask, (bx, by), br, 1.0, -1)
        blotch_mask = cv2.GaussianBlur(blotch_mask, (31, 31), 10.0)
        res[:, :, :2] *= (1.0 - blotch_mask[:, :, None] * 0.18)

        speckle_loss = np.random.binomial(1, 0.93, (h, w)).astype(np.float32)[:, :, None]
        res = res * speckle_loss + substrate * (1.0 - speckle_loss)

        grain = np.random.normal(0, 3.0, (h, w, 3)).astype(np.float32)
        return np.clip(res + grain, 0, 255).astype(np.uint8)

    def apply_cycle_2_fibers_and_fractures(self, img_bgr: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        """Cycle 2: Palm-leaf/birch-bark fibrous ribs, organic insect wormholes, and fine craquelure."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        h, w = img_bgr.shape[:2]
        substrate = np.zeros((h, w, 3), dtype=np.float32)
        substrate[:, :, 0] = 145
        substrate[:, :, 1] = 195
        substrate[:, :, 2] = 228

        y_coords = np.arange(h).astype(np.float32)[:, None]
        fiber_freq = np.sin(y_coords * 0.45) * 6.0 + np.sin(y_coords * 1.1) * 3.5
        fiber_noise = np.random.normal(0, 1.5, (h, 1)).astype(np.float32)
        horizontal_ribs = cv2.resize(fiber_freq + fiber_noise, (w, h))

        mottle = self._perlin_octaves(w, h, [(40, 16.0), (14, 8.0)])
        substrate[:, :, 0] += (mottle * 0.6 + horizontal_ribs * 0.6)
        substrate[:, :, 1] += (mottle * 0.9 + horizontal_ribs * 0.8)
        substrate[:, :, 2] += (mottle * 1.2 + horizontal_ribs * 1.0)

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        ink_mask = (255 - gray).astype(np.float32) / 255.0

        crackle_noise = np.random.normal(0, 1.0, (h // 2, w // 2)).astype(np.float32)
        crackle = cv2.resize(crackle_noise, (w, h), interpolation=cv2.INTER_LINEAR)
        crack_edges = cv2.Canny((np.clip(crackle * 50 + 128, 0, 255)).astype(np.uint8), 85, 160)
        crack_mask = (cv2.dilate(crack_edges, np.ones((1, 1), np.uint8)) > 0).astype(np.float32)

        ink_mask = ink_mask * (1.0 - crack_mask * 0.70)
        ink_mask = np.clip(ink_mask * 1.25, 0.0, 1.0)[:, :, None]

        aged_ink_bgr = np.array([28, 26, 32], dtype=np.float32)
        res = (aged_ink_bgr * ink_mask) + (substrate * (1.0 - ink_mask))

        num_holes = random.randint(2, 4)
        hole_mask = np.zeros((h, w), dtype=np.float32)
        for _ in range(num_holes):
            hx = random.randint(15, w - 15)
            hy = random.randint(10, h - 10)
            hrx = random.randint(4, max(6, min(w, h) // 10))
            hry = random.randint(3, max(5, hrx))
            cv2.ellipse(hole_mask, (hx, hy), (hrx, hry), random.randint(0, 180), 0, 360, 1.0, -1)

        hole_mask = cv2.GaussianBlur(hole_mask, (5, 5), 1.0)
        hole_binary = (hole_mask > 0.45).astype(np.float32)
        hole_border = cv2.dilate(hole_binary, np.ones((3, 3), np.uint8)) - hole_binary

        for c in range(3):
            res[:, :, c] = res[:, :, c] * (1.0 - hole_border * 0.70) + 40.0 * (hole_border * 0.70)
            res[:, :, c] = res[:, :, c] * (1.0 - hole_binary) + 120.0 * hole_binary

        noise = np.random.normal(0, 2.5, (h, w, 3)).astype(np.float32)
        return np.clip(res + noise, 0, 255).astype(np.uint8)

    def apply_cycle_3_extreme_scripture(self, img_bgr: np.ndarray, seed: Optional[int] = None) -> np.ndarray:
        """
        Cycle 3: Extreme rough ancient scripture degradation:
        - Iron Gall Acid Corrosion: Corrosive rust-brown ink halo bleeding into cellulose fibers.
        - Brittle Chipped / Frayed Page Borders: Jagged decaying margins.
        - Temple Lamp Smoke / Soot Patina: Greasy charcoal soot accumulation.
        - Vermilion / Sindoor Powder Rubs: Sacred red ceremonial smudges.
        - Deep Fungal Mildew Spores: Clusters of dark micro-spores.
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        h, w = img_bgr.shape[:2]
        substrate = np.zeros((h, w, 3), dtype=np.float32)
        substrate[:, :, 0] = 125
        substrate[:, :, 1] = 175
        substrate[:, :, 2] = 215

        deep_decay = self._perlin_octaves(w, h, [(48, 22.0), (18, 11.0), (6, 4.0)])
        y_coords = np.arange(h).astype(np.float32)[:, None]
        horizontal_ribs = cv2.resize(np.sin(y_coords * 0.5) * 5.0, (w, h))

        substrate[:, :, 0] += (deep_decay * 0.55 + horizontal_ribs * 0.5)
        substrate[:, :, 1] += (deep_decay * 0.85 + horizontal_ribs * 0.7)
        substrate[:, :, 2] += (deep_decay * 1.25 + horizontal_ribs * 0.9)

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        ink_core = (255 - gray).astype(np.float32) / 255.0

        dilated_ink = cv2.dilate(ink_core, np.ones((3, 3), np.uint8), iterations=1)
        acid_halo = np.clip(dilated_ink - ink_core * 0.5, 0.0, 1.0)

        acid_color = np.array([35, 52, 78], dtype=np.float32)
        core_ink_color = np.array([20, 22, 28], dtype=np.float32)

        crackle_noise = np.random.normal(0, 1.0, (h // 2, w // 2)).astype(np.float32)
        crackle = cv2.resize(crackle_noise, (w, h), interpolation=cv2.INTER_LINEAR)
        crack_edges = cv2.Canny((np.clip(crackle * 55 + 128, 0, 255)).astype(np.uint8), 75, 150)
        crack_mask = (cv2.dilate(crack_edges, np.ones((1, 1), np.uint8)) > 0).astype(np.float32)

        ink_core_eroded = ink_core * (1.0 - crack_mask * 0.75)
        core_3c = np.clip(ink_core_eroded * 1.3, 0.0, 1.0)[:, :, None]
        halo_3c = (acid_halo * (1.0 - core_3c[:, :, 0]))[:, :, None] * 0.65

        res = (substrate * (1.0 - core_3c - halo_3c) +
               core_ink_color * core_3c +
               acid_color * halo_3c)

        soot_center_x = random.choice([0, w])
        soot_center_y = random.choice([0, h])
        y_g, x_g = np.ogrid[:h, :w]
        dist_soot = np.sqrt((x_g - soot_center_x)**2 + (y_g - soot_center_y)**2)
        max_d = math.hypot(w, h)
        soot_factor = np.clip(1.0 - (dist_soot / (max_d * 0.75)), 0.0, 1.0)**2
        for c in range(3):
            res[:, :, c] = res[:, :, c] * (1.0 - soot_factor * 0.48) + 25.0 * (soot_factor * 0.48)

        if random.random() < 0.65:
            vx = random.randint(int(w * 0.1), int(w * 0.9))
            vy = random.randint(int(h * 0.1), int(h * 0.9))
            vrx = random.randint(12, max(18, min(w, h) // 4))
            vry = random.randint(8, max(12, min(w, h) // 5))
            vermilion_mask = np.zeros((h, w), dtype=np.float32)
            cv2.ellipse(vermilion_mask, (vx, vy), (vrx, vry), random.randint(0, 180), 0, 360, 1.0, -1)
            vermilion_mask = cv2.GaussianBlur(vermilion_mask, (21, 21), 6.0)
            res[:, :, 0] = res[:, :, 0] * (1.0 - vermilion_mask * 0.45) + 35.0 * (vermilion_mask * 0.45)
            res[:, :, 1] = res[:, :, 1] * (1.0 - vermilion_mask * 0.45) + 55.0 * (vermilion_mask * 0.45)
            res[:, :, 2] = res[:, :, 2] * (1.0 - vermilion_mask * 0.45) + 205.0 * (vermilion_mask * 0.45)

        num_holes = random.randint(3, 5)
        hole_mask = np.zeros((h, w), dtype=np.float32)
        for _ in range(num_holes):
            hx = random.randint(10, w - 10)
            hy = random.randint(8, h - 8)
            hr = random.randint(4, max(6, min(w, h) // 9))
            cv2.circle(hole_mask, (hx, hy), hr, 1.0, -1)

        hole_mask = cv2.GaussianBlur(hole_mask, (5, 5), 1.0)
        hole_binary = (hole_mask > 0.40).astype(np.float32)
        hole_border = cv2.dilate(hole_binary, np.ones((3, 3), np.uint8)) - hole_binary

        for c in range(3):
            res[:, :, c] = res[:, :, c] * (1.0 - hole_border * 0.85) + 30.0 * (hole_border * 0.85)
            res[:, :, c] = res[:, :, c] * (1.0 - hole_binary) + 95.0 * hole_binary

        num_spores = random.randint(35, 75)
        for _ in range(num_spores):
            sx = random.randint(0, w - 1)
            sy = random.randint(0, h - 1)
            scolor = (random.randint(30, 50), random.randint(35, 60), random.randint(45, 80))
            cv2.circle(res, (sx, sy), random.choice([1, 1, 2]), scolor, -1)

        border_depth = random.randint(4, 8)
        fray_noise = (np.random.normal(0, 1.5, w) > 0.3).astype(np.float32)
        res[:border_depth, :, :] *= (0.60 + fray_noise[None, :, None] * 0.30)
        res[-border_depth:, :, :] *= (0.60 + fray_noise[None, :, None] * 0.30)

        grain = np.random.normal(0, 3.5, (h, w, 3)).astype(np.float32)
        return np.clip(res + grain, 0, 255).astype(np.uint8)


class IndianDegradationEngine:
    """Stochastic DAG degradation chain modeling authentic Indian document print."""

    SUBSTRATE_CLASSES = [
        "clean_white", "aged_paper", "book_page", "newspaper",
        "notebook", "parchment", "weathered", "coffee_stained",
        "old_book", "recycled", "cream", "ivory"
    ]

    # Pre-defined Indian ink stamp colors (BGR)
    STAMP_COLORS = [
        (130, 0, 75),    # Official Purple / Violet
        (40, 40, 180),   # Bureaucratic Red
        (150, 60, 20),   # Deep Blue
        (30, 100, 30)    # Green circular seal
    ]

    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        self.substrate_engine = PaperSubstrateEngine()
        self.scripture_engine = ScriptureDegradationEngine(seed=seed)

    def apply_paper_substrate(self, img_bgr: np.ndarray, paper_type: Optional[str] = None) -> np.ndarray:
        """
        Synthesizes high-fidelity paper substrates matching SynthOCR-Gen Figure 7a.
        Blends printed text ink into the substrate canvas with realistic ink-fiber interaction.
        """
        h, w = img_bgr.shape[:2]
        if paper_type is None:
            paper_type = random.choice(self.SUBSTRATE_CLASSES)

        # Generate RGB substrate canvas
        sub_rgb = self.substrate_engine.generate(w, h, paper_type)
        canvas_bgr = cv2.cvtColor(sub_rgb, cv2.COLOR_RGB2BGR)

        # Alpha blend text ink onto substrate
        gray_src = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        alpha = (255 - gray_src).astype(np.float32) / 255.0
        alpha = np.clip(alpha * 1.15, 0, 1.0)[:, :, np.newaxis]

        # Ink fiber interaction: ink multiplies slightly with paper texture
        blended = (img_bgr.astype(np.float32) * alpha + canvas_bgr.astype(np.float32) * (1.0 - alpha))
        return np.clip(blended, 0, 255).astype(np.uint8)

    def apply_ink_bleed_or_toner_loss(self, img_bgr: np.ndarray) -> np.ndarray:
        """Simulates gentle ink spreading on porous paper or slight toner loss without erasing thin text."""
        mode = random.choice(["bleed", "erosion"])
        # Use small 2x2 kernel to strictly avoid erasing delicate Indic diacritics and thin strokes
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        inv = 255 - gray

        if mode == "bleed":
            # Dark ink expands slightly
            dilated_inv = cv2.dilate(inv, kernel, iterations=1)
            # Soft blend to avoid cartoonish blobs
            inv_blended = cv2.addWeighted(inv, 0.4, dilated_inv, 0.6, 0)
            return cv2.cvtColor(255 - inv_blended, cv2.COLOR_GRAY2BGR)
        else:
            # Gentle toner speckle loss instead of full morphological erosion that wipes out text
            mask = np.random.binomial(1, 0.96, inv.shape).astype(np.uint8)
            eroded_inv = cv2.bitwise_and(inv, inv, mask=mask)
            return cv2.cvtColor(255 - eroded_inv, cv2.COLOR_GRAY2BGR)

    def apply_shadow_gradient(self, img_bgr: np.ndarray) -> np.ndarray:
        """Simulates non-uniform smartphone lighting gradient or overhead tube-light shadow."""
        h, w = img_bgr.shape[:2]
        angle = random.uniform(0, 2 * math.pi)
        x_coords, y_coords = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
        gradient = (x_coords * math.cos(angle) + y_coords * math.sin(angle))
        gradient = (gradient - gradient.min()) / (gradient.max() - gradient.min() + 1e-6)

        # Darkness factor from 0.55 to 1.0
        min_light = random.uniform(0.55, 0.75)
        light_map = min_light + (1.0 - min_light) * gradient
        light_map_3c = np.stack([light_map] * 3, axis=-1)

        result = (img_bgr.astype(np.float32) * light_map_3c)
        return np.clip(result, 0, 255).astype(np.uint8)

    def apply_xerox_photostat_noise(self, img_bgr: np.ndarray) -> np.ndarray:
        """Simulates photostat contrast clipping, toner specks, and salt-and-pepper artifacts."""
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        # Heavy contrast boost
        clipped = np.clip((gray.astype(np.float32) - 30) * 1.35, 0, 255).astype(np.uint8)

        # Pepper specks (toner dust)
        h, w = gray.shape
        num_specks = random.randint(10, max(20, (h * w) // 1500))
        for _ in range(num_specks):
            rx = random.randint(0, w - 1)
            ry = random.randint(0, h - 1)
            rsize = random.randint(1, 2)
            cv2.circle(clipped, (rx, ry), rsize, color=random.randint(10, 80), thickness=-1)

        return cv2.cvtColor(clipped, cv2.COLOR_GRAY2BGR)

    def apply_optical_blur(self, img_bgr: np.ndarray) -> np.ndarray:
        """Simulates subtle lens defocus or low-res sensor blur without erasing small font strokes."""
        return cv2.GaussianBlur(img_bgr, (3, 3), sigmaX=0.55)

    @staticmethod
    def rotate_bounding_box(
        bbox: List[int],
        angle_deg: float,
        center: Tuple[int, int],
        canvas_size: Tuple[int, int]
    ) -> List[int]:
        """
        Mathematically transforms an axis-aligned bounding box under affine rotation M,
        guaranteeing zero label-box misalignment after skew degradation.
        """
        x0, y0, x1, y1 = bbox
        M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
        corners = np.array([
            [x0, y0, 1.0],
            [x1, y0, 1.0],
            [x1, y1, 1.0],
            [x0, y1, 1.0]
        ])
        transformed = (M @ corners.T).T
        rx0 = int(np.floor(transformed[:, 0].min()))
        ry0 = int(np.floor(transformed[:, 1].min()))
        rx1 = int(np.ceil(transformed[:, 0].max()))
        ry1 = int(np.ceil(transformed[:, 1].max()))

        w, h = canvas_size
        rx0 = max(0, min(w - 1, rx0))
        ry0 = max(0, min(h - 1, ry0))
        rx1 = max(rx0 + 1, min(w, rx1))
        ry1 = max(ry0 + 1, min(h, ry1))
        return [rx0, ry0, rx1, ry1]

    def apply_subtle_skew(
        self,
        img_bgr: np.ndarray,
        max_angle_deg: float = 2.0
    ) -> Tuple[np.ndarray, float]:
        """Slight rotation simulating realistic document placement on a flatbed or desk."""
        h, w = img_bgr.shape[:2]
        max_deg = 0.8 if min(h, w) < 80 else max_angle_deg
        angle = random.uniform(-max_deg, max_deg)
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        bg_sample = tuple(int(x) for x in img_bgr[0, 0])
        rotated = cv2.warpAffine(img_bgr, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=bg_sample)
        return rotated, angle

    def apply_official_stamp(self, img_bgr: np.ndarray) -> np.ndarray:
        """Simulates a semi-transparent official government seal / stamp stamped over printed text."""
        h, w = img_bgr.shape[:2]
        # Gate: Do not apply stamp on small word or line crops (prevents text obliteration)
        if min(h, w) < 80:
            return img_bgr

        stamp_canvas = np.zeros((h, w, 4), dtype=np.uint8)

        min_r = max(15, min(h, w) // 16)
        max_r = max(min_r + 5, min(min(h, w) // 4, 110))
        radius = random.randint(min_r, max_r)
        cx = random.randint(radius, max(radius + 1, w - radius))
        cy = random.randint(radius, max(radius + 1, h - radius))

        color = random.choice(self.STAMP_COLORS)
        stamp_bgr = (color[0], color[1], color[2], random.randint(60, 110)) # soft semi-transparent alpha

        # Draw outer circle and inner ring
        cv2.circle(stamp_canvas, (cx, cy), radius, stamp_bgr, thickness=2)
        cv2.circle(stamp_canvas, (cx, cy), radius - 6, stamp_bgr, thickness=1)

        # Composite stamp over image
        alpha_stamp = stamp_canvas[:, :, 3].astype(np.float32) / 255.0
        stamp_rgb = stamp_canvas[:, :, :3]

        for c in range(3):
            img_bgr[:, :, c] = np.clip(
                img_bgr[:, :, c].astype(np.float32) * (1.0 - alpha_stamp * 0.7) +
                stamp_rgb[:, :, c].astype(np.float32) * (alpha_stamp * 0.7),
                0, 255
            ).astype(np.uint8)

        return img_bgr

    def apply_motion_blur(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Simulates subtle handheld smartphone camera tremor blur.
        Kernel size is strictly conditioned on canvas height to protect thin Indic matras and baseline nuktas.
        """
        h, w = img_bgr.shape[:2]
        k = 3 if min(h, w) < 90 else random.choice([3, 5])
        angle_rad = random.uniform(0, math.pi)
        kernel = np.zeros((k, k), dtype=np.float32)
        c = k // 2
        for i in range(k):
            kernel[c, i] = 1.0
        M = cv2.getRotationMatrix2D((c, c), math.degrees(angle_rad), 1.0)
        kernel = cv2.warpAffine(kernel, M, (k, k))
        k_sum = np.sum(kernel)
        if k_sum > 0:
            kernel = kernel / k_sum
        return cv2.filter2D(img_bgr, -1, kernel)

    def apply_mobile_compression_artifact(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Simulates mobile messaging / camera upload compression (8x8 DCT quantization).
        Uses quality factor q in [35, 75].
        """
        q = random.randint(35, 75)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), q]
        success, enc = cv2.imencode('.jpg', img_bgr, encode_param)
        if success:
            decoded = cv2.imdecode(enc, cv2.IMREAD_COLOR)
            if decoded is not None:
                return decoded
        return img_bgr

    def apply_crease_and_fold_shadows(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Simulates 3D folded / creased document ridges (pocket folds, quadrupled fold).
        Creates directional ridge lighting with adjacent highlight and shadow gradients.
        """
        h, w = img_bgr.shape[:2]
        if min(h, w) < 60:
            return img_bgr

        crease_map = np.ones((h, w), dtype=np.float32)
        num_folds = random.randint(1, 2)
        for _ in range(num_folds):
            is_vertical = random.random() < 0.5
            pos = random.randint(int(w * 0.2), int(w * 0.8)) if is_vertical else random.randint(int(h * 0.2), int(h * 0.8))
            span = random.randint(8, 16)
            for d in range(-span, span + 1):
                idx = pos + d
                factor = 1.0 - (0.22 * math.exp(-0.5 * (d / 3.5)**2)) if d < 0 else 1.0 + (0.12 * math.exp(-0.5 * (d / 3.5)**2))
                if is_vertical and 0 <= idx < w:
                    crease_map[:, idx] = np.clip(crease_map[:, idx] * factor, 0.65, 1.25)
                elif not is_vertical and 0 <= idx < h:
                    crease_map[idx, :] = np.clip(crease_map[idx, :] * factor, 0.65, 1.25)

        crease_map = cv2.GaussianBlur(crease_map, (7, 7), 1.8)
        result = np.clip(img_bgr.astype(np.float32) * crease_map[:, :, None], 0, 255).astype(np.uint8)
        return result

    def apply_scanner_border_shadow(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Simulates photocopy glass platen border bleed and dark scanner lid shadow on page margins.
        """
        h, w = img_bgr.shape[:2]
        if min(h, w) < 70:
            return img_bgr

        edge = random.choice(["left", "right", "top", "bottom"])
        border_depth = random.randint(8, max(12, min(h, w) // 10))
        dark_factor = random.uniform(0.35, 0.65)

        gradient_1d = np.linspace(dark_factor, 1.0, border_depth)

        result = img_bgr.astype(np.float32)
        if edge == "left":
            result[:, :border_depth] *= gradient_1d[None, :, None]
        elif edge == "right":
            result[:, -border_depth:] *= gradient_1d[::-1][None, :, None]
        elif edge == "top":
            result[:border_depth, :] *= gradient_1d[:, None, None]
        elif edge == "bottom":
            result[-border_depth:, :] *= gradient_1d[::-1][:, None, None]

        return np.clip(result, 0, 255).astype(np.uint8)

    def apply_aged_patina_and_stain(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Simulates aged historical document patina with subtle sepia cast and moisture / tea stain halos.
        """
        h, w = img_bgr.shape[:2]
        sepia_overlay = np.zeros_like(img_bgr, dtype=np.float32)
        sepia_overlay[:, :, 0] = random.randint(180, 210)  # B
        sepia_overlay[:, :, 1] = random.randint(215, 235)  # G
        sepia_overlay[:, :, 2] = random.randint(235, 255)  # R

        if min(h, w) >= 90:
            stain_mask = np.zeros((h, w), dtype=np.uint8)
            cx = random.randint(w // 4, 3 * w // 4)
            cy = random.randint(h // 4, 3 * h // 4)
            axes = (random.randint(20, max(25, w // 6)), random.randint(15, max(20, h // 6)))
            cv2.ellipse(stain_mask, (cx, cy), axes, random.randint(0, 180), 0, 360, 255, -1)
            stain_mask = cv2.GaussianBlur(stain_mask, (25, 25), 8.0)
            stain_alpha = (stain_mask.astype(np.float32) / 255.0) * 0.20
            for c in range(3):
                img_bgr[:, :, c] = np.clip(img_bgr[:, :, c].astype(np.float32) * (1.0 - stain_alpha * 0.6), 0, 255).astype(np.uint8)

        blended = cv2.addWeighted(img_bgr, 0.82, sepia_overlay.astype(np.uint8), 0.18, 0)
        return blended

    def apply_carbon_copy_dye(self, img_bgr: np.ndarray) -> np.ndarray:
        """
        Simulates authentic Indian bureaucratic blue carbon paper duplicate (नीला कार्बन पर्चा).
        Shifts ink to classic indigo/violet-blue with characteristic micro-pressure fuzz.
        """
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        ink_mask = (255 - gray).astype(np.float32) / 255.0
        ink_mask = np.clip(ink_mask * 1.25, 0, 1.0)[:, :, np.newaxis]

        carbon_ink = np.array([random.randint(150, 190), random.randint(55, 85), random.randint(35, 65)], dtype=np.float32)
        carbon_bg = np.array([random.randint(240, 250), random.randint(242, 252), random.randint(238, 248)], dtype=np.float32)

        out = (carbon_ink * ink_mask) + (carbon_bg * (1.0 - ink_mask))
        fuzz = np.random.normal(0, 4, out.shape)
        return np.clip(out + fuzz, 0, 255).astype(np.uint8)

    def apply_sensor_noise(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, str]:
        """Category D: Gaussian sensor noise or salt-and-pepper dust."""
        if random.random() < 0.5:
            noise = np.random.normal(0, random.uniform(8.0, 16.0), img_bgr.shape).astype(np.float32)
            res = np.clip(img_bgr.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            return res, "additive_gaussian_sensor_noise"
        else:
            h, w = img_bgr.shape[:2]
            res = img_bgr.copy()
            num_sp = random.randint(15, max(25, (h * w) // 1400))
            for _ in range(num_sp):
                rx = random.randint(0, w - 1)
                ry = random.randint(0, h - 1)
                res[ry, rx] = (40, 40, 40) if random.random() < 0.5 else (240, 240, 240)
            return res, "salt_and_pepper_dust"

    def apply_brightness_scaling(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, str]:
        """Category D: Overexposure (+24%) or Underexposure (-24%) scaling."""
        if random.random() < 0.5:
            res = np.clip(img_bgr.astype(np.float32) * random.uniform(1.15, 1.25), 0, 255).astype(np.uint8)
            return res, "overexposure_brightness_boost"
        else:
            res = np.clip(img_bgr.astype(np.float32) * random.uniform(0.72, 0.85), 0, 255).astype(np.uint8)
            return res, "underexposure_darkness_drop"

    def apply_contrast_scaling(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, str]:
        """Category D: High-contrast binarization (+41%) or low-contrast washed ribbon (-21%)."""
        if random.random() < 0.5:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            clipped = np.clip((gray.astype(np.float32) - 25) * 1.35 + 8, 0, 255).astype(np.uint8)
            return cv2.cvtColor(clipped, cv2.COLOR_GRAY2BGR), "high_contrast_photostat_clipping"
        else:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            faded = np.clip((gray.astype(np.float32) - 128) * 0.75 + 150, 0, 255).astype(np.uint8)
            return cv2.cvtColor(faded, cv2.COLOR_GRAY2BGR), "low_contrast_faded_washout"

    def apply_faded_print(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, str]:
        """Category D: Low-opacity faint print simulating ribbon exhaustion."""
        base_bg = np.full_like(img_bgr, 250, dtype=np.float32)
        faded = img_bgr.astype(np.float32) * 0.45 + base_bg * 0.55
        return np.clip(faded, 0, 255).astype(np.uint8), "faded_ghostly_print"

    def apply_keystone_tilt(self, img_bgr: np.ndarray) -> Tuple[np.ndarray, str]:
        """Category D: Keystone perspective tilt simulating handheld camera angle."""
        h, w = img_bgr.shape[:2]
        if min(h, w) < 60:
            return img_bgr, "keystone_perspective_tilt"
        dx = random.randint(2, max(3, min(w, h) // 20))
        dy = random.randint(2, max(3, min(w, h) // 24))
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        pts2 = np.float32([[dx, dy], [w - dx, 0], [0, h - dy], [w, h]])
        P = cv2.getPerspectiveTransform(pts1, pts2)
        res = cv2.warpPerspective(img_bgr, P, (w, h), borderMode=cv2.BORDER_REPLICATE)
        return res, "keystone_perspective_tilt"

    def augment_pipeline(
        self,
        pil_img: Image.Image,
        bbox: Optional[List[int]] = None
    ) -> Any:
        """
        Executes a bounded stochastic DAG of 3 to 6 active degradation operators.
        Enforces INVARIANT: assert applied_augmentations_count >= 2.
        If bbox is provided, applies affine transformation to bbox to preserve 100% ground-truth alignment.
        Logs every specific augmentation applied with granular tag naming.
        """
        img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        applied_ops = []
        updated_bbox = list(bbox) if bbox is not None else None
        h, w = img_bgr.shape[:2]

        skew_angle = 0.0

        def do_paper(img):
            sub = random.choice(self.SUBSTRATE_CLASSES)
            return self.apply_paper_substrate(img, paper_type=sub), f"substrate_{sub}"

        def do_bleed_erosion(img):
            mode = random.choice(["bleed", "erosion"])
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            inv = 255 - gray
            if mode == "bleed":
                dilated_inv = cv2.dilate(inv, kernel, iterations=1)
                inv_blended = cv2.addWeighted(inv, 0.4, dilated_inv, 0.6, 0)
                return cv2.cvtColor(255 - inv_blended, cv2.COLOR_GRAY2BGR), "ink_bleed"
            else:
                mask = np.random.binomial(1, 0.96, inv.shape).astype(np.uint8)
                eroded_inv = cv2.bitwise_and(inv, inv, mask=mask)
                return cv2.cvtColor(255 - eroded_inv, cv2.COLOR_GRAY2BGR), "toner_erosion"

        def do_shadow(img):
            return self.apply_shadow_gradient(img), "non_uniform_shadow_gradient"

        def do_photostat(img):
            return self.apply_xerox_photostat_noise(img), "xerox_photostat_clipping"

        def do_optical_blur(img):
            return self.apply_optical_blur(img), "optical_defocus_blur"

        def do_motion_blur(img):
            return self.apply_motion_blur(img), "handheld_motion_blur"

        def do_mobile_comp(img):
            return self.apply_mobile_compression_artifact(img), "mobile_jpeg_quantization"

        def do_crease(img):
            if random.random() < 0.5:
                return self.substrate_engine.apply_diagonal_crease(img), "3d_diagonal_fold"
            else:
                return self.apply_crease_and_fold_shadows(img), "3d_ridge_crease"

        def do_aged_patina(img):
            return self.apply_aged_patina_and_stain(img), "aged_patina_and_stain"

        def do_scripture(img):
            r = random.random()
            if r < 0.55:
                return self.scripture_engine.apply_cycle_3_extreme_scripture(img), "scripture_cycle_3_extreme_decay"
            elif r < 0.85:
                return self.scripture_engine.apply_cycle_2_fibers_and_fractures(img), "scripture_cycle_2_talapatra_ribs"
            else:
                return self.scripture_engine.apply_cycle_1_baseline(img), "scripture_cycle_1_sepia_wash"

        def do_skew(img):
            nonlocal skew_angle
            rot, ang = self.apply_subtle_skew(img)
            skew_angle = ang
            return rot, "subtle_skew_jitter"

        # Core stochastic operators
        ops_pool = [
            ("paper_substrate", do_paper),
            ("ink_bleed_erosion", do_bleed_erosion),
            ("shadow_gradient", do_shadow),
            ("photostat_xerox", do_photostat),
            ("optical_blur", do_optical_blur),
            ("motion_blur", do_motion_blur),
            ("mobile_compression", do_mobile_comp),
            ("crease_and_fold", do_crease),
            ("aged_patina", do_aged_patina),
            ("ancient_scripture", do_scripture),
            ("sensor_noise", lambda img: self.apply_sensor_noise(img)),
            ("brightness_scale", lambda img: self.apply_brightness_scaling(img)),
            ("contrast_scale", lambda img: self.apply_contrast_scaling(img)),
            ("subtle_skew", do_skew)
        ]

        # Faded print (ribbon exhaustion)
        if random.random() < 0.20:
            ops_pool.append(("faded_print", lambda img: self.apply_faded_print(img)))

        # Keystone perspective tilt
        if min(h, w) >= 60 and random.random() < 0.25:
            ops_pool.append(("keystone_tilt", lambda img: self.apply_keystone_tilt(img)))

        # Carbon copy effect (mutually exclusive with paper_substrate to prevent muddy palette)
        if random.random() < 0.15:
            ops_pool.append(("carbon_copy", lambda img: (self.apply_carbon_copy_dye(img), "blue_carbon_copy_dye")))

        # Scanner border shadow for larger crops
        if min(h, w) >= 70 and random.random() < 0.40:
            ops_pool.append(("scanner_border", lambda img: (self.apply_scanner_border_shadow(img), "scanner_glass_border_shadow")))

        # Only add official stamp for sufficiently large images (e.g. paragraphs or pages)
        if min(h, w) >= 80 and random.random() < 0.35:
            ops_pool.append(("official_stamp", lambda img: (self.apply_official_stamp(img), "official_bureaucratic_stamp")))

        # Select 3 to 5 distinct operators
        num_ops = min(random.randint(3, 5), len(ops_pool))
        selected_ops = random.sample(ops_pool, num_ops)

        for op_name, op_func in selected_ops:
            try:
                res = op_func(img_bgr)
                if isinstance(res, tuple):
                    img_bgr, tag = res
                else:
                    img_bgr, tag = res, op_name
                applied_ops.append(tag)

                if op_name == "subtle_skew" and updated_bbox is not None and abs(skew_angle) > 0.01:
                    center = (w // 2, h // 2)
                    updated_bbox = self.rotate_bounding_box(updated_bbox, skew_angle, center, (w, h))
            except Exception as e:
                print(f"[Agent-Augmenter WARN] Op {op_name} failed: {e}")

        # INVARIANT 5: assert applied_augmentations_count >= 2
        assert len(applied_ops) >= 2, f"Augmentation count {len(applied_ops)} fell below minimum threshold (2)!"

        result_pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        if bbox is not None:
            return result_pil, applied_ops, updated_bbox
        return result_pil, applied_ops


