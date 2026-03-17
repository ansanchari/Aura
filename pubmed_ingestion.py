import os
import json
import time
import logging
from Bio import Entrez
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PubMedFetcher:
    def __init__(self, email: str):
        Entrez.email = email
        self.output_dir = "./aura_raw_data"
        os.makedirs(self.output_dir, exist_ok=True)

    def search_pubmed(self, query: str, max_results: int = 100) -> List[str]:
        logger.info(f"Searching PubMed for: '{query}' (Max results: {max_results})")
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()
            id_list = record.get("IdList", [])
            logger.info(f"Found {len(id_list)} articles.")
            return id_list
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def fetch_article_details(self, id_list: List[str]) -> List[Dict]:
        if not id_list:
            return []
        logger.info("Fetching full article details and abstracts...")
        articles = []
        try:
            handle = Entrez.efetch(db="pubmed", id=",".join(id_list), retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            for pubmed_article in records.get('PubmedArticle', []):
                medline_citation = pubmed_article.get('MedlineCitation', {})
                article_data = medline_citation.get('Article', {})
                title = article_data.get('ArticleTitle', 'No Title Available')
                abstract_text = ""
                abstract = article_data.get('Abstract', {}).get('AbstractText', [])
                if abstract:
                    abstract_text = " ".join([str(text) for text in abstract])
                if abstract_text:
                    articles.append({
                        "pubmed_id": medline_citation.get('PMID', ''),
                        "title": title,
                        "abstract": abstract_text,
                        "source": "PubMed Central",
                        "topic": "Women's Health & Endocrinology"
                    })
            logger.info(f"Successfully extracted {len(articles)} complete abstracts.")
            return articles
        except Exception as e:
            logger.error(f"Failed to fetch article details: {e}")
            return []

    def save_to_json(self, articles: List[Dict], filename: str):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=4)
        logger.info(f"Saved data to {filepath}")

def main():
    fetcher = PubMedFetcher(email="sancharisemanti@gmail.com")
    search_niches = {
        "hormonal_health": ["PCOS insulin resistance", "hyperandrogenism symptoms"],
        "cycle_performance": ["menstrual cycle cognitive function", "estrogen athletic performance"],
        "chronic_pain": ["endometriosis diagnostic markers", "pelvic pain management"],
        "preventive_care": ["WPSI 2026 screening guidelines", "HPV self-collection"]
    }
    all_articles = []
    for niche, queries in search_niches.items():
        for query in queries:
            ids = fetcher.search_pubmed(query, max_results=25)
            articles = fetcher.fetch_article_details(ids)
            for a in articles:
                a['niche'] = niche
            all_articles.extend(articles)
        time.sleep(1) 
    if all_articles:
        fetcher.save_to_json(all_articles, "aura_medical_abstracts.json")
        logger.info(f"Pipeline complete. Total medical documents acquired: {len(all_articles)}")

if __name__ == "__main__":
    main()