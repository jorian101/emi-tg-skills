#!/usr/bin/env python3
"""Capture a static thesis mockup at the canonical 1200x800 viewport."""

from pathlib import Path
import sys

from playwright.sync_api import sync_playwright


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("uso: mockup-html-to-png.py entrada.html salida.png")

    html_path = Path(sys.argv[1]).resolve()
    png_path = Path(sys.argv[2]).resolve()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 800})
        page.goto(html_path.as_uri())
        page.screenshot(path=str(png_path), full_page=False)
        browser.close()


if __name__ == "__main__":
    main()
