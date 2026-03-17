'''
import json
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()


# -----------------------------
# FLATTEN JSON
# -----------------------------
def flatten_json(data, parent_key=""):
    items = []

    for k, v in data.items():
        new_key = f"{parent_key}.{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key))
        elif isinstance(v, list):
            items.append((new_key, ", ".join(map(str, v))))
        else:
            items.append((new_key, str(v)))

    return items


# -----------------------------
# HEADER
# -----------------------------
def draw_header(canvas, doc):
    canvas.saveState()

    width, height = A4
    date = datetime.now().strftime("%d %b %Y")

    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 40, height - 30, f"Generated on {date}")

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(2)
    canvas.line(40, height - 105, width - 40, height - 105)

    canvas.restoreState()


# -----------------------------
# FOOTER
# -----------------------------
def draw_footer(canvas, doc):
    canvas.saveState()

    width, _ = A4
    page_num = canvas.getPageNumber()

    canvas.setLineWidth(1)
    canvas.line(40, 35, width - 40, 35)

    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(width - 40, 20, f"Page {page_num}")

    canvas.restoreState()


# -----------------------------
# CREATE FACE SHEET (ONLY)
# -----------------------------
def generate_facesheet(data: dict) -> bytes:
    buffer = BytesIO()

    elements = []

    title = Paragraph("<b>Candidate Details</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 20))

    rows = [["Field", "Value"]]

    flat_data = flatten_json(data)

    for key, value in flat_data:
        rows.append([
            Paragraph(f"<b>{key}</b>", styles["Normal"]),
            Paragraph(value, styles["Normal"])
        ])

    table = Table(rows, colWidths=[2.2 * inch, 4.8 * inch], repeatRows=1)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(table)

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=140,
        bottomMargin=50
    )

    pdf.build(elements, onFirstPage=draw_header, onLaterPages=draw_footer)

    buffer.seek(0)
    return buffer.read()'''

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()


# -----------------------------
# FLATTEN JSON
# -----------------------------
def flatten_json(data, parent_key=""):
    items = []

    for k, v in data.items():
        new_key = f"{parent_key}.{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key))
        elif isinstance(v, list):
            items.append((new_key, ", ".join(map(str, v))))
        else:
            items.append((new_key, str(v)))

    return items


# -----------------------------
# HEADER
# -----------------------------
def draw_header(canvas, doc):
    canvas.saveState()

    width, height = A4
    date = datetime.now().strftime("%d %b %Y")

    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 40, height - 30, f"Generated on {date}")

    canvas.setStrokeColor(colors.black)
    canvas.setLineWidth(2)
    canvas.line(40, height - 105, width - 40, height - 105)

    canvas.restoreState()


# -----------------------------
# FOOTER
# -----------------------------
def draw_footer(canvas, doc):
    canvas.saveState()

    width, _ = A4
    page_num = canvas.getPageNumber()

    canvas.setLineWidth(1)
    canvas.line(40, 35, width - 40, 35)

    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(width - 40, 20, f"Page {page_num}")

    canvas.restoreState()


# -----------------------------
# GENERATE FACE SHEET
# -----------------------------
def generate_facesheet(candidate_data: dict) -> bytes:
    buffer = BytesIO()
    elements = []

    title = Paragraph("<b>Candidate Details</b>", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 20))

    rows = [["Field", "Value"]]
    flat_data = flatten_json(candidate_data)

    for key, value in flat_data:
        rows.append([
            Paragraph(f"<b>{key}</b>", styles["Normal"]),
            Paragraph(value, styles["Normal"])
        ])

    table = Table(rows, colWidths=[2.2 * inch, 4.8 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(table)

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=140,
        bottomMargin=50
    )

    pdf.build(elements, onFirstPage=draw_header, onLaterPages=draw_footer)
    buffer.seek(0)
    return buffer.read()