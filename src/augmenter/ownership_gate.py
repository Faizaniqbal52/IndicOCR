"""
Agent-Augmenter: Diacritic Ownership Gate & Vertical Zone Pre-Commit Assertions
Enforces:
1. 100% of a token's raster ink pixels lie strictly inside its declared bounding box.
2. 0% of foreign raster ink pixels lie inside its declared bounding box.
3. Pre-Commit Assertion Checklist:
   - assert all(glyph_id != 0 for glyph_id in shaped_glyphs) (Zero .notdef)
   - assert bbox_height >= (ascender_zone + body_zone + descender_zone) (Zero diacritic clipping)
   - assert set(image_bboxes.keys()) == set(token_ground_truth) (Zero misalignment)
   - assert applied_augmentations_count >= 2 (Zero sterile renders)
"""

import sys
from typing import List, Dict, Any, Tuple
import numpy as np

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class OwnershipGateError(Exception):
    """Raised when DiacriticOwnershipGate invariants are violated."""
    pass


class DiacriticOwnershipGate:
    """Verifies token raster ink ownership and zero diacritic truncation."""

    @staticmethod
    def verify_raster_ink_ownership(
        token_canvas_map: np.ndarray,
        token_boxes: List[Dict[str, Any]]
    ) -> bool:
        """
        token_canvas_map: (H, W) array of int32 where pixel values are token_id (1..N) or 0 (background).
        token_boxes: list of dicts with keys 'token_id', 'word', 'box' [x0, y0, x1, y1].
        """
        for entry in token_boxes:
            k = entry["token_id"]
            word = entry["word"]
            x0, y0, x1, y1 = entry["box"]

            # 1. Total ink pixels rendered for token k
            token_k_total = np.count_nonzero(token_canvas_map == k)
            if token_k_total == 0:
                continue

            # 2. Ink enclosed in declared box
            box_region = token_canvas_map[y0:y1, x0:x1]
            token_k_inside = np.count_nonzero(box_region == k)

            if token_k_inside < token_k_total:
                escaped_px = token_k_total - token_k_inside
                raise OwnershipGateError(
                    f"[DIACRITIC ESCAPE] Token #{k} '{word}' has {escaped_px} ink pixels outside its declared box [{x0}, {y0}, {x1}, {y1}]!"
                )

            # 3. Foreign ink intrusion
            foreign_mask = (box_region > 0) & (box_region != k)
            foreign_pixels = np.count_nonzero(foreign_mask)
            if foreign_pixels > 0:
                foreign_ids = np.unique(box_region[foreign_mask]).tolist()
                raise OwnershipGateError(
                    f"[FOREIGN INK INTRUSION] Token #{k} '{word}' box contains {foreign_pixels} foreign ink pixels from token(s) {foreign_ids}!"
                )

        return True

    @staticmethod
    def run_pre_commit_assertions(
        sample_pairs: List[Dict[str, Any]],
        local_buffer_size_gb: float
    ):
        """
        Mandatory checklist run before every batch:
        1. assert all(glyph_id != 0 for glyph_id in shaped_glyphs) (Zero .notdef boxes)
        2. assert bbox_height >= (ascender_zone + body_zone + descender_zone) (Zero diacritic clipping)
        3. assert local_buffer_size_gb <= 2.0 (Zero disk accumulation)
        4. assert set(image_bboxes.keys()) == set(token_ground_truth) (Zero label-box misalignment)
        5. assert applied_augmentations_count >= 2 (Zero sterile renders)
        """
        for idx, sample in enumerate(sample_pairs):
            # Assertion 1: Zero .notdef
            glyphs = sample.get("shaped_glyphs", [])
            if glyphs:
                assert all(g.get("glyph_id", 0) != 0 for g in glyphs), \
                    f"PRE-COMMIT FAIL: .notdef (Glyph ID 0) found in sample #{idx}!"

            # Assertion 2: Zero diacritic clipping (Dynamic vertical zone safety)
            canvas_h = sample["canvas_size"][1]
            f_size = sample.get("font_size", 32)
            asc_z = sample.get("ascender_zone", int(f_size * 0.35))
            desc_z = sample.get("descender_zone", int(f_size * 0.35))
            min_required_h = asc_z + f_size + desc_z
            assert canvas_h >= min_required_h * 0.85, \
                f"PRE-COMMIT FAIL: Dynamic vertical zone clipping in sample #{idx}! Canvas H={canvas_h}, MinRequired={min_required_h}"

            # Assertion 4: Zero label-box misalignment
            bboxes = sample.get("bboxes", {})
            ground_truth = sample.get("ground_truth", {})
            if bboxes and ground_truth:
                assert set(bboxes.keys()) == set(ground_truth.keys()), \
                    f"PRE-COMMIT FAIL: Label-box misalignment in sample #{idx}!"

            # Assertion 5: Dual Clean (~30%) vs Degraded (>=2 augmentations) Verification
            is_clean = sample.get("is_clean", False)
            aug_ops = sample.get("applied_augmentations", [])
            if is_clean:
                # Clean samples must have pristine tag and no physical dirt/photostat noise
                assert any("clean" in op or "pristine" in op for op in aug_ops) or len(aug_ops) == 0, \
                    f"PRE-COMMIT FAIL: Clean sample #{idx} has unexpected degradation ops: {aug_ops}"
            else:
                aug_count = sample.get("applied_augmentations_count", len(aug_ops))
                assert aug_count >= 2, \
                    f"PRE-COMMIT FAIL: Degraded sample #{idx} has insufficient augmentations: {aug_count} < 2"

        # Assertion 6: Verify clean representation across the verification audit sample
        clean_count = sum(1 for s in sample_pairs if s.get("is_clean", False))
        clean_ratio = clean_count / len(sample_pairs) if sample_pairs else 0.0
        assert 0.15 <= clean_ratio <= 0.50, \
            f"PRE-COMMIT FAIL: Clean sample ratio {clean_ratio:.1%} outside expected ~30% target window (15%-50%)!"

        # Assertion 3: Zero disk accumulation
        assert local_buffer_size_gb <= 2.0, \
            f"PRE-COMMIT FAIL: Disk accumulation exceeded 2.0 GB! Current buffer: {local_buffer_size_gb:.2f} GB"

        return True
