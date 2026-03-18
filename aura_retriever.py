import logging
import os
import shutil
from dotenv import load_dotenv

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AuraHealthRouter:
    def __init__(self, github_db_path: str = "./qdrant_aura_db"):
        logger.info("Initializing Aura's Retrieval System...")
        
        writable_db_path = "/tmp/aura_qdrant_db"
        
        if not os.path.exists(writable_db_path):
            logger.info("Moving database to writable Linux memory...")
            try:
                shutil.copytree(github_db_path, writable_db_path)
            except Exception as e:
                logger.error(f"Failed to copy DB: {e}")
        
        logger.info("Connecting to writable vector database...")
        self.client = QdrantClient(
            path=writable_db_path,
            force_disable_check_same_thread=True
        )
        
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name="womens_health_knowledge",
            embedding=self.embeddings,
        )
        
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        
        logger.info("Connecting to the official Mistral AI servers...")
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            temperature=0.1,
            max_tokens=1000,
        )
        
        self.prompt = self._build_prompt()
        self.qa_chain = self._build_chain()
        logger.info("Aura is fully connected and ready.")

    def _build_prompt(self):
        template = """System: You are Aura, an empathetic, highly accurate women's health assistant.
        You must answer the user's question using ONLY the provided Medical Context below.
        If the answer is not in the context, say "I don't have enough verified clinical data to answer that accurately right now."
        Do not make up information.
        
        Medical Context:
        {context}
        
        User's Question: {input}
        
        Aura's Answer:"""
        return PromptTemplate.from_template(template)

    def _build_chain(self):
        combine_docs_chain = create_stuff_documents_chain(self.llm, self.prompt)
        return create_retrieval_chain(self.retriever, combine_docs_chain)

    def ask_aura(self, question: str) -> str:
        logger.info(f"Processing query: '{question}'")
        try:
            response = self.qa_chain.invoke({"input": question})
            return response["answer"]
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "I experienced a minor system error while contacting the cloud server."

def main():
    aura = AuraHealthRouter()
    print("\n" + "="*50)
    print("Aura Health Agent is Online (Type 'quit' to exit)")
    print("="*50 + "\n")
    
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ['quit', 'exit']:
            print("Shutting down safely. Goodbye!")
            break
        
        answer = aura.ask_aura(user_query)
        print(f"\nAura: {answer}")

if __name__ == "__main__":
    main()