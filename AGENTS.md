# AGENTS.md

## 1. Project Overview

This project is a capstone website titled **Traditional Diet vs. Modern Diet**. Its goal is to create an interactive, scientifically grounded educational experience that helps users understand the digestive system and explore how different foods are processed by the body.

The intended experience is a polished, modern science museum, with interactive 3D anatomy as a central feature.

### Current Priorities

1. Ensure the 3D digestive anatomy model loads and displays correctly.
2. Develop the core digestive-system interactions.
3. Implement the food journey and digestion timeline.
4. Ensure the website remains reliable and suitable for GitHub Pages deployment.

Do not begin a broad website redesign while core functionality is still being developed.

## 2. General Development Rules

- Inspect the existing code, project structure, dependencies, and relevant installed skills before making changes.
- Understand how the existing implementation works before modifying it.
- Preserve working functionality unless a change is necessary and approved.
- Prefer small, focused changes over rewriting entire files or rebuilding existing features.
- Do not introduce a new framework, major dependency, or alternative architecture without approval.
- Ask for approval before making significant structural changes or implementing features that substantially expand the project's scope.
- Never delete, overwrite, or replace important project files or 3D assets without permission.
- Avoid unnecessary duplication of code, styles, assets, and functionality.
- Keep code readable and maintainable so future development can build on the existing implementation.
- After completing a task, report the files changed, what was implemented, how it was tested, and any remaining limitations.
- If a requirement cannot be met because of a model, browser, or technical limitation, explain the limitation rather than introducing an unreliable workaround.

## 3. Project Structure and File Management

Follow the existing project organization:

- `index.html`: Website entry point.
- `museum.html`: Main science museum page and navigation.
- `Codes/`: Active website pages and related code.
- `Assets_3D/`: 3D models and other required 3D assets.
- `Archive/`: Older or inactive versions retained for reference.
- `AGENTS.md`: Project requirements and development instructions.

### File Management Rules

- Keep active website files separate from archived versions.
- Do not restore archived pages to active navigation unless explicitly requested.
- Do not remove files simply because they appear duplicated. Inspect their purpose and references first.
- Keep original 3D models and intermediate optimization files intact unless permission is given to remove them.
- Update relative paths when moving files, and verify that references still work.
- Do not create unnecessary backup copies or additional versions without a clear reason.

## 4. 3D Anatomy Model Requirements

The primary 3D exhibit uses a GLB anatomy model.

### Model Loading

- Use the existing compressed model at `Assets_3D/Anatomy_scene_draco.glb` for the active exhibit.
- Use Three.js and the appropriate GLTF and Draco loaders.
- Keep the Draco decoder configuration compatible with the installed Three.js version.
- Preserve the existing model's anatomy, materials, textures, and proportions.
- Do not replace the model with procedural anatomy, placeholder geometry, or a different model without approval.
- Keep model loading compatible with relative paths and GitHub Pages.
- Provide a clear loading state, loading progress where practical, and useful error handling.

### Model Display and Controls

- Check model scale, orientation, framing, camera position, and lighting.
- Ensure the anatomy is positioned appropriately within the viewport.
- Preserve working orbit, zoom, pan, front-view, side-view, reset, and fit controls.
- Keep the exhibit usable on different screen sizes.
- Avoid changes that noticeably reduce anatomical detail or visual quality.
- Diagnose model-display problems before making unrelated visual changes.

### Performance

- Prefer the compressed GLB for the active website.
- Avoid loading the same large model multiple times unnecessarily.
- Keep browser performance in mind when implementing animation, camera movement, and interactions.
- Do not make additional compression or asset changes that could compromise model appearance without testing the result.

## 5. Interactive Food Journey and Digestion

The exhibit should eventually allow users to select individual foods and explore their journey through the digestive system.

### Core Journey

The intended route is:

1. Mouth
2. Esophagus
3. Stomach
4. Small intestine
5. Large intestine

The implementation must follow the actual anatomy and spatial arrangement of the loaded model as closely as practical.

### Interaction Requirements

- Allow users to select or drag individual foods into the exhibit.
- Show the food moving through the digestive tract in a way that is visually understandable.
- Use appropriate camera views or guided focus to help users follow the journey.
- Clearly indicate the current digestive stage.
- Provide educational explanations relevant to each stage.
- Include playback controls for starting, pausing, resuming, resetting, and adjusting the playback speed.
- Display progress through the journey and provide clear feedback when controls are used.
- Keep the model, camera, food movement, and explanatory interface synchronized.
- Do not assume that the food must be represented as a physically accurate 3D object if a simpler representation communicates the process more effectively.

### Anatomical Limitations

- Inspect the model's geometry and positioning before implementing food movement.
- Do not invent anatomical pathways that contradict the visible model.
- If the model does not provide enough detail for an accurate path, explain the limitation and propose a suitable alternative before making major changes.
- Keep the food journey understandable without compromising anatomical accuracy.

## 6. Scientific Accuracy and Educational Content

Scientific accuracy is essential to the project.

- Base explanations on established biology and human digestive physiology.
- Distinguish between actual biological processes and visual simplifications used for the interactive exhibit.
- Do not imply that the entire digestive process happens in the short time shown by the animation.
- Use a compressed educational timeline to make the experience manageable while clearly explaining that the animation represents a longer biological process.
- Explain the roles of digestive organs, enzymes, nutrient breakdown, and nutrient absorption when relevant to the current development stage.
- Treat nutrient absorption as a later feature unless explicitly prioritized.
- Avoid unsupported claims about traditional and modern diets.
- Present dietary comparisons fairly and distinguish established evidence from generalizations or uncertainty.

## 7. User Experience and Accessibility

The website should be clear, usable, and educational.

- Prioritize the 3D anatomy exhibit and make its controls easy to understand.
- Keep explanatory text readable and organized.
- Provide clear feedback for loading, playback, selection, and errors.
- Use descriptive labels for interactive controls.
- Provide keyboard-accessible alternatives for important interactions where practical.
- Do not rely exclusively on animation, color, or drag-and-drop to communicate essential information.
- Maintain responsive behavior so that core functionality remains usable on different screen sizes.
- Avoid unnecessary interface complexity that distracts from the educational experience.

## 8. Preparation for Future UI Development

The website will eventually receive a broader visual refinement, but **the current priority is core functionality**, not a full redesign.

During current development:

- Keep interface styles and reusable components reasonably organized.
- Avoid unnecessary duplication of CSS, controls, and interface elements.
- Where practical, keep presentation styling separate from the Three.js scene and core interaction logic.
- Avoid hard-coding visual assumptions that unnecessarily restrict future layout changes.
- When adding or modifying controls, make them clear and usable without redesigning unrelated parts of the website.
- Preserve existing functionality and the current visual direction unless a change is necessary for usability.

Before a future major UI-design task, inspect the relevant installed UI and web-design skills and recommend an appropriate approach. Do not install additional tools or skills without approval.

## 9. Three.js Development and Testing

Before making significant Three.js changes:

- Inspect the existing implementation and the relevant installed Three.js skills.
- Consult the applicable skills for model loading, scene objects, cameras, lighting, materials, controls, animation, and rendering.
- Follow the existing code conventions unless there is a clear reason to change them.
- Avoid unnecessary rewrites of the rendering pipeline or scene setup.

After changes, test the relevant functionality in a browser using a local HTTP server or Live Server where appropriate.

Verify, as applicable:

- The GLB loads successfully.
- The model is visible and correctly framed.
- Camera and view controls work.
- Food movement and playback controls behave correctly.
- Loading and error states are handled.
- There are no new console errors.
- Asset paths resolve correctly.
- The page remains usable at different viewport sizes.

If a feature cannot be fully tested, state what was and was not verified. Do not report a feature as working based only on code inspection.

## 10. GitHub and Publishing

The website is intended for GitHub Pages deployment.

- Use relative asset paths where appropriate so pages work when hosted under a repository path.
- Avoid dependencies on local absolute file paths.
- Remember that browser-based module loading and GLB loading generally require an HTTP server rather than opening the page directly through `file://`.
- Keep large assets within GitHub's file-size limits.
- Preserve the original and intermediate model files unless permission is given to remove them.
- Ensure external dependencies, including the Draco decoder, are configured correctly for the deployment environment.
- Test the published-path assumptions when changing page locations or asset references.
- Do not publish, commit, or push changes unless explicitly requested.

## 11. Development Workflow

For each task:

1. Inspect the relevant files and understand the existing behavior.
2. Identify the smallest changes that can satisfy the request.
3. Review applicable project instructions and installed skills.
4. Ask for approval if the proposed changes exceed the requested scope or involve significant architectural decisions.
5. Implement the approved changes without disturbing unrelated features.
6. Test the affected functionality.
7. Report the changes, verification results, and remaining issues.

Keep the work focused on the current priority. Do not implement deferred features or undertake a broad redesign unless explicitly requested.