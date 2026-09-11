from rules import evaluate_tenancy_dispute_simple, Claim, evaluate_tenancy_dispute
from pdf_generator import generate_settlement_pdf

print("=" * 60)
print("TEST 1 – Classic Bangalore scenario (18 months)")
print("=" * 60)

results = evaluate_tenancy_dispute_simple(
    rent=25000,
    deposit=150000,
    stayed_months=18,
    deductions_claimed={
        "Painting & Cleaning": 30000,
        "Unpaid Electricity Bill": 4500,
        "Broken Kitchen Cabinet": 8000,
    },
)

print("\nLogs:")
for line in results["logs"]:
    print(" ", line)

print("\nWarnings:")
for w in results.get("warnings", []):
    print(" ", w)

print(f"\nApproved deductions : ₹{results['total_valid_deductions']:,.0f}")
print(f"Final refund        : ₹{results['final_refund']:,.0f}")
print(f"Rejected            : {results.get('rejected')}")

# Generate first PDF
pdf_path = generate_settlement_pdf(
    filename="settlement_agreement.pdf",
    tenant_name="Rahul Sharma",
    landlord_name="Suresh Kumar",
    deposit=150000,
    calc_results=results,
    property_address="Flat 4B, Green Valley Apartments, HSR Layout, Bengaluru – 560102",
    case_id="ODR-2026-0911-001",
    rent=25000,
    stayed_months=18,
    additional_notes="Parties reached agreement after structured negotiation on the ODR platform.",
)
print(f"\nPDF written → {pdf_path}")


print("\n" + "=" * 60)
print("TEST 2 – Rich Claim objects")
print("=" * 60)

rich_claims = [
    Claim("Unpaid March Rent", 25000, category="unpaid_rent", has_evidence=True),
    Claim("Electricity Arrears (BESCOM)", 3200, category="utility", has_evidence=True),
    Claim("Full Repainting of Flat", 28000, category="painting", has_evidence=False),
    Claim("Deep Cleaning", 5000, category="cleaning", has_evidence=False),
    Claim("Cracked Bathroom Mirror (tenant caused)", 2500, category="damage", has_evidence=True),
]

result2 = evaluate_tenancy_dispute(
    rent=25000,
    deposit=100000,
    stayed_months=14,
    deductions_claimed={},
    claims=rich_claims,
    agreement_allows_painting=False,
    agreement_allows_cleaning=False,
)

print("\nDecision log:")
for line in result2.logs:
    print(" ", line)

print(f"\nFinal refund: ₹{result2.final_refund:,.0f}")
print("Valid  :", result2.valid_deductions)
print("Rejected:", result2.rejected_deductions)

# Generate second PDF
generate_settlement_pdf(
    filename="settlement_rich_claims.pdf",
    tenant_name="Priya Nair",
    landlord_name="Anand Realty Pvt Ltd",
    deposit=100000,
    calc_results=result2.to_dict(),
    property_address="2BHK, Whitefield Main Road, Bengaluru",
    case_id="ODR-2026-0911-002",
    rent=25000,
    stayed_months=14,
)
print("PDF written → settlement_rich_claims.pdf")

print("\n✅ All tests completed successfully.")
