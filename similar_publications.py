import streamlit as st
from serpapi import GoogleSearch
from dotenv import load_dotenv
# Replace with your SERP API key

load_dotenv()
def search_serpapi(query, max_results=5):
    """
    Search for articles using SERP API.
    
    Args:
        query (str): The search query (e.g., article title or topic).
        max_results (int): Maximum number of results to return.
    
    Returns:
        list: A list of articles with title, snippet, and URL.
    """
    params = {
        "q": query,              # Search query
        "api_key": API_KEY,      # Your SERP API key
        "num": max_results,      # Number of results to return
        "hl": "en",              # Language (English)
        "gl": "us"               # Country (United States)
    }

    try:
        # Perform the search
        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract organic results
        articles = []
        for result in results.get("organic_results", [])[:max_results]:
            articles.append({
                "title": result.get("title", "No title"),
                "snippet": result.get("snippet", "No snippet available"),
                "url": result.get("link", "#")
            })
        
        return articles

    except Exception as e:
        st.error(f"Error fetching data from SERP API: {e}")
        return []