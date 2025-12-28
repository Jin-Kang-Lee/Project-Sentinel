import os
from dotenv import load_dotenv
from llama_parse import LlamaParse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Import your new strict data model
from src.data.data_contract import FinancialExtraction

load_dotenv()

# Setup LlamaParse
# result_type="markdown" is best for tables
parser = LlamaParse(result_type="markdown", verbose=True, language="en")

# Setup LLM with Structured Output (The Robust Fix)
# We use temperature=0 for maximum determinism
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# This is the Magic Line: "Bind" the model to the Pydantic class
structured_llm = llm.with_structured_output(FinancialExtraction)

# Define Prompt
extraction_prompt = ChatPromptTemplate.from_template(
    """
    You are an expert Forensic Accountant.
    Analyze the following bank statement text and extract the financial data.
    
    BANK STATEMENT CONTENT:
    {context}
    
    INSTRUCTIONS:
    1. Scan for 'Salary' or recurring large deposits to determine Source of Wealth.
    2. Scan for High Risk keywords: Crypto, Binance, Coinbase, Casino, MBS, Betting.
    3. Calculate totals (Income vs Expenditure) precisely based on the transactions.
    4. EXTRACT THE FULL LIST OF TRANSACTIONS into the 'transactions' list.
       - Ensure the 'amount' is a number (no $ symbols).
       - Ensure 'type' is either CREDIT or DEBIT.
    """
)

def extract_data(pdf_path):
    print(f"📄 Processing: {pdf_path}...")
    
    try:
        # Phase 1: OCR (Vision)
        print("   ...Sending to LlamaCloud for OCR...")
        documents = parser.load_data(pdf_path)
        raw_text = "\n".join([doc.text for doc in documents])
        
        # Phase 2: Extraction with Validation
        print("   ...Analyzing with Validated Schema...")
        chain = extraction_prompt | structured_llm
        
        # The result is now a Pydantic Object (FinancialExtraction)
        result = chain.invoke({"context": raw_text})
        
        # Convert back to a clean dictionary for the rest of your app
        return result.model_dump()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in Extraction: {e}")
        return None

if __name__ == "__main__":
    # Test on a PDF
    import json
    
    # Change this to a file you actually generated
    test_file = "synthetic_pdfs/Statement_C005.pdf" 
    
    if os.path.exists(test_file):
        data = extract_data(test_file)
        print(json.dumps(data, indent=2))
        
        # Verification: Check if transactions were extracted
        if data and "transactions" in data:
            print(f"\n✅ Success! Extracted {len(data['transactions'])} transactions.")
        else:
            print("\n⚠️ Warning: No transactions found in output.")
            
    else:
        print("File not found. Please run pdf_generator.py first.")