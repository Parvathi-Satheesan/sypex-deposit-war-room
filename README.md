# Sypex Deposit War Room - Technical Write-Up

## 1. Executive Summary
This project provides an automated toolset for analyzing deposit rules, running rule validation tests, and generating formatted settlement agreement PDFs.

## 2. Tech Stack & Dependencies
* **Language:** Python 3.x
* **Key Libraries:** ReportLab / PyPDF (for PDF generation), Pytest (for testing framework)
* **Tools & Environment:** Git, VS Code

## 3. Project Architecture & Components
The repository is modularized to separate core business logic, testing, and document output:

* `rules.py` — Core logic and business rules engine for deposit processing.
* `test_rules.py` — Automated test suite verifying rules edge cases and output correctness.
* `pdf_generator.py` — Script responsible for rendering formatted PDF documents from calculated data.
* `settlement_agreement.pdf` & `settlement_rich_claims.pdf` — Sample output artifacts produced by the engine.

## 4. Key Features & Accomplishments
* Automated parsing and validation of deposit settlement conditions.
* Dynamic generation of formatted settlement agreement documents.
* Standardized testing script to ensure reliable execution across edge cases.

## 5. Setup & Local Execution

1. **Clone the repository:**
   ```bash
   git clone <YOUR-REPOSITORY-URL>
   cd sypex-deposit-war-room-main/member2

