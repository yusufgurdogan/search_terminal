#!/usr/bin/env python3
import requests
import json
from urllib.parse import quote_plus
import uuid

def get_available_engines():
    """
    Return list of available search engines for this provider
    """
    return ["web"]  # Ekoru only has web search as the main option

def search(query, engine="web", country="", language=""):
    """
    Perform a search query via Ekoru search
    
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
        raise ValueError(f"Engine '{engine}' not supported by Ekoru. Use one of: {', '.join(get_available_engines())}")
    
    url = "https://hs.qacono.com/v2/campaigns"
    
    # Generate UUIDs for tracking
    page_load_uuid = str(uuid.uuid4())
    group_id = str(uuid.uuid4())
    
    # Prepare the request data
    form_data = {
        "publisherId": "E78C989916C6",
        "publisherURL": f"https://www.ekoru.org/?q={quote_plus(query)}",
        "pageLoadUUID": page_load_uuid,
        "groupId": group_id,
        "cdm": "aHR0cHM6Ly93d3cuZWtvcnUub3JnLw==",  # Base64 encoded "https://www.ekoru.org/"
        "demandType": "serpGateway",
        "page[current]": "1",
        "page[next]": "1",
        "page[nextRequestToken]": "",
        "qc[0]": "Search",
        "searchTerm": query,
        "sdkver": "2.81.1",
        "fri": group_id,
        "s": "-1",
        "feedsResults[adsMainline]": "6",
        "feedsResults[organic]": "8",
        "feedsResults[related]": "8",
        "adUnitId": "",
        "gatewayQueryString": f"q={quote_plus(query)}",
        "kwds[0]": query
    }
    
    # Set headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.ekoru.org",
        "Referer": "https://www.ekoru.org/",
    }
    
    try:
        response = requests.post(url, data=form_data, headers=headers)
        response.raise_for_status()
        return parse_search_results(response.json())
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Request error: {e}")
    except json.JSONDecodeError:
        raise ValueError("Error parsing JSON response")

def parse_search_results(json_response):
    """
    Parse the search results from the JSON response
    
    Args:
        json_response (dict): The JSON response from Ekoru
        
    Returns:
        list: List of dictionaries containing search results
    """
    results = []
    
    try:
        # Navigate to the organic results section
        if "pages" in json_response and "1" in json_response["pages"]:
            page_data = json_response["pages"]["1"]
            
            if "cbResults" in page_data and "organic" in page_data["cbResults"]:
                organic_results = page_data["cbResults"]["organic"]
                
                for result in organic_results:
                    title = result.get("title", "No title available")
                    # Remove HTML tags from title if present
                    title = title.replace("<b>", "").replace("</b>", "")
                    
                    link = result.get("url", "")
                    snippet = result.get("description", "No description available")
                    
                    # Remove HTML tags from snippet if present
                    snippet = snippet.replace("<b>", "").replace("</b>", "")
                    
                    results.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet
                    })
    except Exception as e:
        raise ValueError(f"Error parsing search results: {e}")
    
    return results

# Example usage when run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
        
        print(f"Searching for '{query}' using Ekoru...")
        results = search(query)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['link']}")
            print(f"   {result['snippet']}")
            print()