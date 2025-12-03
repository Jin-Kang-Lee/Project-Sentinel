import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
# Set seed for reproducibility (so you get the same 'random' data every time you run it)
random.seed(42)
Faker.seed(42)

# --- Configuration ---
NUM_CLIENTS = 50
RISK_RATIO = 0.2  # 20% of clients will be High Risk (10 clients)

# Compliance Risk Scenarios (The "Red Flags" for your Agent to find)
RISK_SCENARIOS = {
    "STRUCTURING": ["Cash Deposit ATM", "Cash Deposit Branch"], # Smurfing: deposits just under reporting limits
    "CRYPTO_EXIT": ["Binance", "Coinbase", "Crypto.com", "Luno", "Coinhako", "Gemini Trust"],
    "GAMBLING": ["MBS Casino", "Resorts World Sentosa", "Singapore Pools", "Bet365", "888 Casino"],
    "SANCTIONED": ["Tehran Trading", "Pyongyang Import", "Moscow General", "Iran Oil Co"]
}

# Normal, safe merchants for background noise
SAFE_MERCHANTS = [
    "Grab", "Shopee", "NTUC FairPrice", "Netflix", "Spotify", "Toastbox", "Uniqlo", 
    "Starbucks", "Foodpanda", "Singtel", "SP Services", "McDonalds", "Watson's",
    "Cold Storage", "Yakun Kaya Toast", "SimplyGo", "Golden Village"
]

def generate_client_profile(client_id):
    """Generates a bio for a client."""
    # Determine if this client is a "Bad Actor" based on the 20% ratio
    is_risky = random.random() < RISK_RATIO
    
    profile = {
        "Client_ID": client_id,
        "Name": fake.name(),
        "Passport_Number": fake.passport_number(),
        "Nationality": fake.country(),
        "Job_Title": fake.job(),
        "Reported_Income": round(random.uniform(3000, 15000), -2), # e.g. 5000.0, 12000.0
        "Is_High_Risk": is_risky, # Ground Truth (Hidden from Agent, used for checking your work)
        "Risk_Type": "None"
    }
    
    if is_risky:
        profile["Risk_Type"] = random.choice(list(RISK_SCENARIOS.keys()))
        
    return profile

def generate_transactions(client_profile, num_txns=40):
    """Generates 1 month of bank transactions for a specific client."""
    transactions = []
    current_balance = random.uniform(5000, 20000)
    start_date = datetime.now() - timedelta(days=30)
    
    # 1. Monthly Salary Credit (Always comes in first)
    salary_date = start_date + timedelta(days=1)
    transactions.append({
        "Client_ID": client_profile["Client_ID"],
        "Date": salary_date.strftime("%Y-%m-%d"),
        "Description": f"Salary Credit - {fake.company()}",
        "Amount": client_profile["Reported_Income"],
        "Type": "CREDIT",
        "Category": "Income",
        "Balance": round(current_balance + client_profile["Reported_Income"], 2)
    })
    current_balance += client_profile["Reported_Income"]

    # 2. Generate Daily Spend
    for i in range(num_txns):
        date = start_date + timedelta(days=random.randint(1, 28))
        
        # Default: Safe Transaction
        merchant = random.choice(SAFE_MERCHANTS)
        amount = round(random.uniform(10, 200), 2)
        txn_type = "DEBIT"
        category = "Lifestyle"
        
        # INJECT RISK if applicable
        if client_profile["Is_High_Risk"]:
            risk_type = client_profile["Risk_Type"]
            
            # Scenario A: Structuring (Smurfing)
            # Multiple cash deposits just under the $5k reporting limit (e.g. $4,900)
            if risk_type == "STRUCTURING" and random.random() < 0.25:
                merchant = random.choice(RISK_SCENARIOS["STRUCTURING"])
                # Amount is suspiciously close to 5000 (e.g., 4850, 4990)
                amount = round(random.uniform(4800, 4999), 0) 
                txn_type = "CREDIT"
                category = "Cash Deposit"
                
            # Scenario B: Crypto/Gambling/Sanctions
            # Large outflows to risky entities
            elif risk_type in ["CRYPTO_EXIT", "GAMBLING", "SANCTIONED"] and random.random() < 0.15:
                merchant = random.choice(RISK_SCENARIOS[risk_type])
                amount = round(random.uniform(1000, 8000), 2)
                txn_type = "DEBIT"
                category = "High Risk"

        # Update balance logic
        if txn_type == "CREDIT":
            current_balance += amount
        else:
            current_balance -= amount
            
        transactions.append({
            "Client_ID": client_profile["Client_ID"],
            "Date": date.strftime("%Y-%m-%d"),
            "Description": merchant,
            "Amount": amount,
            "Type": txn_type,
            "Category": category,
            "Balance": round(current_balance, 2)
        })
    
    # Sort by date so the statement looks real
    transactions.sort(key=lambda x: x['Date'])
    return transactions

# --- Main Execution ---
if __name__ == "__main__":
    print(f"🚀 Generating synthetic data for {NUM_CLIENTS} clients...")

    all_clients = []
    all_transactions = []

    for i in range(1, NUM_CLIENTS + 1):
        c_id = f"C{i:03d}"
        client = generate_client_profile(c_id)
        txns = generate_transactions(client)
        
        all_clients.append(client)
        all_transactions.extend(txns)

    # Convert to Pandas DataFrames
    df_clients = pd.DataFrame(all_clients)
    df_txns = pd.DataFrame(all_transactions)

    # Save to CSV
    df_clients.to_csv("synthetic_clients_master.csv", index=False)
    df_txns.to_csv("synthetic_transaction_log.csv", index=False)

    print("✅ Data Generation Complete!")
    print(f"Files Created: 'synthetic_clients_master.csv' and 'synthetic_transaction_log.csv'")
    print("-" * 30)
    print("Risk Profile Breakdown:")
    print(df_clients['Risk_Type'].value_counts())
    print("-" * 30)
    print("Preview of Transactions:")
    print(df_txns.head())