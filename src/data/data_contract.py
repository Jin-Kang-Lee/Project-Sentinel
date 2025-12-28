from pydantic import BaseModel, Field
from typing import List, Optional

# Define a sub-model for individual transactions
class TransactionItem(BaseModel):
    date: str = Field(description="Date of transaction in YYYY-MM-DD format")
    description: str = Field(description="Description of the transaction (Merchant name, etc.)")
    amount: float = Field(description="The monetary amount")
    type: str = Field(description="Type of transaction: 'CREDIT' (Deposit) or 'DEBIT' (Withdrawal)")

# This defines the "Shape" of the data we expect from the Bank Statement
class FinancialExtraction(BaseModel):
    client_name: str = Field(description="Name of the client found in the document header")
    account_number: str = Field(description="Account number if found, else 'Unknown'")
    statement_date: str = Field(description="Date of the statement in YYYY-MM-DD format")
    
    # Robustness Feature: Force these to be Floats (Numbers), not Strings
    total_income: float = Field(description="Sum of all CREDIT transactions (Salary, Dividends, etc)")
    total_expenditure: float = Field(description="Sum of all DEBIT transactions")
    
    # Robustness Feature: Constrain the AI to specific choices
    source_of_wealth: str = Field(
        description="The primary source of funds",
        # The AI can ONLY choose one of these. It cannot invent "Crypto Bro" as a source.
        enum=["Salary", "Business", "Investments", "Inheritance", "Unknown"]
    )
    
    # Robustness Feature: Ensure we always get a list, even if empty
    risk_flags: List[str] = Field(
        description="List of suspicious merchants (e.g. Binance, Casino). Return empty list [] if none found."
    )

    # [NEW] Full Transaction List for Velocity Checks
    transactions: List[TransactionItem] = Field(
        description="List of all transactions found in the statement table."
    )