# Digestive asset integration (working branch)

This branch stages the digestive-system asset integration without changing `main`.

## Important format note

Human Atlas's `public/models/atlas.json` manifest points to browser-oriented binary geometry chunks. Those chunks are **not standalone GLB files** and should not be imported into Blender directly. To use individual Human Atlas meshes in this project, export/convert the selected meshes to GLB with a compatible exporter or use separately licensed GLB assets.

## Expected asset folder

Place downloadable, license-cleared GLB assets here (keep each source's attribution and license file alongside the model):

```
assets/anatomy/digestive/
  liver.glb
  large-intestine.glb
  mouth.glb                 # optional
  anal-canal.glb            # optional; only if a suitable licensed asset is found
```

The preview page at `digestive-assets-preview.html` attempts to load these files. Missing files are reported in the page instead of silently substituting a fake mesh.

## First-pass transform tuning

In the preview page, each asset has a transform preset (position, rotation and scale). These are initial staging values only; they must be tuned by viewing the real files together. Do not assume the presets are anatomically aligned until the loaded scene has been checked.

## Recommended workflow

1. Download the chosen GLB files and keep their source URLs, creators, licenses, and attribution text.
2. If using Human Atlas, export the needed named meshes to GLB; do not copy the Atlas viewer code wholesale.
3. Copy the files into the folder above.
4. Open `digestive-assets-preview.html` through a local web server or the project's hosting environment. ES modules and model fetches may not work when opening the file directly as `file://`.
5. Tune transforms until the organs look coherent. This is a visual educational model, not a clinical model.
6. Verify the food path visually from mouth through esophagus, stomach, small intestine, large intestine, rectum and anal canal.
7. Before release, include the required attribution for each model and confirm each license permits the intended redistribution.

## Licensing reminders

- Human Atlas app code has an MIT license; the underlying BodyParts3D data is attributed separately under CC BY 4.0. Follow the repository's `public/ATTRIBUTION.md` and BodyParts3D license terms for exported anatomy.
- HRA reference objects are generally listed under CC BY 4.0; retain entry-specific attribution.
- Check each NIH 3D or Sketchfab entry's own license before adding it. A browser preview being available does not itself grant download or reuse permission.
