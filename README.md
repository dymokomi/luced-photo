# luced-photo

A photo library and RAW editor written in Luce, where every photo goes through
a simulated film process. The window has five modes, a darkroom's rooms in
order: Library, Capture, Develop, Print and View. It looks like luced-2d: grey
and orange docked panes with square buttons. Camera RAWs come through
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

## Modes and recipes

Each photo goes through a film process, its **recipe**: the file, the camera
(a White Balance, the Exposure, and when wanted a Lens and a Filter), a Film
stock and its Development, then an output: a Telecine (scanned, graded, seen on
a display), a Release Print (printed on 2383 and projected), a Lightbox (a
slide), a Paper Print, or a Digital Intermediate. The Easel frames it.

The mode bar picks which stages Properties shows: Capture the camera's and the
film's, Develop the chemistry, Print everything after it (with the Output
menu), View the display rendering and the frame. Library shows the photos and
the Presets pane: the starts (Television, Cinema, Slide, Black & White and
others), your saved presets and the film looks of particular pictures. A click
gives one to the selected photos. A right-click on a photo copies its film
preset (everything but its own light and framing) to paste onto others.

## Where it is going

[docs/DESIGN.md](docs/DESIGN.md) has the plan. The develop pipeline lives in
[luce-develop](../luce-develop): scene-linear ACES AP1, Oklab color tools and the
ACES 2.0 view transform, with a GPU renderer for the viewer and a CPU path for
export.
