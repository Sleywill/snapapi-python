"""
PDF generation example.

Usage:
    SNAPAPI_KEY=sk_live_... python examples/pdf_generation.py
"""

import os

from snapapi import SnapAPI

with SnapAPI(api_key=os.environ["SNAPAPI_KEY"]) as snap:
    # Convert a URL to PDF with custom margins
    pdf_data = snap.pdf(
        url="https://example.com",
        page_size="a4",
        margins={"top": "20mm", "bottom": "20mm", "left": "15mm", "right": "15mm"},
    )
    with open("output.pdf", "wb") as f:
        f.write(pdf_data)
    print(f"Saved output.pdf ({len(pdf_data)} bytes)")

    # Generate PDF from raw HTML
    invoice_pdf = snap.pdf(
        html="""
        <html>
          <body style="font-family: Arial, sans-serif; padding: 40px;">
            <h1>Invoice #1234</h1>
            <p>Date: 2026-03-28</p>
            <p>Total: $79.00</p>
          </body>
        </html>
        """,
        landscape=False,
    )
    with open("invoice.pdf", "wb") as f:
        f.write(invoice_pdf)
    print(f"Saved invoice.pdf ({len(invoice_pdf)} bytes)")

    # Save directly to file (convenience)
    snap.pdf_to_file("https://example.com", "./quick.pdf", page_size="letter")
    print("Saved quick.pdf")
