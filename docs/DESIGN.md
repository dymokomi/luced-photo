# luced-photo design

luced-photo is a photo library and RAW editor. It is meant to be minimal and still
powerful: Capture One's results, an interface friendlier than Capture One's, and more
depth than Apple Photos. The window has three panes:

| Library | Viewer | Properties |
| --- | --- | --- |
| a grid of thumbnails whose size scales, with filters, albums, ratings and flags | the current photo with its develop applied, with zoom, before/after and a histogram | one long scrolling column of correction sections |

The owner's decisions (2026-10-05):
- **Managed library.** Import copies the originals into a library bundle.
- **luce-develop** is a new package that holds the develop engine.
- The default view transform is **ACES 2.0**, implemented in luce-color, with a neutral option beside it.
- **luce-exif** is a new package that reads metadata.

## 1. Packages

```
luced-photo (Luce app) ──► luce-ui ─────────► luce-gpu, luce-color
        │                    ▲  new widgets: ThumbnailGrid, Histogram, Levels,
        │                    │  GradientSlider, HueMixer, ToneWheels, Rating, ...
        ├──► luce-develop (Base) ──► luce-raw, luce-jpeg/png/tiff/exr/heic, luce-color, luce-gpu
        ├──► luce-exif (Base)
        └──► luce-prism (catalog)
```

- **luce-color** owns every color formula: the ACES 2.0 Output Transform (Hellwig
  2022 JMh, Daniele tonescale, chroma compression, gamut compression), the Standard
  tone scale, the Planckian locus and CCT, and Oklab. It has no pixel loops.
- **luce-develop** owns the develop: `Settings` (every parameter, its defaults and
  its text form), `Source` (decoding any supported file to a scene-linear float
  image on worker threads), `Renderer` (GPU passes for the viewer), `process` (the
  same operations as Base CPU kernels, for export and thumbnails), and LUT baking.
  Its hot paths are Base ([hot paths in Base]); nothing in it knows about the UI.
- **luce-exif** reads EXIF, TIFF and XMP metadata from TIFF-based raws, DNG, TIFF,
  JPEG APP1, RAF, CR3 and HEIC. It exposes capture time, camera, lens, exposure,
  GPS, orientation, rating and label.
- **luce-ui** gets the new widgets. They are general, and luced-2d will use them for
  Curves, Levels and Camera Raw.
- **luced-photo** holds the app logic in Luce: the catalog, import, panes,
  commands, settings, export and undo.

## 2. Color pipeline

Everything between decode and the view transform is **scene-referred, linear,
ACES AP1 primaries** (ACEScg). Oklab and OkLCh serve the hue, saturation and
lightness tools. The stages, in order:

```
RAW ─ luce-raw (camera=true): black/white levels, as-shot WB, demosaic (AHD/Markesteijn)
    → camera RGB, linear, white-balanced as shot
  1  white balance    diag(new / as-shot multipliers) in camera space
  2  camera matrix    camera → XYZ(D50) → AP1, interpolated for the new white (DNG rules)
  3  lens             vignetting correction (radial gain), later distortion and CA
  4  exposure         × 2^stops
  5  tone (scene)     highlights/shadows/whites/blacks against a blurred-luminance mask;
                      contrast about 18 % grey in log2 space
  6  color (Oklab)    white-point-preserving saturation and vibrance; HSL mixer on 8 hue
                      bands; color grading (shadows/midtones/highlights wheels + global);
                      selective color; black & white (hue-weighted luminance mixer + tint)
  7  view transform   ACES 2.0 SDR (100 nits, Rec.709/P3-D65 limited) | Standard | none
                      → display-referred 0..1
  8  display tools    levels; curves (RGB, R, G, B, luma)
  9  effects          creative vignette (post-crop); grain
 10  encode           sRGB or Display P3 transfer for the monitor, or the export space
```

Non-RAW sources (JPEG, PNG, TIFF, HEIC, EXR) enter at stage 3. A display-referred
image is linearized into AP1. Its "as shot" white balance is neutral, and
temperature/tint act as a relative shift.

**Why camera RGB.** luce-raw's built-in output applies the camera matrix into
sRGB, and it clips negative values. That clipping throws away exactly the
saturated colors (deep blue skies, neon, flowers) that a wide working space keeps.
luce-develop asks luce-raw for camera RGB and for the camera's matrix, so it needs
a small luce-raw addition: `raw.camera_matrix(data, temperature, tint)`.

**White balance without re-demosaicing.** The demosaic runs once, at the as-shot
balance. A new white is the ratio of multipliers applied in camera space,
followed by the matrix interpolated for that white. Lightroom and RawTherapee
both work this way for interactive edits.

**Highlights.** luce-raw clips at the sensor's white. Highlight reconstruction,
which blends clipped channels toward luminance, is a later luce-raw improvement.
It is not part of the first develop.

## 3. GPU renderer

The viewer runs on the GPU and re-renders on every slider move.

- The source texture is RGBA16F camera RGB at a level of an image pyramid: the
  fit level for the full view, full resolution from 100 %, built on the CPU.
- Parameters: luce-gpu gives a draw 48 bytes of parameters, too few for about
  80 settings. The renderer therefore writes all settings into a **parameter
  texture** (RGBA32F, 64×1). Curves, levels and the HSL mixer bake into a
  **LUT texture** of 1D rows. The view transform bakes on the CPU into a
  **3D LUT** of 65³ entries, tiled into a 2D texture, sampled in a log2 shaper
  space over −12..+12 stops, with trilinear filtering done in the shader. This is
  how OCIO runs ACES on the GPU. The CPU path has the exact transform and uses
  it for export.
- Passes:
  1. Luminance for the local-tone mask, downsampled.
  2. Separable blur, two passes.
  3. Develop: stages 1–9.
  4. Draw into the view rectangle with zoom and pan.

  Before/after reuses pass 4 with a split position.
- The histogram is computed on the CPU from a readback of a small (256²) render.
  This runs after edits settle, not on every frame.

The CPU path (`process`) implements the same stages in Base, without the LUT
shortcut for the view transform. Tests render reference images both ways and
require a mean ΔE2000 below 0.5.

## 4. Library

```
~/Pictures/Luced Photo.library/
    library.prism          catalog (luce-prism Store, WAL)
    originals/2026/10/05/DSCF1234.RAF
    cache/thumbs/<id>.jpg  512 px long edge, regenerated from edits (luce-jpeg)
    cache/previews/<id>.jpg 2048 px, for the fast first view
```

Catalog identities (luce-prism):

| identity | element | properties |
| --- | --- | --- |
| `photos` | `/p<id>` | path, name, format, bytes, sha256, imported, captured, offset, width, height, orientation, make, model, lens, focal, aperture, shutter, iso, exposure_bias, gps, rating, flag, label, keywords, edited |
| `edits` | `/p<id>` | one property per develop setting that differs from the default |
| `presets` | `/r<id>` | id, name, settings (text form, without framing); `/state` next id |
| `albums` | `/a<id>` | name, order, members (int list) |
| `library` | `/state` | schema version, last import, grid size |

- **Import** runs on a Base worker thread, like luced-message's engines. For each
  file it hashes the contents (SHA-256, which also catches duplicates), copies the
  file into `originals/YYYY/MM/DD/` by capture date, reads the EXIF, and extracts
  the embedded preview or decodes a small image. Then it writes the thumbnail and
  commits a batch of rows. The window polls the worker's events through a timer.
- **Thumbnails** come from the embedded JPEG (luce-raw `preview`, under 1 ms)
  until the photo has edits. After an edit, the CPU path renders a 512 px
  thumbnail in the background.
- **Cloud sync** comes later. The bundle layout and content hashes make it a
  matter of syncing files plus prism's journal.

## 5. Interface

The styling is luced's: grey and orange square geometry, toolbars at the bottom
of panes, docked panes (DStack), and a command per action shared by menus,
shortcuts and the command palette.

- **Library pane.** A sidebar lists All Photos, Recent Import, Flagged, Rejected,
  Albums and Trash. Below it is a filter bar for the minimum rating, flag, label,
  camera and text. The ThumbnailGrid has a size slider in the pane's bottom bar
  and supports multi-select. Keys: 0–5 set the rating, P/X/U set or clear the
  flag, 6–9 set the label.
- **Viewer.** Fit or 100 % (space or Z), scroll to zoom, a before/after split
  (Y), a clipping overlay (J), and a film strip along the bottom showing the
  library's current filter.
- **Properties pane.** Collapsible sections (Accordion), each with a reset
  button and an on/off toggle:
  1. Histogram + capture info
  2. White Balance: GradientSlider for temperature (blue→amber) and tint
     (green→magenta), a picker, and presets (As Shot, Auto, Daylight…)
  3. Exposure & Tone: exposure, contrast, highlights, shadows, whites, blacks
  4. Curves: CurveEditor with RGB/R/G/B/Luma tabs
  5. Levels: a Levels widget (histogram + black/grey/white input handles + output range)
  6. Color: vibrance, saturation, and the HueMixer (8 hue chips × hue/sat/lum)
  7. Color Grading: ToneWheels (shadows/midtones/highlights/global) + balance and blending
  8. Selective Color: chips for reds…blacks, CMYK sliders
  9. Black & White: on/off, the hue-weight mixer, tint
  10. Lens: vignetting correction (amount, midpoint)
  11. Effects: vignette (amount, midpoint, roundness, feather), grain
  12. Detail: sharpening, noise reduction (later milestone)
  13. View: the view transform (ACES 2.0 / Standard / Linear) and the display space
- **Edits** are non-destructive and stored in the catalog. Every change is an
  undo step, with drags coalesced. Copy/paste settings, sync to the selection,
  and reset are supported. None of them carries framing (perspective, crop,
  guides) from one photo to another.
- **Presets pane**, below the Library: named settings kept in the catalog, so
  they travel with the library. A click stacks the preset on the selected
  photos, as Capture One's styles do: the values it holds replace the photo's,
  and the rest stay. Each photo changed gets an undo step. The footer saves the
  developed photo's settings as a new preset, saves them over the chosen one,
  renames it and deletes it. A right-click on a row offers the same.
- **Export** runs the CPU path to JPEG, TIFF 16-bit or PNG, in sRGB, Display P3 or
  Rec.2020, with a resize option. It runs on a worker, with progress shown in the
  status line.

## 6. Milestones

1. **Library** (this first). luce-exif 0.1; the luced-photo skeleton with the
   library bundle, prism catalog and threaded import (copy, hash, EXIF, embedded
   previews); the ThumbnailGrid; a viewer showing the preview; metadata in
   Properties; ratings and flags.
2. **Develop v1.** luce-raw `camera_matrix`; luce-develop with Source, Settings
   and a Renderer covering WB, exposure, contrast, H/S/W/B, saturation/vibrance
   and Standard tone. The viewer renders RAWs, edits persist, and edited
   thumbnails regenerate.
3. **ACES 2.0** in luce-color, with LUT baking and the View section.
4. **Tools.** Histogram, Curves, Levels, HueMixer, color grading, selective
   color, B&W, lens and creative vignette, grain, and the luce-ui widgets for
   each.
5. **Export.** The CPU path, GPU/CPU parity tests, and the export dialog.
6. **Workflow.** Crop/straighten, albums, filters/search, copy/paste/sync
   settings, sharpening and noise reduction, Windows/Linux checks.

[hot paths in Base]: ../../luce-base/docs/language/base.md
