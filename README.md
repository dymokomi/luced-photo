# luced-photo

A photo library and RAW editor written in Luce. The window has three panes: a
grid of your photos whose thumbnails scale, a viewer for the current photo, and
the photo's recipe as a graph of film stages, and the picked stage's controls. It looks like luced-2d: grey and
orange docked panes with square buttons. Camera RAWs come through
[luce-raw](https://github.com/dymokomi/luce-raw), which reads Fujifilm X-Trans and
Bayer RAFs, Leica DNGs and most other cameras' raws. JPEG, PNG, TIFF and HEIC
files work too.

```sh
luc run --release                         # opens ~/Pictures/Luced Photo.library
luc run --release -- --library DIR --import ~/Pictures/card
```

## The library

The library is managed. Import copies each photo into the library bundle and
files it by capture date, so cloud sync can later move a single folder:

```
Luced Photo.library/
    library.prism            the catalog (luce-prism)
    originals/YYYY/MM/DD/    the imported files
    cache/thumbs/<id>.jpg    512 px grid thumbnails
    cache/previews/<id>.jpg  2048 px viewer previews
```

- **Importing.** Use Library › Import Photos… (Cmd/Ctrl-Shift-I), or drop files
  and folders on the grid. The import runs on its own thread. A photo whose
  SHA-256 the library already holds is skipped. Thumbnails show up while the
  import is still running.
- **Rating and flagging.** Keys 0–5 set the stars, P picks, X rejects and U
  clears the flag. Keys 6–9 set a red, yellow, green or blue label. Each key acts
  on the whole selection.
- **Browsing.** Command-scroll or pinch the grid, or use the slider below it, to
  change the thumbnail size. Arrows move the selection. The Filter menu shows
  picked, rejected or rated photos.

## Recipes

Each photo goes through a film process, its **recipe**: a small graph of stages
in the Recipe pane beside the viewer, read top to bottom as luced-3d's network.
The File (the photo picked in the library) gives light, which passes White
Balance, Exposure, and, when added, a Lens and a Filter, then exposes a Film
stock, the film is Developed, and then Scanned, Graded and Viewed, or Printed on
2383 and Projected, or shown on a Lightbox as a slide; the Easel frames it.
Wires take the color of what flows on them, and only matching media connect.
Every control lives in a stage: pick one and Properties shows its controls.
Boxes are colored by family (source, camera, chemistry, presentation); the left
strip on a box bypasses it (B), the right one makes it the displayed stage (D).
Tab or a right click adds stages and starts from a mode; Delete removes one; Alt
on an input or a Y-drag across wires cuts them. The Recipes pane lists the modes
(Television, Cinema, Slide, Black & White), your saved recipes and the film
looks; a click applies one to the selected photos.
[docs/FILM-GRAPH.md](docs/FILM-GRAPH.md) has the design.

## Where it is going

[docs/DESIGN.md](docs/DESIGN.md) has the plan. The develop pipeline lives in
[luce-develop](../luce-develop): scene-linear ACES AP1, Oklab color tools and the
ACES 2.0 view transform, with a GPU renderer for the viewer and a CPU path for
export.
