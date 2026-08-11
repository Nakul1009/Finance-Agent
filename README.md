# FinBank AI — Financial Document Intelligence Agent

**FinBank AI** is a lightweight, production-quality financial document analysis agent built to automate banking and financial operations by extracting, normalizing, and analyzing bank statements (PDF, CSV, XLSX).

It features a **Hybrid AI Architecture** combining deterministic rule engines, statistical analytics, and **NVIDIA Nemotron LLM** to deliver explainable transaction categorization, anomaly detection, stability assessments, interactive AI chat, and exportable PDF reports.

---

## 🌟 7 Core Features

1. **Financial Document Upload & Extraction**:
   - Multi-format support: PDF bank statements, CSV, and Excel XLSX files.
   - Modular parsers with automatic column detection (Date, Narration, Debit, Credit, Amount, Balance, Reference).
   - Scanned PDF support via open-source OCR fallback (`pytesseract`).
   - Standard transaction schema normalization.

2. **Automatic Transaction Categorization**:
   - Hybrid approach: Keyword/Regex Merchant Normalizer first.
   - NVIDIA Nemotron LLM fallback for ambiguous transactions (`confidence < 0.70`).
   - Every transaction tracks `category`, `confidence`, and `categorization_method` (`rule`, `nemotron`, `manual`).
   - Interactive manual category override capability.

3. **Financial Dashboard & Analytics**:
   - Real-time financial KPIs: Total Income, Total Expenses, Net Cash Flow, Transaction Count, Average Transaction Value, Savings Rate, Expense-to-Income Ratio.
   - Minimalist charts: Income vs Expenses over time, Top Spending Categories.

4. **Financial Insights & Anomaly Detection**:
   - Statistical detection of unusually large expenses (> 2.5 std dev).
   - Category spending spikes (month-over-month % jumps).
   - Detected recurring financial commitments (rent, utilities, subscriptions).
   - Negative cash flow periods and potential duplicate transactions.

5. **AI Financial Assistant**:
   - Grounded Q&A chat interface using structured financial context constructed by backend logic.
   - Deterministic numerical calculations in Python backend — zero numerical hallucinations by LLM.

6. **Loan / Financial Assessment Summary**:
   - Evaluates income consistency, cash-flow stability, and recurring commitment ratios.
   - Financial Stability Rating: **Good**, **Moderate**, or **Needs Attention** with clear summary explanations.
   - Explicit disclaimer: *AI-assisted financial analysis — not a lending decision.*

7. **Exportable PDF Financial Report**:
   - Professional PDF report generated using `ReportLab`.
   - Includes executive summary, metric breakdowns, category distribution, detected anomalies, recurring commitments, and assessment.

---

## 🏗️ Architecture & Data Pipeline

```text
                    ┌────────────────────┐
                    │   User Uploads     │
                    │ PDF / CSV / XLSX   │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Document Processor │
                    │ Parsers + OCR      │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Normalization      │
                    │ & Validation       │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ SQLite Database    │
                    └─────────┬──────────┘
                              ↓
                 ┌────────────┴────────────┐
                 ↓                         ↓
       ┌──────────────────┐      ┌──────────────────┐
       │ Rules / Stats    │      │ NVIDIA Nemotron  │
       │ Engine           │      │ LLM Service      │
       └────────┬─────────┘      └────────┬─────────┘
                └────────────┬────────────┘
                             ↓
                  ┌──────────────────────┐
                  │ Financial Analytics  │
                  └──────────┬───────────┘
                             ↓
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
          Dashboard      AI Assistant    PDF Report
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Pydantic
- **Data Processing**: Pandas, OpenPyXL, PyMuPDF (Fitz), pdfplumber, pytesseract
- **Reporting**: ReportLab
- **LLM**: NVIDIA Nemotron API (`httpx`)
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

*Note: If `NVIDIA_API_KEY` is not provided, FinBank AI operates seamlessly in **Deterministic Rule Mode** without crashing.*

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

## 🐳 Hugging Face Spaces Deployment

FinBank AI is ready for one-click deployment to Hugging Face Spaces using the Docker runtime:

1. Create a new Space on Hugging Face and select **Docker** as the SDK.
2. Push this repository to your Space.
3. In Space Settings -> **Variables and Secrets**:
   - Add Secret: `NVIDIA_API_KEY` (e.g. `nvapi-...`)
   - Add Variable or Secret: `NVIDIA_MODEL` (`mistralai/mistral-nemotron`)
   - Add Variable or Secret: `NVIDIA_API_URL` (`https://integrate.api.nvidia.com/v1`)
4. The Space will automatically build using `Dockerfile` and serve on port `7860`.

---

## ⚠️ Limitations & Disclaimers

- **Statement Format Variability**: Bank statements vary significantly across institutions. While modular parsers cover standard table and text layouts, non-standard formats may require customized rules.
- **OCR Quality**: Scanned PDF quality impacts OCR extraction accuracy.
- **Financial Advice Disclaimer**: This application provides AI-assisted financial analysis and does not provide financial, legal, or lending advice.

---

## 📜 License

MIT License. Free for open-source and professional evaluation.
