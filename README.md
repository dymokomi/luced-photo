# luced-photo

A photo library and RAW editor written in Luce. The window has three panes: a
grid of your photos whose thumbnails scale, a viewer for the current photo, and
one long column of properties and corrections. It looks like luced-2d: grey and
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

## Where it is going

[docs/DESIGN.md](docs/DESIGN.md) has the plan. The develop pipeline lives in
[luce-develop](../luce-develop): scene-linear ACES AP1, Oklab color tools and the
ACES 2.0 view transform, with a GPU renderer for the viewer and a CPU path for
export.
