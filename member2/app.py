import io
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="The Deposit War Room - ODR Platform", layout="wide")

# --- Initialize Persistent Session State ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "tenant_done" not in st.session_state:
    st.session_state.tenant_done = False
if "landlord_done" not in st.session_state:
    st.session_state.landlord_done = False

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- Function to Generate Styled PDF Buffer ---
def generate_pdf_bytes(tenant_name, landlord_name, address, rent, deposit, duration, 
                       painting_claim, allow_painting, fixture_claim, fixture_age, 
                       utility_claim, approved_deductions, final_refund, logs):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1E293B'))
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#64748B'))
    section_heading = ParagraphStyle('SecHeading', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#0F172A'), spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#334155'))
    bold_body = ParagraphStyle('BoldBody', parent=body_style, fontName='Helvetica-Bold')

    elements = []

    # Title Banner
    elements.append(Paragraph("BINDING SETTLEMENT AGREEMENT", title_style))
    elements.append(Paragraph("Online Dispute Resolution Platform for Residential Tenancy Deposits", subtitle_style))
    elements.append(Paragraph("Under the Karnataka Rent Act, 1999 (as amended) & contractual principles", subtitle_style))
    elements.append(Paragraph("<b>Case ID:</b> ODR-2026-BLR-001", subtitle_style))
    elements.append(Spacer(1, 10))

    # 1. Parties & Property
    elements.append(Paragraph("1. Parties & Property", section_heading))
    p_text = f"<b>Landlord:</b> {landlord_name} | <b>Tenant:</b> {tenant_name}<br/>" \
             f"<b>Property:</b> {address}<br/>" \
             f"<b>Monthly Rent:</b> ₹{rent:,.0f} | <b>Occupation:</b> {duration} months"
    elements.append(Paragraph(p_text, body_style))
    elements.append(Spacer(1, 10))

    # 2. Financial Summary Table
    elements.append(Paragraph("2. Financial Summary", section_heading))
    fin_data = [
        [Paragraph("<b>Description</b>", bold_body), Paragraph("<b>Amount (₹)</b>", bold_body)],
        ["Initial Security Deposit Held", f"₹{deposit:,.0f}"],
        ["Total Approved Deductions", f"₹{approved_deductions:,.0f}"],
        [Paragraph("<b>FINAL REFUND DUE TO TENANT</b>", bold_body), Paragraph(f"<b>₹{final_refund:,.0f}</b>", bold_body)]
    ]
    t_fin = Table(fin_data, colWidths=[380, 160])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#E2E8F0'))
    ]))
    elements.append(t_fin)
    elements.append(Spacer(1, 10))

    # 3. Itemised Deduction Decisions Table
    elements.append(Paragraph("3. Itemised Deduction Decisions", section_heading))
    
    p_status = "APPROVED" if allow_painting else "REJECTED"
    deprec_val = max(0.0, fixture_claim * (1 - (0.10 * fixture_age)))
    
    item_data = [
        [Paragraph("<b>Claim</b>", bold_body), Paragraph("<b>Amount (₹)</b>", bold_body), Paragraph("<b>Decision</b>", bold_body)],
        ["Painting Charges", f"₹{painting_claim:,.0f}", p_status],
        ["Fixture / Appliance Damage", f"₹{deprec_val:,.0f}", "APPROVED (Depreciated)"],
        ["Unpaid Electricity / Utility Bill", f"₹{utility_claim:,.0f}", "APPROVED"]
    ]
    t_item = Table(item_data, colWidths=[240, 140, 160])
    t_item.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    elements.append(t_item)
    elements.append(Spacer(1, 10))

    # 4. Rules Engine Decision Log
    elements.append(Paragraph("4. Rules Engine Decision Log", section_heading))
    for log in logs:
        elements.append(Paragraph(f"• {log}", body_style))
    elements.append(Spacer(1, 10))

    # 5. Warnings / Notes
    if deposit > (2 * rent) and rent > 0:
        elements.append(Paragraph("5. Warnings / Notes", section_heading))
        warn_msg = f"• Collected deposit ₹{deposit:,.0f} exceeds the commonly cited 2-month residential guidance (₹{2*rent:,.0f}). Excess ₹{deposit - (2*rent):,.0f} is noted for transparency only."
        elements.append(Paragraph(warn_msg, body_style))
        elements.append(Spacer(1, 10))

    # 6. Binding Effect & Signatures
    elements.append(Paragraph("6. Binding Effect", section_heading))
    binding_text = "This document records the outcome of the Online Dispute Resolution process for the security deposit under the tenancy between the parties named above. Both parties acknowledge that the Final Refund figure stated herein constitutes a full and final settlement of all claims relating to the security deposit for the said premises."
    elements.append(Paragraph(binding_text, body_style))
    elements.append(Spacer(1, 15))

    sig_data = [
        [Paragraph("<b>Landlord Acceptance</b>", bold_body), Paragraph("<b>Tenant Acceptance</b>", bold_body)],
        ["Signature/Digital Acceptance:\n\n_______________________", "Signature/Digital Acceptance:\n\n_______________________"],
        ["Date:", "Date:"]
    ]
    t_sig = Table(sig_data, colWidths=[270, 270])
    t_sig.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 6)
    ]))
    elements.append(t_sig)

    doc.build(elements)
    buffer.seek(0)
    return buffer

# =========================================================
# PAGE 1: LANDING / ROLE SELECTION
# =========================================================
if st.session_state.page == "home":
    st.title("⚖️ The Deposit War Room")
    st.caption("Online Dispute Resolution Platform under Karnataka Rent Act")
    st.divider()

    st.subheader("Select portal to begin dispute resolution:")
    col1, col2 = st.columns(2)

    with col1:
        st.info("### 👤 Start as Tenant")
        st.write("Submit tenancy agreement details, security deposit paid, and requested refund amount.")
        if st.session_state.tenant_done:
            st.success("✅ Tenant details already submitted!")
        if st.button("Start Tenant Intake", type="primary", use_container_width=True):
            go_to("tenant")

    with col2:
        st.warning("### 🏠 Start as Landlord")
        st.write("Itemize property damage deductions, utility arrears, and submit initial refund offer.")
        if st.session_state.landlord_done:
            st.success("✅ Landlord details already submitted!")
        if st.button("Start Landlord Claims", type="primary", use_container_width=True):
            go_to("landlord")

# =========================================================
# PAGE 2: TENANT PORTAL
# =========================================================
elif st.session_state.page == "tenant":
    if st.button("← Back to Home"):
        go_to("home")
    
    st.title("👤 Tenant Intake Portal")
    st.caption("Submit tenancy parameters and review statutory protections under Karnataka Rent Act.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Tenancy Intake Information")
        st.session_state.tenant_name = st.text_input("Tenant Name", value=st.session_state.get("tenant_name", ""))
        st.session_state.address = st.text_input("Property Address", value=st.session_state.get("address", ""))
        st.session_state.duration = st.number_input("Tenancy Duration (Months)", value=st.session_state.get("duration", 0), min_value=0)
    with col2:
        st.subheader("Financial Details")
        st.session_state.rent = st.number_input("Monthly Rent (₹)", value=st.session_state.get("rent", 0), min_value=0)
        st.session_state.deposit = st.number_input("Security Deposit Held (₹)", value=st.session_state.get("deposit", 0), min_value=0)
        st.session_state.requested_refund = st.number_input("Requested Deposit Refund (₹)", value=st.session_state.get("requested_refund", 0), min_value=0)

    if st.button("Save Tenant Data & Proceed →", type="primary"):
        st.session_state.tenant_done = True
        if not st.session_state.landlord_done:
            go_to("landlord")
        else:
            go_to("settlement")

# =========================================================
# PAGE 3: LANDLORD PORTAL
# =========================================================
elif st.session_state.page == "landlord":
    if st.button("← Back to Home"):
        go_to("home")
        
    st.title("🏠 Landlord Claims Portal")
    st.caption("Itemize property damage, maintenance claims, and official refund offers.")
    st.divider()
    
    st.session_state.landlord_name = st.text_input("Landlord Name", value=st.session_state.get("landlord_name", ""))
    
    st.subheader("2. Itemised Claims & Evidence Input")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.painting_claim = st.number_input("Painting Claim Amount (₹)", value=st.session_state.get("painting_claim", 0), min_value=0)
        st.session_state.allow_painting = st.checkbox("Agreement explicitly allows painting deductions?", value=st.session_state.get("allow_painting", False))
    with col2:
        st.session_state.fixture_claim = st.number_input("Fixture Claim Amount (₹)", value=st.session_state.get("fixture_claim", 0), min_value=0)
        st.session_state.fixture_age = st.number_input("Fixture Age (Years)", value=st.session_state.get("fixture_age", 0.0), min_value=0.0)
    with col3:
        st.session_state.utility_claim = st.number_input("Utility Arrears Amount (₹)", value=st.session_state.get("utility_claim", 0), min_value=0)
        st.session_state.evidence_attached = st.checkbox("Evidence Provided?", value=st.session_state.get("evidence_attached", False))

    st.session_state.landlord_offer = st.number_input("Landlord Refund Offer (₹)", value=st.session_state.get("landlord_offer", 0), min_value=0)

    if st.button("Save Landlord Data & Proceed →", type="primary"):
        st.session_state.landlord_done = True
        if not st.session_state.tenant_done:
            go_to("tenant")
        else:
            go_to("settlement")

# =========================================================
# PAGE 4: JOINT SETTLEMENT & DECISION ENGINE
# =========================================================
elif st.session_state.page == "settlement":
    if st.button("← Edit Data / Back to Home"):
        go_to("home")

    st.title("⚖️ Results & Decision Breakdown")
    st.caption("Neutral ODR Engine evaluating submitted tenant and landlord data against statutory rules.")
    st.divider()

    # Retrieve Inputs
    tenant_name = st.session_state.get("tenant_name", "N/A")
    landlord_name = st.session_state.get("landlord_name", "N/A")
    address = st.session_state.get("address", "N/A")
    duration = st.session_state.get("duration", 0)
    rent = st.session_state.get("rent", 0)
    deposit = st.session_state.get("deposit", 0)
    painting_claim = st.session_state.get("painting_claim", 0)
    allow_painting = st.session_state.get("allow_painting", False)
    fixture_claim = st.session_state.get("fixture_claim", 0)
    fixture_age = st.session_state.get("fixture_age", 0.0)
    utility_claim = st.session_state.get("utility_claim", 0)
    landlord_offer = st.session_state.get("landlord_offer", 0)
    requested_refund = st.session_state.get("requested_refund", 0)

    # Statutory Engine Logic
    approved_deductions = 0
    logs = []

    guidance_cap = 2 * rent
    if rent > 0 and deposit > guidance_cap:
        excess = deposit - guidance_cap
        logs.append(f"Soft warning: deposit exceeds 2x rent guidance by Rs. {excess:,.0f}.")

    if allow_painting:
        approved_deductions += painting_claim
        logs.append(f"'Painting Charges' (Rs. {painting_claim:,.0f}) allowed agreement + evidence.")
    else:
        logs.append(f"'Painting Charges' (Rs. {painting_claim:,.0f}) rejected: normal wear & tear.")

    depreciation_rate = 0.10
    depreciated_fixture = max(0.0, fixture_claim * (1 - (depreciation_rate * fixture_age)))
    approved_deductions += depreciated_fixture
    logs.append(f"'Fixture Damage' approved at Rs. {depreciated_fixture:,.0f} (Applied 10%/yr depreciation for {fixture_age} year(s) age).")

    approved_deductions += utility_claim
    logs.append(f"'Unpaid Electricity Bill' (Rs. {utility_claim:,.0f}) approved as unpaid contractual dues.")

    final_statutory_refund = deposit - approved_deductions

    # Dashboard Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Initial Deposit", f"₹{deposit:,.0f}")
    m2.metric("Approved Deductions", f"₹{approved_deductions:,.0f}")
    m3.metric("Final Refund Due", f"₹{final_statutory_refund:,.0f}")

    st.subheader("4. Rules Engine Decision Log")
    for log in logs:
        st.write(f"• {log}")

    st.divider()

    st.subheader("5. Structured Negotiation")
    c1, c2 = st.columns(2)
    with c1:
        offered = st.number_input("Landlord Refund Offer (₹)", value=float(landlord_offer))
    with c2:
        requested = st.number_input("Tenant Requested Refund (₹)", value=float(requested_refund))

    gap = abs(requested - offered)
    gap_percent = (gap / deposit) * 100 if deposit > 0 else 0

    st.info(f"Current Gap: ₹{gap:,.0f} ({gap_percent:.2f}% of total deposit)")

    if deposit > 0 and gap_percent <= 5:
        st.success("🎉 Settlement Reached! Gap is within the ≤ 5% threshold.")

        # Generate Styled PDF Buffer
        pdf_buffer = generate_pdf_bytes(
            tenant_name=tenant_name,
            landlord_name=landlord_name,
            address=address,
            rent=rent,
            deposit=deposit,
            duration=duration,
            painting_claim=painting_claim,
            allow_painting=allow_painting,
            fixture_claim=fixture_claim,
            fixture_age=fixture_age,
            utility_claim=utility_claim,
            approved_deductions=approved_deductions,
            final_refund=final_statutory_refund,
            logs=logs
        )

        st.download_button(
            label="📄 Auto-Generate Binding Settlement PDF",
            data=pdf_buffer,
            file_name=f"Binding_Settlement_Agreement_{tenant_name if tenant_name else 'Document'}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    elif deposit == 0:
        st.warning("Please enter tenancy parameters to calculate negotiation settlement.")
    else:
        st.error("⚠️ Gap exceeds 5% threshold. Settlement negotiation recommended.")
