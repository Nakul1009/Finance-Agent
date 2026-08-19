import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger("finbank.llm")

class LLMService:
    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.model = settings.NVIDIA_MODEL
        self.api_url = f"{settings.NVIDIA_API_URL}/chat/completions"

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def _call_nemotron(self, messages: List[Dict[str, str]], temperature: float = 0.2, response_format_json: bool = False) -> Optional[str]:
        if not self.is_available():
            logger.warning("NVIDIA_API_KEY not configured. Skipping LLM request.")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Candidate models list: primary model first, followed by fallbacks
        models_to_try = [self.model]
        if "nvidia/nemotron-mini-4b-instruct" not in models_to_try:
            models_to_try.append("nvidia/nemotron-mini-4b-instruct")
        if "nvidia/nemotron-3-nano-30b-a3b" not in models_to_try:
            models_to_try.append("nvidia/nemotron-3-nano-30b-a3b")

        async with httpx.AsyncClient(timeout=8.0) as client:
            for m in models_to_try:
                payload: Dict[str, Any] = {
                    "model": m,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 1024
                }
                if response_format_json:
                    payload["response_format"] = {"type": "json_object"}

                try:
                    resp = await client.post(self.api_url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        choices = data.get("choices", [])
                        if choices and len(choices) > 0:
                            content = choices[0].get("message", {}).get("content", "").strip()
                            if content:
                                return content
                    else:
                        logger.warning(f"NVIDIA API model '{m}' returned [{resp.status_code}]: {resp.text}")
                except Exception as e:
                    logger.warning(f"Failed NVIDIA API call for model '{m}': {e}")

        return None

    async def classify_transaction(self, merchant: str, description: str, amount: float, tx_type: str) -> Dict[str, Any]:
        """
        Uses Nemotron to classify ambiguous transactions into one of 15 categories.
        """
        if not self.is_available():
            return {"category": "Other", "confidence": 0.50, "method": "rule_fallback"}

        prompt = f"""You are a financial classification AI. Classify this bank transaction into EXACTLY ONE of the following categories:
- Salary / Income
- Food & Dining
- Shopping
- Utilities
- Rent / Housing
- Transport
- Healthcare
- Entertainment
- Education
- Insurance
- Investments
- Transfers
- ATM / Cash Withdrawal
- Fees / Charges
- Other

Transaction Details:
Merchant: {merchant}
Description: {description}
Amount: ₹{amount}
Type: {tx_type}

Return a valid JSON object with keys:
"category": "<chosen_category>",
"confidence": <float_between_0.70_and_0.99>
"""
        messages = [
            {"role": "system", "content": "You are a precise JSON financial classifier. Respond strictly with JSON."},
            {"role": "user", "content": prompt}
        ]

        res = await self._call_nemotron(messages, temperature=0.1, response_format_json=True)
        if res:
            try:
                data = json.loads(res)
                cat = data.get("category", "Other")
                conf = float(data.get("confidence", 0.81))
                return {"category": cat, "confidence": conf, "method": "nemotron"}
            except Exception:
                pass

        return {"category": "Other", "confidence": 0.60, "method": "nemotron_fallback"}

    async def generate_executive_summary(self, context: Dict[str, Any]) -> str:
        """
        Generates an AI executive summary for the financial report.
        """
        if not self.is_available():
            return f"Financial Analysis Summary: Total income for the period was ₹{context.get('total_income', 0):,.2f} against total expenses of ₹{context.get('total_expenses', 0):,.2f}, resulting in net cash flow of ₹{context.get('net_cash_flow', 0):,.2f}. The overall savings rate is {context.get('savings_rate', 0):.1f}%."

        prompt = f"""Provide a concise 3-paragraph executive financial summary based strictly on this normalized bank statement data:

Financial Metrics:
- Total Income: ₹{context.get('total_income', 0):,.2f}
- Total Expenses: ₹{context.get('total_expenses', 0):,.2f}
- Net Cash Flow: ₹{context.get('net_cash_flow', 0):,.2f}
- Savings Rate: {context.get('savings_rate', 0):.1f}%
- Expense to Income Ratio: {context.get('expense_to_income_ratio', 0):.1f}%

Top Categories:
{json.dumps(context.get('top_categories', []), indent=2)}

Recurring Commitments:
{json.dumps(context.get('recurring_payments', []), indent=2)}

Detected Anomalies:
{json.dumps(context.get('anomalies', []), indent=2)}

Financial Assessment:
{json.dumps(context.get('assessment', {}), indent=2)}

Instructions:
Highlight key cash flow trends, main expense drivers, and financial health observations. Do not invent any numbers.
"""
        messages = [
            {"role": "system", "content": "You are a senior financial analyst writing an executive report summary."},
            {"role": "user", "content": prompt}
        ]

        res = await self._call_nemotron(messages, temperature=0.3)
        if res:
            return res

        return f"Financial Analysis Summary: Total income of ₹{context.get('total_income', 0):,.2f} and total expenses of ₹{context.get('total_expenses', 0):,.2f} with net cash flow of ₹{context.get('net_cash_flow', 0):,.2f}."

    async def answer_financial_query(self, query: str, context: Dict[str, Any], history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Answers user questions using structured financial context.
        """
        if not self.is_available():
            # Deterministic fallback answer generator
            q_clean = query.lower()
            if 'food' in q_clean or 'dining' in q_clean:
                food_cat = next((c for c in context.get('top_categories', []) if 'food' in c['category'].lower()), None)
                amt = food_cat['amount'] if food_cat else 0.0
                return f"Based on your processed bank statement data, you spent **₹{amt:,.2f}** on Food & Dining."
            elif 'largest' in q_clean or 'top expense' in q_clean:
                top_m = context.get('top_merchants', [])
                if top_m:
                    return f"Your largest merchant expense was **{top_m[0]['merchant']}** at **₹{top_m[0]['amount']:,.2f}** ({top_m[0]['count']} transactions)."
                return f"Your top spending category is **{context.get('top_categories', [{}])[0].get('category', 'N/A')}** at **₹{context.get('top_categories', [{}])[0].get('amount', 0):,.2f}**."
            elif 'recurring' in q_clean or 'subscription' in q_clean:
                recurs = context.get('recurring_payments', [])
                if recurs:
                    items = [f"- **{r['merchant']}**: ~₹{r['estimated_amount']:,.2f} ({r['frequency']})" for r in recurs]
                    return "Here are your detected recurring payments:\n" + "\n".join(items)
                return "No recurring monthly payments were detected in your uploaded bank statement."
            elif 'unusual' in q_clean or 'anomal' in q_clean:
                anoms = context.get('anomalies', [])
                if anoms:
                    items = [f"- **{a['title']}**: {a['description']}" for a in anoms]
                    return "Here are the unusual patterns detected:\n" + "\n".join(items)
                return "No significant financial anomalies were detected."
            else:
                return f"Based on your statement data:\n- **Total Income**: ₹{context.get('total_income', 0):,.2f}\n- **Total Expenses**: ₹{context.get('total_expenses', 0):,.2f}\n- **Net Cash Flow**: ₹{context.get('net_cash_flow', 0):,.2f}\n- **Savings Rate**: {context.get('savings_rate', 0):.1f}%"

        messages = [
            {
                "role": "system",
                "content": f"""You are FinBank AI, an expert financial intelligence assistant.
Answer the user's question accurately using ONLY the provided structured financial context.
DO NOT fabricate or hallucinate any numbers or dates not present in the context.
If the required data is not available in the context, explicitly say that the data is unavailable.

STRUCTURED FINANCIAL CONTEXT:
{json.dumps(context, indent=2)}
"""
            }
        ]

        if history:
            for msg in history[-4:]:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query})

        res = await self._call_nemotron(messages, temperature=0.2)
        if res:
            return res

        return f"Based on your statement data: Total Income: ₹{context.get('total_income', 0):,.2f}, Total Expenses: ₹{context.get('total_expenses', 0):,.2f}, Net Cash Flow: ₹{context.get('net_cash_flow', 0):,.2f}."
