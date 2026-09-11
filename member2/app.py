import io
import datetime
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="Deposit War Room - ODR Platform", layout="wide", page_icon="⚖️")

# =========================================================
# SESSION STATE INITIALIZATION
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "tenant_submitted" not in st.session_state:
    st.session_state.tenant_submitted = False
if "landlord_submitted" not in st.session_state:
    st.session_state.landlord_submitted = False

# Negotiation Round Tracking
if "negotiation_rounds" not in st.session_state:
    st.session_state.negotiation_rounds = []
if "tenant_consent" not in st.session_state:
    st.session_state.tenant_consent = False
if "landlord_consent" not in st.session_state:
    st.session_state.landlord_consent = False

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# =========================================================
# PDF GENERATOR ENGINE (REPORTLAB)
# =========================================================
def generate_settlement_pdf(tenant_name, landlord_name, address, rent, deposit, duration,
                            painting_claim, allow_painting, fixture_claim, fixture_age,
                            utility_claim, approved_deductions, final_refund, logs,
                            agreed_amount, tenant_consent, landlord_consent):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=16, leading=20, textColor=colors.HexColor('#1E293B'))
    subtitle_style = ParagraphStyle('DocSub', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#64748B'))
    sec_heading = ParagraphStyle('SecHeading', parent=styles['Heading2'], fontSize=11, leading=15, textColor=colors.HexColor('#0F172A'), spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('DocBody', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#334155'))
    bold_body = ParagraphStyle('BoldBody', parent=body_style, fontName='Helvetica-Bold')

    elements = []

    # Title Header
    elements.append(Paragraph("BINDING SETTLEMENT AGREEMENT", title_style))
    elements.append(Paragraph("Online Dispute Resolution Platform for Residential Tenancy Deposits", subtitle_style))
    elements.append(Paragraph("Evaluated under Karnataka Rent Control Act Provisions & Contractual Statutory Principles", subtitle_style))
    elements.append(Paragraph(f"<b>Case ID:</b> ODR-2026-BLR-{datetime.datetime.now().strftime('%M%S')}", subtitle_style))
    elements.append(Spacer(1, 10))

    # 1. Parties & Property
    elements.append(Paragraph("1. Parties & Property Information", sec_heading))
    p_text = f"<b>Landlord:</b> {landlord_name} | <b>Tenant:</b> {tenant_name}<br/>" \
             f"<b>Property Address:</b> {address}<br/>" \
             f"<b>Monthly Rent:</b> ₹{rent:,.2f} | <b>Tenancy Duration:</b> {duration} Months"
    elements.append(Paragraph(p_text, body_style))
    elements.append(Spacer(1, 8))

    # 2. Financial Summary
    elements.append(Paragraph("2. Financial Summary & Statutory Calculations", sec_heading))
    fin_data = [
        [Paragraph("<b>Description</b>", bold_body), Paragraph("<b>Amount (₹)</b>", bold_body)],
        ["Initial Security Deposit Paid", f"₹{deposit:,.2f}"],
        ["Total Statutory Deductions Approved", f"₹{approved_deductions:,.2f}"],
        ["Statutory Net Refund Calculated", f"₹{final_refund:,.2f}"],
        [Paragraph("<b>FINAL MUTUALLY AGREED REFUND AMOUNT</b>", bold_body), Paragraph(f"<b>₹{agreed_amount:,.2f}</b>", bold_body)]
    ]
    t_fin = Table(fin_data, colWidths=[380, 160])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#DCFCE7'))
    ]))
    elements.append(t_fin)
    elements.append(Spacer(1, 8))

    # 3. Itemized Deductions Decisions
    elements.append(Paragraph("3. Itemized Damage & Deduction Assessment", sec_heading))
    p_status = "APPROVED" if allow_painting else "REJECTED (Normal Wear & Tear)"
    deprec_val = max(0.0, fixture_claim * (1 - (0.10 * fixture_age)))
    
    item_data = [
        [Paragraph("<b>Claim Type</b>", bold_body), Paragraph("<b>Claimed Amount</b>", bold_body), Paragraph("<b>Statutory Decision / Approved</b>", bold_body)],
        ["Painting & Maintenance", f"₹{painting_claim:,.2f}", f"{p_status}"],
        ["Fixture Damage", f"₹{fixture_claim:,.2f}", f"₹{deprec_val:,.2f} (10%/yr Deprecated)"],
        ["Utility Arrears & Unpaid Bills", f"₹{utility_claim:,.2f}", f"₹{utility_claim:,.2f} (APPROVED)"]
    ]
    t_item = Table(item_data, colWidths=[200, 140, 200])
    t_item.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5)
    ]))
    elements.append(t_item)
    elements.append(Spacer(1, 8))

    # 4. Decision Engine Audit Log
    elements.append(Paragraph("4. Rules Engine Audit Log", sec_heading))
    for log in logs:
        elements.append(Paragraph(f"• {log}", body_style))
    elements.append(Spacer(1, 10))

    # 5. Signatures & Digital Consent
    elements.append(Paragraph("5. Digital Consent & Binding Effect", sec_heading))
    binding_text = "This document records the final outcome of the ODR process. Both parties explicitly confirm that the agreed refund amount constitutes full and final settlement of all deposit claims."
    elements.append(Paragraph(binding_text, body_style))
    elements.append(Spacer(1, 10))

    t_status = "DIGITALLY SIGNED & CONSENTED" if tenant_consent else "PENDING SIGNATURE"
    l_status = "DIGITALLY SIGNED & CONSENTED" if landlord_consent else "PENDING SIGNATURE"

    sig_data = [
        [Paragraph("<b>Landlord Digital Acceptance</b>", bold_body), Paragraph("<b>Tenant Digital Acceptance</b>", bold_body)],
        [f"Status: {l_status}\nLandlord: {landlord_name}", f"Status: {t_status}\nTenant: {tenant_name}"],
        [f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
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
# STAGE 1 & 2: LANDING & INTAKE PORTALS
# =========================================================
if st.session_state.page == "home":
    st.title("⚖️ Deposit War Room — ODR Platform")
    st.caption("Automated Dispute Resolution Engine compliant with the Karnataka Rent Control Act")
    st.divider()

    st.subheader("Select Interface Portal to Begin Dispute Resolution:")
    c1, c2 = st.columns(2)

    with c1:
        st.info("### 👤 Tenant Interface")
        st.write("Submit tenancy parameters, deposit details, notice history, and requested refund.")
        if st.session_state.tenant_submitted:
            st.success("✅ Tenant Data Submitted")
        if st.button("Enter Tenant Portal", type="primary", use_container_width=True):
            navigate_to("tenant")

    with c2:
        st.warning("### 🏠 Landlord Interface")
        st.write("Itemize property damage claims, upload evidence receipts, and record utility arrears.")
        if st.session_state.landlord_submitted:
            st.success("✅ Landlord Data Submitted")
        if st.button("Enter Landlord Portal", type="primary", use_container_width=True):
            navigate_to("landlord")

    st.divider()
    if st.session_state.tenant_submitted and st.session_state.landlord_submitted:
        st.success("🎉 Both parties have submitted data! You can proceed to statutory calculation & negotiation.")
        if st.button("Proceed to Engine & Negotiation Room →", type="primary", use_container_width=True):
            navigate_to("settlement")

elif st.session_state.page == "tenant":
    if st.button("← Back to Landing"):
        navigate_to("home")
    st.title("Tenant Intake & Evidence Portal")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("1. Tenancy Identification")
        st.session_state.tenant_name = st.text_input("Tenant Full Name", value=st.session_state.get("tenant_name", ""))
        st.session_state.address = st.text_input("Property Address", value=st.session_state.get("address", ""))
        st.session_state.duration = st.number_input("Tenancy Duration (Months)", min_value=0, value=st.session_state.get("duration", 0))

    with c2:
        st.subheader("2. Financial & Notice Details")
        st.session_state.rent = st.number_input("Monthly Rent (₹)", min_value=0, value=st.session_state.get("rent", 0))
        st.session_state.deposit = st.number_input("Security Deposit Paid (₹)", min_value=0, value=st.session_state.get("deposit", 0))
        st.session_state.requested_refund = st.number_input("Requested Refund Amount (₹)", min_value=0, value=st.session_state.get("requested_refund", 0))

    st.subheader("3. Evidence Upload & Notice History")
    col_a, col_b = st.columns(2)
    with col_a:
        st.session_state.notice_given = st.checkbox("Gave minimum 1-Month Move-Out Notice?", value=st.session_state.get("notice_given", True))
        st.session_state.tenant_agreement_file = st.file_uploader("Upload Rent Agreement (PDF/Image)", type=["pdf", "png", "jpg"])
    with col_b:
        st.session_state.moveout_pics = st.file_uploader("Upload Move-Out Handover Photos", type=["png", "jpg"], accept_multiple_files=True)

    if st.button("Save & Submit Tenant Profile", type="primary"):
        st.session_state.tenant_submitted = True
        st.success("Tenant information recorded.")
        navigate_to("home")

elif st.session_state.page == "landlord":
    if st.button("← Back to Landing"):
        navigate_to("home")
    st.title("Landlord Intake & Claims Portal")
    st.divider()

    st.session_state.landlord_name = st.text_input("Landlord Full Name", value=st.session_state.get("landlord_name", ""))
    
    st.subheader("Structured Evidence Entry & Claims")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("####  Painting Claim")
        st.session_state.painting_claim = st.number_input("Painting Claim (₹)", min_value=0, value=st.session_state.get("painting_claim", 0))
        st.session_state.allow_painting = st.checkbox("Agreement explicitly mandates tenant painting?", value=st.session_state.get("allow_painting", False))
        st.file_uploader("Upload Painting Invoices/Photos", type=["pdf", "png", "jpg"], key="paint_file")

    with c2:
        st.markdown("####  Fixture & Appliance Damage")
        st.session_state.fixture_claim = st.number_input("Fixture Claim (₹)", min_value=0, value=st.session_state.get("fixture_claim", 0))
        st.session_state.fixture_age = st.number_input("Age of Fixture (Years)", min_value=0.0, value=st.session_state.get("fixture_age", 0.0), step=0.5)
        st.file_uploader("Upload Repair Estimates", type=["pdf", "png", "jpg"], key="fix_file")

    with c3:
        st.markdown("####  Utility Arrears")
        st.session_state.utility_claim = st.number_input("Unpaid Bills (₹)", min_value=0, value=st.session_state.get("utility_claim", 0))
        st.file_uploader("Upload Utility Bills", type=["pdf", "png", "jpg"], key="util_file")

    st.session_state.landlord_offer = st.number_input("Initial Landlord Refund Offer (₹)", min_value=0, value=st.session_state.get("landlord_offer", 0))

    if st.button("Save & Submit Landlord Claims", type="primary"):
        st.session_state.landlord_submitted = True
        st.success("Landlord information recorded.")
        navigate_to("home")

# =========================================================
# STAGE 3, 4 & 5: CALCULATIONS, NEGOTIATION & SETTLEMENT
# =========================================================
elif st.session_state.page == "settlement":
    if st.button("← Back to Landing / Edit Intake Data"):
        navigate_to("home")

    st.title("⚖️ ODR Rules Engine & Negotiation War Room")
    st.divider()

    # Retrieve Values
    t_name = st.session_state.get("tenant_name", "Tenant")
    l_name = st.session_state.get("landlord_name", "Landlord")
    addr = st.session_state.get("address", "N/A")
    duration = st.session_state.get("duration", 0)
    rent = st.session_state.get("rent", 0)
    deposit = st.session_state.get("deposit", 0)
    painting_claim = st.session_state.get("painting_claim", 0)
    allow_painting = st.session_state.get("allow_painting", False)
    fixture_claim = st.session_state.get("fixture_claim", 0)
    fixture_age = st.session_state.get("fixture_age", 0.0)
    utility_claim = st.session_state.get("utility_claim", 0)
    notice_given = st.session_state.get("notice_given", True)
    
    landlord_offer = st.session_state.get("landlord_offer", 0)
    requested_refund = st.session_state.get("requested_refund", 0)

    # ---------------------------------------------------------
    # STAGE 3: AUTOMATED STATUTORY CALCULATION ENGINE
    # ---------------------------------------------------------
    st.subheader("Automated Karnataka Rent Control Statutory Evaluation")
    
    approved_deductions = 0.0
    logs = []

    # Rule 1: 1-Month Notice Deduction Rule
    if not notice_given and rent > 0:
        approved_deductions += rent
        logs.append(f"❌ Notice Shortfall penalty applied: ₹{rent:,.2f} deducted (1 month rent penalty for lack of move-out notice).")
    else:
        logs.append("✅ Notice Protection: 1-Month notice requirement satisfied.")

    # Rule 2: Wear & Tear Prohibition vs Painting Clause
    if allow_painting:
        approved_deductions += painting_claim
        logs.append(f"✅ Painting Deductions: Approved ₹{painting_claim:,.2f} based on explicit agreement clause.")
    else:
        logs.append(f"🛡️ Wear & Tear Protection: Painting claim of ₹{painting_claim:,.2f} REJECTED. Routine repainting post-tenancy is statutory normal wear & tear.")

    # Rule 3: 10% Annual Fixture Depreciation Cap Rule
    depreciation_rate = 0.10
    depreciated_fixture = max(0.0, fixture_claim * (1 - (depreciation_rate * fixture_age)))
    approved_deductions += depreciated_fixture
    logs.append(f"📉 Fixture Depreciation Rule: Claim of ₹{fixture_claim:,.2f} reduced to ₹{depreciated_fixture:,.2f} (Applied statutory 10%/yr depreciation cap for {fixture_age} year(s)).")

    # Rule 4: Utility Dues
    approved_deductions += utility_claim
    logs.append(f"✅ Utility Arrears: Approved ₹{utility_claim:,.2f} for unpaid contractual bills.")

    # Net Statutory Calculations
    final_statutory_refund = max(0.0, deposit - approved_deductions)

    m1, m2, m3 = st.columns(3)
    m1.metric("Initial Deposit", f"₹{deposit:,.2f}")
    m2.metric("Total Approved Statutory Deductions", f"₹{approved_deductions:,.2f}")
    m3.metric("Statutory Net Refund Due", f"₹{final_statutory_refund:,.2f}")

    with st.expander("🔍 View Engine Rules & Statutory Audit Logs", expanded=True):
        for log in logs:
            st.write(log)

    st.divider()

    # ---------------------------------------------------------
    # STAGE 4: STRUCTURED NEGOTIATION (MAX 3 ROUNDS)
    # ---------------------------------------------------------
    st.subheader("Multi-Round Structured Negotiation (Max 3 Rounds)")

    # Initialize Round 1 if empty
    if len(st.session_state.negotiation_rounds) == 0:
        st.session_state.negotiation_rounds.append({
            "round": 1,
            "tenant_req": float(requested_refund),
            "landlord_off": float(landlord_offer)
        })

    current_round_num = len(st.session_state.negotiation_rounds)
    current_round_data = st.session_state.negotiation_rounds[-1]

    curr_tenant = current_round_data["tenant_req"]
    curr_landlord = current_round_data["landlord_off"]

    # Calculate Gap
    gap = abs(curr_tenant - curr_landlord)
    gap_percent = (gap / deposit * 100) if deposit > 0 else 0

    st.markdown(f"#### **Round {current_round_num} of 3 Analysis**")
    
    # Gap Visualizer Metric
    col_g1, col_g2, col_g3 = st.columns(3)
    col_g1.metric("Tenant Asking Refund", f"₹{curr_tenant:,.2f}")
    col_g2.metric("Landlord Offered Refund", f"₹{curr_landlord:,.2f}")
    col_g3.metric("Dispute Gap Amount", f"₹{gap:,.2f}", delta=f"{gap_percent:.2f}% of deposit", delta_color="inverse")

    # Visual Progress Bar
    st.write("**Dispute Settlement Gap Visualization:**")
    st.progress(max(0.0, min(1.0, 1.0 - (gap_percent / 100))))

    # Negotiation History Table
    if len(st.session_state.negotiation_rounds) > 0:
        st.write("**Negotiation Audit Trail:**")
        st.table(st.session_state.negotiation_rounds)

    # Allow counteroffers if under 3 rounds and gap > 5%
    if gap_percent > 5.0 and current_round_num < 3:
        st.warning(f"⚠️ Current Gap is {gap_percent:.2f}% (exceeds ≤ 5% threshold). Submit Round {current_round_num + 1} Counteroffer:")
        
        nc1, nc2 = st.columns(2)
        with nc1:
            new_t_req = st.number_input("New Tenant Request (₹)", value=curr_tenant, key=f"t_req_{current_round_num}")
        with nc2:
            new_l_off = st.number_input("New Landlord Offer (₹)", value=curr_landlord, key=f"l_off_{current_round_num}")

        if st.button(f"Submit Round {current_round_num + 1} Counteroffer"):
            st.session_state.negotiation_rounds.append({
                "round": current_round_num + 1,
                "tenant_req": new_t_req,
                "landlord_off": new_l_off
            })
            st.rerun()

    elif gap_percent > 5.0 and current_round_num >= 3:
        st.error("❌ Maximum 3 Negotiation Rounds Exceeded without convergence. Case flagged for Formal Human Arbitrator / Small Claims Court referral.")

    # ---------------------------------------------------------
    # STAGE 5: SETTLEMENT & DIGITAL SIGNATURES
    # ---------------------------------------------------------
    st.divider()
    st.subheader("Binding Settlement & Document Execution")

    if gap_percent <= 5.0:
        st.success(f"🎉 Dispute Successfully Resolved! Settlement gap is within the allowable threshold ({gap_percent:.2f}% ≤ 5.0%).")
        agreed_amount = (curr_tenant + curr_landlord) / 2.0
        st.info(f"**Final Settled Refund Amount:** ₹{agreed_amount:,.2f}")

        st.markdown("#### Digital Acceptance & Execution Signatures")
        sc1, sc2 = st.columns(2)
        with sc1:
            st.session_state.tenant_consent = st.checkbox(f"Digital Signature: Tenant ({t_name}) accepts ₹{agreed_amount:,.2f}")
        with sc2:
            st.session_state.landlord_consent = st.checkbox(f"Digital Signature: Landlord ({l_name}) accepts ₹{agreed_amount:,.2f}")

        if st.session_state.tenant_consent and st.session_state.landlord_consent:
            st.balloons()
            
            # Generate ReportLab PDF
            pdf_bytes = generate_settlement_pdf(
                tenant_name=t_name,
                landlord_name=l_name,
                address=addr,
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
                logs=logs,
                agreed_amount=agreed_amount,
                tenant_consent=st.session_state.tenant_consent,
                landlord_consent=st.session_state.landlord_consent
            )

            st.download_button(
                label="📄 Download Binding Settlement Agreement (PDF)",
                data=pdf_bytes,
                file_name=f"Settlement_Agreement_{t_name}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        else:
            st.warning("Both parties must check their respective digital consent boxes to unlock PDF generation.")
    else:
        st.info("Settlement agreement PDF generation will unlock once the dispute gap reaches ≤ 5%.")
