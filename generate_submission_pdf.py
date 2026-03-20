from __future__ import annotations

from pathlib import Path
from textwrap import wrap


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "submission_report.pdf"


TITLE = "Customer Churn Deployment Submission"


BODY = [
    "Student Submission Report",
    "",
    "GitHub Repository Link:",
    "https://github.com/raorajat10/saras-project",
    "",
    "Project Overview",
    "This submission deploys a customer churn prediction model as a real-time Flask API and includes a batch scoring pipeline that sends each customer record to the API and writes scored output.",
    "",
    "Implementation Summary",
    "- Flask API implemented in app/main.py with a /predict endpoint.",
    "- Model saved in app/model.pkl and preprocessing pipeline saved in app/transformer.pkl.",
    "- Helper functions are included in app/utils.py.",
    "- Batch scoring script implemented in batch.py.",
    "- Test inputs stored in test_data/sample_input.json and test_data/all_customers.csv.",
    "",
    "How the Project Runs",
    "1. Start the API from the project root with: python -m app.main",
    "2. Run batch scoring with: python batch.py --input test_data/all_customers.csv",
    "3. The batch script writes scored_customers.csv and logs/batch_log.txt",
    "",
    "Monitoring and Maintenance",
    "The README includes the required maintenance plan covering retraining, drift detection, and versioning. The batch process logs total requests, failures, and average churn probability using Python logging.",
    "",
    "Submission Structure",
    "- app/__init__.py",
    "- app/main.py",
    "- app/model.pkl",
    "- app/transformer.pkl",
    "- app/utils.py",
    "- test_data/sample_input.json",
    "- test_data/all_customers.csv",
    "- batch.py",
    "- requirements.txt",
    "- README.md",
    "- .gitignore",
]


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def build_lines() -> list[str]:
    lines: list[str] = []
    for paragraph in BODY:
        if not paragraph:
            lines.append("")
            continue
        if paragraph.startswith("- ") or paragraph[:2].isdigit():
            wrapped = wrap(paragraph, width=92, subsequent_indent="   ")
        else:
            wrapped = wrap(paragraph, width=92) or [paragraph]
        lines.extend(wrapped)
    return lines


def content_stream(lines: list[str]) -> bytes:
    stream_lines = [
        "BT",
        "/F1 18 Tf",
        "72 780 Td",
        f"({escape_pdf_text(TITLE)}) Tj",
        "0 -28 Td",
        "/F1 11 Tf",
    ]
    for line in lines:
        safe = escape_pdf_text(line)
        stream_lines.append(f"({safe}) Tj")
        stream_lines.append("0 -15 Td")
    stream_lines.append("ET")
    return "\n".join(stream_lines).encode("latin-1", errors="replace")


def write_pdf(path: Path, stream: bytes) -> None:
    objects: list[bytes] = []

    def add_object(payload: bytes) -> int:
        objects.append(payload)
        return len(objects)

    catalog_id = add_object(b"<< /Type /Catalog /Pages 2 0 R >>")
    pages_id = add_object(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    page_id = add_object(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
    )
    font_id = add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    content_id = add_object(f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1") + stream + b"\nendstream")

    assert [catalog_id, pages_id, page_id, font_id, content_id] == [1, 2, 3, 4, 5]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("latin-1"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode(
            "latin-1"
        )
    )
    path.write_bytes(pdf)


if __name__ == "__main__":
    lines = build_lines()
    stream = content_stream(lines)
    write_pdf(OUTPUT_PATH, stream)
    print(f"Created {OUTPUT_PATH}")
