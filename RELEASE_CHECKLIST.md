# TCG TableForge release checklist

This checklist tracks release readiness for TCG TableForge, a local-first Progressive Web App. The repository now includes a package manifest, build and preview scripts, data tests, Chrome browser checks, release documentation, and a GitHub Pages workflow. Items below are checked only where the implementation or available verification supports them.

## 1. Product decisions and requirements

- [x] Resolve the save and connectivity status requirement. The SRS requires visible saved/online/offline status, while the toolbar status was removed during UI work. Choose a quieter location for this information or revise the SRS and acceptance criteria deliberately. Status is shown in the workspace footer.
- [x] Update the SRS, guide copy, and acceptance criteria to use the selected one-word card types: **World, Experience, Theme, Mechanic, Question**. Preserve support for importing older names such as “World Idea,” “Player Experience,” and “Open Question.”
- [x] Confirm the product name, icon, supported browsers, minimum viewport, and whether the first release includes custom relationship labels and card sorting. Product: TCG TableForge; icon: `icon.svg`; support: current stable Chrome, Edge, Firefox, and Safari on desktop and mobile, with a 320–1280 CSS px viewport; sorting and custom relationship labels are in scope.
- [x] Define a versioning and release-note convention, plus who owns the Pages repository and production deploy. Use SemVer with concise release notes; Bored Polymath Studios owns the repository and production deploy.

## 2. App behavior and data integrity

- [x] Confirm project creation, project switching, rename/edit settings, deletion, and empty states work from a clean install. Chrome acceptance flow covers project creation, rename/details edit, switching, project deletion, and clear-all confirmation.
- [x] Confirm card creation, editing, deletion, all five types, and useful empty states. Chrome acceptance flow creates all five types, edits a card, deletes a card, and checks first-run and cleared-data empty states.
- [x] Confirm relationship creation, editing, removal, link counts, and the Connections modal opened from a card’s Link hint. Chrome acceptance flow covers all four actions.
- [x] Confirm search, type filtering, sorting, and Board/List switching work together and retain sensible state when switching projects. Chrome acceptance flow covers search, filtering, title sorting, List view, and project switching.
- [x] Confirm data saves locally after each edit and survives reload, browser restart, and offline use. Surface save failures and storage quota errors without losing the last saved data. Chrome checks reload, offline reopen, a simulated browser restart, unavailable storage, and quota failure while confirming the last persisted value remains.
- [x] Confirm deleting one project and clearing all local data require explicit confirmation that states the deletion scope. Chrome acceptance flow accepts each confirmation and verifies the empty state after clearing.
- [x] Harden and document the JSON schema. Validate schema version, required fields, types, sizes, IDs, relationships, and unsupported versions before changing current data. `data.js` enforces the documented limits and `tests/data.test.mjs` covers import boundaries and structural checks; the CI workflow runs the suite.
- [x] Verify invalid imports leave existing projects untouched and explain the failure. Cover malformed JSON, wrong root shape, duplicate IDs, missing relationship endpoints, oversized files, unsupported schema versions, and boundary-size documents. Chrome checks invalid import preservation; data validation checks cover exact limits and structural errors.
- [x] Verify import normalization/migration for legacy card type names and old exported files. Chrome acceptance flow imports a versionless legacy file and checks the normalized type and new IDs.
- [x] Verify JSON export round-trips project data without loss. Verify Markdown export is readable and includes cards and relationships in a predictable order. Chrome acceptance flow checks exported JSON and imports it, then checks Markdown headings, cards, and connections.
- [x] Verify export errors are visible and do not silently discard data. Chrome acceptance simulates a failed export and confirms the saved project remains unchanged.
- [x] Decide and document storage limits and recovery guidance. Check behavior when local storage is unavailable, full, or cleared by browser settings. Limits and recovery guidance are documented; Chrome simulates unavailable and full storage, and clearing stored site data returns to the first-run state.
- [x] Confirm no project contents are sent to a server; inspect runtime requests and dependencies for analytics, telemetry, remote fonts, or other unexpected network access. Chrome acceptance flow observes app requests as same-origin; runtime has no external dependencies.

## 3. PWA and offline readiness

- [x] Add install-ready raster icons at the sizes required by supported browsers (at least 192×192 and 512×512), plus an Apple touch icon if iOS installation is supported. Verify artwork, transparency, and maskable safe zones. Raster sizes and artwork were checked; visual artwork was inspected.
- [x] Update `manifest.webmanifest` to reference the final icons and confirm name, short name, start URL, scope, standalone display, theme color, and background color on the deployed project-site path. Production smoke check confirmed the manifest loads and its relative start URL and scope resolve to `https://boredpolymath.github.io/TCGTableForge/`.
- [x] Make the service worker cache name/version change on every release so the updated shell is installed reliably. The build stamps package version and source revision; Chrome acceptance verifies an update.
- [x] Limit service-worker cache cleanup to cache names owned by this app; do not delete unrelated CacheStorage entries on the same origin. Chrome acceptance confirms an unrelated cache remains after activation.
- [x] Restrict the offline HTML fallback to navigation requests. A missing script, icon, or other asset should not receive `index.html` as its response. Release checks verify the navigation-only fallback and the service worker returns an error for missing assets.
- [x] Confirm first load online, subsequent load offline, offline project editing, and reload while offline. Chrome acceptance flow loads online, saves edits, then reopens the app offline.
- [x] Confirm update flow preserves saved data, clearly tells the user when a refresh is needed, and cannot reload ahead of a pending save. Chrome acceptance flow installs an update, makes an unsaved edit, refreshes, and checks the saved value.
- [x] Confirm install prompts/instructions are accurate where supported and fall back cleanly where installation is unavailable. The guide gives browser-based install/Add to Home Screen directions and states the app remains usable without installation.
- [x] Confirm the app explains that projects are stored only on the current device and are not synchronized. The README and guide say so.
- [x] Confirm users can clear app data from Settings and are told that clearing browser site data may also remove it. Settings and the guide state the scope and risk; Chrome acceptance checks clear-all behavior.
- [x] Verify production is served over HTTPS and the service worker registers from the final GitHub Pages URL. Production returned HTTPS 200; the active worker and controller use `https://boredpolymath.github.io/TCGTableForge/sw.js` and control the expected project-site scope.

## 4. Accessibility, responsive layout, and content

- [x] Run keyboard-only walkthroughs for project selection, toolbar actions, cards, filters, every modal, confirmation dialogs, and guide panels. The live production walkthrough in Google Chrome 156.0.8078.81 passed project selection, card and relationship creation, filtering/sorting, Board/List switching, card activation/deletion, project/files/settings dialogs, guide panels, JSON export, and project/clear-all confirmations. It also found and fixed guide-panel focus trapping; regression coverage is in the Chrome suite.
- [x] Verify visible focus, logical tab order, Escape behavior, focus trapping/restoration in modals, and no keyboard traps. Chrome checks tab order, Escape, and modal focus return; focus outlines have 3px contrasting colors.
- [ ] Check semantic landmarks, heading order, button names, input labels, list/card relationships, status announcements, and error announcements with a screen reader. Automated accessible-name/tab checks pass; card validation and error toasts now expose assertive alert roles. Actual VoiceOver spoken output still needs a manual check.
- [x] Check color contrast against WCAG 2.2 AA, including green buttons, colored card types, disabled states, focus indicators, and muted text. Key foreground/background pairs are checked by `scripts/check_release.py`; text and focus colors were darkened where needed. Manual screen-reader checks remain separate.
- [x] Check minimum target sizes and spacing for touch interactions. Chrome acceptance measures all visible buttons and card actions at 320px against the 24px minimum.
- [x] Verify no horizontal overflow and usable reflow at 320px, 375px, tablet widths, and desktop widths up to 1280px; inspect both Board and List views and all modals, including the How To guide. Chrome acceptance checks both views at all four widths and checks the primary dialogs at 320px. A production mobile-emulation check also passed both views at all four widths, the 24px touch-target minimum, and guide/files/settings/project/card dialog fit at 320px.
- [x] Proofread all first-run instructions, empty states, import/export messages, offline/update notices, and destructive-action confirmations.
- [x] Test long titles, long notes, special characters, emoji, non-Latin text, and unusually large card counts for clipping or layout breakage. Chrome checks a 100-character multilingual title and 3,000-character note; the 500-card fixture checks large projects.

## 5. Performance and compatibility

- [x] Create a repeatable fixture with 500 cards and 1,000 relationships. Measure project open, search/filter, board/list switching, and edits on a representative 4 GB device; meet the SRS target of under two seconds for the specified operations. Fixture and Mac measurements are in `PERFORMANCE_REPORT.md`; the M2 Mac has 8 GB RAM and measured operations are below two seconds.
- [x] Check memory use and responsiveness with large notes and repeated project switching. The Mac stress run used a 3,000-character note and ten project switches; heap and timings are recorded in `PERFORMANCE_REPORT.md`.
- [ ] Verify current supported Chrome, Edge, Firefox, and Safari on desktop, plus Safari on iOS and Chrome on Android. Record versions and known limitations. Installed Google Chrome 156.0.8078.81 passed production create/export/offline checks; Playwright WebKit 26.4 passed desktop core flows and an iPhone 15 Safari user-agent layout check. Native Safari automation requires enabling Remote Automation in macOS Settings; Firefox’s helper process was blocked by macOS; Edge is not installed; the iOS Simulator app is missing and the Android emulator remained offline.
- [ ] Verify data persists across app updates and browser restarts on each supported browser. Cold browser restart persistence passed in Google Chrome 156.0.8078.81 and Playwright WebKit 26.4; Chrome also reopened offline. Other supported browsers and update persistence in each remain unverified.

## 6. Development scripts and repository setup

- [x] Add `package.json` and commit a lockfile so local and CI dependency resolution is reproducible. Keep runtime dependencies minimal; the app should continue to work offline. The manifest and lockfile are committed and contain no runtime dependencies. `npm ci` passed in GitHub Actions on commit `30740ef`.
- [x] Add scripts with stable, documented behavior, for example:
  - `npm run dev` — serve the app over localhost (not `file://`) for service-worker development.
  - `npm run check` — validate the manifest, required assets, references, and build inputs.
  - `npm test` — run unit and integration tests.
  - `npm run build` — create a clean `dist/` deploy artifact and stamp the service-worker cache version.
  - `npm run preview` — serve the built artifact locally under a project-site subpath to catch relative URL issues.
- [x] Add a build script that copies only runtime files into `dist/`, includes `.nojekyll`, and does not publish source notes, test fixtures, or repository metadata. The built output was inspected and contains only runtime files and `.nojekyll`.
- [x] Add automated tests for import validation/migration, local persistence, project/card/relationship operations, search/filter/sort, exports, and deletion scope. Six data tests and the full Chrome acceptance suite passed in the GitHub Actions build job on commit `30740ef`.
- [x] Add browser end-to-end tests for first run, project creation, editing, reload persistence, import/export, modal behavior, offline behavior, update behavior, and mobile layout. Chrome acceptance script covers these flows at 320px and the project-site subpath.
- [x] Add automated accessibility checks, then keep manual screen-reader and keyboard checks in the release process. Chrome acceptance checks accessible names, alert roles for errors, modal Escape/focus restoration, guide-panel keyboard access, and tab behavior; manual assistive-technology checks remain required.
- [x] Keep `README.md` current with local development, data-storage/privacy behavior, deployment status, and release guidance as those workflows are implemented.
- [x] Add a `.gitignore` for generated output, local browser/test artifacts, and dependencies.
- [x] Confirm the GitHub repository (`boredpolymath/TCGTableForge`), default branch (`main`), MIT license, and repository remote.
- [x] Commit and push the actual source files to `main` before production deployment. Commit `31b9232` is on `main`; automated build checks and Pages deployment pass.

## 7. GitHub Pages deployment

- [x] Add `.github/workflows/pages.yml` using GitHub’s Pages artifact deployment flow.
- [x] Configure the workflow to run on pushes to the production branch and on manual `workflow_dispatch`; optionally run checks on pull requests without deploying. It also validates pull requests without deploying.
- [x] Workflow build job: checkout source, install the supported Node version, run `npm ci`, `npm run check`, `npm test`, and `npm run build`, then upload `dist/` as the Pages artifact.
- [x] Workflow deploy job: depend on a successful build, grant only the required `pages: write` and `id-token: write` permissions (plus `contents: read` for checkout), use the `github-pages` environment, and deploy the uploaded artifact.
- [x] Set concurrency so two production deployments do not race, and retain the deployment URL as the environment URL.
- [x] Pin GitHub Actions to reviewed stable versions. Confirm action versions and workflow syntax against the current [GitHub Pages custom workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) and the [official Pages starter workflow](https://github.com/actions/starter-workflows/blob/main/pages/static.yml) when implementing; GitHub’s examples can use different action versions as they evolve.
- [x] In repository Settings → Pages, select **GitHub Actions** as the build and deployment source. The Pages deployment workflow completed successfully on commit `31b9232`.
- [x] Verify whether the app uses a repository subpath such as `https://<owner>.github.io/<repository>/`; keep all manifest, icon, CSS, script, and service-worker URLs relative or scope-aware so they work there. Production is served at `https://boredpolymath.github.io/TCGTableForge/`; the manifest and service worker resolve correctly under that path.
- [x] Do not add deployment secrets unless the chosen hosting setup actually requires them; standard GitHub Pages Actions deployment uses repository permissions and an environment. No deployment secrets were added.
- [x] Confirm the first deploy is HTTPS, the manifest loads, the service worker controls the expected path, and deep navigation/reload behavior works. Production smoke check confirmed HTTPS, manifest, service-worker scope and control, and reload behavior at `https://boredpolymath.github.io/TCGTableForge/`.

## 8. Release verification and operations

- [ ] Run the full automated suite and record results for the release candidate. Commit `31b9232` passed `npm ci`, release checks, all six data tests, the Chrome acceptance suite including guide keyboard regression, build, the 500-card performance run, and Pages deployment. Error-announcement regressions are being run on the current local changes and must pass on the deployed release commit before checking this item.
- [ ] Complete the manual acceptance walkthrough on a clean browser profile and with an existing project, online and offline. Production Chrome automation covered a fresh profile, project creation/editing, JSON backup, restart persistence, and offline reopen; manual sign-off remains.
- [ ] Check the deployed app at its final URL on desktop and mobile; install it where supported and test a cold launch. Desktop Chrome and mobile Chrome/WebKit emulation passed responsive checks; WebKit used an iPhone 15 Safari user-agent profile. Chrome’s manifest diagnostics returned no manifest errors. Physical-device install and installed-app cold-launch checks remain.
- [x] Verify import/export backup instructions and test restoring a backup into a fresh browser profile. Chrome imports the exported JSON in a separate, empty browser context and checks all five cards.
- [x] Review the production bundle for accidental test data, secrets, debug output, and unintended external requests. The built artifact contains only runtime files and `.nojekyll`; fixture/debug/credential scans found none, and Chrome observed only same-origin app requests.
- [ ] Tag the release and publish concise release notes with supported browsers, known limitations, and backup guidance.
- [x] Keep a rollback path: retain the last known-good artifact or commit and document how to redeploy it through Actions. Procedure and current known-good deployed revision are recorded in `RELEASE_OPERATIONS.md`.
- [ ] After deployment, monitor the Actions run, browser console, service-worker registration, install behavior, and reported data-loss or import/export issues. The latest Actions run passed; Chrome and WebKit console checks had no page errors; service-worker registration and Chrome manifest diagnostics returned no errors; the repository currently has no open issues. Installed-app behavior and ongoing issue monitoring remain.

## Release gate

- [ ] No unresolved data-loss, import-validation, offline-update, accessibility, or deployment-path issues.
- [ ] All required checks pass on the exact commit being released.
- [x] Production smoke checks pass at the GitHub Pages URL, including an offline reopen and a verified backup export. HTTPS, manifest, service-worker scope/control, JSON backup export, offline reload, mobile layout, modal fit, touch targets, same-origin requests, and zero browser page errors passed at `https://boredpolymath.github.io/TCGTableForge/`.
