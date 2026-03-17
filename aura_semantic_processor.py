import json
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_medical_data_fast(input_file: str, output_file: str):
    logger.info("Initializing fast NLP-aware chunker...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,       
        chunk_overlap=100,   
        length_function=len,
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""] 
    )

    with open(input_file, 'r') as f:
        raw_articles = json.load(f)

    processed_chunks = []
    logger.info(f"Processing {len(raw_articles)} medical papers...")

    for article in raw_articles:
        text_content = f"TITLE: {article['title']}\nABSTRACT: {article['abstract']}"
        
    
        chunks = text_splitter.split_text(text_content)
        
        for i, chunk in enumerate(chunks):
            processed_chunks.append({
                "chunk_id": f"{article['pubmed_id']}_{i}",
                "text": chunk,
                "metadata": {
                    "source": article['source'],
                    "niche": article.get('niche', 'general'),
                    "pubmed_id": article['pubmed_id']
                }
            })

    with open(output_file, 'w') as f:
        json.dump(processed_chunks, f, indent=4)
    
    logger.info(f"Done! Created {len(processed_chunks)} high-quality, economical chunks.")

if __name__ == "__main__":
    process_medical_data_fast("aura_raw_data/aura_medical_abstracts.json", "aura_economical_chunks.json")