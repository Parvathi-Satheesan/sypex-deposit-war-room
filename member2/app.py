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
# PAGE 4: JOINT SETTLEMENT / DECISION ENGINE
# ---------------------------------------------------------
elif st.session_state.page == "settlement":
    if st.button("← Edit Data / Back to Home"):
        go_to("home")

    st.title("⚖️ Results & Decision Breakdown")
    st.caption("Neutral ODR Engine evaluating submitted tenant and landlord data against statutory rules.")
    st.divider()

    # Extract state variables with defaults
    rent = st.session_state.get("rent", 25000)
    deposit = st.session_state.get("deposit", 150000)
    painting_claim = st.session_state.get("painting_claim", 25000)
    allow_painting = st.session_state.get("allow_painting", False)
    fixture_claim = st.session_state.get("fixture_claim", 10000)
    fixture_age = st.session_state.get("fixture_age", 3.0)
    utility_claim = st.session_state.get("utility_claim", 4500)
    landlord_offer = st.session_state.get("landlord_offer", 138000)
    requested_refund = st.session_state.get("requested_refund", 142000)

    # --- Statutory Calculation Logic ---
    approved_deductions = 0
    logs = []

    # 1. Deposit Cap Guidance Check
    guidance_cap = 2 * rent
    if deposit > guidance_cap:
        excess = deposit - guidance_cap
        logs.append(f"⚠️ Soft warning: deposit exceeds 2× rent guidance by ₹{excess:,.0f}.")

    # 2. Painting Claim Evaluation
    if allow_painting:
        approved_deductions += painting_claim
        logs.append(f"✅ 'Painting Charges' (₹{painting_claim:,.0f}) approved based on explicit agreement clause.")
    else:
        logs.append(f"❌ 'Painting Charges' (₹{painting_claim:,.0f}) rejected: normal wear & tear / routine painting is a landlord expense after reasonable occupancy.")

    # 3. Fixtures Depreciation Evaluation
    depreciation_rate = 0.10  # 10% per year
    depreciated_fixture = max(0.0, fixture_claim * (1 - (depreciation_rate * fixture_age)))
    approved_deductions += depreciated_fixture
    logs.append(f"✅ 'Fixture Damage' approved at ₹{depreciated_fixture:,.0f} (Applied 10%/yr depreciation for {fixture_age} year(s) age).")

    # 4. Utilities Claim Evaluation
    approved_deductions += utility_claim
    logs.append(f"✅ 'Unpaid Utility Bill' (₹{utility_claim:,.0f}) approved as unpaid contractual dues.")

    # Final Refund Math
    final_statutory_refund = deposit - approved_deductions

    # --- Visual Display ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Initial Deposit", f"₹{deposit:,.0f}")
    m2.metric("Approved Deductions", f"₹{approved_deductions:,.0f}")
    m3.metric("Final Refund Due", f"₹{final_statutory_refund:,.0f}")

    if deposit > guidance_cap:
        st.warning(f"Collected deposit ₹{deposit:,.0f} exceeds the commonly cited 2-month residential guidance (₹{guidance_cap:,.0f}). Excess ₹{deposit - guidance_cap:,.0f} is noted for transparency only.")

    st.subheader("Rules Engine Decision Logs")
    for log in logs:
        st.write(log)

    st.divider()

    # --- Section 3: Structured Negotiation ---
    st.subheader("3. Structured Negotiation")
    c1, c2 = st.columns(2)
    with c1:
        offered = st.number_input("Landlord Refund Offer (₹)", value=float(landlord_offer))
    with c2:
        requested = st.number_input("Tenant Requested Refund (₹)", value=float(requested_refund))

    gap = abs(requested - offered)
    gap_percent = (gap / deposit) * 100 if deposit > 0 else 0

    st.info(f"Current Gap: ₹{gap:,.0f} ({gap_percent:.2f}% of total deposit)")

    if gap_percent <= 5:
        st.success("🎉 Settlement Reached! Gap is within the ≤ 5% threshold.")
        st.button("📄 Auto-Generate Binding Settlement PDF", type="primary")
    else:
        st.error("⚠️ Gap exceeds 5% threshold. Settlement negotiation recommended.")
