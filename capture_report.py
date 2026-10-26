"""Capture real MoodSense text-analysis results for the lab report."""
import threading
from pathlib import Path
from http.server import ThreadingHTTPServer
from playwright.sync_api import sync_playwright, expect
from web_app import MoodSenseHandler

shots = Path(__file__).parent / 'report' / 'screenshots'
shots.mkdir(parents=True, exist_ok=True)
cases = [
    ('happy', 'I am very happy today'),
    ('sad', 'I feel lonely and sad'),
    ('angry', 'I am extremely angry'),
    ('love', 'I love this so much'),
    ('surprised', "Wow, I didn't expect this!"),
    ('neutral', 'I am okay'),
]
server = ThreadingHTTPServer(('127.0.0.1', 0), MoodSenseHandler)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width':1093, 'height':614}, device_scale_factor=2)
        page.goto(f'http://127.0.0.1:{server.server_port}')
        page.wait_for_selector('#scene canvas')
        for key, sentence in cases:
            page.locator('#feeling').fill(sentence)
            page.locator('#analyze').click()
            expect(page.locator('#label')).to_have_text(key.upper())
            expect(page.locator('#analyze')).to_be_enabled()
            page.wait_for_timeout(850)
            page.screenshot(path=str(shots / f'{key}.png'))
        browser.close()
finally:
    server.shutdown()
    server.server_close()
print('Captured six real analysis results in', shots)
