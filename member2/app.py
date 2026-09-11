import streamlit as st

st.set_page_config(page_title="The Deposit War Room - ODR Platform", layout="wide")

# Manage navigation state
if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ---------------------------------------------------------
# PAGE 1: LANDING PAGE (Select Role)
# ---------------------------------------------------------
if st.session_state.page == "home":
    st.title("⚖️ The Deposit War Room")
    st.caption("Online Dispute Resolution Platform under Karnataka Rent Act")
    st.divider()

    st.subheader("Select your portal to continue:")
    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        st.info("### 🏠 Landlord Portal")
        st.write("File itemized property damage claims, utility arrears, and deduction evidence.")
        st.write("")
        if st.button("File Complaint / Claims as Landlord", type="primary", use_container_width=True):
            go_to("landlord")

    with col2:
        st.success("### 👤 Tenant Portal")
        st.write("Submit tenancy parameters, review landlord claims, and verify statutory protections.")
        st.write("")
        if st.button("File Complaint / Dispute as Tenant", type="primary", use_container_width=True):
            go_to("tenant")

# ---------------------------------------------------------
# PAGE 2: TENANT PORTAL
# ---------------------------------------------------------
elif st.session_state.page == "tenant":
    if st.button("← Back to Role Selection"):
        go_to("home")
    
    st.title("👤 Tenant Portal")
    st.caption("Submit your tenancy parameters and dispute unjust deposit deductions.")
    st.divider()
    
    # --- Put your tenant input fields here ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Tenancy Intake")
        tenant_name = st.text_input("Tenant Name", "Rahul Sharma")
        address = st.text_input("Property Address", "Flat 4B, Green Valley Apartments, Bengaluru")
        duration = st.number_input("Tenancy Duration (Months)", value=18)
    with col2:
        st.subheader("Financial Details")
        rent = st.number_input("Monthly Rent (₹)", value=25000)
        deposit = st.number_input("Security Deposit Held (₹)", value=150000)
        requested_refund = st.number_input("Requested Deposit Refund (₹)", value=142000)

    st.write("")
    if st.button("Proceed to Joint Settlement Engine", type="primary"):
        go_to("settlement")

# ---------------------------------------------------------
# PAGE 3: LANDLORD PORTAL
# ---------------------------------------------------------
elif st.session_state.page == "landlord":
    if st.button("← Back to Role Selection"):
        go_to("home")
        
    st.title("🏠 Landlord Portal")
    st.caption("Itemize property damage and submit official deduction claims.")
    st.divider()
    
    # --- Put your landlord input fields here ---
    landlord_name = st.text_input("Landlord Name", "Suresh Kumar")
    
    st.subheader("Itemised Claims & Evidence")
    col1, col2, col3 = st.columns(3)
    with col1:
        painting_claim = st.number_input("Painting Claim (₹)", value=25000)
        st.checkbox("Agreement explicitly allows painting deductions?")
    with col2:
        fixture_claim = st.number_input("Fixture Damage Claim (₹)", value=10000)
        fixture_age = st.number_input("Fixture Age (Years)", value=3.0)
    with col3:
        utility_claim = st.number_input("Unpaid Utility Arrears (₹)", value=4500)
        st.checkbox("Evidence Attached?", value=True)

    landlord_offer = st.number_input("Landlord Refund Offer (₹)", value=138000)

    st.write("")
    if st.button("Submit Claims to Settlement Engine", type="primary"):
        go_to("settlement")

# ---------------------------------------------------------
# PAGE 4: JOINT SETTLEMENT / DECISION ENGINE
# ---------------------------------------------------------
elif st.session_state.page == "settlement":
    if st.button("← Back to Role Selection"):
        go_to("home")

    st.title("⚖️ Results & Decision Breakdown")
    st.caption("Neutral ODR Engine evaluating claims against Karnataka Rent Act statutory rules.")
    st.divider()

    # Place your existing rules engine logs, breakdown metrics, and PDF generator code here!
