import os
from operator import itemgetter
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. Load Secrets
load_dotenv()

# 2. Configuration
PRODUCT_FILE = "dbs_products.txt"
DB_PATH = "products_faiss_index"

class WealthAdvisor:
    def __init__(self):
        self.vectorstore = None
        self.retriever = None
        self.chain = None
        self._initialize_db()

    def _initialize_db(self):
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        if os.path.exists(DB_PATH):
            print("💼 Wealth Advisor: Loading Product Database...")
            self.vectorstore = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            print("💼 Wealth Advisor: Indexing Products (One-time)...")
            
            if not os.path.exists(PRODUCT_FILE):
                raise FileNotFoundError(f"❌ {PRODUCT_FILE} not found. Please create the product list.")

            loader = TextLoader(PRODUCT_FILE)
            docs = loader.load()
            
            text_splitter = CharacterTextSplitter(separator="---", chunk_size=500, chunk_overlap=0)
            splits = text_splitter.split_documents(docs)
            
            self.vectorstore = FAISS.from_documents(splits, embeddings)
            self.vectorstore.save_local(DB_PATH)
            print("✅ Product Database Ready!")

        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
        template = """You are a Wealth Manager at DBS.
        Based on the client's profile, recommend suitable financial products.
        
        CLIENT PROFILE:
        Income: ${income}
        Risk Profile: {risk_profile}
        
        AVAILABLE PRODUCTS (from database):
        {context}
        
        INSTRUCTIONS:
        1. Recommend 2 products that match the client's risk level.
        2. Explain WHY you chose them.
        3. Be professional but persuasive.
        
        YOUR RECOMMENDATION:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # --- THE FIX IS HERE ---
        # We use itemgetter to grab specific keys from the input dictionary
        self.chain = (
            {
                "context": itemgetter("query") | self.retriever, 
                "income": itemgetter("income"), 
                "risk_profile": itemgetter("risk_profile")
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def recommend(self, income, risk_profile):
        print(f"💼 Wealth Advisor: Finding products for {risk_profile} profile...")
        
        query = f"{risk_profile} Investment Products"
        
        # We pass a dictionary with 'query', 'income', and 'risk_profile'
        response = self.chain.invoke({
            "query": query, 
            "income": str(income),
            "risk_profile": risk_profile
        })
        return response

if __name__ == "__main__":
    advisor = WealthAdvisor()
    print("\n👇 RECOMMENDATION 👇")
    print(advisor.recommend(income=12000, risk_profile="Low Risk"))