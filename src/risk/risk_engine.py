import json

class RiskEngine:
    def __init__(self):
        # 1. Expense Ratio Limit (For Lifestyle Spends)
        self.MAX_EXPENSE_RATIO = 0.60  
        
        # 2. High Risk Keywords (Compliance)
        self.HIGH_RISK_KEYWORDS = ["Binance", "Casino", "Betting", "Luno", "Coinhako"]

        # 3. Structuring / Smurfing Configuration
        self.REPORTING_LIMIT = 5000
        self.SMURF_MIN = 4000 
        self.SMURF_MAX = 4999
        self.STRUCTURING_THRESHOLD = 1 

    def detect_smart_structuring(self, transactions):
        """
        [NEW FEATURE] Velocity Check.
        Counts deposits in the 'Smurfing Zone' ($4k-$5k).
        """
        sus_count = 0
        evidence = []

        for txn in transactions:
            # Handle Pydantic model object or dict
            if hasattr(txn, 'description'):
                description = txn.description.lower()
                amount = txn.amount
                txn_type = txn.type.upper()
            else:
                description = txn.get("description", "").lower()
                amount = txn.get("amount", 0.0)
                txn_type = txn.get("type", "").upper()

            # Logic: Must be a CREDIT (money in) and look like Cash
            if txn_type == "CREDIT" and "cash" in description:
                # The "Smart" Check: Is it trying to evade the limit?
                if self.SMURF_MIN <= amount < self.REPORTING_LIMIT:
                    sus_count += 1
                    evidence.append(f"${amount} on {txn.get('date', 'Unknown') if isinstance(txn, dict) else txn.date}")

        if sus_count > self.STRUCTURING_THRESHOLD:
            return {
                "detected": True,
                "reason": f"POTENTIAL STRUCTURING: Detected {sus_count} deposits in the 'Smurfing Zone' ($4k-$5k). Logic suggests evasion of the ${self.REPORTING_LIMIT} reporting threshold."
            }
        return {"detected": False, "reason": ""}

    def analyze_spending_patterns(self, data):
        """
        Deterministic Math: Calculates TDSR / Expense Ratio.
        """
        income = data.get("total_income", 0.0)
        spending = data.get("total_expenditure", 0.0)
        
        if income == 0:
            return {"ratio": 1.0, "status": "CRITICAL_NO_INCOME", "breakdown": "N/A", "income": 0, "spending": spending}
            
        ratio = spending / income
        status = "PASS" if ratio < self.MAX_EXPENSE_RATIO else "FAIL_AFFORDABILITY"
        
        return {
            "ratio": round(ratio, 2),
            "status": status,
            "income": income,
            "spending": spending
        }

    def evaluate_risk_flags(self, data):
        """
        Compliance Logic (AML/KYC) - Keywords Only.
        Structuring check is handled separately in analyze().
        """
        flags = data.get("risk_flags", [])
        risk_score = 0
        reasons = []
        category = "LOW_RISK"

        # Check 1: Source of Wealth
        if "Salary" not in data.get("source_of_wealth", "Unknown"):
            risk_score += 30
            reasons.append("Unclear Source of Wealth (No Salary Detected)")

        # Check 2: High Risk Merchant Check
        for flag in flags:
            if any(kw.lower() in flag.lower() for kw in self.HIGH_RISK_KEYWORDS):
                risk_score += 50
                if f"Found '{flag}'" not in reasons:
                     reasons.append(f"High Risk Entity: {flag}")
        
        # Intermediate Categorization (before structuring check)
        if risk_score >= 50: 
            category = "HIGH_RISK"
        elif risk_score >= 30: 
            category = "MEDIUM_RISK"

        return {
            "risk_score": risk_score,
            "category": category,
            "reasons": reasons
        }

    def analyze(self, extracted_data):
        print("🧠 Risk Engine: Analyzing Financial Health...")
        
        # 1. Get Transactions List
        # Handle case where extracted_data might not have transactions
        transactions = extracted_data.get("transactions", [])

        # 2. Run Checks
        structuring_check = self.detect_smart_structuring(transactions)
        financial_check = self.analyze_spending_patterns(extracted_data)
        compliance_check = self.evaluate_risk_flags(extracted_data)

        # 3. Integrate Structuring Result
        if structuring_check["detected"]:
            compliance_check["category"] = "HIGH_RISK"
            compliance_check["risk_score"] += 100 # Instant Fail
            compliance_check["reasons"].append(structuring_check["reason"])

        # 4. Final Decision
        # Reject if Affordability Fails OR Compliance Risk is High
        final_decision = "APPROVE"
        if financial_check["status"] != "PASS" or compliance_check["category"] == "HIGH_RISK":
            final_decision = "REJECT"
            
        return {
            "client_name": extracted_data.get("client_name"),
            "final_decision": final_decision,
            "math_analysis": financial_check,
            "compliance_analysis": compliance_check
        }

if __name__ == "__main__":
    # Test with dummy data containing transaction objects
    class DummyTxn:
        def __init__(self, desc, amt, typ, date="2023-01-01"):
            self.description = desc
            self.amount = amt
            self.type = typ
            self.date = date

    dummy_input = {
        "client_name": "Test Subject Smurf",
        "total_income": 5000.0,
        "total_expenditure": 2000.0,
        "risk_flags": [],
        "source_of_wealth": "Salary",
        "transactions": [
            DummyTxn("CASH DEPOSIT BRANCH A", 4850.00, "CREDIT"),
            DummyTxn("CASH DEPOSIT ATM", 4900.00, "CREDIT"),
            DummyTxn("Starbucks", 5.50, "DEBIT")
        ]
    }
    
    engine = RiskEngine()
    report = engine.analyze(dummy_input)
    print(json.dumps(report, indent=2, default=lambda o: o.__dict__))