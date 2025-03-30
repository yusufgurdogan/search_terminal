#!/usr/bin/env python3
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def get_available_engines():
    """
    Return list of available search engines for this provider
    """
    return ["web"]  # Excite only has web search as the base option

def search(query, engine="web", country="", language=""):
    """
    Perform a search query via Excite search
    
    Args:
        query (str): The search query
        engine (str): Search engine to use (only "web" is supported)
        country (str): Country code (not used)
        language (str): Language code (not used)
    
    Returns:
        list: List of search result dictionaries
    """
    # Validate engine
    if engine not in get_available_engines():
        raise ValueError(f"Engine '{engine}' not supported by Excite. Use one of: {', '.join(get_available_engines())}")
    
    url = "https://results.excite.com/serp"
    
    # Prepare the request data
    params = {
        "q": query
    }
    
    # Set headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://results.excite.com/",
        "Origin": "https://results.excite.com",
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return parse_search_results(response.text)
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Request error: {e}")

def parse_search_results(html_content):
    """
    Parse the search results from the HTML response
    
    Args:
        html_content (str): The HTML content from Excite
        
    Returns:
        list: List of dictionaries containing search results
    """
    results = []
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all web result divs
        web_bing_results = soup.select("div.web-bing__result")
        
        for result in web_bing_results:
            title_elem = result.select_one("a.web-bing__title")
            description_elem = result.select_one("span.web-bing__description")
            url_elem = result.select_one("span.web-bing__url")
            
            if title_elem and url_elem:
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href')
                description = description_elem.get_text(strip=True) if description_elem else ""
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": description
                })
        
    except Exception as e:
        raise ValueError(f"Error parsing search results: {e}")
    
    return results

# Example usage when run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
        
        print(f"Searching for '{query}' using Excite...")
        results = search(query)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['link']}")
            print(f"   {result['snippet']}")
            print()