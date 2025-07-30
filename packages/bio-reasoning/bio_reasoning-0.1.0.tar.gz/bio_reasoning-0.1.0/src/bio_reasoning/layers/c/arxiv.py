from typing import List
from datetime import datetime
import requests
import feedparser


class ArxivSearch:
    """Factory function for arXiv paper search functionality."""

    BASE_URL = "http://export.arxiv.org/api/query"

    @staticmethod
    def search(query: str, max_results: int = 10) -> List[dict]:
        """Search for papers on arXiv.

        Args:
            query (str): Search query string.
            max_results (int): Maximum number of results to return.

        Returns:
            List[dict]: List of paper metadata dictionaries.
        """
        params = {
            "search_query": query,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        response = requests.get(ArxivSearch.BASE_URL, params=params)
        feed = feedparser.parse(response.content)
        papers = []
        for entry in feed.entries:
            try:
                authors = [author.name for author in entry.authors]
                published = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                updated = datetime.strptime(entry.updated, "%Y-%m-%dT%H:%M:%SZ")
                pdf_url = next(
                    (
                        link.href
                        for link in entry.links
                        if link.type == "application/pdf"
                    ),
                    "",
                )
                papers.append(
                    {
                        "paper_id": entry.id.split("/")[-1],
                        "title": entry.title,
                        "authors": authors,
                        "abstract": entry.summary,
                        "url": entry.id,
                        "pdf_url": pdf_url,
                        "published_date": published.isoformat(),
                        "updated_date": updated.isoformat(),
                        "source": "arxiv",
                        "categories": [tag.term for tag in entry.tags],
                        "keywords": [],
                        "doi": entry.get("doi", ""),
                    }
                )
            except Exception as e:
                print(f"Error parsing arXiv entry: {e}")
        return papers
