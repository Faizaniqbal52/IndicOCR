# IndicPixel Master Augmentation Registry

This registry provides a complete, itemized record of all **54 augmentations** active across the IndicPixel OCR synthesis pipeline, spanning procedural paper substrates, physical degradation operators, ancient scripture decay cycles, geometric sensor transformations, and kinematic handwriting deformations.

---

## Category A: Procedural Document Substrates (Paper Physics)
1. **Clean White:** Pristine digital scan baseline (`#FFFFFF`, noise $\sigma \le 0.3$).
2. **Aged Paper:** Warm honey-tan base (`#EFE0BD`) with multi-octave organic Perlin cloud aging.
3. **Book Page:** Paperback novel off-white (`#F5EFE4`) with fine cellulose wood pulp fibers.
4. **Newspaper:** Newsprint grey-buff (`#DAD8D0`) with coarse pulp speckles & double-sided print bleed-through ghosting.
5. **Ruled Notebook:** School exercise notebook (`#FAF8EE`) with horizontal slate-blue ruling lines (26px) and red margin.
6. **Parchment:** Antique calfskin vellum (`#EBD7A2`) with multi-octave amber and ochre cloud mottling.
7. **Weathered:** Damp decayed grey-beige (`#C6C2B8`) with soft moisture clouds, mildew patina, and dust.
8. **Coffee Stained:** Warm paper (`#F4ECDA`) with organic capillary coffee ring stains (dark perimeter `#9B693A`) and splatter droplets.
9. **Old Book:** Deep sepia paper (`#ECDEB9`) with dark edge burning vignette falloff and scattered foxing spots.
10. **Recycled Kraft:** Unbleached cardboard substrate (`#D4C6B2`) with embedded dark brown and grey cellulose wood fibers.
11. **Cream:** Smooth, elegant butter-cream ledger paper (`#FDF6D8`) with subtle paper texture.
12. **Ivory:** Soft pale ivory formal stationery (`#FCFAEE`) with delicate micro-grain.

---

## Category B: Physical Document Degradation Operators (Indian Realism)
13. **Ink Bleed:** Capillary expansion of wet ink along porous paper fibers.
14. **Toner Erosion:** Micro-speckle toner flaking and dry typewriter ribbon stroke erosion.
15. **Non-Uniform Shadow Gradient:** Multi-directional linear lighting falloff simulating smartphone capture and overhead tube-lights.
16. **Xerox Photostat Clipping:** High-contrast binarization thresholding with dense toner pepper dust.
17. **Optical / Defocus Blur:** Gaussian lens softness ($\sigma = 0.55$) simulating slight focal defocus without erasing matras.
18. **Handheld Motion Blur:** Directional camera tremor blur conditioned on stroke thickness to protect thin Indic matras.
19. **Mobile JPEG Quantization:** 8×8 DCT block compression artifacts simulating WhatsApp / camera uploads ($q \in [35, 75]$).
20. **3D Ridge Crease / Pocket Fold:** Directional ridge lighting with adjacent highlight and shadow gradients.
21. **3D Diagonal Fold / Paper Crease:** Diagonal page folding with exponential illumination gradient.
22. **Aged Patina & Stain:** Sepia color balance shift combined with localized moisture / tea stain halos.
23. **Blue Carbon Copy Dye:** Authentic Indian bureaucratic blue carbon paper duplicate (*नीला कार्बन पर्चा*) with indigo-violet shift and micro-pressure fuzz.
24. **Scanner Glass Platen Border:** Photocopy glass margin bleed and dark scanner lid shadow on page borders.
25. **Subtle Skew Jitter:** Micro-rotation ($-3^\circ$ to $+3^\circ$) simulating realistic document placement on a flatbed or desk.
26. **Official Bureaucratic Ink Stamp:** Semi-transparent official government seal / revenue stamps in purple, red, deep blue, or green.

---

## Category C: Ancient Scripture & Historical Manuscript Cycles
27. **Antique Folio Sepia Wash (Cycle 1):** Deep antique amber/sepia tonal wash across the manuscript base.
28. **Moisture Damp Patches (Cycle 1):** Broad circular moisture blotches softening ink contrast.
29. **Talapatra Palm-Leaf Striations (Cycle 2):** Horizontal fibrous ribs and grain characteristic of dried palm-leaf manuscripts.
30. **Insect Wormhole Boreholes (Cycle 2):** Organic void perforations cutting through text with dark necrotic borders.
31. **Ink Craquelure / Micro-Fissuring (Cycle 2):** Surface micro-crack networks flaking dried carbon ink.
32. **Capillary Water Tidemarks (Cycle 2):** Multi-layered fluid tide lines with concentrated mineral perimeter deposition.
33. **Iron Gall Acid Corrosion (Cycle 3):** Corrosive rust-brown halos bleeding into cellulose fibers with hollowed stroke centers.
34. **Temple Lamp Soot / Smoke (Cycle 3):** Greasy charcoal smoke gradients across corners and edges from decades of oil lamps (*दीया*).
35. **Sacred Vermilion (*Sindoor / Kumkum*) Rubs (Cycle 3):** Ceremonial orange-red powder smudges and finger daubs.
36. **Fungal Mildew Spore Colonies (Cycle 3):** Clustered micro-colonies of dark fungal foxing across moisture zones.
37. **Brittle Chipped / Frayed Margins (Cycle 3):** Jagged, decayed page edges simulating ancient brittle folios.

---

## Category D: Geometric, Optical & Sensor Transformations (SynthOCR-Gen Adapted)
38. **Planar Rotation:** Rigid affine rotation from $-15^\circ$ to $+15^\circ$ with bicubic boundary interpolation.
39. **Horizontal Shear / Skew:** Affine slanting ($s_x = \tan(5^\circ)$) simulating scanner feeding skew and italicization.
40. **Keystone Perspective Tilt:** Trapezoidal perspective transformation simulating handheld camera angles.
41. **Off-Axis Perspective Homography:** 3D perspective warp from oblique smartphone photography angles.
42. **Overexposure / Brightness Scaling:** $+24\%$ linear luminance boost simulating washed-out direct lighting.
43. **Underexposure / Darkness Scaling:** $-24\%$ luminance reduction simulating dim ambient room lighting.
44. **High-Contrast Hard Thresholding:** $+41\%$ contrast expansion simulating harsh photostat binarization.
45. **Low-Contrast Faded Washout:** $-21\%$ contrast compression simulating faded vintage ribbons.
46. **Additive Gaussian Sensor Noise:** Zero-mean normal pixel noise ($\sigma_n = 16$) simulating high-ISO digital cameras.
47. **Salt-and-Pepper Dust Noise:** Random impulse noise simulating surface dust particles and platen lint.
48. **Faded / Ghostly Print:** Low-opacity ($40\%$) ink dilution simulating ribbon exhaustion and faint pencil marks.

---

## Category E: Kinematic Human Handwriting & Freestyle Deformations
49. **Elastic Mesh Deformation:** Non-linear grid remap (Simard et al.) simulating biomechanical finger and wrist muscle fluctuations.
50. **Kinematic Slant & Shear:** Variable forward and backward handwriting slant angles ($-15^\circ$ to $+15^\circ$).
51. **Stroke Pressure Variation:** Morphological stroke width modulation along the pen trajectory simulating pen tip pressure.
52. **Baseline Waviness & Drift:** Low-frequency sinusoidal trajectory drift simulating handwriting slant and hand tremor.
53. **Pen Lift / Ink Discontinuity:** Micro-breaks in continuous strokes simulating fast pen lifts and ballpoint skipping.
54. **Multi-Persona Kinematic Profiling:** 6 distinct human writing profiles with tailored slant, speed, spacing, and pen styles.
