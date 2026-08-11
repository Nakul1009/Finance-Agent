from typing import List, Dict, Any
from collections import defaultdict
import numpy as np
import uuid

class FinancialAnalyticsEngine:
    def compute_analytics(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not transactions:
            return self._empty_analytics()

        total_income = sum(t["amount"] for t in transactions if t["transaction_type"] == "income")
        total_expenses = sum(t["amount"] for t in transactions if t["transaction_type"] == "expense")
        net_cash_flow = total_income - total_expenses
        tx_count = len(transactions)
        avg_tx_val = round((total_income + total_expenses) / tx_count, 2) if tx_count > 0 else 0.0

        savings_rate = round((net_cash_flow / total_income * 100.0), 2) if total_income > 0 else 0.0
        expense_ratio = round((total_expenses / total_income * 100.0), 2) if total_income > 0 else 0.0

        # Category Breakdown
        cat_sums = defaultdict(float)
        cat_counts = defaultdict(int)
        for t in transactions:
            if t["transaction_type"] == "expense":
                cat_sums[t["category"]] += t["amount"]
                cat_counts[t["category"]] += 1

        top_categories = []
        for cat, amt in sorted(cat_sums.items(), key=lambda x: x[1], reverse=True):
            pct = round((amt / total_expenses * 100.0), 2) if total_expenses > 0 else 0.0
            top_categories.append({
                "category": cat,
                "amount": round(amt, 2),
                "percentage": pct,
                "count": cat_counts[cat]
            })

        # Monthly Trends
        monthly_inc = defaultdict(float)
        monthly_exp = defaultdict(float)
        for t in transactions:
            month = t["date"][:7] # YYYY-MM
            if t["transaction_type"] == "income":
                monthly_inc[month] += t["amount"]
            elif t["transaction_type"] == "expense":
                monthly_exp[month] += t["amount"]

        all_months = sorted(list(set(list(monthly_inc.keys()) + list(monthly_exp.keys()))))
        monthly_trends = []
        for m in all_months:
            inc = round(monthly_inc[m], 2)
            exp = round(monthly_exp[m], 2)
            monthly_trends.append({
                "month": m,
                "income": inc,
                "expense": exp,
                "net": round(inc - exp, 2)
            })

        # Top Merchants
        merchant_sums = defaultdict(float)
        merchant_cats = {}
        merchant_counts = defaultdict(int)
        for t in transactions:
            if t["transaction_type"] == "expense":
                m_name = t["merchant"]
                merchant_sums[m_name] += t["amount"]
                merchant_cats[m_name] = t["category"]
                merchant_counts[m_name] += 1

        top_merchants = []
        for m_name, amt in sorted(merchant_sums.items(), key=lambda x: x[1], reverse=True)[:8]:
            top_merchants.append({
                "merchant": m_name,
                "category": merchant_cats.get(m_name, "Other"),
                "amount": round(amt, 2),
                "count": merchant_counts[m_name]
            })

        # Anomaly & Recurring Payment Detection
        recurring_payments = self._detect_recurring_payments(transactions)
        anomalies = self._detect_anomalies(transactions, top_categories, monthly_trends)

        # Loan / Financial Assessment
        assessment = self._assess_financial_health(
            total_income, total_expenses, net_cash_flow, savings_rate, expense_ratio, monthly_trends, recurring_payments
        )

        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net_cash_flow": round(net_cash_flow, 2),
            "transaction_count": tx_count,
            "avg_transaction_value": avg_tx_val,
            "savings_rate": savings_rate,
            "expense_to_income_ratio": expense_ratio,
            "top_categories": top_categories,
            "monthly_trends": monthly_trends,
            "top_merchants": top_merchants,
            "recurring_payments": recurring_payments,
            "anomalies": anomalies,
            "assessment": assessment
        }

    @staticmethod
    def _clean_float(val: Any, default: float = 0.0) -> float:
        try:
            if val is None or np.isnan(val) or np.isinf(val):
                return default
            return round(float(val), 2)
        except Exception:
            return default

    def _detect_recurring_payments(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Group expense transactions by normalized merchant
        m_txs = defaultdict(list)
        for t in transactions:
            if t["transaction_type"] == "expense":
                m_txs[t["merchant"]].append(t)

        recurring = []
        for merchant, txs in m_txs.items():
            if len(txs) >= 2:
                amounts = [t["amount"] for t in txs if isinstance(t.get("amount"), (int, float))]
                if not amounts:
                    continue
                avg_amt = float(np.mean(amounts))
                std_amt = float(np.std(amounts))
                # Check if amounts are consistent (low coefficient of variation)
                if avg_amt > 100 and avg_amt > 0 and (std_amt / avg_amt < 0.15):
                    sorted_txs = sorted(txs, key=lambda x: x["date"])
                    recurring.append({
                        "merchant": merchant,
                        "category": sorted_txs[0]["category"],
                        "estimated_amount": self._clean_float(avg_amt),
                        "frequency": "monthly",
                        "last_date": sorted_txs[-1]["date"]
                    })

        return sorted(recurring, key=lambda x: x["estimated_amount"], reverse=True)

    def _detect_anomalies(self, transactions: List[Dict[str, Any]], top_categories: List[Dict[str, Any]], monthly_trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        anomalies = []
        
        # 1. Unusually large expense transactions
        expenses = [t for t in transactions if t["transaction_type"] == "expense"]
        if expenses:
            exp_amounts = [t["amount"] for t in expenses]
            mean_exp = float(np.mean(exp_amounts))
            std_exp = float(np.std(exp_amounts))
            threshold = mean_exp + (2.5 * std_exp)

            for t in expenses:
                if t["amount"] > threshold and t["amount"] > 10000:
                    anomalies.append({
                        "id": str(uuid.uuid4()),
                        "type": "unusual_large",
                        "severity": "high",
                        "title": f"Unusually Large Transaction: {t['merchant']}",
                        "description": f"Expense of ₹{t['amount']:,.2f} on {t['date']} is significantly higher than your average expense (₹{mean_exp:,.2f}).",
                        "date": t["date"],
                        "amount": t["amount"],
                        "transaction_id": t.get("id")
                    })

        # 2. Category spending spikes (month-over-month)
        if len(monthly_trends) >= 2:
            prev_m = monthly_trends[-2]
            curr_m = monthly_trends[-1]
            if prev_m["expense"] > 0:
                pct_change = ((curr_m["expense"] - prev_m["expense"]) / prev_m["expense"]) * 100
                if pct_change >= 25.0:
                    anomalies.append({
                        "id": str(uuid.uuid4()),
                        "type": "category_spike",
                        "severity": "medium",
                        "title": f"Monthly Expense Spike in {curr_m['month']}",
                        "description": f"Total monthly spending increased by {pct_change:.1f}% compared to {prev_m['month']}.",
                        "date": curr_m["month"],
                        "amount": curr_m["expense"]
                    })

        # 3. Negative cash flow months
        for m in monthly_trends:
            if m["net"] < 0:
                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "type": "negative_cashflow",
                    "severity": "high",
                    "title": f"Negative Cash Flow in {m['month']}",
                    "description": f"Expenses (₹{m['expense']:,.2f}) exceeded income (₹{m['income']:,.2f}) by ₹{abs(m['net']):,.2f}.",
                    "date": m["month"],
                    "amount": abs(m["net"])
                })

        # 4. Duplicate transaction check (same merchant, date, and amount)
        seen = {}
        for t in transactions:
            key = (t["merchant"], t["date"], t["amount"])
            if key in seen:
                anomalies.append({
                    "id": str(uuid.uuid4()),
                    "type": "potential_duplicate",
                    "severity": "medium",
                    "title": f"Possible Duplicate Transaction: {t['merchant']}",
                    "description": f"Duplicate transaction of ₹{t['amount']:,.2f} detected on {t['date']}.",
                    "date": t["date"],
                    "amount": t["amount"],
                    "transaction_id": t.get("id")
                })
            else:
                seen[key] = t

        return anomalies

    def _assess_financial_health(
        self, total_income: float, total_expenses: float, net_cash_flow: float,
        savings_rate: float, expense_ratio: float, monthly_trends: List[Dict[str, Any]],
        recurring_payments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        num_months = max(1, len(monthly_trends))
        est_monthly_inc = round(total_income / num_months, 2)
        est_monthly_exp = round(total_expenses / num_months, 2)
        avg_net = round(net_cash_flow / num_months, 2)

        income_list = [m["income"] for m in monthly_trends]
        inc_std = float(np.std(income_list)) if len(income_list) > 1 else 0.0
        inc_mean = float(np.mean(income_list)) if len(income_list) > 0 else 1.0
        
        inc_consistency = "High"
        if (inc_std / inc_mean) > 0.35:
            inc_consistency = "Volatile"
        elif (inc_std / inc_mean) > 0.15:
            inc_consistency = "Moderate"

        if savings_rate >= 20.0 and expense_ratio <= 75.0 and net_cash_flow > 0:
            rating = "Good"
            explanation = f"Financial stability appears Good. Net savings rate is healthy at {savings_rate:.1f}%, and monthly expense ratio ({expense_ratio:.1f}%) leaves a comfortable cash buffer."
        elif savings_rate >= 5.0 and expense_ratio <= 88.0 and net_cash_flow >= 0:
            rating = "Moderate"
            explanation = f"Financial stability appears Moderate. Income is relatively consistent, but recurring expenses account for {expense_ratio:.1f}% of monthly income."
        else:
            rating = "Needs Attention"
            explanation = f"Financial stability Needs Attention. Expense ratio is high ({expense_ratio:.1f}%) and net cash flow is constrained or negative."

        return {
            "rating": rating,
            "estimated_monthly_income": est_monthly_inc,
            "estimated_monthly_expenses": est_monthly_exp,
            "average_net_cashflow": avg_net,
            "expense_to_income_ratio": expense_ratio,
            "savings_rate": savings_rate,
            "income_consistency": inc_consistency,
            "summary_explanation": explanation,
            "disclaimer": "AI-assisted financial analysis — not a lending decision."
        }

    def _empty_analytics() -> Dict[str, Any]:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_cash_flow": 0.0,
            "transaction_count": 0,
            "avg_transaction_value": 0.0,
            "savings_rate": 0.0,
            "expense_to_income_ratio": 0.0,
            "top_categories": [],
            "monthly_trends": [],
            "top_merchants": [],
            "recurring_payments": [],
            "anomalies": [],
            "assessment": {
                "rating": "Needs Attention",
                "estimated_monthly_income": 0.0,
                "estimated_monthly_expenses": 0.0,
                "average_net_cashflow": 0.0,
                "expense_to_income_ratio": 0.0,
                "savings_rate": 0.0,
                "income_consistency": "N/A",
                "summary_explanation": "No transaction data uploaded.",
                "disclaimer": "AI-assisted financial analysis — not a lending decision."
            }
        }
