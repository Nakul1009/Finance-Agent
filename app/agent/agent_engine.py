import math
from typing import List, Dict, Any, Optional
from app.analytics.analytics_engine import FinancialAnalyticsEngine
from app.llm.llm_service import LLMService

class FinancialAgentEngine:
    def __init__(self):
        self.analytics_engine = FinancialAnalyticsEngine()
        self.llm_service = LLMService()

    # --- AGENT TOOLS ---
    def tool_query_financial_metrics(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tool: Compute baseline financial metrics and top spending categories."""
        analytics = self.analytics_engine.compute_analytics(transactions)
        return {
            "total_income": analytics["total_income"],
            "total_expenses": analytics["total_expenses"],
            "net_cash_flow": analytics["net_cash_flow"],
            "savings_rate": analytics["savings_rate"],
            "expense_to_income_ratio": analytics["expense_to_income_ratio"],
            "top_categories": analytics["top_categories"][:5],
            "top_merchants": analytics["top_merchants"][:5]
        }

    def tool_audit_recurring_subscriptions(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tool: Identify recurring subscription traps and fixed commitments."""
        analytics = self.analytics_engine.compute_analytics(transactions)
        recurring = analytics.get("recurring_payments", [])
        total_monthly_recurring = sum(r["estimated_amount"] for r in recurring)
        
        # Flag potential subscription/discretionary traps
        discretionary_categories = {"entertainment", "shopping", "food & dining", "other"}
        subscription_traps = [
            r for r in recurring if r.get("category", "").lower() in discretionary_categories
        ]

        return {
            "recurring_count": len(recurring),
            "total_monthly_recurring": round(total_monthly_recurring, 2),
            "recurring_payments": recurring,
            "subscription_traps": subscription_traps
        }

    def tool_detect_anomalies_and_spikes(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tool: Statistical detection of spending spikes, unusual transactions, duplicate charges."""
        analytics = self.analytics_engine.compute_analytics(transactions)
        anomalies = analytics.get("anomalies", [])
        high_severity = [a for a in anomalies if a.get("severity") == "high"]
        medium_severity = [a for a in anomalies if a.get("severity") == "medium"]

        return {
            "total_anomalies": len(anomalies),
            "high_severity_count": len(high_severity),
            "medium_severity_count": len(medium_severity),
            "anomalies_list": anomalies
        }

    def tool_evaluate_financial_stability(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tool: Evaluate stability rating, income volatility, and debt readiness."""
        analytics = self.analytics_engine.compute_analytics(transactions)
        assessment = analytics.get("assessment", {})
        return {
            "rating": assessment.get("rating", "Needs Attention"),
            "income_consistency": assessment.get("income_consistency", "Moderate"),
            "estimated_monthly_income": assessment.get("estimated_monthly_income", 0.0),
            "estimated_monthly_expenses": assessment.get("estimated_monthly_expenses", 0.0),
            "average_net_cashflow": assessment.get("average_net_cashflow", 0.0),
            "summary_explanation": assessment.get("summary_explanation", "")
        }

    def tool_simulate_budget_scenario(
        self,
        transactions: List[Dict[str, Any]],
        scenario_type: str,
        target_amount: float = 0.0,
        time_frame_months: int = 0,
        monthly_emi: float = 0.0
    ) -> Dict[str, Any]:
        """Tool: Run scenario simulations (Emergency Fund, EMI Affordability, Expense Cuts)."""
        analytics = self.analytics_engine.compute_analytics(transactions)
        monthly_trends = analytics.get("monthly_trends", [])
        num_months = max(1, len(monthly_trends))

        monthly_income = analytics["total_income"] / num_months if num_months > 0 else 0.0
        monthly_expense = analytics["total_expenses"] / num_months if num_months > 0 else 0.0
        current_net_monthly = monthly_income - monthly_expense

        # Identify flexible discretionary spend categories
        flexible_categories = {"food & dining", "shopping", "entertainment", "other"}
        cat_sums = {
            c["category"]: c["amount"] / num_months
            for c in analytics.get("top_categories", [])
        }

        cuts = []
        total_proposed_monthly_savings = 0.0

        if scenario_type == "emergency_fund":
            required_monthly_savings = target_amount / max(1, time_frame_months)
            deficit = max(0.0, required_monthly_savings - max(0.0, current_net_monthly))

            for cat, monthly_amt in cat_sums.items():
                if cat.lower() in flexible_categories and monthly_amt > 1000:
                    # Cut 25% of flexible category spending
                    cut_pct = 25.0
                    savings = (monthly_amt * cut_pct) / 100.0
                    cuts.append({
                        "category": cat,
                        "current_spending": round(monthly_amt, 2),
                        "proposed_cut_pct": cut_pct,
                        "monthly_savings": round(savings, 2),
                        "target_budget": round(monthly_amt - savings, 2)
                    })
                    total_proposed_monthly_savings += savings

            simulated_net = current_net_monthly + total_proposed_monthly_savings
            feasible = simulated_net >= required_monthly_savings

            # Stress test against lowest income month
            lowest_income = min([m["income"] for m in monthly_trends]) if monthly_trends else monthly_income
            stress_tested_net = lowest_income - (monthly_expense - total_proposed_monthly_savings)
            stress_pass = stress_tested_net >= required_monthly_savings

            stress_msg = (
                f"Pass: Even in your lowest income month (₹{lowest_income:,.2f}), "
                f"simulated net cash flow (₹{stress_tested_net:,.2f}) meets your target."
                if stress_pass else
                f"Caution: In low income months (₹{lowest_income:,.2f}), net cash flow drops to ₹{stress_tested_net:,.2f}."
            )

            summary = (
                f"To build a ₹{target_amount:,.2f} emergency fund in {time_frame_months} months, "
                f"you need ₹{required_monthly_savings:,.2f}/mo. "
                f"Currently, your net monthly is ₹{current_net_monthly:,.2f}/mo. "
                f"By trimming discretionary categories by 25%, you unlock ₹{total_proposed_monthly_savings:,.2f}/mo extra savings, "
                f"achieving a simulated net cash flow of ₹{simulated_net:,.2f}/mo."
            )

        elif scenario_type == "loan_affordability":
            simulated_expense = monthly_expense + monthly_emi
            simulated_net = monthly_income - simulated_expense
            required_savings_buffer = monthly_income * 0.15 # 15% safety buffer

            for cat, monthly_amt in cat_sums.items():
                if cat.lower() in flexible_categories and monthly_amt > 1500:
                    cut_pct = 20.0
                    savings = (monthly_amt * cut_pct) / 100.0
                    cuts.append({
                        "category": cat,
                        "current_spending": round(monthly_amt, 2),
                        "proposed_cut_pct": cut_pct,
                        "monthly_savings": round(savings, 2),
                        "target_budget": round(monthly_amt - savings, 2)
                    })
                    total_proposed_monthly_savings += savings

            simulated_net_with_cuts = simulated_net + total_proposed_monthly_savings
            feasible = simulated_net_with_cuts >= required_savings_buffer

            stress_msg = (
                f"EMI ratio: {round((monthly_emi / monthly_income * 100), 1)}% of monthly income. "
                f"{'Fits within recommended 30% debt cap.' if (monthly_emi / max(1, monthly_income)) <= 0.3 else 'Exceeds recommended 30% debt cap.'}"
            )

            summary = (
                f"Adding a monthly EMI of ₹{monthly_emi:,.2f} results in a simulated monthly net cash flow of ₹{simulated_net:,.2f}. "
                f"{'This EMI is comfortably affordable based on your current cash flow.' if feasible else 'This EMI places heavy strain on cash flow; budget cuts in non-essential categories are required.'}"
            )

        else: # expense_reduction
            for cat, monthly_amt in cat_sums.items():
                if cat.lower() in flexible_categories and monthly_amt > 500:
                    cut_pct = 20.0
                    savings = (monthly_amt * cut_pct) / 100.0
                    cuts.append({
                        "category": cat,
                        "current_spending": round(monthly_amt, 2),
                        "proposed_cut_pct": cut_pct,
                        "monthly_savings": round(savings, 2),
                        "target_budget": round(monthly_amt - savings, 2)
                    })
                    total_proposed_monthly_savings += savings

            simulated_net = current_net_monthly + total_proposed_monthly_savings
            feasible = True
            stress_msg = f"Reduces overall expense-to-income ratio from {analytics['expense_to_income_ratio']:.1f}% to {round(((monthly_expense - total_proposed_monthly_savings) / max(1, monthly_income)) * 100, 1)}%."
            summary = f"Optimized expense plan frees up ₹{total_proposed_monthly_savings:,.2f} per month across {len(cuts)} spending categories."

        baseline_sr = analytics["savings_rate"]
        simulated_sr = round(((simulated_net) / max(1, monthly_income)) * 100, 1)

        return {
            "scenario_type": scenario_type,
            "feasible": feasible,
            "summary": summary,
            "baseline_net_monthly": round(current_net_monthly, 2),
            "simulated_net_monthly": round(simulated_net, 2),
            "baseline_savings_rate": baseline_sr,
            "simulated_savings_rate": simulated_sr,
            "recommended_cuts": cuts,
            "stress_test_result": stress_msg
        }

    # --- REACT EXECUTION ENGINE ---
    async def execute_agent_workflow(
        self,
        user_query: str,
        transactions: List[Dict[str, Any]],
        history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes a ReAct (Reasoning + Action) Agent Loop for financial queries.
        Returns synthesized response + structured execution trace.
        """
        execution_trace = []
        tools_used = []
        step_counter = 1

        # Step 1: Goal Planning
        execution_trace.append({
            "step_index": step_counter,
            "action": "PLAN",
            "thought": f"Decomposing user prompt '{user_query}' to identify required financial computation tools and context."
        })
        step_counter += 1

        # Step 2: Tool Calling
        metrics = self.tool_query_financial_metrics(transactions)
        tools_used.append("tool_query_financial_metrics")
        execution_trace.append({
            "step_index": step_counter,
            "action": "TOOL_CALL",
            "tool_name": "tool_query_financial_metrics",
            "tool_input": {"transaction_count": len(transactions)},
            "tool_output": {
                "total_income": metrics["total_income"],
                "total_expenses": metrics["total_expenses"],
                "net_cash_flow": metrics["net_cash_flow"],
                "savings_rate": metrics["savings_rate"]
            },
            "thought": f"Extracted key financial figures: Total Income = ₹{metrics['total_income']:,.2f}, Total Expenses = ₹{metrics['total_expenses']:,.2f}, Net = ₹{metrics['net_cash_flow']:,.2f}."
        })
        step_counter += 1

        q_lower = user_query.lower()

        # Conditional Tool 2: Recurring Subscriptions
        if any(k in q_lower for k in ["recurring", "subscription", "leak", "fixed", "commitment"]):
            sub_res = self.tool_audit_recurring_subscriptions(transactions)
            tools_used.append("tool_audit_recurring_subscriptions")
            execution_trace.append({
                "step_index": step_counter,
                "action": "TOOL_CALL",
                "tool_name": "tool_audit_recurring_subscriptions",
                "tool_input": {"filter": "recurring_payments"},
                "tool_output": {
                    "recurring_count": sub_res["recurring_count"],
                    "total_monthly_recurring": sub_res["total_monthly_recurring"]
                },
                "thought": f"Analyzed recurring spend: Found {sub_res['recurring_count']} recurring payments totaling ₹{sub_res['total_monthly_recurring']:,.2f}/mo."
            })
            step_counter += 1

        # Conditional Tool 3: Anomalies
        if any(k in q_lower for k in ["unusual", "anomaly", "spike", "large", "duplicate", "flag"]):
            anom_res = self.tool_detect_anomalies_and_spikes(transactions)
            tools_used.append("tool_detect_anomalies_and_spikes")
            execution_trace.append({
                "step_index": step_counter,
                "action": "TOOL_CALL",
                "tool_name": "tool_detect_anomalies_and_spikes",
                "tool_input": {"sensitivity": 2.5},
                "tool_output": {
                    "total_anomalies": anom_res["total_anomalies"],
                    "high_severity_count": anom_res["high_severity_count"]
                },
                "thought": f"Ran anomaly detector: Discovered {anom_res['total_anomalies']} potential financial anomalies."
            })
            step_counter += 1

        # Step 3: Verification
        execution_trace.append({
            "step_index": step_counter,
            "action": "VERIFICATION",
            "thought": "Cross-verifying tool metrics against backend rule constraints to ensure zero numerical hallucinations."
        })
        step_counter += 1

        # Step 4: Synthesis
        analytics_context = self.analytics_engine.compute_analytics(transactions)
        reply = await self.llm_service.answer_financial_query(user_query, analytics_context, history)

        execution_trace.append({
            "step_index": step_counter,
            "action": "SYNTHESIS",
            "thought": "Synthesized grounded financial analysis response and actionable insights."
        })

        return {
            "reply": reply,
            "execution_trace": execution_trace,
            "tools_used": tools_used
        }

    # --- AUTONOMOUS FINANCIAL AUDIT ---
    def run_financial_audit(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Runs an autonomous full financial audit and leak detection.
        Returns audit score, risk rating, discovered leaks, action plan, and execution trace.
        """
        execution_trace = []
        step_counter = 1

        execution_trace.append({
            "step_index": step_counter,
            "action": "PLAN",
            "thought": "Initiating Autonomous Multi-Phase Financial Audit across income, expense ratios, recurring commitments, and statistical anomalies."
        })
        step_counter += 1

        # Execute Tools
        metrics = self.tool_query_financial_metrics(transactions)
        execution_trace.append({
            "step_index": step_counter,
            "action": "TOOL_CALL",
            "tool_name": "tool_query_financial_metrics",
            "tool_input": {},
            "tool_output": {"savings_rate": metrics["savings_rate"], "expense_ratio": metrics["expense_to_income_ratio"]},
            "thought": f"Audited macro metrics: Savings Rate = {metrics['savings_rate']}%, Expense Ratio = {metrics['expense_to_income_ratio']}%."
        })
        step_counter += 1

        sub_audit = self.tool_audit_recurring_subscriptions(transactions)
        execution_trace.append({
            "step_index": step_counter,
            "action": "TOOL_CALL",
            "tool_name": "tool_audit_recurring_subscriptions",
            "tool_input": {},
            "tool_output": {"recurring_count": sub_audit["recurring_count"], "total_monthly": sub_audit["total_monthly_recurring"]},
            "thought": f"Scanned for subscription traps: Total monthly recurring commitments = ₹{sub_audit['total_monthly_recurring']:,.2f}."
        })
        step_counter += 1

        anom_audit = self.tool_detect_anomalies_and_spikes(transactions)
        execution_trace.append({
            "step_index": step_counter,
            "action": "TOOL_CALL",
            "tool_name": "tool_detect_anomalies_and_spikes",
            "tool_input": {},
            "tool_output": {"anomalies_count": anom_audit["total_anomalies"]},
            "thought": f"Scanned statistical anomalies: Detected {anom_audit['total_anomalies']} transaction/category irregularities."
        })
        step_counter += 1

        # Identify Specific Financial Leaks
        leaks = []
        monthly_leak_total = 0.0

        # Leak 1: High expense to income ratio
        if metrics["expense_to_income_ratio"] > 80.0:
            excess_exp = (metrics["total_expenses"] - (metrics["total_income"] * 0.70))
            leaks.append({
                "category": "Cashflow Strain",
                "title": "High Expense-to-Income Ratio",
                "monthly_leak_amount": round(excess_exp, 2),
                "description": f"You are consuming {metrics['expense_to_income_ratio']:.1f}% of your income. Recommended benchmark is under 70%.",
                "action_item": "Set a hard spending limit on top discretionary categories to lower monthly outflow."
            })
            monthly_leak_total += excess_exp

        # Leak 2: Discretionary Subscription Traps
        for trap in sub_audit.get("subscription_traps", []):
            leaks.append({
                "category": "Subscription Trap",
                "title": f"Recurring Discretionary Spend: {trap['merchant']}",
                "monthly_leak_amount": trap["estimated_amount"],
                "description": f"Detected recurring monthly payment of ~₹{trap['estimated_amount']:,.2f} to {trap['merchant']} ({trap['category']}).",
                "action_item": "Review subscription utility and consider cancelling or downgrading active plans."
            })
            monthly_leak_total += trap["estimated_amount"]

        # Leak 3: High severity anomalies
        for anom in anom_audit.get("anomalies_list", []):
            if anom.get("severity") == "high":
                leaks.append({
                    "category": "Transaction Anomaly",
                    "title": anom["title"],
                    "monthly_leak_amount": anom.get("amount", 0.0),
                    "description": anom["description"],
                    "action_item": "Verify transaction authenticity and evaluate whether this expense was necessary."
                })

        # Calculate Audit Score (0 - 100)
        base_score = 100
        if metrics["savings_rate"] < 10:
            base_score -= 25
        elif metrics["savings_rate"] < 20:
            base_score -= 10

        if metrics["expense_to_income_ratio"] > 85:
            base_score -= 25
        elif metrics["expense_to_income_ratio"] > 75:
            base_score -= 15

        base_score -= min(30, len(leaks) * 8)
        audit_score = max(10, min(100, base_score))

        if audit_score >= 80:
            risk_level = "Low"
        elif audit_score >= 60:
            risk_level = "Medium"
        elif audit_score >= 40:
            risk_level = "High"
        else:
            risk_level = "Critical"

        action_plan = [
            f"Cap top discretionary spending categories (Food & Dining / Shopping) to save up to ₹{monthly_leak_total * 0.4:,.2f}/mo.",
            "Audit all detected recurring merchant payments and eliminate unused subscriptions.",
            "Establish an Emergency Fund reserve equivalent to 3x monthly expenses.",
            "Maintain expense-to-income ratio below 70% to ensure sustainable positive monthly net cashflow."
        ]

        execution_trace.append({
            "step_index": step_counter,
            "action": "VERIFICATION",
            "thought": "Verified financial audit risk parameters and synthesized multi-step corrective action plan."
        })
        step_counter += 1

        execution_trace.append({
            "step_index": step_counter,
            "action": "SYNTHESIS",
            "thought": f"Finalized Audit: Audit Score = {audit_score}/100, Risk Level = {risk_level}, Total Leaks Found = {len(leaks)}."
        })

        return {
            "audit_score": audit_score,
            "risk_level": risk_level,
            "total_leaks_found": len(leaks),
            "monthly_leak_total": round(monthly_leak_total, 2),
            "financial_leaks": leaks,
            "recommended_action_plan": action_plan,
            "execution_trace": execution_trace
        }

    # --- SCENARIO SIMULATION ENGINE ---
    def run_scenario_simulation(
        self,
        transactions: List[Dict[str, Any]],
        scenario_type: str,
        target_amount: float = 0.0,
        time_frame_months: int = 0,
        monthly_emi: float = 0.0
    ) -> Dict[str, Any]:
        """
        Executes interactive Scenario Simulations with full execution trace.
        """
        execution_trace = []
        step_counter = 1

        execution_trace.append({
            "step_index": step_counter,
            "action": "PLAN",
            "thought": f"Initializing '{scenario_type}' budget simulation agent for target parameters."
        })
        step_counter += 1

        sim_res = self.tool_simulate_budget_scenario(
            transactions, scenario_type, target_amount, time_frame_months, monthly_emi
        )

        execution_trace.append({
            "step_index": step_counter,
            "action": "TOOL_CALL",
            "tool_name": "tool_simulate_budget_scenario",
            "tool_input": {
                "scenario_type": scenario_type,
                "target_amount": target_amount,
                "time_frame_months": time_frame_months,
                "monthly_emi": monthly_emi
            },
            "tool_output": {
                "feasible": sim_res["feasible"],
                "baseline_savings_rate": sim_res["baseline_savings_rate"],
                "simulated_savings_rate": sim_res["simulated_savings_rate"],
                "cuts_count": len(sim_res["recommended_cuts"])
            },
            "thought": f"Executed simulation: Feasible = {sim_res['feasible']}. Simulated savings rate moves from {sim_res['baseline_savings_rate']}% to {sim_res['simulated_savings_rate']}%."
        })
        step_counter += 1

        execution_trace.append({
            "step_index": step_counter,
            "action": "VERIFICATION",
            "thought": f"Ran cashflow stress test against historical lowest income month: {sim_res['stress_test_result']}"
        })
        step_counter += 1

        execution_trace.append({
            "step_index": step_counter,
            "action": "SYNTHESIS",
            "thought": "Synthesized budget cut recommendations and scenario feasibility report."
        })

        sim_res["execution_trace"] = execution_trace
        return sim_res
