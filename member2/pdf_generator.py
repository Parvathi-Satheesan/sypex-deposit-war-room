"""
Deposit War Room - PDF Settlement Generator
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime
from typing import Dict, Any, List


def _money(v: float) -> str:
    return f"₹{v:,.0f}"


def generate_settlement_pdf(
    filename: str,
    tenant_name: str,
    landlord_name: str,
    deposit: float,
    calc_results: Dict[str, Any],
    *,
    property_address: str = "",
    case_id: str = "",
    rent: float = 0,
    stayed_months: int = 0,
    additional_notes: str = "",
) -> str:

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Heading1"], fontSize=16,
        textColor=colors.HexColor("#1E3A8A"), alignment=TA_CENTER,
        spaceAfter=4, fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"], fontSize=9,
        textColor=colors.HexColor("#475569"), alignment=TA_CENTER, spaceAfter=8,
    )
    section_style = ParagraphStyle(
        "SectionStyle", parent=styles["Heading2"], fontSize=11,
        textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["Normal"], fontSize=9, leading=12, alignment=TA_JUSTIFY,
    )
    small_style = ParagraphStyle(
        "SmallStyle", parent=styles["Normal"], fontSize=8,
        textColor=colors.HexColor("#64748B"), leading=10,
    )
    log_style = ParagraphStyle(
        "LogStyle", parent=styles["Normal"], fontSize=8, leading=11, leftIndent=4,
    )

    story: List = []

    # Header
    story.append(Paragraph("BINDING SETTLEMENT AGREEMENT", title_style))
    story.append(Paragraph(
        "Online Dispute Resolution Platform for Residential Tenancy Deposits<br/>"
        "Under the Karnataka Rent Act, 1999 (as amended) &amp; contractual principles",
        subtitle_style,
    ))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    # Meta
    meta_data = [[
        Paragraph(f"<b>Case ID:</b> {case_id or 'ODR-' + datetime.now().strftime('%Y%m%d-%H%M')}", small_style),
        Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%d %b %Y, %H:%M IST')}", small_style),
    ]]
    meta_table = Table(meta_data, colWidths=[95 * mm, 75 * mm])
    meta_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Parties
    story.append(Paragraph("1. Parties &amp; Property", section_style))
    parties_text = f"<b>Landlord:</b> {landlord_name}<br/><b>Tenant:</b> {tenant_name}<br/>"
    if property_address:
        parties_text += f"<b>Property:</b> {property_address}<br/>"
    if rent:
        parties_text += f"<b>Monthly Rent:</b> {_money(rent)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Occupation:</b> {stayed_months} months"
    story.append(Paragraph(parties_text, body_style))
    story.append(Spacer(1, 4))

    # Financial Summary
    story.append(Paragraph("2. Financial Summary", section_style))

    total_valid = calc_results.get("total_valid_deductions", 0)
    final_refund = calc_results.get("final_refund", 0)

    summary_data = [
        [Paragraph("<b>Description</b>", body_style), Paragraph("<b>Amount</b>", body_style)],
        ["Initial Security Deposit Held", _money(deposit)],
        ["Total Approved Deductions", _money(total_valid)],
        [Paragraph("<b>FINAL REFUND DUE TO TENANT</b>", body_style),
         Paragraph(f"<b>{_money(final_refund)}</b>", body_style)],
    ]

    summary_table = Table(summary_data, colWidths=[120 * mm, 50 * mm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#DCFCE7")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # Itemised breakdown
    breakdown = calc_results.get("breakdown") or calc_results.get("valid_deductions") or {}
    rejected = calc_results.get("rejected") or calc_results.get("rejected_deductions") or {}

    if breakdown or rejected:
        story.append(Paragraph("3. Itemised Deduction Decisions", section_style))
        rows = [[Paragraph("<b>Claim</b>", small_style),
                 Paragraph("<b>Amount</b>", small_style),
                 Paragraph("<b>Decision</b>", small_style)]]

        for desc, amt in breakdown.items():
            rows.append([
                Paragraph(desc, small_style),
                Paragraph(_money(amt), small_style),
                Paragraph("<font color='#15803D'><b>APPROVED</b></font>", small_style),
            ])
        for desc, amt in rejected.items():
            rows.append([
                Paragraph(desc, small_style),
                Paragraph(_money(amt), small_style),
                Paragraph("<font color='#B91C1C'><b>REJECTED</b></font>", small_style),
            ])

        item_table = Table(rows, colWidths=[95 * mm, 35 * mm, 40 * mm])
        item_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(item_table)
        story.append(Spacer(1, 6))

    # Decision Log
    logs = calc_results.get("logs", [])
    if logs:
        story.append(Paragraph("4. Rules Engine Decision Log", section_style))
        for entry in logs:
            story.append(Paragraph(entry.replace("₹", "Rs."), log_style))
        story.append(Spacer(1, 4))

    warnings = calc_results.get("warnings", [])
    if warnings:
        story.append(Paragraph("5. Warnings / Notes", section_style))
        for w in warnings:
            story.append(Paragraph(f"• {w}", small_style))
        story.append(Spacer(1, 4))

    # Legal clause
    story.append(Paragraph("6. Binding Effect", section_style))
    legal = (
        "This document records the outcome of the Online Dispute Resolution process for the "
        "security deposit under the tenancy between the parties named above. Both parties "
        "acknowledge that the Final Refund figure stated herein constitutes a full and final "
        "settlement of all claims relating to the security deposit for the said premises. "
        "Payment of the Final Refund within the agreed timeline discharges the landlord of "
        "further liability in respect of the deposit."
    )
    story.append(Paragraph(legal, body_style))
    story.append(Spacer(1, 6))

    if additional_notes:
        story.append(Paragraph("Additional Notes", section_style))
        story.append(Paragraph(additional_notes, body_style))
        story.append(Spacer(1, 6))

    # Signatures
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#94A3B8"), spaceAfter=8))

    sig_data = [[
        Paragraph("<b>Landlord Acceptance</b><br/><br/><br/>Signature / Digital Acceptance<br/>Date: _______________", small_style),
        Paragraph("<b>Tenant Acceptance</b><br/><br/><br/>Signature / Digital Acceptance<br/>Date: _______________", small_style),
    ]]
    sig_table = Table(sig_data, colWidths=[85 * mm, 85 * mm])
    sig_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(sig_table)

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Generated by Deposit War Room ODR Platform • For demonstration / hackathon use.",
        ParagraphStyle("Footer", parent=small_style, alignment=TA_CENTER, fontSize=7),
    ))

    doc.build(story)
    return filename
