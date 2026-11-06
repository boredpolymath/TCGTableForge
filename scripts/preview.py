#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PREFIX = "/TCGTableForge"


class ProjectPathHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        path = path.split("?", 1)[0].split("#", 1)[0]
        if path.rstrip("/") != PREFIX and not path.startswith(PREFIX + "/"):
            return str(DIST / "__not_found__")
        relative = path[len(PREFIX):].lstrip("/") or "index.html"
        target = (DIST / relative).resolve()
        return str(target if target.is_relative_to(DIST) else DIST / "__not_found__")


if not DIST.is_dir():
    raise SystemExit("Run npm run build before npm run preview")
print("Previewing project-site path at http://localhost:8001/TCGTableForge/")
ThreadingHTTPServer(("127.0.0.1", 8001), ProjectPathHandler).serve_forever()
