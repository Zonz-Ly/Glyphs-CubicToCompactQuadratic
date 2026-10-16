# Compact Quadratic Curves 1.0

[English](README.en.md) · [简体中文](README.sc.md) · [繁體中文](README.tc.md)

By Zonz. Converts cubic Bézier curves to quadratic outlines with fewer control points in Glyphs 3 with Python 3. Supports Intel and Apple Silicon, with no additional Python dependency.

## Installation and use

Extract the archive, double-click CubicToQuadratic.glyphsPlugin, replace the previous version and restart Glyphs.

Choose Convert to Compact Quadratic Curves in the Path menu, or press Shift+Command+2. Hold Option to reveal settings, or press Shift+Option+Command+2.

In Edit view, select both cubic controls or both endpoints to convert particular curves. Without selected nodes, the current glyph is processed. In Font view, selected glyphs are processed.

Compatible masters and relevant special layers are synchronized with matching node structures. Components retain their references, and their base glyphs may also be converted. Selected backup or background layers are processed independently without modifying other layers or component bases.

## Settings

Valid changes are saved immediately. Use the arrow keys to adjust numbers and hold Shift for faster changes. Tab moves between settings; Space toggles checkboxes.

| Setting | Default | Description |
| --- | --- | --- |
| Outline fitting tolerance | 1 (units at 1000 UPM) | Controls how far the converted outline may deviate from the original. Smaller values favor fidelity; larger values make it easier to reduce control points. |
| Maximum control points | 3 | Limits the control count per converted result and accepts any positive integer. A lower cap favors simpler outlines but may reduce fitting accuracy. |
| Centering range for controls near the chord | 7 (units at 1000 UPM) | When a result has one control near the endpoint chord, tries moving it toward the center while limiting outline changes. Set to 0 to disable. |
| Angle tolerance for smooth joins | 5° | Determines whether adjacent curves count as smoothly joined, for tangent preservation and merging. Larger values allow greater differences in original directions. |
| Maintain smooth straight-line joins | On | Preserves the tangent direction where a curve originally joins a straight line smoothly, helping prevent a kink after conversion. |
| Maintain smooth curve joins | On | Preserves smoothness at retained curve joins using the mean of the original tangent directions, including when merging is disabled or unsuccessful. |
| Try merging smoothly joined curves | On | Tries fitting adjacent smooth curves together to remove original join points. If merging cannot stay within tolerance, retains the joins and converts smaller groups. |
| Insert points between controls | Off | Adds explicit nodes between neighboring quadratic controls for direct selection and editing. When disabled, the joins use implicit midpoints. |
| Fit using integer coordinates | On | Fits control points directly on the integer grid while considering outline shape and join directions. Original endpoint coordinates stay fixed. |

Distances scale automatically with the font UPM, so settings use a consistent scale across fonts.

## Notes

No control counts beyond the configured maximum are tried, so ordinary conversion may exceed the fitting tolerance. Merging stays within tolerance and does not cross lines, existing quadratics, selection boundaries or hint-protected joins.

Original endpoint coordinates remain fixed. Incompatible glyphs or conversions with unsatisfiable constraints are not forcibly written.

Conversion supports cancellation and one-step undo. The interface follows Glyphs’ language, supporting English, Simplified and Traditional Chinese, Japanese, Korean, German, French, Spanish, Italian, Portuguese and Russian.

ConvertToCompactQuadratic.py is a synchronous alternative whose top-level constants are independent of plugin settings. Sources are in development. See THIRD-PARTY.md and GlyphsSDK-LICENSE.txt for licensing.
