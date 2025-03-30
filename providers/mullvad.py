#!/usr/bin/env python3
import requests
import json
from urllib.parse import quote_plus

def get_available_engines():
    """
    Return list of available search engines for this provider
    """
    return ["google", "brave"]

def search(query, engine="google", country="", language=""):
    """
    Perform a search query via Mullvad search
    
    Args:
        query (str): The search query
        engine (str): Search engine to use (google or brave)
        country (str): Country code (optional)
        language (str): Language code (optional)
    
    Returns:
        list: List of search result dictionaries
    """
    # Validate engine
    if engine not in get_available_engines():
        raise ValueError(f"Engine '{engine}' not supported by Mullvad. Use one of: {', '.join(get_available_engines())}")
    
    url = "https://leta.mullvad.net/"
    
    # Prepare the request data
    request_url = f"{url}?q={quote_plus(query)}"
    form_data = {
        "q": query,
        "engine": engine,
        "country": country,
        "language": language,
        "lastUpdated": ""
    }
    
    # Set headers to mimic a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Referer": request_url,
        "Origin": "https://leta.mullvad.net",
    }
    
    try:
        response = requests.post(request_url, data=form_data, headers=headers)
        response.raise_for_status()
        result = response.json()
        return parse_search_results(result)
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Request error: {e}")
    except json.JSONDecodeError:
        raise ValueError("Error parsing JSON response")

def parse_search_results(json_response):
    """
    Parse the search results from the JSON response
    
    Args:
        json_response (dict): The JSON response from Mullvad
        
    Returns:
        list: List of dictionaries containing search results
    """
    try:
        if json_response and "data" in json_response:
            # Parse the data string into a JSON object
            data = json.loads(json_response["data"])
            
            # The data is a complex structure. Let's extract the keys from the first object
            if isinstance(data, list) and len(data) > 0:
                header = data[0]
                results = []
                
                # Check if the required keys exist
                if "items" in header and isinstance(header["items"], int):
                    items_index = header["items"]
                    if items_index < len(data) and isinstance(data[items_index], list):
                        item_indices = data[items_index]
                        
                        # Process each search result
                        for idx in item_indices:
                            if isinstance(idx, int) and idx < len(data):
                                item_struct = data[idx]
                                if isinstance(item_struct, dict) and "link" in item_struct and "title" in item_struct:
                                    link_index = item_struct.get("link")
                                    title_index = item_struct.get("title")
                                    snippet_index = item_struct.get("snippet")
                                    
                                    # Now extract the actual values from their respective indices
                                    if isinstance(link_index, int) and link_index < len(data):
                                        link = data[link_index]
                                    else:
                                        link = "No link available"
                                    
                                    if isinstance(title_index, int) and title_index < len(data):
                                        title = data[title_index]
                                    else:
                                        title = "No title available"
                                    
                                    if isinstance(snippet_index, int) and snippet_index < len(data):
                                        snippet = data[snippet_index]
                                    else:
                                        snippet = "No description available"
                                    
                                    results.append({
                                        "title": title,
                                        "link": link,
                                        "snippet": snippet
                                    })
                
                return results
    except Exception as e:
        raise ValueError(f"Error parsing search results: {e}")
    
    return []

# Example usage when run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = sys.argv[1]
        engine = sys.argv[2] if len(sys.argv) > 2 else "google"
        
        print(f"Searching for '{query}' using {engine}...")
        results = search(query, engine)
        
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['link']}")
            print(f"   {result['snippet']}")
            print()