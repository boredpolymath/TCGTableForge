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

TableForge is a static web app with no runtime dependencies. Node.js and Python are used for development checks and build tasks.

```sh
npm ci
npm run dev
```

Open [http://localhost:8000](http://localhost:8000) in your browser. Explore the sample project and the illustrated How To guide, or start a project of your own. Changes save to this browser's local storage. Export a JSON backup before clearing browser data or moving your work to another device.

Run `npm run check` to validate the manifest, icons, local asset references, and service-worker safeguards. Run `npm test` for data validation tests. For browser acceptance tests, install the pinned test dependency with `python3 -m pip install -r requirements-test.txt`, install Chromium with `python3 -m playwright install chromium`, then run `npm run test:e2e` or `npm run test:performance`. `npm run fixture` regenerates the 500-card/1,000-relationship performance fixture; results from the Mac reference run are in [PERFORMANCE_REPORT.md](PERFORMANCE_REPORT.md). `npm run build` creates the deployable `dist/` folder; `npm run preview` serves it under `/TCGTableForge/` to check repository-site paths.

After the app has loaded once from localhost or HTTPS, its service worker caches the app shell for offline use. Projects remain on the device where they were created.

## Your projects, on your device

TableForge has no account, cloud sync, or server-side project storage. Project data stays in the current browser on the current device. Clearing the browser's site data may delete it, so keep JSON backups of work you want to preserve. The app's **Clear all data** action removes every TableForge project in this browser after a confirmation step.

JSON imports are limited to 10 MB, 5,000 cards, and 10,000 relationships. Card titles can be up to 120 characters, notes up to 3,000, descriptions up to 500, and design goals up to 300. Projects can have up to 100 custom relationship labels, each up to 50 characters. Browser storage quotas vary by browser and device, so export backups regularly and before clearing site data.

## Hosting and project status

The live app is hosted on [GitHub Pages](https://boredpolymath.github.io/TCGTableForge/). Pushes to `main` run the release checks and deploy the built app. The production smoke check confirmed HTTPS, the project-site manifest and service-worker scope, JSON backup export, and an offline reload. Deployment and rollback steps are in [RELEASE_OPERATIONS.md](RELEASE_OPERATIONS.md).

The automated data and Chrome browser suites pass in GitHub Actions. Manual screen-reader and full keyboard walkthroughs, checks across the other supported browsers and mobile devices, and installed-app cold-launch checks remain open in the [release checklist](RELEASE_CHECKLIST.md). Consult it for current release readiness and known verification gaps.

## Project files

- `index.html` — application interface and styling.
- `app.js` — client-side application behavior.
- `data.js` — JSON validation, migration, and export helpers.
- `manifest.webmanifest` — install metadata.
- `sw.js` — offline app-shell cache and update handling.
- `icon.svg`, `icon-192.png`, `icon-512.png`, and `apple-touch-icon.png` — selected app artwork for browser and install surfaces.
- `LICENSE` — MIT license.
- `assets/readme/tableforge-thumbnail.png` — README artwork.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
