import streamlit as st

st.set_page_config(page_title="The Deposit War Room - ODR Platform", layout="wide")

# Initialize persistent session state variables
if "page" not in st.session_state:
    st.session_state.page = "home"
if "tenant_done" not in st.session_state:
    st.session_state.tenant_done = False
if "landlord_done" not in st.session_state:
    st.session_state.landlord_done = False

def go_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ---------------------------------------------------------
# PAGE 1: LANDING / ROLE SELECTION PAGE
# ---------------------------------------------------------
if st.session_state.page == "home":
    st.title("⚖️ The Deposit War Room")
    st.caption("Online Dispute Resolution Platform under Karnataka Rent Act")
    st.divider()

    st.subheader("Select who is filing first:")
    st.write("Both tenant and landlord details must be filled to generate a binding settlement.")

    col1, col2 = st.columns(2)

    with col1:
        st.info("### 👤 Start as Tenant")
        st.write("Input tenancy parameters, deposit paid, and requested refund amount.")
        if st.session_state.tenant_done:
            st.success("✅ Tenant details already submitted!")
        if st.button("Start Tenant Intake", type="primary", use_container_width=True):
            go_to("tenant")

    with col2:
        st.warning("### 🏠 Start as Landlord")
        st.write("Itemize property damage claims, utility arrears, and refund offers.")
        if st.session_state.landlord_done:
            st.success("✅ Landlord details already submitted!")
        if st.button("Start Landlord Claims", type="primary", use_container_width=True):
            go_to("landlord")

# ---------------------------------------------------------
# PAGE 2: TENANT PORTAL
# ---------------------------------------------------------
elif st.session_state.page == "tenant":
    if st.button("← Back to Home"):
        go_to("home")
    
    st.title("👤 Step 1: Tenant Intake Portal")
    st.caption("Submit tenancy parameters and dispute unjust deposit deductions.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Tenancy Intake")
        st.session_state.tenant_name = st.text_input("Tenant Name", value=st.session_state.get("tenant_name", "Rahul Sharma"))
        st.session_state.address = st.text_input("Property Address", value=st.session_state.get("address", "Flat 4B, Green Valley Apartments, Bengaluru"))
        st.session_state.duration = st.number_input("Tenancy Duration (Months)", value=st.session_state.get("duration", 18))
    with col2:
        st.subheader("Financial Details")
        st.session_state.rent = st.number_input("Monthly Rent (₹)", value=st.session_state.get("rent", 25000))
        st.session_state.deposit = st.number_input("Security Deposit Held (₹)", value=st.session_state.get("deposit", 150000))
        st.session_state.requested_refund = st.number_input("Requested Deposit Refund (₹)", value=st.session_state.get("requested_refund", 142000))

    st.write("")
    
    # Determine next destination based on landlord completion
    if st.button("Save Tenant Data & Proceed →", type="primary"):
        st.session_state.tenant_done = True
        if not st.session_state.landlord_done:
            go_to("landlord")  # Redirect to landlord portal if not completed yet
        else:
            go_to("settlement")  # Go straight to settlement if both are done

# ---------------------------------------------------------
# PAGE 3: LANDLORD PORTAL
# ---------------------------------------------------------
elif st.session_state.page == "landlord":
    if st.button("← Back to Home"):
        go_to("home")
        
    st.title("🏠 Step 2: Landlord Claims Portal")
    st.caption("Itemize property damage and submit official deduction claims.")
    st.divider()
    
    st.session_state.landlord_name = st.text_input("Landlord Name", value=st.session_state.get("landlord_name", "Suresh Kumar"))
    
    st.subheader("Itemised Claims & Evidence")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.painting_claim = st.number_input("Painting Claim (₹)", value=st.session_state.get("painting_claim", 25000))
        st.session_state.allow_painting = st.checkbox("Agreement explicitly allows painting deductions?", value=st.session_state.get("allow_painting", False))
    with col2:
        st.session_state.fixture_claim = st.number_input("Fixture Damage Claim (₹)", value=st.session_state.get("fixture_claim", 10000))
        st.session_state.fixture_age = st.number_input("Fixture Age (Years)", value=st.session_state.get("fixture_age", 3.0))
    with col3:
        st.session_state.utility_claim = st.number_input("Unpaid Utility Arrears (₹)", value=st.session_state.get("utility_claim", 4500))
        st.session_state.evidence_attached = st.checkbox("Evidence Attached?", value=st.session_state.get("evidence_attached", True))

    st.session_state.landlord_offer = st.number_input("Landlord Refund Offer (₹)", value=st.session_state.get("landlord_offer", 138000))

    st.write("")
    
    # Determine next destination based on tenant completion
    if st.button("Save Landlord Data & Proceed →", type="primary"):
        st.session_state.landlord_done = True
        if not st.session_state.tenant_done:
            go_to("tenant")  # Redirect to tenant portal if not completed yet
        else:
            go_to("settlement")  # Go straight to settlement if both are done

# ---------------------------------------------------------
# PAGE 4: JOINT SETTLEMENT ENGINE
# ---------------------------------------------------------
elif st.session_state.page == "settlement":
    if st.button("← Edit Data / Back to Home"):
        go_to("home")

    st.title("⚖️ Results & Decision Breakdown")
    st.caption("Neutral ODR Engine evaluating submitted tenant and landlord data against statutory rules.")
    st.divider()

    # Access all combined values directly from st.session_state
    # Place your decision logic, rules logs, metrics, and PDF generator here!
