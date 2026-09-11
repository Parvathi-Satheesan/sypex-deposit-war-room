"""
Deposit War Room - Rules & Logic Engine
Member 2: Statutory deduction calculations under Karnataka Rent Act, 1999
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Claim:
    description: str
    amount: float
    category: str = "other"          # unpaid_rent | utility | damage | painting | cleaning | fixtures | other
    has_evidence: bool = False
    evidence_notes: str = ""
    age_years: float = 0.0           # Required for fixtures 10% annual depreciation rule


@dataclass
class CalculationResult:
    original_deposit: float
    monthly_rent: float
    stayed_months: int
    valid_deductions: Dict[str, float]
    rejected_deductions: Dict[str, float]
    total_valid_deductions: float
    final_refund: float
    logs: List[str]
    warnings: List[str]
    calculation_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _is_wear_and_tear(description: str, category: str, stayed_months: int) -> bool:
    desc = description.lower()
    wear_keywords = ["paint", "painting", "polish", "polishing", "wear", "tear", "scuff", "faded"]
    if any(k in desc for k in wear_keywords) or category in ("painting", "cleaning"):
        if stayed_months >= 12:
            return True
        if "paint" in desc and "damage" not in desc:
            return True
    return False


def check_settlement_gap(landlord_offer: float, tenant_offer: float, total_deposit: float) -> Dict[str, Any]:
    """
    Checks if parties are within the <= 5% gap threshold for auto-generating the settlement PDF.
    """
    gap = abs(landlord_offer - tenant_offer)
    gap_percentage = (gap / total_deposit) * 100 if total_deposit > 0 else 0.0
    can_auto_settle = gap_percentage <= 5.0

    return {
        "gap": gap,
        "gap_percentage": round(gap_percentage, 2),
        "can_auto_settle": can_auto_settle,
        "agreed_amount": round((landlord_offer + tenant_offer) / 2, 2) if can_auto_settle else None
    }


def evaluate_tenancy_dispute(
    rent: float,
    deposit: float,
    stayed_months: int,
    deductions_claimed: Dict[str, float],
    *,
    claims: Optional[List[Claim]] = None,
    agreement_allows_painting: bool = False,
    agreement_allows_cleaning: bool = False,
) -> CalculationResult:

    logs: List[str] = []
    warnings: List[str] = []
    valid: Dict[str, float] = {}
    rejected: Dict[str, float] = {}

    # Soft deposit-cap warning
    max_suggested = rent * 2
    if deposit > max_suggested:
        excess = deposit - max_suggested
        warnings.append(
            f"Collected deposit ₹{deposit:,.0f} exceeds the commonly cited "
            f"2-month residential guidance (₹{max_suggested:,.0f}). "
            f"Excess ₹{excess:,.0f} is noted for transparency only."
        )
        logs.append(f"⚠️ Soft warning: deposit exceeds 2× rent guidance by ₹{excess:,.0f}.")

    # Convert simple dict to Claim objects if needed
    if claims is None:
        claims = []
        for desc, amount in deductions_claimed.items():
            cat = "other"
            low = desc.lower()
            if any(k in low for k in ["rent", "arrear"]):
                cat = "unpaid_rent"
            elif any(k in low for k in ["electric", "water", "utility", "bill", "gas"]):
                cat = "utility"
            elif any(k in low for k in ["paint", "polish"]):
                cat = "painting"
            elif "clean" in low:
                cat = "cleaning"
            elif any(k in low for k in ["fan", "light", "fixture", "appliance", "geyser", "cabinet"]):
                cat = "fixtures"
            elif any(k in low for k in ["damage", "break", "hole", "crack", "missing"]):
                cat = "damage"
            claims.append(Claim(description=desc, amount=float(amount), category=cat, has_evidence=False))

    # Evaluate each claim
    for claim in claims:
        amount = float(claim.amount)
        if amount <= 0:
            continue

        if claim.category in ("unpaid_rent", "utility"):
            valid[claim.description] = amount
            logs.append(f"✅ '{claim.description}' (₹{amount:,.0f}) approved as unpaid contractual dues.")
            continue

        # Fixture 10% annual depreciation cap rule
        if claim.category == "fixtures":
            if claim.has_evidence or claim.age_years > 0:
                depreciation_rate = min(1.0, 0.10 * claim.age_years)
                depreciated_amount = amount * (1.0 - depreciation_rate)
                valid[claim.description] = depreciated_amount
                logs.append(
                    f"✅ '{claim.description}' approved at ₹{depreciated_amount:,.0f} "
                    f"(Applied 10%/yr depreciation for {claim.age_years} year(s) age)."
                )
            else:
                rejected[claim.description] = amount
                logs.append(f"❌ '{claim.description}' (₹{amount:,.0f}) rejected pending evidence.")
            continue

        if claim.category in ("painting", "cleaning") or _is_wear_and_tear(
            claim.description, claim.category, stayed_months
        ):
            if claim.category == "painting" and agreement_allows_painting and claim.has_evidence:
                valid[claim.description] = amount
                logs.append(f"✅ '{claim.description}' (₹{amount:,.0f}) allowed – agreement + evidence.")
            elif claim.category == "cleaning" and agreement_allows_cleaning and claim.has_evidence:
                valid[claim.description] = amount
                logs.append(f"✅ '{claim.description}' (₹{amount:,.0f}) allowed – agreement + evidence.")
            else:
                rejected[claim.description] = amount
                reason = (
                    "normal wear & tear / routine painting is a landlord expense after reasonable occupancy"
                    if stayed_months >= 12
                    else "painting/cleaning claim lacks clear evidence of tenant-caused damage"
                )
                logs.append(f"❌ '{claim.description}' (₹{amount:,.0f}) rejected: {reason}.")
            continue

        if claim.category == "damage":
            if claim.has_evidence:
                valid[claim.description] = amount
                logs.append(f"✅ '{claim.description}' (₹{amount:,.0f}) approved – damage + evidence.")
            else:
                rejected[claim.description] = amount
                logs.append(f"❌ '{claim.description}' (₹{amount:,.0f}) rejected pending evidence.")
            continue

        # Default
        if claim.has_evidence:
            valid[claim.description] = amount
            logs.append(f"✅ '{claim.description}' (₹{amount:,.0f}) approved with evidence.")
        else:
            rejected[claim.description] = amount
            logs.append(f"ℹ️ '{claim.description}' (₹{amount:,.0f}) held pending evidence.")

    total_valid = sum(valid.values())
    final_refund = max(0.0, deposit - total_valid)

    if total_valid > deposit:
        warnings.append(f"Approved deductions exceed deposit. Refund set to ₹0.")

    return CalculationResult(
        original_deposit=deposit,
        monthly_rent=rent,
        stayed_months=stayed_months,
        valid_deductions=valid,
        rejected_deductions=rejected,
        total_valid_deductions=total_valid,
        final_refund=final_refund,
        logs=logs,
        warnings=warnings,
    )


def evaluate_tenancy_dispute_simple(
    rent: float,
    deposit: float,
    stayed_months: int,
    deductions_claimed: Dict[str, float],
) -> Dict[str, Any]:
    """Simple version compatible with original Gemini code."""
    result = evaluate_tenancy_dispute(rent, deposit, stayed_months, deductions_claimed)
    return {
        "final_refund": result.final_refund,
        "total_valid_deductions": result.total_valid_deductions,
        "logs": result.logs,
        "breakdown": result.valid_deductions,
        "rejected": result.rejected_deductions,
        "warnings": result.warnings,
    }
