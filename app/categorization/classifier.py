from typing import Dict, Any, List
from app.categorization.merchant_normalizer import MerchantNormalizer
from app.categorization.rules import CategorizationRulesEngine
from app.llm.llm_service import LLMService

class HybridTransactionClassifier:
    def __init__(self, llm_service: LLMService = None):
        self.normalizer = MerchantNormalizer()
        self.rules_engine = CategorizationRulesEngine()
        self.llm_service = llm_service or LLMService()

    async def categorize_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Categorizes a raw parsed transaction using Hybrid Rule + LLM approach.
        """
        desc = tx.get("description", "")
        tx_type = tx.get("transaction_type", "expense")
        amount = tx.get("amount", 0.0)

        # 1. Normalize merchant name
        merchant = self.normalizer.normalize(desc)
        tx["merchant"] = merchant

        # 2. Try Rule-based classification
        category, confidence = self.rules_engine.classify_by_rules(merchant, desc, tx_type)
        method = "rule"

        # 3. If confidence < 0.70, use Nemotron LLM fallback
        if confidence < 0.70 and self.llm_service.is_available():
            llm_res = await self.llm_service.classify_transaction(merchant, desc, amount, tx_type)
            if llm_res and llm_res.get("category"):
                category = llm_res.get("category")
                confidence = llm_res.get("confidence", 0.81)
                method = "nemotron"

        tx["category"] = category
        tx["confidence"] = round(confidence, 2)
        tx["categorization_method"] = method
        return tx

    async def categorize_batch(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        categorized = []
        for tx in transactions:
            c_tx = await self.categorize_transaction(tx)
            categorized.append(c_tx)
        return categorized
