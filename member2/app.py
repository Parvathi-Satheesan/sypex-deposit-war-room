import streamlit as st
from rules import evaluate_tenancy_dispute, check_settlement_gap, Claim
from pdf_generator import generate_settlement_pdf

# Set page configuration
st.set_page_config(page_title="Deposit War Room - ODR Platform", layout="wide")

st.title("🛡️ The Deposit War Room")
st.caption("Online Dispute Resolution Platform under Karnataka Rent Act")

# --- SECTION 1: Intake Forms ---
st.header("1. Tenancy & Intake Information")
col1, col2 = st.columns(2)

with col1:
    tenant_name = st.text_input("Tenant Name", "Rahul Sharma")
    landlord_name = st.text_input("Landlord Name", "Suresh Kumar")
    property_address = st.text_input("Property Address", "Flat 4B, Green Valley Apartments, HSR Layout, Bengaluru")

with col2:
    rent = st.number_input("Monthly Rent (₹)", value=25000, step=1000)
    deposit = st.number_input("Security Deposit Held (₹)", value=150000, step=5000)
    stayed_months = st.number_input("Tenancy Duration (Months)", value=18, min_value=1)

# --- SECTION 2: Evidence & Claims ---
st.header("2. Itemised Claims & Evidence Input")

claims_list = []

# Painting Claim
with st.expander("Painting & Cleaning Claim", expanded=True):
    p_amt = st.number_input("Painting Claim Amount (₹)", value=25000, key="p_amt")
    p_ev = st.checkbox("Evidence Provided (Photos/Invoice)?", value=False, key="p_ev")
    p_agree = st.checkbox("Agreement explicitly allows painting deductions?", value=False, key="p_agree")
    if p_amt > 0:
        claims_list.append(Claim(description="Painting Charges", amount=p_amt, category="painting", has_evidence=p_ev))

# Fixtures Claim
with st.expander("Fixtures / Appliances Damage Claim", expanded=True):
    f_amt = st.number_input("Fixture Claim Amount (₹)", value=10000, key="f_amt")
    f_age = st.number_input("Fixture Age (Years)", value=3.0, step=0.5, key="f_age")
    f_ev = st.checkbox("Evidence Provided?", value=True, key="f_ev")
    if f_amt > 0:
        claims_list.append(Claim(description="Water Heater Damage", amount=f_amt, category="fixtures", has_evidence=f_ev, age_years=f_age))

# Utility Bill Claim
with st.expander("Unpaid Utilities Claim", expanded=True):
    u_amt = st.number_input("Utility Arrears Amount (₹)", value=4500, key="u_amt")
    if u_amt > 0:
        claims_list.append(Claim(description="Unpaid Electricity Bill", amount=u_amt, category="utility", has_evidence=True))

# --- SECTION 3: Rules Engine Execution ---
if st.button("⚖️ Run Statutory Dispute Rules Engine", type="primary"):
    res = evaluate_tenancy_dispute(
        rent=rent,
        deposit=deposit,
        stayed_months=stayed_months,
        deductions_claimed={},
        claims=claims_list,
        agreement_allows_painting=p_agree
    )
    st.session_state["calc_result"] = res.to_dict()

# Display Evaluation Results
if "calc_result" in st.session_state:
    res = st.session_state["calc_result"]
    st.divider()
    st.subheader("Results & Decision Breakdown")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Initial Deposit", f"₹{res['original_deposit']:,.0f}")
    m2.metric("Approved Deductions", f"₹{res['total_valid_deductions']:,.0f}")
    m3.metric("Final Refund Due", f"₹{res['final_refund']:,.0f}")

    if res.get("warnings"):
        for w in res["warnings"]:
            st.warning(w)

    st.write("### Rules Engine Decision Logs")
    for log in res.get("logs", []):
        st.write(log)

    # --- SECTION 4: Negotiation Interface ---
    st.divider()
    st.header("3. Structured Negotiation")
    
    n1, n2 = st.columns(2)
    landlord_offer = n1.number_input("Landlord Refund Offer (₹)", value=138000, step=1000)
    tenant_offer = n2.number_input("Tenant Requested Refund (₹)", value=142000, step=1000)

    gap_data = check_settlement_gap(landlord_offer, tenant_offer, deposit)
    
    st.info(f"Current Gap: **₹{gap_data['gap']:,.0f}** ({gap_data['gap_percentage']}% of total deposit)")

    # --- SECTION 5: Auto-Generate PDF ---
    if gap_data["can_auto_settle"]:
        st.success("🎉 Settlement Reached! Gap is within the <= 5% threshold.")
        
        if st.button("📄 Auto-Generate Binding Settlement PDF"):
            pdf_path = generate_settlement_pdf(
                filename="settlement_agreement.pdf",
                tenant_name=tenant_name,
                landlord_name=landlord_name,
                deposit=deposit,
                calc_results=res,
                property_address=property_address,
                case_id="ODR-2026-BLR-001",
                rent=rent,
                stayed_months=stayed_months
            )
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="⬇️ Download Binding Settlement PDF",
                    data=pdf_file,
                    file_name="Binding_Settlement_Agreement.pdf",
                    mime="application/pdf"
                )
