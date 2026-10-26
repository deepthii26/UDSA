"""End-to-end regression checks. Requires playwright and installed Edge.

Run: python test_browser.py
Test tooling is optional and not needed to run MoodSense.
"""
import threading
from http.server import ThreadingHTTPServer

from playwright.sync_api import sync_playwright, expect
from web_app import MoodSenseHandler


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), MoodSenseHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel='msedge', headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 900})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(url)
            expect(page.locator('#scene canvas')).to_have_count(1)
            expect(page.locator('.pick')).to_have_count(6)
            expect(page.locator('#feeling')).to_have_value('')
            page.locator('#analyze').click()
            expect(page.locator('#validation')).to_contain_text('Please enter')
            cases = [
                ('I am very happy today', 'happy'),
                ('I feel lonely and sad', 'sad'),
                ('I am extremely angry', 'angry'),
                ('I love this so much', 'love'),
                ("Wow, I didn't expect this!", 'surprised'),
                ('I am okay', 'neutral'),
                ('The clouds are above the building', 'neutral'),
                ('I am not happy about this', 'sad'),
                ('😊', 'happy'), ('😢', 'sad'), ('😡', 'angry'),
                ('❤', 'love'), ('❤️', 'love'), ('😲', 'surprised'), ('😐', 'neutral'),
            ]
            for text, key in cases:
                page.locator('#feeling').fill(text)
                page.locator('#analyze').click()
                expect(page.locator('#analyze')).to_be_enabled()
                expect(page.locator('#label')).to_have_text(key.upper())
            for key in ('happy', 'sad', 'angry', 'love', 'surprised', 'neutral'):
                page.locator(f'[data-key={key}]').click()
                expect(page.locator('#label')).to_have_text(key.upper())
                expect(page.locator('#confidence')).to_have_text('Emoji selection')
            page.locator('#reset').click()
            expect(page.locator('#feeling')).to_have_value('')
            expect(page.locator('#label')).to_have_text('Welcome to MoodSense')
            assert not errors, errors
            # Laptop windows must show every control without page scrolling.
            for width, height in [(1366, 768), (1280, 650), (1093, 614), (1024, 600), (1536, 864)]:
                page.set_viewport_size({'width': width, 'height': height})
                for key in ('happy', 'sad', 'angry', 'love', 'surprised', 'neutral'):
                    page.locator(f'[data-key={key}]').click()
                    dimensions = page.evaluate('''() => ({
                        width: document.documentElement.scrollWidth,
                        height: document.documentElement.scrollHeight,
                        resetBottom: document.querySelector('#reset').getBoundingClientRect().bottom
                    })''')
                    assert dimensions['width'] <= width, dimensions
                    assert dimensions['height'] <= height, dimensions
                    assert dimensions['resetBottom'] <= height, dimensions
            page.set_viewport_size({'width': 390, 'height': 844})
            assert page.evaluate('document.documentElement.scrollWidth') <= 390
            page.set_viewport_size({'width': 1280, 'height': 900})
            # A failed graphics module must not disable application controls.
            page.route('**/app.js', lambda route: route.abort())
            page.reload()
            page.locator('#feeling').fill('I love this so much')
            page.locator('#analyze').click()
            expect(page.locator('#label')).to_have_text('LOVE')
            # Server failure is visible and leaves the button usable.
            page.route('**/api/analyze', lambda route: route.abort())
            page.locator('#analyze').click()
            expect(page.locator('#validation')).to_contain_text('Could not reach')
            expect(page.locator('#analyze')).to_be_enabled()
            browser.close()
            print(f'PASS: {len(cases)} text/emoji inputs, six picks, validation, reset, 3D, fallback, and network failure.')
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    main()
