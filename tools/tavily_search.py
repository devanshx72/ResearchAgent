"""
Tavily Search API wrapper for web research.
"""

import os
from typing import List, Dict
from tavily import TavilyClient


class TavilySearch:
    """Wrapper for Tavily Search API."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize Tavily client.
        
        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
        
        self.client = TavilyClient(api_key=self.api_key)
    
    def search_query(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search for a query using Tavily API.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search result dictionaries with title, snippet, url, score
        """
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("content", "")[:500],  # Limit snippet length
                    "url": result.get("url", ""),
                    "score": result.get("score", 0.0)
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching Tavily: {e}")
            return []
    
    def search_multiple(self, queries: List[str], max_results: int = 5) -> Dict[str, List[Dict]]:
        """
        Search multiple queries in parallel.
        
        Args:
            queries: List of search query strings
            max_results: Maximum results per query
            
        Returns:
            Dictionary mapping query -> list of results
        """
        results = {}
        for query in queries:
            results[query] = self.search_query(query, max_results)
        return results
