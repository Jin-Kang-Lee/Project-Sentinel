import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# --- Import your "Specialists" ---
from src.io.extractor import extract_data
from src.risk.risk_engine import RiskEngine
from src.agents.legal_agent import LegalAgent
from src.agents.wealth_advisor import WealthAdvisor

# Initialize the logic classes
print("🚀 System: Initializing Agents...")
risk_engine = RiskEngine()
legal_agent = LegalAgent()
wealth_advisor = WealthAdvisor()
print("✅ System: Agents Ready.")

# 1. Define the Shared State
class AgentState(TypedDict):
    pdf_path: str           # Input
    client_data: dict       # Data from Extractor
    risk_analysis: dict     # Output from Risk Engine
    legal_opinion: str      # Output from Legal Agent (if rejected for AML)
    wealth_plan: str        # Output from Wealth Advisor (if approved)
    final_decision: str     # "APPROVE" or "REJECT"

# 2. Define the Nodes

def extraction_node(state: AgentState):
    """Station 1: The Eyes (Vision)"""
    print("\n--- PHASE 1: EXTRACTION ---")
    pdf = state["pdf_path"]
    data = extract_data(pdf) 
    
    if not data:
        return {"final_decision": "ERROR_READING_PDF"}
    return {"client_data": data}

def risk_assessment_node(state: AgentState):
    """Station 2: The Logic (Math & Rules)"""
    print("\n--- PHASE 2: RISK ASSESSMENT ---")
    data = state["client_data"]
    analysis = risk_engine.analyze(data)
    return {"risk_analysis": analysis}

def legal_check_node(state: AgentState):
    """Station 3A: The Lawyer (RAG) - Only runs if High AML Risk"""
    print("\n--- PHASE 3A: LEGAL REVIEW ---")
    risk_data = state["risk_analysis"]["compliance_analysis"]
    flags = risk_data["reasons"]
    
    opinion = legal_agent.consult(flags)
    return {"legal_opinion": opinion}

def wealth_advisory_node(state: AgentState):
    """Station 3B: The Salesperson (RAG) - Only runs if Low AML Risk"""
    print("\n--- PHASE 3B: WEALTH ADVISORY ---")
    data = state["client_data"]
    
    # Extract simple profile data for recommendation
    income = data.get("total_income", 0)
    risk_profile = "High Risk" if income > 20000 else "Low Risk"
    
    recommendation = wealth_advisor.recommend(income, risk_profile)
    return {"wealth_plan": recommendation}

def final_decision_node(state: AgentState):
    """Station 4: The Stamper (Updated for Bank-Grade Reporting)"""
    print("\n--- PHASE 4: FINAL VERDICT ---")
    
    # Retrieve data from State
    decision = state["risk_analysis"]["final_decision"]
    math_check = state["risk_analysis"]["math_analysis"]
    compliance_check = state["risk_analysis"]["compliance_analysis"]
    
    # Construct the final report
    print(f"🛑 FINAL DECISION: {decision}")
    
    if decision == "REJECT":
        print("\n❌ REJECTION ANALYSIS:")
        
        # 1. Check Affordability (Math) - FIXED TO USE 'ratio' instead of 'tdsr'
        if math_check["status"] != "PASS":
            # The new risk engine uses 'ratio' (Expense Ratio), not 'tdsr'
            ratio_pct = math_check["ratio"] * 100
            print(f"   [FINANCIAL RISK]: Unsustainable Spending Patterns")
            print(f"   - Expense Ratio: {ratio_pct:.1f}% (Policy Limit: 60.0%)")
            print(f"   - Assessment: Applicant has insufficient Net Disposable Income (NDI).")

        # 2. Check Compliance (AML)
        if compliance_check["category"] == "HIGH_RISK":
            print(f"   [COMPLIANCE RISK]: AML Red Flags Detected")
            print(f"   - Flags: {', '.join(compliance_check['reasons'])}")
            
            # If Legal Agent ran, show the legal opinion
            if state.get("legal_opinion"):
                print(f"   [LEGAL MEMO]: {state['legal_opinion']}")
    
    else:
        print("\n✅ APPROVED. NEXT STEPS:")
        print(f"   {state.get('wealth_plan', 'Open Standard Account')}")
        
    return {"final_decision": decision}

# 3. Define the Router
def compliance_router(state: AgentState) -> Literal["call_lawyer", "call_advisor"]:
    analysis = state["risk_analysis"]
    category = analysis["compliance_analysis"]["category"]
    
    # If AML Risk is High -> Lawyer
    if category == "HIGH_RISK":
        print("   --> ⚠️ High AML Risk detected. Routing to Legal Agent.")
        return "call_lawyer"
    else:
        # Low AML Risk -> Wealth Advisor
        print("   --> ✅ Low AML Risk. Routing to Wealth Advisor path.")
        return "call_advisor"

# 4. Build the Graph
workflow = StateGraph(AgentState)

workflow.add_node("extractor", extraction_node)
workflow.add_node("risk_engine", risk_assessment_node)
workflow.add_node("legal_agent", legal_check_node)
workflow.add_node("wealth_advisor", wealth_advisory_node)
workflow.add_node("finalizer", final_decision_node)

workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "risk_engine")

workflow.add_conditional_edges(
    "risk_engine",
    compliance_router,
    {
        "call_lawyer": "legal_agent",
        "call_advisor": "wealth_advisor"
    }
)

workflow.add_edge("legal_agent", "finalizer")
workflow.add_edge("wealth_advisor", "finalizer")
workflow.add_edge("finalizer", END)

app = workflow.compile()

# --- CLI Entry Point ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the Sentinel pipeline on a PDF.")
    parser.add_argument("--pdf", required=True, help="Path to the bank statement PDF")
    args = parser.parse_args()

    pdf_path = args.pdf
    if os.path.exists(pdf_path):
        print(f"dYs? Launching Sentinel Pipeline for {pdf_path}...")
        result = app.invoke({"pdf_path": pdf_path})
        print("-----------------------------------------")
        print("?o. WORKFLOW COMPLETE")
        print("-----------------------------------------")
        print(result)
    else:
        print(f"??O File {pdf_path} not found.")
