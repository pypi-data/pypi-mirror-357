from typing import List
from datetime import datetime
import requests
import feedparser

class PubMedSearch:
    """Factory function for PubMed paper search functionality."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    @staticmethod
    def search(query: str, max_results: int = 10) -> List[dict]:
        """Search for papers on PubMed.

        Args:
            query (str): Search query string.
            max_results (int): Maximum number of results to return.

        Returns:
            List[dict]: List of paper metadata dictionaries.
        """
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        response = requests.get(PubMedSearch.BASE_URL, params=params)
        data = response.json()
        papers = []
        for paper_id in data.get("esearchresult", {}).get("idlist", []):
            try:
                papers.append(
                    {
                        "paper_id": paper_id,
                        "title": f"Title for {paper_id}",  # Placeholder
                        "authors": [],  # Placeholder
                        "abstract": f"Abstract for {paper_id}",  # Placeholder
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{paper_id}/",
                        "pdf_url": "",  # PubMed does not provide direct PDF links
                        "published_date": "",  # Placeholder
                        "updated_date": "",  # Placeholder
                        "source": "pubmed",
                        "categories": [],
                        "keywords": [],
                        "doi": "",
                    }
                )
            except Exception as e:
                print(f"Error parsing PubMed entry: {e}")
        return papers
