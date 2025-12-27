# Sentinel: Automated KYC & Wealth Onboarding Engine to detect AML
An autonomous agentic workflow that automates Customer Due Diligence (CDD) and Wealth Onboarding for financial institutions.
Designed to eliminate the 90-day onboarding bottleneck by replacing manual due diligence with autonomous agents. Delivers a MAS 626-compliant, audit-ready workflow that slashes processing time to under 24 hours.

# The Problem
Financial institutions face a massive bottleneck in High-Net-Worth & Corporate Onboarding. Compliance teams must manually cross-reference thousands of pages of unstructured bank statements against strict Anti-Money Laundering (AML) laws.
- 120-Day Cycles: Corporate and Private Banking onboarding now averages 90–120 days, causing a 70% client drop-off rate (Fenergo 2025).
- Massive Costs: Institutions spend up to $25,000 per corporate client on manual due diligence and "stare-and-compare" verification.
- Crypto Scalability: Crypto exchanges face 50–80% abandonment and massive backlogs during market surges because human teams cannot scale linearly with user volume.
- Regulatory Risk: Manual fatigue leads to missed red flags, resulting in billions in fines for non-compliance with MAS 626, BSA, and MiCA frameworks.

# The Solution
Sentinel is not just a chatbot; it is an autonomous, event-driven compliance officer. It fundamentally changes the workflow by decoupling Probabilistic AI (reading documents) from Deterministic Logic (calculating risk), ensuring decisions are legally defensible.
Instead of a human analyst, Sentinel:
1. Ingest: Extracts data from unstructured PDFs (Source of Wealth, Bank Statements) using Vision AI (LlamaParse).
2. Verify: Calculates financial risk ratios using strict Python logic (Zero Hallucination).
3. Audit: Cross-references findings against MAS Notice 626 regulations using RAG.
4. Decide: Instantly flags high-risk entities or approves standard cases for onboarding.




# Core Capabilities
Intelligent Document Processing (IDP)
What it does: Converts messy, unstructured bank statements (PDFs) into clean, structured data.
Tech: Uses LlamaParse (Vision AI) to "see" table layouts that standard tools miss.

Zero-Hallucination Risk Guardrails
What it does: Prevents the AI from making up numbers.
Tech: Uses a Neuro-Symbolic approach. The AI extracts the data, but a strict Python Engine calculates the financial ratios (TDSR/Debt), ensuring 100% mathematical accuracy.

Automated Compliance Checks
What it does: Checks every transaction against money laundering typologies (e.g., Structuring, Crypto Layering).
Tech: Uses RAG (Retrieval Augmented Generation) to cross-reference findings against the MAS Notice 626 (Singapore's AML Laws) for legally defensible decisions.

Built With
AI Agent Orchestration: LangGraph, LangChain
AI Models: OpenAI GPT-4o, LlamaParse (Vision)
Data Engineering: Pydantic (Validation), FAISS (Vector DB)

This project was built as a specialized portfolio piece demonstrating Agentic AI applications in FinTech & Regulatory Compliance.
