import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Load Secrets
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("❌ OPENAI_API_KEY not found in .env file.")

# 2. Configuration
PDF_PATH = "mas_guidelines.pdf"
DB_PATH = "faiss_index"         # FAISS saves as a folder

class LegalAgent:
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.chain = None
        self._initialize_db()

    def _initialize_db(self):
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # A. Check if DB exists
        if os.path.exists(DB_PATH):
            print("⚖️ Legal Agent: Loading existing FAISS Database...")
            # Allow dangerous deserialization is required for local pickle files
            self.vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            print("⚖️ Legal Agent: Building new FAISS Database from PDF...")
            
            # 1. Load PDF
            if not os.path.exists(PDF_PATH):
                print(f"⚠️ Warning: {PDF_PATH} not found. Creating dummy data for testing.")
                from langchain_core.documents import Document
                docs = [
                    Document(page_content="MAS Guidelines Section 4.1: Banks must perform Enhanced Due Diligence (EDD) on high-risk customers."),
                    Document(page_content="MAS Guidelines Section 8.2: Virtual Assets (Crypto) payments are considered high risk and require Source of Funds verification.")
                ]
            else:
                loader = PyPDFLoader(PDF_PATH)
                docs = loader.load()
            
            # 2. Split
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            # 3. Create FAISS Index
            self.vectorstore = FAISS.from_documents(splits, embeddings)
            
            # 4. Save to Disk
            self.vectorstore.save_local(DB_PATH)
            print("✅ FAISS Database saved to disk!")

        # B. Create Retriever
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})

        # C. Reasoning Chain
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        template = """You are a Banking Compliance Officer. 
        Justify your rejection of this client using the regulations below.
        
        REGULATIONS:
        {context}
        
        RISKS FOUND:
        {risk_factors}
        
        DECISION: REJECTED
        REASON:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        self.chain = (
            {"context": self.retriever, "risk_factors": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def consult(self, risk_flags):
        print(f"⚖️ Legal Agent: Researching laws for {risk_flags}...")
        # Join list into a string for the prompt
        risk_string = ", ".join(risk_flags) if isinstance(risk_flags, list) else str(risk_flags)
        return self.chain.invoke(risk_string)

# --- Test Block ---
if __name__ == "__main__":
    agent = LegalAgent()
    print("\n👇 TEST OPINION 👇")
    print(agent.consult(["Crypto Transfer to Binance"]))