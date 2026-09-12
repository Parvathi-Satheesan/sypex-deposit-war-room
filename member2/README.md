# SYPEx — ODR Platform for Residential Tenancy Deposits

An automated Online Dispute Resolution (ODR) platform compliant with the Karnataka Rent Control Act, built with Python, Streamlit, and a modular architecture.

## 1. Executive Summary & Technical Write-Up
Traditional residential tenancy deposit disputes are frequently bogged down by asymmetric information, protracted litigation, and a lack of standardized adjudication. Landlords often deduct arbitrary amounts for routine wear-and-tear, while tenants lack accessible mechanisms to challenge these claims under local legislation (such as the Karnataka Rent Control Act). **SYPEx** is an automated web-based ODR platform designed to streamline the entire dispute lifecycle—from dual intake and algorithmic evidence evaluation to structured negotiation and legally binding PDF settlement generation—in under 10 minutes.

### Core System Workflow:
1. **Dual Intake Portals:** Separate, persistent interfaces for Tenants and Landlords to log tenancy parameters and notice history.
2. **Structured Evidence Evaluation:** Manual entry and tracking for damage photos, lease agreements, and utility bills.
3. **Statutory Rules Engine:** Automated application of Karnataka Rent Control Act rules (`rules.py`):
   - Prohibits painting deductions for normal wear-and-tear unless explicitly mandated by lease clauses.
   - Applies a 10% annual depreciation cap on fixture and appliance damage claims.
   - Evaluates compliance with the standard 1-month move-out notice requirement.
4. **Multi-Round Negotiation:** Structured counteroffer workflow with a dynamic gap visualizer (capped at 3 rounds).
5. **Binding Settlement Generation:** Auto-generated PDF agreements (`pdf_generator.py`) unlocked upon dual digital consent when the negotiation gap drops to $\le 5\%$.

## 2. Tech Stack & Architecture
The repository is modularized to separate core business logic, testing, and UI:
* `member2/app.py` — Main Streamlit application and UI router.
* `member2/rules.py` — Core logic and business rules engine for deposit processing.
* `member2/pdf_generator.py` — Script responsible for rendering formatted PDF documents.
* `member2/test_rules.py` — Automated test suite verifying rules and edge cases.
* `member2/requirements.txt` — Project dependencies (`streamlit`, `reportlab`, etc.).

## 3. Setup & Local Execution

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/Parvathi-Satheesan/sypex-deposit-war-room.git](https://github.com/Parvathi-Satheesan/sypex-deposit-war-room.git)
   cd sypex-deposit-war-room/member2
