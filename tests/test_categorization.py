from app.categorization.merchant_normalizer import MerchantNormalizer
from app.categorization.rules import CategorizationRulesEngine

def test_merchant_normalizer():
    norm = MerchantNormalizer()
    assert norm.normalize("POS SWIGGY BANGALORE IN") == "Swiggy"
    assert norm.normalize("UPI-ZOMATO-PAYMENT-12930") == "Zomato"
    assert norm.normalize("NFLX DIGITAL SERVICES") == "Netflix"
    assert norm.normalize("UBER RIDE TRIP") == "Uber"

def test_categorization_rules():
    rules = CategorizationRulesEngine()
    cat, conf = rules.classify_by_rules("Swiggy", "SWIGGY BANGALORE IN", "expense")
    assert cat == "Food & Dining"
    assert conf >= 0.90

    cat_rent, conf_rent = rules.classify_by_rules("House Rent", "HOUSE RENT PAYMENT TO LANDLORD", "expense")
    assert cat_rent == "Rent / Housing"
    assert conf_rent >= 0.95

    cat_sal, conf_sal = rules.classify_by_rules("Acme Corp Salary", "ACH SALARY CREDIT ACME TECH CORP", "income")
    assert cat_sal == "Salary / Income"
    assert conf_sal >= 0.95
