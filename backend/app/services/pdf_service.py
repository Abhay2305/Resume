import os
import subprocess
from playwright.sync_api import sync_playwright

class PDFExportService:
    @staticmethod
    def html_to_pdf(html_content: str) -> bytes:
        """
        Converts raw HTML string into an A4 PDF byte stream using Playwright.
        Includes automated headless Chromium installation checks to make local setup painless.
        """
        try:
            # Ensure playwright browsers are installed
            try:
                # Test if we can launch playwright
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    browser.close()
            except Exception as ex:
                print(f"Playwright chromium not detected, attempting auto-installation: {ex}")
                subprocess.run(["playwright", "install", "chromium"], check=False)
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Make sure styles are rendered correctly by setting viewport
                page.set_viewport_size({"width": 794, "height": 1123})  # A4 size in pixels at 96 DPI
                
                page.set_content(html_content)
                # Wait for styles and network to settle
                page.wait_for_load_state("networkidle")
                page.wait_for_load_state("domcontentloaded")
                
                # Print to PDF with full colors and layout options
                pdf_bytes = page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "0in", "bottom": "0in", "left": "0in", "right": "0in"}
                )
                browser.close()
                return pdf_bytes
        except Exception as e:
            # Surface the failure instead of returning HTML bytes mislabeled as a
            # PDF (which produces a corrupt download). The router converts this
            # into a clear HTTP 500 so the client can show a real error.
            print(f"Playwright PDF generation failed: {e}")
            raise RuntimeError(
                "PDF rendering is unavailable. Ensure Playwright Chromium is installed "
                f"on the server (playwright install chromium). Original error: {e}"
            )
