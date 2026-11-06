# Contributing to TCG TableForge

Thanks for helping improve TableForge. Bug reports, thoughtful feature proposals, documentation updates, and code contributions are welcome.

## Before opening an issue or pull request

- Search existing issues and pull requests to avoid duplicates.
- For larger changes, open an issue first to discuss the approach.
- Keep changes focused and describe the user-facing effect and any relevant limitations.

## Development setup

The app is a static site. It has no runtime dependencies. Development checks use Node.js and Python.

```sh
npm ci
npm run dev
```

Open `http://localhost:8000` to try the app. Projects are stored in the browser's local storage; use exported JSON backups for data you want to keep.

## Checks

Before submitting a code change, run the checks relevant to it:

```sh
npm run check
npm test
```

Browser checks require the pinned test dependency and Chromium:

```sh
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium
npm run test:e2e
npm run test:performance
```

The release workflow runs these checks and builds the Pages artifact. If you change the app shell, build configuration, manifest, icons, or offline behavior, also run `npm run build` and `npm run preview` and describe what you checked.

## Pull requests

- Explain the problem and the change, and link any related issue.
- Include screenshots or a short recording for visible interface changes.
- Update the README or release documentation when behavior or contributor steps change.
- Keep generated `dist/` output and unrelated formatting changes out of pull requests.
- Call out checks you ran and any checks you could not run.

By submitting a contribution, you agree that it will be distributed under the project's [MIT License](LICENSE).
