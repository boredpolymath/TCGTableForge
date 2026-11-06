#!/usr/bin/env python3
import json
import re
import struct
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.webmanifest"


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script" and attrs.get("src"):
            self.assets.append(attrs["src"])
        elif tag in {"link", "img", "source"}:
            url = attrs.get("href") or attrs.get("src")
            if url:
                self.assets.append(url)


def png_size(path):
    with path.open("rb") as image:
        header = image.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} is not a PNG file")
    return struct.unpack(">II", header[16:24])


def luminance(color):
    value = color.lstrip("#")
    if len(value) == 3:
        value = "".join(channel * 2 for channel in value)
    channels = [int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)]
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first, second):
    bright, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (bright + 0.05) / (dark + 0.05)


def main():
    manifest = json.loads(MANIFEST.read_text())
    assert manifest["name"] == "TCG TableForge"
    assert manifest["short_name"] == "TableForge"
    assert manifest["start_url"] == "./" and manifest["scope"] == "./"
    assert manifest["display"] == "standalone"
    for icon in manifest["icons"]:
        path = ROOT / icon["src"]
        assert path.is_file(), f"Missing manifest icon: {icon['src']}"
        expected = int(icon["sizes"].split("x")[0])
        assert png_size(path) == (expected, expected), f"Wrong dimensions: {icon['src']}"
    assert (ROOT / "apple-touch-icon.png").is_file()

    parser = AssetParser()
    parser.feed((ROOT / "index.html").read_text())
    for reference in parser.assets:
        parsed = urlsplit(reference)
        if parsed.scheme or parsed.netloc or reference.startswith("#"):
            continue
        local = (ROOT / parsed.path).resolve()
        assert local.is_relative_to(ROOT) and local.is_file(), f"Broken local asset reference: {reference}"

    service_worker = (ROOT / "sw.js").read_text()
    assert "CACHE_PREFIX = 'tcg-tableforge-shell-'" in service_worker
    assert "request.mode === 'navigate'" in service_worker
    assert "__BUILD_CACHE_VERSION__" in service_worker
    assert "url.pathname.startsWith(scopePath)" in service_worker
    assert not re.search(r"(?:fonts\.googleapis|google-analytics|googletagmanager)", (ROOT / "index.html").read_text(), re.I)

    app_script = (ROOT / "app.js").read_text()
    palette = re.search(r"const COLORS=(\{[^}]+\})", app_script)
    assert palette, "Card type color palette is missing"
    for color in re.findall(r"#[0-9a-fA-F]{6}", palette.group(1)):
        assert contrast(color, "#ffffff") >= 4.5, f"Card type text color {color} misses 4.5:1 on white"
    for foreground, background, label in [
        ("#262626", "#80ab00", "primary button"),
        ("#262626", "#96bb2e", "primary button hover"),
        ("#626262", "#ffffff", "muted text"),
        ("#555555", "#e8e8e3", "disabled controls"),
        ("#557300", "#ffffff", "light surface focus ring"),
        ("#91b500", "#262626", "dark surface focus ring"),
        ("#262626", "#80ab00", "top navigation focus ring")
    ]:
        assert contrast(foreground, background) >= 4.5, f"{label} contrast is below 4.5:1"
    print("Release checks passed: manifest, icons, asset references, service-worker safeguards, and key text contrast pairs.")


if __name__ == "__main__":
    main()
