#!/usr/bin/env python3
import argparse
import os
import json
import sys
import importlib.util
from urllib.parse import quote_plus

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_provider(provider_name):
    """
    Dynamically load a provider module
    """
    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        provider_path = os.path.join(current_dir, "providers", f"{provider_name}.py")
        
        if not os.path.exists(provider_path):
            print(f"{Colors.RED}Provider {provider_name} not found at {provider_path}{Colors.ENDC}")
            return None
            
        spec = importlib.util.spec_from_file_location(provider_name, provider_path)
        if not spec:
            print(f"{Colors.RED}Failed to load spec for {provider_name}{Colors.ENDC}")
            return None
            
        provider = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(provider)
        return provider
    except Exception as e:
        print(f"{Colors.RED}Error loading provider {provider_name}: {e}{Colors.ENDC}")
        return None

def get_available_providers():
    """
    Get list of available provider modules
    """
    providers = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    providers_dir = os.path.join(current_dir, "providers")
    
    # Create providers directory if it doesn't exist
    if not os.path.exists(providers_dir):
        os.makedirs(providers_dir)
        return providers
    
    for file in os.listdir(providers_dir):
        if file.endswith(".py") and not file.startswith("__"):
            providers.append(file[:-3])  # Remove .py extension
    
    return providers

def save_config(config):
    """Save configuration to a config file"""
    config_dir = os.path.expanduser("~/.config/search-tool")
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, "config.json")
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not save config: {e}{Colors.ENDC}")

def load_config():
    """Load configuration from the config file"""
    config_file = os.path.expanduser("~/.config/search-tool/config.json")
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"{Colors.YELLOW}Warning: Could not load config: {e}{Colors.ENDC}")
    
    # Default config
    return {
        "provider": "mullvad",
        "engine": "google"
    }

def display_results(results):
    """
    Display search results in a nice format
    """
    if not results:
        print(f"{Colors.YELLOW}No results found or couldn't parse the response.{Colors.ENDC}")
        return
    
    for i, result in enumerate(results, 1):
        print(f"{Colors.BOLD}{i}. {result['title']}{Colors.ENDC}")
        print(f"{Colors.GREEN}{result['link']}{Colors.ENDC}")
        print(f"{result.get('snippet', 'No description available')}")
        print()

def get_default_engine(provider):
    """
    Get the default search engine for a provider
    """
    if not provider:
        return None
    
    try:
        engines = provider.get_available_engines()
        if engines and len(engines) > 0:
            return engines[0]
    except Exception:
        pass
    
    return None

def interactive_search(config, providers):
    """
    Run an interactive search session
    """
    provider_name = config.get("provider", "mullvad")
    engine = config.get("engine", "google")
    
    if provider_name not in providers:
        print(f"{Colors.RED}Provider '{provider_name}' not available. Using first available provider.{Colors.ENDC}")
        if providers:
            provider_name = providers[0]
        else:
            print(f"{Colors.RED}No providers available. Exiting.{Colors.ENDC}")
            return
    
    provider = load_provider(provider_name)
    if not provider:
        print(f"{Colors.RED}Failed to load provider '{provider_name}'. Exiting.{Colors.ENDC}")
        return
    
    # Ensure the engine is valid for this provider
    available_engines = provider.get_available_engines()
    if engine not in available_engines:
        engine = get_default_engine(provider)
        config["engine"] = engine
        save_config(config)
        print(f"{Colors.YELLOW}Selected engine is not available for this provider. Using default: {engine}{Colors.ENDC}")
    
    clear_screen()
    print(f"{Colors.HEADER}╭───────────────────────────────────╮{Colors.ENDC}")
    print(f"{Colors.HEADER}│        Search Terminal Tool       │{Colors.ENDC}")
    print(f"{Colors.HEADER}╰───────────────────────────────────╯{Colors.ENDC}")
    
    while True:
        try:
            print(f"\n{Colors.BLUE}Current provider: {Colors.BOLD}{provider_name.upper()}{Colors.ENDC}")
            print(f"{Colors.BLUE}Current search engine: {Colors.BOLD}{engine.upper()}{Colors.ENDC}")
            
            print("\n╭─ Options ─────────────────────────╮")
            print("│ 1. Change provider                 │")
            print("│ 2. Change search engine            │")
            print("│ 3. Perform a search                │")
            print("│ 4. Exit                            │")
            print("╰────────────────────────────────────╯")
            
            choice = input(f"{Colors.BOLD}Select an option (1-4): {Colors.ENDC}")
            
            if choice == "1":
                if not providers:
                    print(f"{Colors.RED}No providers available.{Colors.ENDC}")
                    continue
                
                print("\n╭─ Available providers ─────────────╮")
                for i, p in enumerate(providers, 1):
                    print(f"│ {i}. {p.capitalize()}") 
                print("╰────────────────────────────────────╯")
                
                provider_choice = input(f"{Colors.BOLD}Select provider (1-{len(providers)}): {Colors.ENDC}")
                try:
                    idx = int(provider_choice) - 1
                    if 0 <= idx < len(providers):
                        provider_name = providers[idx]
                        provider = load_provider(provider_name)
                        if provider:
                            config["provider"] = provider_name
                            
                            # Set default engine for the new provider
                            default_engine = get_default_engine(provider)
                            if default_engine:
                                engine = default_engine
                                config["engine"] = engine
                                print(f"{Colors.BLUE}Provider changed to: {Colors.BOLD}{provider_name.upper()}{Colors.ENDC}")
                                print(f"{Colors.BLUE}Default engine set to: {Colors.BOLD}{engine.upper()}{Colors.ENDC}")
                            
                            save_config(config)
                        else:
                            print(f"{Colors.RED}Failed to load provider.{Colors.ENDC}")
                    else:
                        print(f"{Colors.RED}Invalid choice.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}Invalid input.{Colors.ENDC}")
                
            elif choice == "2":
                available_engines = provider.get_available_engines() if provider else []
                
                if not available_engines:
                    print(f"{Colors.RED}No engines available for this provider.{Colors.ENDC}")
                    continue
                
                print("\n╭─ Available engines ─────────────────╮")
                for i, e in enumerate(available_engines, 1):
                    print(f"│ {i}. {e.capitalize()}") 
                print("╰────────────────────────────────────╯")
                
                engine_choice = input(f"{Colors.BOLD}Select engine (1-{len(available_engines)}): {Colors.ENDC}")
                try:
                    idx = int(engine_choice) - 1
                    if 0 <= idx < len(available_engines):
                        engine = available_engines[idx]
                        config["engine"] = engine
                        save_config(config)
                        print(f"{Colors.BLUE}Engine changed to: {Colors.BOLD}{engine.upper()}{Colors.ENDC}")
                    else:
                        print(f"{Colors.RED}Invalid choice.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}Invalid input.{Colors.ENDC}")
                
            elif choice == "3":
                query = input(f"{Colors.BOLD}Enter search query: {Colors.ENDC}")
                if query.strip():
                    print(f"{Colors.YELLOW}Searching for '{query}' via {provider_name.capitalize()} ({engine})...{Colors.ENDC}")
                    
                    try:
                        results = provider.search(query, engine)
                        display_results(results)
                    except Exception as e:
                        print(f"{Colors.RED}Error performing search: {e}{Colors.ENDC}")
                    
                    input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")
                    clear_screen()
                    print(f"{Colors.HEADER}╭───────────────────────────────────╮{Colors.ENDC}")
                    print(f"{Colors.HEADER}│        Search Terminal Tool       │{Colors.ENDC}")
                    print(f"{Colors.HEADER}╰───────────────────────────────────╯{Colors.ENDC}")
                
            elif choice == "4":
                print(f"{Colors.BLUE}Goodbye!{Colors.ENDC}")
                break
                
            else:
                print(f"{Colors.RED}Invalid option, please try again.{Colors.ENDC}")
                
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}Exiting...{Colors.ENDC}")
            break
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.ENDC}")

def main():
    # Ensure providers directory exists
    current_dir = os.path.dirname(os.path.abspath(__file__))
    providers_dir = os.path.join(current_dir, "providers")
    os.makedirs(providers_dir, exist_ok=True)
    
    # Load available providers
    providers = get_available_providers()
    
    if not providers:
        print(f"{Colors.YELLOW}No search providers found. Please add provider modules to the 'providers' directory.{Colors.ENDC}")
        sys.exit(1)
    
    # Load configuration
    config = load_config()
    
    parser = argparse.ArgumentParser(description="Search Terminal Tool")
    parser.add_argument("-q", "--query", help="Search query")
    parser.add_argument("-p", "--provider", default=config.get("provider", "mullvad"), 
                        help="Search provider to use")
    parser.add_argument("-e", "--engine", default=config.get("engine", "google"), 
                        help="Search engine to use")
    parser.add_argument("-o", "--open", action="store_true", help="Open the first result in browser")
    parser.add_argument("-l", "--list", action="store_true", help="List available providers")
    
    args = parser.parse_args()
    
    if args.list:
        print(f"{Colors.HEADER}Available providers:{Colors.ENDC}")
        for p in providers:
            provider = load_provider(p)
            if provider:
                engines = provider.get_available_engines()
                print(f"{Colors.BOLD}{p.capitalize()}{Colors.ENDC}: {', '.join(engines)}")
        return
    
    if args.provider and args.provider not in providers:
        print(f"{Colors.RED}Provider '{args.provider}' not found. Available providers: {', '.join(providers)}{Colors.ENDC}")
        return
    
    provider_name = args.provider
    provider = load_provider(provider_name)
    
    if not provider:
        print(f"{Colors.RED}Failed to load provider '{provider_name}'.{Colors.ENDC}")
        return
    
    # Ensure the engine is valid for this provider
    engine = args.engine
    available_engines = provider.get_available_engines()
    if engine not in available_engines:
        engine = get_default_engine(provider)
        if args.engine != config.get("engine"):
            print(f"{Colors.YELLOW}Specified engine '{args.engine}' is not available for this provider. Using default: {engine}{Colors.ENDC}")
    
    if args.query:
        # Non-interactive mode
        print(f"{Colors.YELLOW}Searching for '{args.query}' via {provider_name.capitalize()} ({engine})...{Colors.ENDC}")
        
        try:
            results = provider.search(args.query, engine)
            display_results(results)
            
            if args.open and results and len(results) > 0:
                import webbrowser
                link = results[0]["link"]
                print(f"{Colors.YELLOW}Opening first result: {link}{Colors.ENDC}")
                webbrowser.open(link)
        except Exception as e:
            print(f"{Colors.RED}Error performing search: {e}{Colors.ENDC}")
    else:
        # Interactive mode
        interactive_search(config, providers)

if __name__ == "__main__":
    main()