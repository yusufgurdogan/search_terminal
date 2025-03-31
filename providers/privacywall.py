#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def get_available_engines():
    """
    Return list of available search engines for this provider
    """
    return ["web"]  # PrivacyWall only has web search as the main option

def search(query, engine="web", country="", language=""):
    """
    Perform a search query via PrivacyWall search
    
    Args:
        query (str): The search query
        engine (str): Search engine to use (only "web" is supported)
        country (str): Country code (optional)
        language (str): Language code (not used)
    
    Returns:
        list: List of search result dictionaries
    """
    # Validate engine
    if engine not in get_available_engines():
        raise ValueError(f"Engine '{engine}' not supported by PrivacyWall. Use one of: {', '.join(get_available_engines())}")
    
    # Use country code if provided, otherwise default to empty
    country_code = country if country else "US"
    
    # Base URL for PrivacyWall search
    url = "https://www.privacywall.org/search/secure"
    
    # Parameters for the search query
    params = {
        "q": query,
        "cc": country_code
    }
    
    # Set headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.privacywall.org/"
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
        html_content (str): The HTML content from PrivacyWall
        
    Returns:
        list: List of dictionaries containing search results
    """
    results = []
    
    try:
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all result cards
        result_cards = soup.select("div.result-card")
        
        for card in result_cards:
            # Extract title element
            title_elem = card.select_one("div.result_title")
            
            # Extract description element
            description_elem = card.select_one("div.result-description")
            
            # Extract URL element
            url_elem = card.select_one("div.result-url")
            
            # Extract the link element which contains the href attribute
            link_elem = card.select_one("a[href]")
            
            if title_elem and link_elem:
                # Clean text by removing HTML tags
                title = title_elem.get_text(strip=True).replace("<b>", "").replace("</b>", "")
                link = link_elem.get("href")
                
                # Get description if available, otherwise use a default message
                description = ""
                if description_elem:
                    description = description_elem.get_text(strip=True).replace("<b>", "").replace("</b>", "")
                
                # Create result object
                result = {
                    "title": title,
                    "link": link,
                    "snippet": description
                }
                
                results.append(result)
    
    except Exception as e:
        raise ValueError(f"Error parsing search results: {e}")
    
    return results

# Example usage when run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
        country = sys.argv[2] if len(sys.argv) > 2 else ""
        
        print(f"Searching for '{query}' using PrivacyWall...")
        results = search(query, country=country)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['link']}")
            print(f"   {result['snippet']}")
            print()