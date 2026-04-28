import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Color palette
PRIMARY = colors.HexColor("#1a1a2e")
ACCENT = colors.HexColor("#e94560")
SUCCESS = colors.HexColor("#0f9b58")
WARNING = colors.HexColor("#f5a623")
DANGER = colors.HexColor("#e94560")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
MID_GRAY = colors.HexColor("#cccccc")
WHITE = colors.white

SEVERITY_COLORS = {
    "HIGH": DANGER,
    "MEDIUM": WARNING,
    "LOW": SUCCESS
}


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "Title",
            parent=base["Normal"],
            fontSize=24,
            fontName="Helvetica-Bold",
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=6
        ),
        "subtitle": ParagraphStyle(
            "Subtitle",
            parent=base["Normal"],
            fontSize=11,
            fontName="Helvetica",
            textColor=colors.HexColor("#cccccc"),
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        "section_header": ParagraphStyle(
            "SectionHeader",
            parent=base["Normal"],
            fontSize=13,
            fontName="Helvetica-Bold",
            textColor=PRIMARY,
            spaceBefore=16,
            spaceAfter=8
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontSize=10,
            fontName="Helvetica",
            textColor=colors.HexColor("#333333"),
            spaceAfter=6,
            leading=16
        ),
        "label": ParagraphStyle(
            "Label",
            parent=base["Normal"],
            fontSize=9,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#666666"),
            spaceAfter=2
        ),
        "small": ParagraphStyle(
            "Small",
            parent=base["Normal"],
            fontSize=8,
            fontName="Helvetica",
            textColor=colors.HexColor("#999999")
        ),
        "url": ParagraphStyle(
            "URL",
            parent=base["Normal"],
            fontSize=8,
            fontName="Helvetica",
            textColor=colors.HexColor("#0066cc"),
            spaceAfter=4
        )
    }
    return styles


def header_block(story, styles, asset: dict, report_id: str):
    """Dark header banner with report title"""

    header_data = [[
        Paragraph("🛡️ SportShield AI", styles["title"]),
        Paragraph("Digital Asset Protection Report", styles["subtitle"]),
        Paragraph(f"Report ID: {report_id}", styles["small"]),
        Paragraph(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            styles["small"]
        )
    ]]

    header_table = Table(header_data, colWidths=[6.5 * inch])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), 8),
    ]))

    story.append(header_table)
    story.append(Spacer(1, 16))


def summary_block(story, styles, asset: dict, violations: list):
    """3-column summary stats row"""

    total = len(violations)
    high = sum(1 for v in violations if v.get("severity") == "HIGH")
    medium = sum(1 for v in violations if v.get("severity") == "MEDIUM")
    low = sum(1 for v in violations if v.get("severity") == "LOW")
    
    valid_conf = [v.get("confidence", 0) for v in violations if v.get("confidence") is not None]
    avg_conf = round(sum(valid_conf) / len(valid_conf), 1) if valid_conf else 0


    stats = [
        ["Total Violations", "High Severity", "Avg Confidence"],
        [str(total), str(high), f"{avg_conf}%"]
    ]

    stat_table = Table(stats, colWidths=[2.16 * inch] * 3)
    stat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 22),
        ("TEXTCOLOR", (0, 1), (0, 1), ACCENT if total > 0 else SUCCESS),
        ("TEXTCOLOR", (1, 1), (1, 1), DANGER if high > 0 else SUCCESS),
        ("TEXTCOLOR", (2, 1), (2, 1), PRIMARY),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), 4),
    ]))

    story.append(Paragraph("Summary", styles["section_header"]))
    story.append(stat_table)
    story.append(Spacer(1, 12))


def asset_info_block(story, styles, asset: dict):
    """Asset metadata table"""

    story.append(Paragraph("Protected Asset Details", styles["section_header"]))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
    story.append(Spacer(1, 8))

    rows = [
        ["Asset ID", asset.get("asset_id", "N/A")],
        ["Original Filename", asset.get("original_filename", "N/A")],
        ["Sport", asset.get("sport", "N/A")],
        ["Team", asset.get("team", "N/A")],
        ["Event", asset.get("event", "N/A")],
        ["Owner", asset.get("owner", "N/A")],
        ["Upload Date", asset.get("uploaded_at", "N/A")],
    ]

    table = Table(rows, colWidths=[2 * inch, 4.5 * inch])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#555555")),
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.3, MID_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))


def violation_card(story, styles, violation: dict, index: int):
    """Single violation card with severity badge"""

    severity = violation.get("severity", "LOW")
    confidence = violation.get("confidence", 0)
    sev_color = SEVERITY_COLORS.get(severity, SUCCESS)

    # Card header row
    header_data = [[
        Paragraph(f"Violation #{index + 1}", ParagraphStyle(
            "VH", fontSize=11, fontName="Helvetica-Bold", textColor=WHITE
        )),
        Paragraph(f"● {severity}", ParagraphStyle(
            "VS", fontSize=10, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_RIGHT
        ))
    ]]

    header = Table(header_data, colWidths=[4 * inch, 2.5 * inch])
    header.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), sev_color),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (0, -1), 12),
        ("RIGHTPADDING", (-1, 0), (-1, -1), 12),
    ]))
    story.append(header)

    # Card body
    body_rows = [
        [Paragraph("Page URL", styles["label"]),
         Paragraph(violation.get("page_url", "N/A")[:80], styles["url"])],
        [Paragraph("Image URL", styles["label"]),
         Paragraph(violation.get("image_url", "N/A")[:80], styles["url"])],
        [Paragraph("Confidence", styles["label"]),
         Paragraph(f"{confidence}%", styles["body"])],
        [Paragraph("Similarity Score", styles["label"]),
         Paragraph(str(violation.get("clip_similarity", "N/A")), styles["body"])],
        [Paragraph("Detected At", styles["label"]),
         Paragraph(violation.get("detected_at", "N/A"), styles["body"])],
    ]

    body_table = Table(body_rows, colWidths=[1.5 * inch, 5 * inch])
    body_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.3, MID_GRAY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(body_table)

    # Legal explanation
    explanation = violation.get("explanation", "")
    if explanation:
        exp_data = [[Paragraph(explanation, styles["body"])]]
        exp_table = Table(exp_data, colWidths=[6.5 * inch])
        exp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), WHITE),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ]))
        story.append(exp_table)

    # Recommended action footer
    action = violation.get("recommended_action", "")
    if action:
        action_data = [[
            Paragraph("⚡ Recommended Action", ParagraphStyle(
                "AL", fontSize=9, fontName="Helvetica-Bold",
                textColor=sev_color
            )),
            Paragraph(action, styles["body"])
        ]]
        action_table = Table(action_data, colWidths=[1.8 * inch, 4.7 * inch])
        action_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fafafa")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 1, sev_color),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(action_table)

    story.append(Spacer(1, 14))


def generate_report(
    asset: dict,
    violations: list,
    report_id: str,
    output_dir: str = "reports"
) -> str:
    """
    Generate full PDF violation report.
    Returns the file path of the generated PDF.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{report_id}.pdf")

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch
    )

    styles = build_styles()
    story = []

    # Build report sections
    header_block(story, styles, asset, report_id)
    summary_block(story, styles, asset, violations)
    asset_info_block(story, styles, asset)

    # Violations section
    if violations:
        story.append(Paragraph("Detected Violations", styles["section_header"]))
        story.append(HRFlowable(width="100%", thickness=1, color=MID_GRAY))
        story.append(Spacer(1, 8))

        # Sort HIGH first
        sorted_violations = sorted(
            violations,
            key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(
                x.get("severity", "LOW"), 2
            )
        )

        for i, violation in enumerate(sorted_violations):
            violation_card(story, styles, violation, i)

    else:
        story.append(Paragraph(
            " No violations detected. Your asset appears to be protected.",
            styles["body"]
        ))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated by SportShield AI — {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} — Report ID: {report_id}",
        styles["small"]
    ))

    doc.build(story)
    print(f"Report generated: {file_path}")
    return file_path