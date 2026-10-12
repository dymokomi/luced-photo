# The file: light as the camera measured it

A raw file holds what each photosite of the sensor counted: photons, nearly in proportion to the light that fell on it. Nothing has been decided yet. There is no white balance, no contrast curve and no color rendering, only a record of the scene's light behind a mosaic of red, green and blue filters.

That is why the recipe starts here. Developing the raw recovers the scene's light as numbers that still add up the way light does: twice the light is twice the value. Everything after this node treats those numbers as light falling on a lens and then on film, just as the real scene once did.

A JPEG is different. It has already been through a camera's own rendering, so it is turned back into light first (the inverse of a display transform), which works well for textures and screen content but cannot bring back what the camera threw away.
