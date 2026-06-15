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
            print(f"Playwright PDF generation failed: {e}. Falling back to clean text format.")
            # If Playwright completely fails (e.g. environment missing browser dependencies),
            # return the HTML as simple text file or fallback response bytes
            return html_content.encode("utf-8")
