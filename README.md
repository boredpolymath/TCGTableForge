![Illustrated game world branching into experience, mechanic, and theme cards](assets/readme/tableforge-thumbnail.png)

# TCG TableForge

**Turn a game world into playable ideas.**

TCG TableForge is a visual design canvas for tabletop and trading card games. Bring a setting, a gameplay hook, or a question you want to explore. Shape those ideas into cards, connect the pieces, and see how a game concept is coming together.

## From a spark to a system

Start where your idea is strongest. Build **world-first** from a place, people, or conflict, or go **mechanics-first** from an action or rule. Then connect the design dots:

1. Capture a **World**, **Experience**, **Theme**, **Mechanic**, or **Question** as a card.
2. Add notes about what the idea means and what it could do.
3. Link cards with relationships such as *Supports*, *Expresses*, *Creates Tension With*, and *Depends On*.
4. Browse the project as a visual board or a focused list. Search, filter, and sort as the design grows.

The connections help you follow an idea from the world you imagine to the choices players make and the mechanics that bring those choices to life.

## A flexible workspace for game design

- **Begin with either half of the puzzle.** Start from a world or from a mechanic, then let the rest of the concept emerge.
- **Keep different kinds of thinking visible.** Separate setting details, intended player feelings, recurring themes, possible rules, and open questions.
- **Make the relationships legible.** Connect ideas directly and inspect how a card fits into the wider project.
- **Keep the work portable.** Export a project as JSON for backup and later import, or export a readable Markdown outline for sharing and notes.
- **Stay in control of your work.** Projects are saved in this browser on this device; they are not uploaded or synchronized.

## Get started

TableForge is a static web app. There is no package installation or build step required to run it locally.

```sh
python3 -m http.server 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser. Explore the sample project and the illustrated How To guide, or start a project of your own. Changes save to this browser's local storage. Export a JSON backup before clearing browser data or moving your work to another device.

After the app has loaded once from localhost or HTTPS, its service worker caches the app shell for offline use. Projects remain on the device where they were created.

## Your projects, on your device

TableForge has no account, cloud sync, or server-side project storage. Project data stays in the current browser on the current device. Clearing the browser's site data may delete it, so keep JSON backups of work you want to preserve. The app's **Clear all data** action removes every TableForge project in this browser after a confirmation step.

## Hosting and project status

The app is built from static files and can be hosted with GitHub Pages. GitHub Pages deployment is not configured in this repository yet; the [release checklist](RELEASE_CHECKLIST.md) tracks the workflow, deployment settings, and remaining verification before a release.

The interface and core flows are prototyped. Automated tests, cross-browser acceptance checks, accessibility and offline verification, and other release gates remain on the checklist. Use the checklist as the current guide to release readiness.

## Project files

- `index.html` — application interface, styling, and client-side behavior.
- `manifest.webmanifest` — install metadata.
- `sw.js` — offline app-shell cache and update handling.
- `icon.svg` and `icon-tabletop-anvil.svg` — app icon concepts.
- `assets/readme/tableforge-thumbnail.png` — README artwork.

## License

No license has been selected yet. Until one is added, normal copyright restrictions apply.
