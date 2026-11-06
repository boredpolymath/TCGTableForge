#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RUNTIME_FILES = [
    "index.html", "app.js", "data.js", "sw.js", "manifest.webmanifest",
    "icon.svg", "icon-192.png", "icon-512.png", "apple-touch-icon.png", "LICENSE"
]


def build_version():
    version = json.loads((ROOT / "package.json").read_text())["version"]
    revision = os.environ.get("GITHUB_SHA")
    if not revision:
        try:
            revision = subprocess.check_output(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT, text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            revision = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{version}-{revision[:12]}"


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name in RUNTIME_FILES:
        source = ROOT / name
        if not source.is_file():
            raise SystemExit(f"Missing runtime file: {name}")
        shutil.copy2(source, DIST / name)
    version = build_version()
    service_worker = (DIST / "sw.js").read_text()
    if service_worker.count("__BUILD_CACHE_VERSION__") != 1:
        raise SystemExit("Service-worker build-version marker is missing or ambiguous")
    (DIST / "sw.js").write_text(service_worker.replace("__BUILD_CACHE_VERSION__", version))
    (DIST / ".nojekyll").write_text("")
    print(f"Built {len(RUNTIME_FILES)} runtime files into dist/ with cache version {version}.")


if __name__ == "__main__":
    main()
