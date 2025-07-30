"""
Example showing how to use AkvoFormPrint with Akvo Flow forms.
"""

import json
from pathlib import Path

from AkvoFormPrint.stylers.weasyprint_styler import WeasyPrintStyler
from AkvoFormPrint.stylers.docx_renderer import DocxRenderer

# Define paths
DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main(filename: str):
    # Load Flow form data
    with open(DATA_DIR / f"{filename}.json", "r", encoding="utf-8") as f:
        flow_json = json.load(f)

    # Initialize styler with Flow parser
    styler = WeasyPrintStyler(
        orientation="landscape",
        add_section_numbering=False,
        add_question_numbering=False,
        parser_type="flow",
        raw_json=flow_json,
    )

    # Generate HTML
    html_content = styler.render_html()
    html_path = OUTPUT_DIR / f"{filename}.html"
    html_path.write_text(html_content, encoding="utf-8")
    print(f"HTML saved to {html_path}")

    # Generate PDF
    pdf_content = styler.render_pdf()
    pdf_path = OUTPUT_DIR / f"{filename}.pdf"
    pdf_path.write_bytes(pdf_content)
    print(f"PDF saved to {pdf_path}")

    # Generate DOCX
    docx_path = OUTPUT_DIR / f"{filename}.docx"
    renderer = DocxRenderer(
        orientation="landscape",
        add_section_numbering=False,
        add_question_numbering=False,
        parser_type="flow",
        raw_json=flow_json,
        output_path=docx_path,
    )
    renderer.render_docx()
    print(f"DOCX saved to {docx_path}")


if __name__ == "__main__":
    forms = ["flow_form"]
    for f in forms:
        main(filename=f)
