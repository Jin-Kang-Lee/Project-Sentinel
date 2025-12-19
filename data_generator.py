import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
Faker.seed(42)

# --- Configuration ---
NUM_CLIENTS = 50
RISK_RATIO = 0.2  # 20% High Risk

# Suspicious Categories
RISK_SCENARIOS = {
    "STRUCTURING": ["Cash Deposit ATM", "Cash Deposit Branch"], 
    "CRYPTO_EXIT": ["BINANCE HOLDINGS LTD", "COINBASE IRELAND", "LUNO PTE LTD"],
    "GAMBLING": ["MBS CASINO CASHIER", "RESORTS WORLD SENTOSA", "SG POOLS (PRIVATE) LTD"],
    "SANCTIONED": ["TEHRAN TRADING", "PYONGYANG IMPORT", "MOSCOW GENERAL TRADING"]
}

# Safe Lifestyle Categories (Mapped to messy variants)
LIFESTYLE = {
    "Dining": [
        "POS - TOAST BOX SG", "STARBUCKS COFFEE SINGAPORE", "MCDONALDS - JEWEL", 
        "DIN TAI FUNG - PARAGON", "JUMBO SEAFOOD RIVERSIDE", "GRABFOOD SINGAPORE"
    ],
    "Shopping": [
        "UNIQLO ORCHARD CENTRAL", "SHOPEE PAY SINGAPORE", "LAZADA SINGAPORE", 
        "WATSONS PERSONAL CARE", "ZARA ION ORCHARD", "NTUC FAIRPRICE FIN"
    ],
    "Transport": [
        "GRAB - TRANSPORT", "GOJEK SINGAPORE", "SIMPLYGO TRANSIT", 
        "COMFORTDELGRO TAXI", "SHELL STATION"
    ],
    "Services": [
        "SINGTEL MY BILL", "SP SERVICES UTILITY", "NETFLIX.COM PREM", 
        "SPOTIFY SINGAPORE", "CLOUDFLARE INC", "APPLE SERVICES"
    ]
}

# Transaction Codes for Noise
TXN_CODES = ["MST", "POS", "ATW", "ITR", "DD"] 

def generate_messy_description(base_name):
    """Injects random noise into merchant names to mimic real statements."""
    # If it's already a long messy name (like from LIFESTYLE), maybe just add a code
    # If it's a short risk name (like "Binance"), make it messier
    
    code = random.choice(TXN_CODES)
    ref_num = random.randint(100000, 999999)
    
    # 30% chance of being 'clean', 70% chance of being 'messy'
    if random.random() < 0.3:
        return base_name
    else:
        return f"{code} {base_name} REF-{ref_num}"

def generate_smart_profile(client_id):
    is_risky = random.random() < RISK_RATIO
    income = round(random.uniform(3000, 12000), -2)
    
    return {
        "Client_ID": client_id,
        "Name": fake.name(),
        "Reported_Income": income,
        "Is_High_Risk": is_risky,
        "Risk_Type": random.choice(list(RISK_SCENARIOS.keys())) if is_risky else "None"
    }

def generate_smart_transactions(client):
    transactions = []
    income = client["Reported_Income"]
    
    # 1. Salary Credit (Day 1)
    start_date = datetime.now() - timedelta(days=30)
    transactions.append({
        "Client_ID": client["Client_ID"],
        "Date": (start_date + timedelta(days=1)).strftime("%Y-%m-%d"),
        "Description": f"GIRO SALARY CREDIT - {fake.company().upper()}",
        "Amount": income,
        "Type": "CREDIT",
        "Category": "Income",
        "Balance": 0 
    })

    # 2. Set Spend Targets
    if client["Is_High_Risk"]:
        target_spend_ratio = random.uniform(0.7, 1.5) 
    else:
        target_spend_ratio = random.uniform(0.3, 0.55) 

    target_spend = income * target_spend_ratio
    current_spend = 0
    day_offset = 2
    
    # --- SPECIAL LOGIC: STRUCTURING (The "Smurfing" Scenario) ---
    # If client is a "STRUCTURING" risk, we force multiple deposits just under $5k
    if client["Is_High_Risk"] and client["Risk_Type"] == "STRUCTURING":
        # Create 3-4 large cash deposits
        for _ in range(random.randint(3, 4)):
            day_offset += random.randint(1, 5)
            if day_offset > 28: break
            
            # Amount is suspiciously close to $5,000 (e.g., $4,850)
            structuring_amount = round(random.uniform(4500, 4950), 0)
            
            transactions.append({
                "Client_ID": client["Client_ID"],
                "Date": (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
                "Description": "CASH DEPOSIT BRANCH A", # Clean desc for deposit is common
                "Amount": structuring_amount,
                "Type": "CREDIT", # It's money coming IN (Placement stage of Laundering)
                "Category": "High Risk",
                "Balance": 0
            })

    # 3. Generate Normal/Risky Spending
    while current_spend < target_spend:
        day_offset += random.randint(1, 3)
        if day_offset > 28: break 

        is_risk_txn = False
        # If Risky Client (but NOT Structuring type, as that is deposit-heavy), add bad spending
        if client["Is_High_Risk"] and client["Risk_Type"] != "STRUCTURING":
            if random.random() < 0.3:
                is_risk_txn = True
        
        if is_risk_txn:
            risk_cat = client["Risk_Type"]
            base_merchant = random.choice(RISK_SCENARIOS[risk_cat])
            merchant = generate_messy_description(base_merchant)
            amount = round(random.uniform(500, 3000), 0)
            category = "High Risk"
        else:
            cat_key = random.choice(list(LIFESTYLE.keys()))
            base_merchant = random.choice(LIFESTYLE[cat_key])
            merchant = generate_messy_description(base_merchant) # Add noise!
            amount = round(random.uniform(10, 150), 2)
            category = cat_key

        if (current_spend + amount) > (target_spend * 1.1):
            break

        transactions.append({
            "Client_ID": client["Client_ID"],
            "Date": (start_date + timedelta(days=day_offset)).strftime("%Y-%m-%d"),
            "Description": merchant,
            "Amount": amount,
            "Type": "DEBIT",
            "Category": category,
            "Balance": 0
        })
        current_spend += amount

    # 4. Calculate Running Balance
    balance = random.uniform(5000, 20000)
    transactions.sort(key=lambda x: x['Date'])
    
    final_txns = []
    for t in transactions:
        if t["Type"] == "CREDIT":
            balance += t["Amount"]
        else:
            balance -= t["Amount"]
        
        t["Balance"] = round(balance, 2)
        final_txns.append(t)
        
    return final_txns

# --- Execution ---
if __name__ == "__main__":
    print(f"🚀 Generating NOISY & STRUCTURING synthetic data...")
    all_clients = []
    all_txns = []

    for i in range(1, NUM_CLIENTS + 1):
        client = generate_smart_profile(f"C{i:03d}")
        txns = generate_smart_transactions(client)
        all_clients.append(client)
        all_txns.extend(txns)

    pd.DataFrame(all_clients).to_csv("synthetic_clients_master.csv", index=False)
    pd.DataFrame(all_txns).to_csv("synthetic_transaction_log.csv", index=False)
    
    print("✅ Done! Data is now messy (OCR-ready) and contains Smurfing attacks.")