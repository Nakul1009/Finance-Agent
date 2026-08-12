# FinBank AI — Financial Document Intelligence Agent

**FinBank AI** is a lightweight, production-quality **Autonomous Financial Intelligence Agent** built to automate banking and financial operations by extracting, normalizing, auditing, and simulating bank statement data (PDF, CSV, XLSX).

Unlike simple LLM wrappers that merely generate text responses from raw prompts, **FinBank AI operates as a true AI Agent**. It uses a **ReAct (Reasoning + Action) Tool-Calling Engine**, executes deterministic backend Python tools server-side, exposes a step-by-step **Execution Trace**, performs **Autonomous Financial Audits**, and runs **"What-If" Scenario Simulations**.

---

## 🌟 Core AI Agent Capabilities

1. **ReAct Tool-Calling Engine & Verifiable Execution Trace**:
   - Decomposes complex financial queries into structured multi-step goals (`PLAN`, `TOOL_CALL`, `VERIFICATION`, `SYNTHESIS`).
   - Server-side tool execution (`tool_query_financial_metrics`, `tool_audit_recurring_subscriptions`, `tool_detect_anomalies`, `tool_simulate_budget_scenario`).
   - Every agent interaction includes a visual **Execution Trace** accordion in the UI showing tool calls, inputs, outputs, and verification steps to guarantee zero numerical hallucinations.

2. **Autonomous Financial Leak Audit Engine**:
   - One-click autonomous audit scanning across transactions, expense ratios, subscription traps, and statistical spikes.
   - Calculates an overall **Audit Score** (0–100) and **Risk Rating** (Low, Medium, High, Critical).
   - Generates a prioritized list of financial leaks with monthly outflow costs and an actionable corrective plan.

3. **"What-If" Goal & Scenario Simulator**:
   - Interactive agent simulator for key financial decisions:
     - 🎯 **Emergency Fund Builder**: Calculates required monthly savings, proposes 20–25% category spend cuts, and stress-tests against historical lowest income months.
     - 🏦 **Loan EMI Affordability Test**: Evaluates loan EMI impact against debt capacity caps and monthly cash flow buffers.
     - ✂️ **Expense Reduction Strategy**: Identifies flexible discretionary categories (Food & Dining, Shopping, Entertainment) and calculates achievable monthly savings.

4. **Financial Document Upload & Extraction**:
   - Multi-format support: PDF bank statements, CSV, and Excel XLSX files.
   - Modular parsers with automatic column detection (Date, Narration, Debit, Credit, Amount, Balance, Reference).
   - Scanned PDF support via open-source OCR fallback (`pytesseract`).

5. **Hybrid Transaction Categorization**:
   - Keyword/Regex Merchant Normalizer first.
   - NVIDIA Nemotron LLM fallback for ambiguous transactions (`confidence < 0.70`).
   - Tracks `category`, `confidence`, and `categorization_method` (`rule`, `nemotron`, `manual`).

6. **Financial Dashboard & Analytics**:
   - Real-time financial KPIs: Total Income, Total Expenses, Net Cash Flow, Transaction Count, Average Transaction Value, Savings Rate, Expense-to-Income Ratio.
   - Minimalist charts: Income vs Expenses over time, Top Spending Categories.

7. **Exportable PDF Financial Report**:
   - Professional PDF report generated using `ReportLab`.
   - Includes executive summary, metric breakdowns, category distribution, detected anomalies, recurring commitments, and financial health rating.

---

## 🏗️ Autonomous Agent Architecture

```text
                    ┌────────────────────────────┐
                    │      User Goal / Query     │
                    └─────────────┬──────────────┘
                                  ↓
                    ┌────────────────────────────┐
                    │    ReAct Agent Engine      │
                    │   (Plan -> Tool -> Verify) │
                    └─────────────┬──────────────┘
                                  ↓
      ┌───────────────────────────┼───────────────────────────┐
      ↓                           ↓                           ↓
┌───────────┐               ┌───────────┐               ┌───────────┐
│ Analytics │               │  Anomaly  │               │ Scenario  │
│ Tool      │               │ Audit Tool│               │ Simulator │
└─────┬─────┘               └─────┬─────┘               └─────┬─────┘
      └───────────────────────────┼───────────────────────────┘
                                  ↓
                    ┌────────────────────────────┐
                    │ Numerical Verification &   │
                    │ LLM Synthesis (Nemotron)   │
                    └─────────────┬──────────────┘
                                  ↓
                    ┌────────────────────────────┐
                    │ Response + Execution Trace │
                    └────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Pydantic
- **AI Agent Engine**: Custom ReAct Tool-Calling Engine, Execution Trace Generator
- **LLM Integration**: NVIDIA Nemotron API (`httpx`)
- **Data Processing**: Pandas, OpenPyXL, PyMuPDF (Fitz), pdfplumber, pytesseract
- **Reporting**: ReportLab
- **Database**: SQLite (SQLAlchemy models configurable for PostgreSQL)
- **Frontend**: Single-Page Application (HTML5, Tailwind CSS, Chart.js, Lucide Icons)

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
NVIDIA_API_KEY=your_nvidia_api_key
NVIDIA_MODEL=nvidia/llama-3.1-nemotron-70b-instruct
NVIDIA_API_URL=https://integrate.api.nvidia.com/v1
DATABASE_URL=sqlite:///./finbank.db
UPLOAD_DIR=./uploads
```

*Note: If `NVIDIA_API_KEY` is not provided, FinBank AI operates seamlessly in **Deterministic Rule & Agent Mode** without crashing.*

---

## 🚀 Running Locally

1. **Clone repository & navigate to directory**:
   ```bash
   cd FinBank-AI
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the FastAPI application**:
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Access the application**:
   Open browser at `http://127.0.0.1:8000`

---

## 🧪 Running Tests

Run the unit test suite covering parsers, categorization, analytics, guardrails, and the ReAct agent engine:

```bash
pytest
```

---

## ⚠️ Limitations & Disclaimers

- **Statement Format Variability**: Bank statements vary significantly across institutions. Modular parsers cover standard table and text layouts.
- **Financial Advice Disclaimer**: This application provides AI-assisted financial analysis and does not provide financial, legal, or lending advice.

---

## 📜 License

MIT License. Free for open-source and professional evaluation.
