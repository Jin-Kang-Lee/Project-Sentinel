# Project-Sentinel
An autonomous agentic workflow that automates Customer Due Diligence (CDD) and Wealth Onboarding for financial institutions.

# The Problem
Financial institutions face a massive bottleneck: Manual Document Review.
High-net-worth onboarding requires analysts to manually cross-reference thousands of bank statements against strict Anti-Money Laundering (AML) laws. This process is:
- Slow: Takes days to onboard one client.
- Expensive: Requires teams of human analysts.
- Risky: Humans miss subtle red flags, leading to regulatory fines.

# The Solution
Project Sentinel is an AI-native compliance officer. It automates the forensic review process by deploying a team of AI agents that can read, reason, and decide.
Instead of a human analyst, Sentinel:
Reads unstructured PDFs using Computer Vision.
Calculates financial risk using deterministic math (no AI hallucinations).
Verifies compliance against real-world regulations (MAS Notice 626).
Decides whether to onboard or reject the client instantly.




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
