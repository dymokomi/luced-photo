# The film graph

luced-photo develops a photo the way film was: the camera's light is exposed on a
film stock, developed in a chemistry for a time, and then scanned, printed or
projected. Each photo carries a **recipe**, a small graph of those stages, and
the photographer edits it as nodes, Houdini-style, as in luced-3d. Recipes come
in **modes** (television, cinema, slide, black and white, darkroom) that start a
photo from a sensible graph; the film looks (Friends and others) are values
set on a Television recipe.

## Nodes and what flows between them

Wires are typed, so a graph can only say something physical. Five kinds of
image flow:

| Type | What it is | Engine form |
|---|---|---|
| **Light** | light from the scene, before film: radiometric, scene-linear | AP1 scene light |
| **Exposure** | a latent image: each layer's exposure on a stock | layer exposures (film passes, stage 0–2) |
| **Film** | processed film: a negative or a positive, its dye or silver | dye amounts / densities |
| **Image** | a scan: scene light again, for grading | AP1 scene light |
| **Display** | light from a print, a screen or a lightbox, as seen | display-linear light |

The nodes, with their properties (each node's are what the Properties pane
shows when it is selected):

| Node | In → out | Properties |
|---|---|---|
| **File** | → Light | the photo picked in the library, as its raw recorded the light |
| **White Balance** | Light → Light | the light on set: temperature and tint (as shot by default) |
| **Exposure** | Light → Light | stops over or under the camera's exposure |
| **Lens** | Light → Light | vignetting and its falloff; later diffusion |
| **Filter** | Light → Light | a light-balancing filter (Matched, None, 85); a black-and-white color filter (8, 21, 25, 11, 47) |
| **Film** | Light → Exposure | stock, format (frame size, which sets grain and sharpness in pixels), grain, halation, interimage |
| **Develop** | Exposure → Film | the process and its chemistry (ECN-2, C-41, E-6, D-76, Microfine…), time and temperature, push and pull |
| **Scan** | Film → Image | scanner or telecine: printing-density or Status M read, timing (warmth, tint), contrast, black |
| **Grade** | Image → Image | the colorist's tools: tone, color, color mixer, wheels, curves, levels, black and white |
| **Print** | Film → Film | contact or enlarged (the enlargement sets the negative's grain and softness on the print); printer lights or filtration; the print material: Vision 2383, color paper, black-and-white paper and grade |
| **Project** | Film → Display | a projector (xenon arc, flare) for print film |
| **Lightbox** | Film → Display | a slide on a D50 light table |
| **View** | Image → Display | a display rendering for a scan: ACES 2.0, Standard, Linear |
| **Easel** | Display → Display | the frame: crop, perspective, and burning in the edges (vignette) |

White Balance, Exposure, Lens and Filter each scale the light, so they chain in
any order to the same result. Every control lives in a stage; nothing is set
outside the graph.

Stages are colored by their family: the source (File), the camera (White
Balance, Exposure, Lens, Filter), the chemistry (Film, Develop) and the
presentation (Scan, Grade, Print, Project, Lightbox, View, Easel). Wires are
colored by what flows on them.

A recipe has one output (the node with the display flag), which the viewer and
exports show. Bypassing a node passes its input through when the types allow
(a bypassed Grade or Lens; never a Film).

## Modes

| Mode | Graph |
|---|---|
| Television | File → White Balance → Exposure → Film (tungsten negative) → Develop (ECN-2) → Scan (telecine) → Grade → View → Easel |
| Cinema | File → White Balance → Exposure → Film → Develop (ECN-2) → Print (2383) → Project → Easel |
| Slide | File → White Balance → Exposure → Film (Velvia) → Develop (E-6) → Lightbox → Easel |
| Black & white | File → Exposure → Filter (color filter) → Film (Acros) → Develop (D-76) → Scan → Grade → View → Easel |
| Darkroom (next) | File → Exposure → Filter → Film (Acros) → Develop (D-76) → Print (paper, contact or enlarged) → Easel |

## The engine

luce-develop keeps doing the work. A recipe compiles to it:

1. **Now:** a valid chain maps onto luce-develop's settings (each node owns its
   group of parameters) and its output mode (scan → view, print → projection,
   slide → lightbox). Today's film passes, scan, print and view stay as they are,
   so GPU and CPU still agree.
2. **Next, in luce-develop:** the slide viewed directly on its lightbox as
   display light (no round trip through the ACES inverse); printer lights;
   development by chemistry and time (Acros' D-76 4, 7 and 10 minutes are
   already traced; push and pull); contact and enlarged prints; black-and-white
   and color paper (their datasheets); cross-processing (E-6 film in C-41).

## The graph editor

luced-photo owns its node editor, as luced-3d owns its own (taken from luced-3d's
network: its view, wires, inspector binding and transactions), shaped for film:

- **Model** (luce-develop's `recipe.lucb`, edited through `Look`): nodes (kind, position, bypass, the display flag) and
  their wires; connect with a type check and a cycle check. One node of each
  kind per recipe, so each node owns its kind's develop parameters outright;
  branches are fine (a negative both scanned and printed), and the display flag
  picks which one the viewer shows.
- **Kinds:** each stage's input and output types, description and develop
  sections come from luce-develop (`recipe.stage_*`).
- **View** (`recipe_view.luc`, `recipe_pane.luc`): a Painter widget drawn as
  luced-3d's network (its nodes, reading top to bottom), with typed, colored wires, pan and zoom, drag to connect, Alt and
  Y-drag to cut, delete, Tab or a right click to add a stage or start from a
  mode.
- **Properties:** the selected node's sections of the develop controls, under a
  header with its name, kind and flags.

## Saving and the engine

A photo's catalog record keeps one settings text, as before; the recipe is part
of it (`recipe=`, only when it differs from Television), and every node's values
stay in it, so a bypassed node keeps its settings. The engine compiles it when
it renders (`settings.compile`): the values of the stages on the path to the
displayed one, the rest at their defaults, and the engine's mode set by the path
(a Film stage turns film on; Print and Project choose the 2383 print view; a
Lightbox a slide; a View its display rendering). Thumbnails, previews and
exports read the settings, as they always have.

## In luced-photo

- The **Recipe** pane (beside the viewer) shows the selected photo's recipe;
  its display flag picks what the viewer shows.
- **Properties** shows the photo's facts and the selected node's properties.
- **Recipes** lists the modes, the saved recipes and the film looks;
  a click applies one to the selected photos.
- Undo and redo keep both, per photo, as today.
