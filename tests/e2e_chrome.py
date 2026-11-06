#!/usr/bin/env python3
import json
import os
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
CHROME = os.environ.get("TABLEFORGE_CHROME")


class QuietHandler(SimpleHTTPRequestHandler):
    updated_worker = False

    def do_GET(self):
        if urlsplit(self.path).path == "/sw.js" and self.updated_worker:
            content = (ROOT / "sw.js").read_text().replace("'__BUILD_CACHE_VERSION__'", "'e2e-updated'").encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/javascript")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        return super().do_GET()

    def translate_path(self, path):
        local_path = unquote(urlsplit(path).path)
        prefix = "/TCGTableForge"
        if local_path.rstrip("/") == prefix or local_path.startswith(prefix + "/"):
            relative = local_path[len(prefix):].lstrip("/") or "index.html"
            target = (DIST / relative).resolve()
            return str(target if target.is_relative_to(DIST) else DIST / "__not_found__")
        return super().translate_path(path)

    def log_message(self, *_args):
        pass


def tab_to(page, selector, attempts=40):
    target = page.locator(selector).first
    for _ in range(attempts):
        if target.count() and target.is_visible() and target.evaluate("el => document.activeElement === el"):
            return
        page.keyboard.press("Tab")
    raise AssertionError(f"Could not reach {selector} using Tab")


def run():
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=str(ROOT), **kwargs)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with TemporaryDirectory(prefix="tableforge-e2e-") as profile, sync_playwright() as playwright:
            launch = {"headless": True, "args": ["--no-sandbox"]}
            if CHROME:
                launch["executable_path"] = CHROME
            browser = playwright.chromium.launch(**launch)
            context = browser.new_context(accept_downloads=True, viewport={"width": 1280, "height": 900})
            page = context.new_page()
            errors = []
            requests = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("request", lambda request: requests.append(request.url))
            page.goto(origin, wait_until="networkidle")
            page.wait_for_timeout(400)
            if page.locator("[data-close-guide]").count():
                page.locator("[data-close-guide]").click()

            assert page.get_by_text("Your design space is ready").is_visible(), (page.locator("body").inner_text(), errors)
            page.locator("#settingsBtn").click()
            assert page.get_by_role("dialog").is_visible()
            page.keyboard.press("Tab")
            page.keyboard.press("Shift+Tab")
            page.keyboard.press("Escape")
            assert page.get_by_role("dialog").count() == 0
            assert page.locator("#settingsBtn").evaluate("el => document.activeElement === el")
            page.locator("#newProject").click()
            page.locator("#projectName").fill("E2E Project")
            page.locator("#createProject").click()
            assert page.get_by_role("heading", name="E2E Project").is_visible()
            page.locator("#settingsBtn").click()
            page.locator("#editProjectName").fill("Renamed Project")
            page.locator("#editProjectDesc").fill("Description with café and 東京.")
            page.locator("#editProjectGoals").fill("Readable rules and curious choices")
            page.locator("#saveSettings").click()
            assert page.get_by_role("heading", name="Renamed Project").is_visible()
            page.locator("#settingsBtn").click()
            page.locator("#editProjectName").fill("E2E Project")
            page.locator("#saveSettings").click()

            def audit_accessible_names(target):
                issues = target.evaluate("""() => {
                  const controls = [...document.querySelectorAll('button, input:not([type=hidden]), select, textarea, [role=button]')];
                  return controls.filter(el => !(el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.innerText || el.labels?.length || el.title || el.getAttribute('alt') || '').trim())
                    .map(el => `${el.tagName.toLowerCase()}#${el.id}.${el.className}`);
                }""")
                assert not issues, f"Controls without accessible names: {issues}"

            def audit_touch_targets(target):
                undersized = target.evaluate("""() => [...document.querySelectorAll('button, [role=button]')]
                  .filter(el => el.getClientRects().length)
                  .map(el => ({el, rect: el.getBoundingClientRect()}))
                  .filter(({rect}) => rect.width < 24 || rect.height < 24)
                  .map(({el, rect}) => `${el.tagName.toLowerCase()}#${el.id}.${el.className} ${Math.round(rect.width)}x${Math.round(rect.height)}`)""")
                assert not undersized, f"Touch targets below 24px: {undersized}"

            def audit_modal_fit(target):
                overflow = target.evaluate("""() => [...document.querySelectorAll('.modal')]
                  .filter(el => el.getClientRects().length)
                  .filter(el => el.scrollWidth > el.clientWidth + 1)
                  .map(el => `${el.getAttribute('aria-labelledby') || el.className}: ${el.scrollWidth}/${el.clientWidth}`)""")
                assert not overflow, f"Modal content overflows horizontally: {overflow}"

            audit_accessible_names(page)

            def add_card(title, card_type):
                page.locator("#emptyAdd" if page.locator("#emptyAdd").count() else "#addCard").click()
                page.locator("#cardType").select_option(label=card_type)
                page.locator("#cardTitle").fill(title)
                page.locator("#cardNotes").fill(f"Notes for {title}")
                page.locator("#saveCard").click()

            add_card("First world", "World")
            add_card("Player mood", "Experience")
            add_card("Shared theme", "Theme")
            add_card("Core mechanic", "Mechanic")
            add_card("Open question", "Question")
            page.locator("#connectCards").click()
            page.locator("#fromCard").select_option(index=0)
            page.locator("#toCard").select_option(index=3)
            page.locator("#relationshipLabel").select_option(value="__custom__")
            page.locator("#customRelationshipLabel").fill("Complicates")
            page.locator("#saveRelation").click()
            assert "1 link" in page.locator(".relation-mark").first.inner_text()

            add_card("Temporary card", "Question")
            page.locator(".card-main").filter(has_text="Temporary card").click()
            page.locator("#cardTitle").fill("東京🚀 " * 20)
            page.locator("#cardNotes").fill("長" * 3000)
            page.locator("#saveCard").click()
            page.wait_for_function("JSON.parse(localStorage.getItem('world-mechanic-projects-v1') || '[]')[0]?.cards.find(card => card.title.startsWith('東京'))?.notes.length === 3000")
            page.locator(".card-main").filter(has_text="東京🚀").click()
            page.once("dialog", lambda dialog: dialog.accept())
            page.locator("#deleteCard").click()
            assert page.locator(".card").count() == 5

            page.locator("[data-card-links]").first.click()
            assert page.get_by_text("Complicates", exact=False).is_visible()
            page.locator("[data-edit-connection]").click()
            page.locator("#relationshipLabel").select_option(label="Supports")
            page.locator("#saveRelation").click()
            page.locator("[data-card-links]").first.click()
            page.once("dialog", lambda dialog: dialog.accept())
            page.locator("[data-delete-connection]").click()
            assert "connect" in page.locator(".relation-mark").first.inner_text()
            page.locator("#connectCards").click()
            page.locator("#fromCard").select_option(index=0)
            page.locator("#toCard").select_option(index=3)
            page.locator("#relationshipLabel").select_option(label="Supports")
            page.locator("#saveRelation").click()

            page.locator("#search").fill("Core mechanic")
            assert page.get_by_text("Core mechanic", exact=True).count() == 1
            page.locator("#search").fill("")
            page.locator("#filter").select_option(label="World")
            assert page.locator(".card").count() == 1
            page.locator("#filter").select_option(label="All types")
            page.locator("#sort").select_option(label="Title")
            page.locator("#listView").click()
            assert page.locator(".list-row").count() == 5
            page.locator("#newProject").click()
            page.locator("#projectName").fill("Temporary project")
            page.locator("#createProject").click()
            page.get_by_role("heading", name="Temporary project").wait_for()
            page.locator('[data-open]').filter(has_text="E2E Project").click()
            assert page.get_by_role("heading", name="E2E Project").is_visible()
            assert page.locator(".list-row").count() == 5
            page.locator('[data-open]').filter(has_text="Temporary project").click()
            page.locator("#settingsBtn").click()
            page.once("dialog", lambda dialog: dialog.accept())
            page.locator("#deleteProject").click()
            page.get_by_role("heading", name="E2E Project").wait_for()
            page.wait_for_function("JSON.parse(localStorage.getItem('world-mechanic-projects-v1') || '[]')[0]?.relationships?.[0]?.label === 'Supports'", timeout=5000)
            page.reload(wait_until="networkidle")
            assert page.get_by_role("heading", name="E2E Project").is_visible()
            saved = page.evaluate("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))")
            assert len(saved[0]["cards"]) == 5 and saved[0]["relationships"][0]["label"] == "Supports", saved[0]

            page.locator("#filesBtn").click()
            with page.expect_download() as download_info:
                page.locator('[data-file-action="json"]').click()
            download = download_info.value
            exported = json.loads(Path(download.path()).read_text())
            assert exported["schemaVersion"] == 1
            assert len(exported["project"]["cards"]) == 5
            backup_context = browser.new_context(accept_downloads=True, viewport={"width": 1280, "height": 900})
            backup_page = backup_context.new_page()
            backup_page.goto(origin, wait_until="networkidle")
            if backup_page.locator("[data-close-guide]").count():
                backup_page.locator("[data-close-guide]").click()
            backup_page.locator("#importFile").set_input_files({"name": "backup.json", "mimeType": "application/json", "buffer": json.dumps(exported).encode()})
            backup_page.get_by_role("heading", name="E2E Project (imported)").wait_for()
            assert backup_page.locator(".card").count() == 5
            backup_page.wait_for_timeout(250)
            backup_page.evaluate("localStorage.removeItem('world-mechanic-projects-v1')")
            backup_page.reload(wait_until="networkidle")
            assert backup_page.get_by_text("Your design space is ready").is_visible()
            backup_page.add_init_script("Storage.prototype.getItem = function(key) { if (key === 'world-mechanic-projects-v1') throw new DOMException('Storage unavailable', 'SecurityError'); return null; };")
            backup_page.reload(wait_until="networkidle")
            backup_page.get_by_text("Stored project data could not be read", exact=False).wait_for(timeout=5000)
            backup_context.close()
            page.locator("#filesBtn").click()
            with page.expect_download() as markdown_info:
                page.locator('[data-file-action="markdown"]').click()
            markdown = Path(markdown_info.value.path()).read_text()
            assert "## Cards" in markdown and "## Connections" in markdown and "Core mechanic" in markdown
            project_before_export_error = page.evaluate("localStorage.getItem('world-mechanic-projects-v1')")
            page.evaluate("() => { URL.createObjectURL = function() { throw new Error('Export unavailable') }; }")
            page.locator("#filesBtn").click()
            page.locator('[data-file-action="markdown"]').click()
            page.get_by_text("Export failed", exact=False).wait_for(timeout=5000)
            assert page.evaluate("localStorage.getItem('world-mechanic-projects-v1')") == project_before_export_error
            page.reload(wait_until="networkidle")

            bad_file = {"schemaVersion": 2, "project": exported["project"]}
            page.locator("#importFile").set_input_files({"name": "unsupported.json", "mimeType": "application/json", "buffer": json.dumps(bad_file).encode()})
            page.get_by_text("Schema version 2 is not supported.").wait_for(state="visible", timeout=5000)
            assert len(page.evaluate("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))")) == 1
            invalid_inputs = [
                ("malformed.json", b"{not json", "the file is not valid JSON"),
                ("wrong-root.json", b'{"unexpected":true}', "Project ID must be non-empty text"),
                ("oversized.json", b" " * (10 * 1024 * 1024 + 1), "10 MB or smaller")
            ]
            duplicate_ids = json.loads(json.dumps(exported))
            duplicate_ids["project"]["cards"][1]["cardId"] = duplicate_ids["project"]["cards"][0]["cardId"]
            invalid_inputs.append(("duplicate-ids.json", json.dumps(duplicate_ids).encode(), "Card IDs must be unique"))
            missing_endpoint = json.loads(json.dumps(exported))
            missing_endpoint["project"]["relationships"][0]["toCardId"] = "missing-card"
            invalid_inputs.append(("missing-endpoint.json", json.dumps(missing_endpoint).encode(), "missing card"))
            for name, content, message in invalid_inputs:
                page.locator("#importFile").set_input_files({"name": name, "mimeType": "application/json", "buffer": content})
                page.get_by_text(message, exact=False).wait_for(state="visible", timeout=5000)
                assert len(page.evaluate("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))")) == 1

            legacy = json.loads(json.dumps(exported))
            legacy.pop("schemaVersion")
            legacy["project"]["cards"][0]["type"] = "World Idea"
            page.locator("#importFile").set_input_files({"name": "legacy.json", "mimeType": "application/json", "buffer": json.dumps(legacy).encode()})
            page.wait_for_function("JSON.parse(localStorage.getItem('world-mechanic-projects-v1') || '[]').length === 2", timeout=5000)
            imported = page.evaluate("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))[0]")
            assert imported["cards"][0]["type"] == "World"
            assert imported["projectId"] != exported["project"]["projectId"]

            page.locator(".card-main").first.click()
            page.locator("#cardNotes").fill("Immediate reload save")
            page.locator("#saveCard").click()
            page.reload(wait_until="networkidle")
            assert page.evaluate("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))[0].cards[0].notes") == "Immediate reload save"

            page.evaluate("caches.open('unrelated-test-cache')")
            QuietHandler.updated_worker = True
            page.evaluate("navigator.serviceWorker.getRegistration().then(reg => reg.update())")
            page.wait_for_function("navigator.serviceWorker.getRegistration().then(reg => Boolean(reg && reg.waiting))", timeout=15000)
            page.get_by_text("An app update is ready", exact=False).wait_for(state="visible", timeout=5000)
            page.locator(".card-main").first.click()
            page.locator("#cardNotes").fill("Pending update-safe edit")
            page.locator("#saveCard").click()
            page.locator("#refreshBtn").click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(300)
            page.wait_for_function("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))[0].cards[0].notes === 'Pending update-safe edit'", timeout=5000)
            assert "unrelated-test-cache" in page.evaluate("caches.keys()")

            page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=10000)
            context.set_offline(True)
            page.reload(wait_until="domcontentloaded")
            assert page.get_by_role("heading", name="E2E Project (imported)").is_visible(timeout=5000)
            assert page.get_by_text("Offline", exact=True).is_visible()
            context.set_offline(False)

            project_site = context.new_page()
            project_site.goto(origin + "/TCGTableForge/", wait_until="networkidle")
            assert project_site.title() == "TCG TableForge"
            project_site.wait_for_function("navigator.serviceWorker.controller !== null", timeout=10000)
            scope = project_site.evaluate("navigator.serviceWorker.controller.scriptURL")
            assert scope.endswith("/TCGTableForge/sw.js"), scope

            mobile = context.new_page()
            mobile.goto(origin, wait_until="networkidle")
            for viewport_width in (320, 375, 768, 1280):
                mobile.set_viewport_size({"width": viewport_width, "height": 740})
                width = mobile.evaluate("({body:document.body.scrollWidth, viewport:innerWidth})")
                assert width["body"] <= width["viewport"], (viewport_width, width)
            mobile.set_viewport_size({"width": 320, "height": 740})
            mobile.locator("#listView").click()
            audit_touch_targets(mobile)
            for viewport_width in (320, 375, 768, 1280):
                mobile.set_viewport_size({"width": viewport_width, "height": 740})
                width = mobile.evaluate("({body:document.body.scrollWidth, viewport:innerWidth})")
                assert width["body"] <= width["viewport"], ("List view", viewport_width, width)
            mobile.set_viewport_size({"width": 320, "height": 740})
            mobile.locator("#guideBtn").click()
            audit_modal_fit(mobile)
            width = mobile.evaluate("({body:document.body.scrollWidth, viewport:innerWidth})")
            assert width["body"] <= width["viewport"], ("Guide", width)
            mobile.locator("[data-close-guide]").click()
            mobile.locator("#filesBtn").click()
            audit_modal_fit(mobile)
            mobile.locator("[data-cancel]").click()
            mobile.locator("#settingsBtn").click()
            audit_modal_fit(mobile)
            mobile.locator("[data-cancel]").click()
            mobile.locator("#mobileProjectSwitch").click()
            audit_modal_fit(mobile)
            mobile.locator("[data-cancel]").click()
            mobile.locator("#newProject").click()
            audit_modal_fit(mobile)
            mobile.locator("[data-cancel]").click()
            mobile.locator(".list-row").first.click()
            audit_modal_fit(mobile)
            mobile.locator("[data-cancel]").click()
            mobile.locator("#boardView").click()
            mobile.locator("[data-card-links]").first.click()
            audit_modal_fit(mobile)
            mobile.locator("[data-cancel]").click()
            mobile.locator("#connectCards").click()
            audit_modal_fit(mobile)
            mobile.locator("[data-cancel]").click()
            audit_accessible_names(mobile)
            assert all(url.startswith(origin) for url in requests), requests

            before_failure = mobile.evaluate("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))[0].cards[0].notes")
            mobile.locator(".card-main, .list-row").first.click()
            mobile.evaluate("""() => {
              window.__tableForgeOriginalSetItem = Storage.prototype.setItem;
              Storage.prototype.setItem = function(key, value) {
                if (key === 'world-mechanic-projects-v1') throw new DOMException('Storage is full', 'QuotaExceededError');
                return window.__tableForgeOriginalSetItem.call(this, key, value);
              };
            }""")
            mobile.locator("#cardNotes").fill("This edit cannot be stored")
            mobile.locator("#saveCard").click()
            mobile.get_by_text("Could not save locally", exact=False).wait_for(timeout=5000)
            assert mobile.evaluate("JSON.parse(localStorage.getItem('world-mechanic-projects-v1'))[0].cards[0].notes") == before_failure
            mobile.reload(wait_until="networkidle")

            mobile.locator("#settingsBtn").click()
            mobile.once("dialog", lambda dialog: dialog.accept())
            mobile.locator("#deleteAllBtn").click()
            assert mobile.get_by_text("Your design space is ready").is_visible()
            mobile.wait_for_function("localStorage.getItem('world-mechanic-projects-v1') === '[]'", timeout=5000)

            keyboard_context = browser.new_context(viewport={"width": 1280, "height": 900})
            keyboard_page = keyboard_context.new_page()
            keyboard_page.goto(origin, wait_until="networkidle")
            keyboard_page.get_by_role("dialog").wait_for()
            keyboard_page.keyboard.press("Escape")
            assert keyboard_page.get_by_role("dialog").count() == 0
            keyboard_page.keyboard.press("Tab")
            assert keyboard_page.locator("#newProject").evaluate("el => document.activeElement === el")
            keyboard_page.keyboard.press("Enter")
            keyboard_page.get_by_role("dialog").wait_for()
            keyboard_page.keyboard.insert_text("Keyboard project")
            tab_to(keyboard_page, "#createProject")
            keyboard_page.keyboard.press("Enter")
            keyboard_page.get_by_role("heading", name="Keyboard project").wait_for()
            tab_to(keyboard_page, "#emptyAdd")
            keyboard_page.keyboard.press("Enter")
            keyboard_page.get_by_role("dialog").wait_for()
            tab_to(keyboard_page, "#cardType")
            keyboard_page.keyboard.press("ArrowDown")
            tab_to(keyboard_page, "#cardTitle")
            keyboard_page.keyboard.insert_text("Keyboard card")
            tab_to(keyboard_page, "#cardNotes")
            keyboard_page.keyboard.insert_text("Added without a mouse")
            tab_to(keyboard_page, "#saveCard")
            keyboard_page.keyboard.press("Enter")
            keyboard_page.wait_for_timeout(250)
            assert keyboard_page.get_by_text("Keyboard card", exact=True).count() == 1, keyboard_page.locator("body").inner_text()
            tab_to(keyboard_page, "#filter")
            keyboard_page.keyboard.press("ArrowDown")
            keyboard_page.keyboard.press("ArrowDown")
            keyboard_page.keyboard.press("Enter")
            assert keyboard_page.locator(".card").count() == 1
            tab_to(keyboard_page, "#sort")
            keyboard_page.keyboard.press("ArrowDown")
            keyboard_page.keyboard.press("Enter")
            tab_to(keyboard_page, "#listView")
            keyboard_page.keyboard.press("Enter")
            tab_to(keyboard_page, ".list-row")
            keyboard_page.keyboard.press("Space")
            keyboard_page.get_by_role("dialog").wait_for()
            keyboard_page.keyboard.press("Escape")
            assert keyboard_page.get_by_role("dialog").count() == 0
            tab_to(keyboard_page, "#newProject")
            keyboard_page.keyboard.press("Enter")
            tab_to(keyboard_page, "#projectName")
            keyboard_page.keyboard.insert_text("Second keyboard project")
            tab_to(keyboard_page, "#createProject")
            keyboard_page.keyboard.press("Enter")
            keyboard_page.get_by_role("heading", name="Second keyboard project").wait_for()
            tab_to(keyboard_page, "#projectList [data-open]:nth-child(2)")
            keyboard_page.keyboard.press("Enter")
            keyboard_page.get_by_role("heading", name="Keyboard project").wait_for()
            tab_to(keyboard_page, "#projectList [data-open]:nth-child(1)")
            keyboard_page.keyboard.press("Enter")
            keyboard_page.get_by_role("heading", name="Second keyboard project").wait_for()
            keyboard_context.close()

            restart_path = str(Path(profile) / "restart-profile")
            restart_context = playwright.chromium.launch_persistent_context(restart_path, **launch, viewport={"width": 1280, "height": 900})
            restart_page = restart_context.pages[0]
            restart_page.goto(origin, wait_until="networkidle")
            if restart_page.locator("[data-close-guide]").count():
                restart_page.locator("[data-close-guide]").click()
            restart_page.locator("#newProject").click()
            restart_page.locator("#projectName").fill("Restart persistence")
            restart_page.locator("#createProject").click()
            restart_page.locator("#emptyAdd").click()
            restart_page.locator("#cardTitle").fill("Saved card")
            restart_page.locator("#saveCard").click()
            restart_page.wait_for_function("JSON.parse(localStorage.getItem('world-mechanic-projects-v1') || '[]').length === 1")
            restart_context.close()
            restart_context = playwright.chromium.launch_persistent_context(restart_path, **launch, viewport={"width": 1280, "height": 900})
            restart_page = restart_context.pages[0]
            restart_page.goto(origin, wait_until="networkidle")
            assert restart_page.get_by_role("heading", name="Restart persistence").is_visible()
            assert restart_page.get_by_text("Saved card", exact=True).is_visible()
            restart_context.close()
            assert not errors, errors
            context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    print("Browser smoke checks passed.")


if __name__ == "__main__":
    run()
