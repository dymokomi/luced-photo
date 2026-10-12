# The view: showing light on a display

A display cannot show the light a scan holds. Scene light ranges over many stops; a screen has a fixed white and a limited range. A view transform decides how one maps to the other, rolling off highlights, keeping midtones and choosing how saturated colors are shown.

ACES 2.0 is the Academy Color Encoding System's current output transform, used across the film industry, with highlights that desaturate gracefully as they approach white. Standard is a plainer filmic curve. Linear shows the values as they are, clipped.

In the cinema chain this node is replaced by Print and Project, which are their own view transform: the print film's curve and the theater.
