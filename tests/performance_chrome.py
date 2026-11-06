#!/usr/bin/env python3
import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "performance-500-1000.json"
CHROME = os.environ.get("TABLEFORGE_CHROME")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def run():
    fixture = json.loads(FIXTURE.read_text())["project"]
    support_projects = [{
        "projectId": f"switch-project-{index}", "name": f"Switch Project {index}",
        "approach": "world-first", "cards": [], "relationships": []
    } for index in (1, 2)]
    all_projects = [fixture, *support_projects]
    server = ThreadingHTTPServer(("127.0.0.1", 0), lambda *args, **kwargs: QuietHandler(*args, directory=str(ROOT), **kwargs))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as playwright:
            launch = {"headless": True, "args": ["--no-sandbox"]}
            if CHROME:
                launch["executable_path"] = CHROME
            browser = playwright.chromium.launch(**launch)
            context = browser.new_context(viewport={"width": 1280, "height": 900})
            context.add_init_script("localStorage.setItem('world-mechanic-projects-v1', " + json.dumps(json.dumps(all_projects)) + "); localStorage.setItem('world-mechanic-guide-seen','1');")
            page = context.new_page()
            page.goto(f"http://127.0.0.1:{server.server_port}", wait_until="networkidle")
            assert page.get_by_role("heading", name="Performance Fixture").is_visible()

            results = {"open_ms": page.evaluate("performance.getEntriesByType('navigation')[0].domContentLoadedEventEnd")}
            results["filter_ms"] = page.evaluate("""() => { const started=performance.now(),el=document.querySelector('#filter');el.value='Mechanic';el.dispatchEvent(new Event('change',{bubbles:true}));return performance.now()-started; }""")
            results["search_ms"] = page.evaluate("""() => { const started=performance.now(),el=document.querySelector('#search');el.value='Fixture idea 04';el.dispatchEvent(new Event('input',{bubbles:true}));return performance.now()-started; }""")
            results["board_list_switch_ms"] = page.evaluate("""() => { const started=performance.now();document.querySelector('#listView').click();document.querySelector('#boardView').click();return performance.now()-started; }""")
            results["ten_project_switches_ms"] = page.evaluate("""() => {
              const buttons = [...document.querySelectorAll('#projectList [data-open]')];
              const started = performance.now();
              for (let i = 0; i < 5; i++) { buttons[1].click(); buttons[2].click(); buttons[0].click(); }
              return performance.now() - started;
            }""")
            page.locator("#search").fill("")
            page.locator("#filter").select_option(label="All types")
            page.locator(".card-main").first.click()
            page.locator("#cardNotes").fill("Performance fixture edit")
            results["edit_ms"] = page.evaluate("""() => { const started=performance.now();document.querySelector('#saveCard').click();return performance.now()-started; }""")
            results["heap_bytes"] = page.evaluate("performance.memory ? performance.memory.usedJSHeapSize : null")
            results["cards"] = page.locator(".card").count()
            results["relationships"] = len(fixture["relationships"])
            if any(results[key] >= 2000 for key in ["open_ms", "filter_ms"]):
                raise AssertionError(f"SRS performance target missed: {results}")
            print(json.dumps(results, indent=2))
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    run()
