import streamlit as st

st.set_page_config(page_title="The Deposit War Room", layout="wide")

# --- 1. Tenant Interface Page ---
def tenant_page():
    st.title("👤 Tenant Portal")
    st.caption("Submit tenancy parameters, review landlord claims, and verify statutory protections.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tenancy Details")
        st.text_input("Tenant Name", "Rahul Sharma")
        st.text_input("Property Address", "Flat 4B, Green Valley Apartments, Bengaluru")
        st.number_input("Tenancy Duration (Months)", value=18)
    with col2:
        st.subheader("Financial Positions")
        st.number_input("Monthly Rent (₹)", value=25000)
        st.number_input("Security Deposit Paid (₹)", value=150000)
        st.number_input("Requested Deposit Refund (₹)", value=142000)
        
    st.info("💡 Your statutory rights under the Karnataka Rent Act are automatically applied during dispute evaluation.")

# --- 2. Landlord Interface Page ---
def landlord_page():
    st.title("🏠 Landlord Portal")
    st.caption("File itemized property damage claims, utility arrears, and submit deduction evidence.")
    st.divider()
    
    st.subheader("Landlord Information")
    st.text_input("Landlord Name", "Suresh Kumar")
    
    st.subheader("Itemised Deductions & Claims")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("Painting & Cleaning Claim (₹)", value=25000)
        st.checkbox("Agreement explicitly allows painting deductions?")
    with col2:
        st.number_input("Fixture / Appliance Damage (₹)", value=10000)
        st.number_input("Fixture Age (Years)", value=3.0)
    with col3:
        st.number_input("Unpaid Utility Arrears (₹)", value=4500)
        st.checkbox("Attach Proof / Bills", value=True)
        
    st.number_input("Proposed Refund Offer (₹)", value=138000)
    st.success("Claims submitted will be evaluated against wear-and-tear & depreciation rules.")

# --- 3. Joint Settlement / Mediator Page ---
def settlement_page():
    st.title("⚖️ Joint Settlement & Resolution Room")
    st.caption("Neutral ODR Engine evaluating claims against statutory rules.")
    st.divider()
    
    # Place your existing full decision breakdown, rules engine logs, and PDF generator code here!
    st.subheader("Results & Decision Breakdown")
    st.write("Initial Deposit: ₹150,000 | Approved Deductions: ₹11,500 | Final Refund: ₹138,500")

# --- Multi-Page Navigation Setup ---
pg = st.navigation([
    st.Page(tenant_page, title="Tenant Portal", icon="👤"),
    st.Page(landlord_page, title="Landlord Portal", icon="🏠"),
    st.Page(settlement_page, title="Joint Settlement Room", icon="⚖️")
])

pg.run()
