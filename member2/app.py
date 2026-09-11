import streamlit as st

st.set_page_config(page_title="The Deposit War Room", layout="wide")

# Sidebar Role Selector
role = st.sidebar.radio(
    "Select Portal View:",
    ["Tenant Portal", "Landlord Portal", "Joint Settlement Room (Mediator)"]
)

if role == "Tenant Portal":
    st.header("👤 Tenant Portal")
    st.caption("Submit your tenancy details and review landlord claims under statutory rules.")
    
    # Render Tenant Inputs
    tenant_name = st.text_input("Tenant Name", "Rahul Sharma")
    rent = st.number_input("Monthly Rent (₹)", value=25000)
    deposit = st.number_input("Security Deposit Held (₹)", value=150000)
    tenant_requested = st.number_input("Requested Refund (₹)", value=142000)
    
    st.success("Your rights are protected under Karnataka Rent Act guidelines.")

elif role == "Landlord Portal":
    st.header("🏠 Landlord Portal")
    st.caption("File itemized property damage and utility deduction claims with evidence.")
    
    # Render Landlord Inputs
    landlord_name = st.text_input("Landlord Name", "Suresh Kumar")
    painting_claim = st.number_input("Painting Claim Amount (₹)", value=25000)
    fixture_claim = st.number_input("Fixture Damage Claim (₹)", value=10000)
    utility_claim = st.number_input("Utility Arrears (₹)", value=4500)
    landlord_offer = st.number_input("Landlord Refund Offer (₹)", value=138000)

elif role == "Joint Settlement Room (Mediator)":
    st.header("⚖️ The Deposit War Room — Neutral Resolution")
    st.caption("Automated decision engine evaluating claims against statutory rules.")
    
    # Place your existing full screen results & decision logic here!
