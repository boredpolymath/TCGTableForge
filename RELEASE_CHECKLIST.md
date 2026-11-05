# TCG TableForge release checklist

This checklist turns the current UI prototype into a release-ready, local-first Progressive Web App. The prototype currently consists of `index.html`, `manifest.webmanifest`, `sw.js`, and SVG icons. There is no package manifest, automated test suite, build script, or GitHub Pages workflow yet. Items below are unchecked until implemented and verified.

## 1. Product decisions and requirements

- [ ] Resolve the save and connectivity status requirement. The SRS requires visible saved/online/offline status, while the toolbar status was removed during UI work. Choose a quieter location for this information or revise the SRS and acceptance criteria deliberately.
- [ ] Update the SRS, guide copy, and acceptance criteria to use the selected one-word card types: **World, Experience, Theme, Mechanic, Question**. Preserve support for importing older names such as “World Idea,” “Player Experience,” and “Open Question.”
- [ ] Confirm the product name, icon, supported browsers, minimum viewport, and whether the first release includes custom relationship labels and card sorting.
- [ ] Define a versioning and release-note convention, plus who owns the Pages repository and production deploy.

## 2. App behavior and data integrity

- [ ] Confirm project creation, project switching, rename/edit settings, deletion, and empty states work from a clean install.
- [ ] Confirm card creation, editing, deletion, all five types, and useful empty states.
- [ ] Confirm relationship creation, editing, removal, link counts, and the Connections modal opened from a card’s Link hint.
- [ ] Confirm search, type filtering, sorting, and Board/List switching work together and retain sensible state when switching projects.
- [ ] Confirm data saves locally after each edit and survives reload, browser restart, and offline use. Surface save failures and storage quota errors without losing the last saved data.
- [ ] Confirm deleting one project and clearing all local data require explicit confirmation that states the deletion scope.
- [ ] Harden and document the JSON schema. Validate schema version, required fields, types, sizes, IDs, relationships, and unsupported versions before changing current data.
- [ ] Verify invalid imports leave existing projects untouched and explain the failure. Cover malformed JSON, wrong root shape, duplicate IDs, missing relationship endpoints, oversized files, unsupported schema versions, and boundary-size documents.
- [ ] Verify import normalization/migration for legacy card type names and old exported files.
- [ ] Verify JSON export round-trips project data without loss. Verify Markdown export is readable and includes cards and relationships in a predictable order.
- [ ] Verify export errors are visible and do not silently discard data.
- [ ] Decide and document storage limits and recovery guidance. Check behavior when local storage is unavailable, full, or cleared by browser settings.
- [ ] Confirm no project contents are sent to a server; inspect runtime requests and dependencies for analytics, telemetry, remote fonts, or other unexpected network access.

## 3. PWA and offline readiness

- [ ] Add install-ready raster icons at the sizes required by supported browsers (at least 192×192 and 512×512), plus an Apple touch icon if iOS installation is supported. Verify artwork, transparency, and maskable safe zones.
- [ ] Update `manifest.webmanifest` to reference the final icons and confirm name, short name, start URL, scope, standalone display, theme color, and background color on the deployed project-site path.
- [ ] Make the service worker cache name/version change on every release so the updated shell is installed reliably.
- [ ] Limit service-worker cache cleanup to cache names owned by this app; do not delete unrelated CacheStorage entries on the same origin.
- [ ] Restrict the offline HTML fallback to navigation requests. A missing script, icon, or other asset should not receive `index.html` as its response.
- [ ] Confirm first load online, subsequent load offline, offline project editing, and reload while offline.
- [ ] Confirm update flow preserves saved data, clearly tells the user when a refresh is needed, and cannot reload ahead of a pending save.
- [ ] Confirm install prompts/instructions are accurate where supported and fall back cleanly where installation is unavailable.
- [ ] Confirm the app explains that projects are stored only on the current device and are not synchronized.
- [ ] Confirm users can clear app data from Settings and are told that clearing browser site data may also remove it.
- [ ] Verify production is served over HTTPS and the service worker registers from the final GitHub Pages URL.

## 4. Accessibility, responsive layout, and content

- [ ] Run keyboard-only walkthroughs for project selection, toolbar actions, cards, filters, every modal, confirmation dialogs, and guide panels.
- [ ] Verify visible focus, logical tab order, Escape behavior, focus trapping/restoration in modals, and no keyboard traps.
- [ ] Check semantic landmarks, heading order, button names, input labels, list/card relationships, status announcements, and error announcements with a screen reader.
- [ ] Check color contrast against WCAG 2.2 AA, including green buttons, colored card types, disabled states, focus indicators, and muted text.
- [ ] Check minimum target sizes and spacing for touch interactions.
- [ ] Verify no horizontal overflow and usable reflow at 320px, 375px, tablet widths, and desktop widths up to 1280px; inspect both Board and List views and all modals, including the How To guide.
- [ ] Proofread all first-run instructions, empty states, import/export messages, offline/update notices, and destructive-action confirmations.
- [ ] Test long titles, long notes, special characters, emoji, non-Latin text, and unusually large card counts for clipping or layout breakage.

## 5. Performance and compatibility

- [ ] Create a repeatable fixture with 500 cards and 1,000 relationships. Measure project open, search/filter, board/list switching, and edits on a representative 4 GB device; meet the SRS target of under two seconds for the specified operations.
- [ ] Check memory use and responsiveness with large notes and repeated project switching.
- [ ] Verify current supported Chrome, Edge, Firefox, and Safari on desktop, plus Safari on iOS and Chrome on Android. Record versions and known limitations.
- [ ] Verify data persists across app updates and browser restarts on each supported browser.

## 6. Development scripts and repository setup

- [ ] Add `package.json` and commit the generated lockfile so local and CI dependency resolution is reproducible. Keep runtime dependencies minimal; the app should continue to work offline.
- [ ] Add scripts with stable, documented behavior, for example:
  - `npm run dev` — serve the app over localhost (not `file://`) for service-worker development.
  - `npm run check` — validate the manifest, required assets, references, and build inputs.
  - `npm test` — run unit and integration tests.
  - `npm run build` — create a clean `dist/` deploy artifact and stamp the service-worker cache version.
  - `npm run preview` — serve the built artifact locally under a project-site subpath to catch relative URL issues.
- [ ] Add a build script that copies only runtime files into `dist/`, includes `.nojekyll`, and does not publish source notes, test fixtures, or repository metadata.
- [ ] Add automated tests for import validation/migration, local persistence, project/card/relationship operations, search/filter/sort, exports, and deletion scope.
- [ ] Add browser end-to-end tests for first run, project creation, editing, reload persistence, import/export, modal behavior, offline behavior, update behavior, and mobile layout.
- [ ] Add automated accessibility checks, then keep manual screen-reader and keyboard checks in the release process.
- [ ] Add `README.md` with prerequisites, local development, script usage, test instructions, deployment setup, data-storage/privacy behavior, and release steps.
- [ ] Add a `.gitignore` for generated output, local browser/test artifacts, and dependencies.
- [ ] Create/confirm the GitHub repository, default branch, license decision, and repository remote; commit the actual source files before setting up deployment.

## 7. GitHub Pages deployment

- [ ] Add `.github/workflows/pages.yml` using GitHub’s Pages artifact deployment flow.
- [ ] Configure the workflow to run on pushes to the production branch and on manual `workflow_dispatch`; optionally run checks on pull requests without deploying.
- [ ] Workflow build job: checkout source, install the supported Node version, run `npm ci`, `npm run check`, `npm test`, and `npm run build`, then upload `dist/` as the Pages artifact.
- [ ] Workflow deploy job: depend on a successful build, grant only the required `pages: write` and `id-token: write` permissions (plus `contents: read` for checkout), use the `github-pages` environment, and deploy the uploaded artifact.
- [ ] Set concurrency so two production deployments do not race, and retain the deployment URL as the environment URL.
- [ ] Pin GitHub Actions to reviewed stable versions. Confirm action versions and workflow syntax against the current [GitHub Pages custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) and the [official Pages starter workflow](https://github.com/actions/starter-workflows/blob/main/pages/static.yml) when implementing; GitHub’s examples can use different action versions as they evolve.
- [ ] In repository Settings → Pages, select **GitHub Actions** as the build and deployment source.
- [ ] Verify whether the app uses a repository subpath such as `https://<owner>.github.io/<repository>/`; keep all manifest, icon, CSS, script, and service-worker URLs relative or scope-aware so they work there.
- [ ] Do not add deployment secrets unless the chosen hosting setup actually requires them; standard GitHub Pages Actions deployment uses repository permissions and an environment.
- [ ] Confirm the first deploy is HTTPS, the manifest loads, the service worker controls the expected path, and deep navigation/reload behavior works.

## 8. Release verification and operations

- [ ] Run the full automated suite and record results for the release commit.
- [ ] Complete the manual acceptance walkthrough on a clean browser profile and with an existing project, online and offline.
- [ ] Check the deployed app at its final URL on desktop and mobile; install it where supported and test a cold launch.
- [ ] Verify import/export backup instructions and test restoring a backup into a fresh browser profile.
- [ ] Review the production bundle for accidental test data, secrets, debug output, and unintended external requests.
- [ ] Tag the release and publish concise release notes with supported browsers, known limitations, and backup guidance.
- [ ] Keep a rollback path: retain the last known-good artifact or commit and document how to redeploy it through Actions.
- [ ] After deployment, monitor the Actions run, browser console, service-worker registration, install behavior, and reported data-loss or import/export issues.

## Release gate

- [ ] No unresolved data-loss, import-validation, offline-update, accessibility, or deployment-path issues.
- [ ] All required checks pass on the exact commit being released.
- [ ] Production smoke checks pass at the GitHub Pages URL, including an offline reopen and a verified backup export.
