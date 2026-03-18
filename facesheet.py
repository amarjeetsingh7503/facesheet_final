from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors

styles = getSampleStyleSheet()


# -----------------------------
# CUSTOM STYLES
# -----------------------------
title_style = ParagraphStyle(
    name="TitleStyle",
    fontSize=18,
    leading=22,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#313647"),
    spaceAfter=15
)

field_style = ParagraphStyle(
    name="FieldStyle",
    fontSize=10,
    textColor=colors.black
)

value_style = ParagraphStyle(
    name="ValueStyle",
    fontSize=10,
    textColor=colors.HexColor("#333333")
)


# -----------------------------
# CLEAN FIELD NAMES
# -----------------------------
def clean_key(key):
    return key.replace("_", " ").replace("'", "").title()


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

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(width - 40, height - 40, f"Generated on {date}")

    canvas.setStrokeColor(colors.HexColor("#313647"))
    canvas.setLineWidth(2)
    canvas.line(40, height - 90, width - 40, height - 90)

    canvas.restoreState()


# -----------------------------
# FOOTER
# -----------------------------
def draw_footer(canvas, doc):
    canvas.saveState()

    width, _ = A4
    page_num = canvas.getPageNumber()

    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(0.8)
    canvas.line(40, 40, width - 40, 40)

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(width - 40, 25, f"Page {page_num}")

    canvas.restoreState()


# -----------------------------
# GENERATE FACE SHEET
# -----------------------------
def generate_facesheet(candidate_data: dict) -> bytes:
    buffer = BytesIO()
    elements = []

    # Title
    elements.append(Paragraph("<b>Candidate Profile</b>", title_style))
    elements.append(Spacer(1, 15))

    # Table Data
    rows = [["Field", "Details"]]
    flat_data = flatten_json(candidate_data)

    for key, value in flat_data:
        rows.append([
            Paragraph(f"<b>{clean_key(key)}</b>", field_style),
            Paragraph(value if value != "None" else "-", value_style)
        ])

    # Table
    table = Table(rows, colWidths=[2.3 * inch, 4.7 * inch], repeatRows=1)

    table_style = TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#313647")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        # Alignment
        ("VALIGN", (0, 0), (-1, -1), "TOP"),

        # Grid (light)
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
    ])

    # Zebra rows
    for i in range(1, len(rows)):
        bg = colors.whitesmoke if i % 2 == 0 else colors.transparent
        table_style.add("BACKGROUND", (0, i), (-1, i), bg)

    table.setStyle(table_style)

    elements.append(table)

    # PDF Build
    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=120,
        bottomMargin=60
    )

    pdf.build(elements, onFirstPage=draw_header, onLaterPages=draw_footer)

    buffer.seek(0)
    return buffer.read()