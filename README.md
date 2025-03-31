# Privacy-Focused Search Terminal Tool

A versatile command-line search tool that allows you to search the web through privacy-focused search proxies and engines. This modular tool supports multiple search providers and engines, with options for automatic fallback and private browsing.

## Features

- **Multiple Search Providers**: Search through Mullvad, Excite, PrivacyWall, and more
- **Modular Design**: Easy to add new search providers
- **Aggressive Search Mode**: Automatically try alternative providers if one fails
- **Interactive Interface**: User-friendly terminal UI with color coding
- **Provider-Specific Engines**: Each provider can offer multiple search engines
- **Command-Line Options**: Use directly from the command line or in interactive mode
- **Configuration Memory**: Remembers your preferences between sessions
- **Browser Integration**: Open search results directly in your browser

## Installation

### Prerequisites

- Python 3.6 or higher
- Required Python packages: `requests`, `beautifulsoup4`

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yusufgurdogan/search_terminal.git
   cd search_terminal
   ```

2. Install required packages:
   ```bash
   pip install requests beautifulsoup4
   ```

3. Make the script executable:
   ```bash
   chmod +x search_terminal.py
   ```

4. Run the tool:
   ```bash
   ./search_terminal.py
   ```

## Usage

### Interactive Mode

Run without arguments to enter interactive mode:
```bash
python search_terminal.py
```

In interactive mode you can:
- Change search providers
- Change search engines
- Toggle aggressive search mode
- Perform searches
- View search results

### Command-Line Usage

Search directly from the command line:
```bash
python search_terminal.py -q "your search query"
```

Specify a different provider:
```bash
python search_terminal.py -q "your search query" -p privacywall
```

Use a specific engine:
```bash
python search_terminal.py -q "your search query" -p mullvad -e brave
```

Enable aggressive mode (try multiple providers):
```bash
python search_terminal.py -q "your search query" -a
```

Open the first result in your browser:
```bash
python search_terminal.py -q "your search query" -o
```

List all available providers:
```bash
python search_terminal.py -l
```

## Supported Providers

- **Mullvad**: Privacy-focused VPN provider's search proxy
  - Engines: `google`, `brave`
- **Excite**: Web search engine
  - Engines: `web`
- **PrivacyWall**: Privacy-focused search engine
  - Engines: `web`

## Adding New Providers

To add a new search provider:

1. Create a new Python file in the `providers` directory (e.g., `providers/new_provider.py`)
2. Implement the following functions:
   - `get_available_engines()`: Returns a list of available search engines
   - `search(query, engine, ...)`: Performs the search and returns results

Each provider must return results in the following format:
```python
[
    {
        "title": "Result Title",
        "link": "https://result.url",
        "snippet": "Result description or snippet"
    },
    # More results...
]
```

## Aggressive Search Mode

When enabled, aggressive search mode will:
1. Try the default/selected provider first
2. If that fails, try other available providers
3. Make up to 3 attempts per provider
4. Return the first successful results

This is useful for ensuring you always get search results, even if some providers are temporarily unavailable.

## Configuration

The tool saves your configuration in `~/.config/search_terminal/config.json`, including:
- Last used provider
- Last used search engine
- Aggressive mode setting

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Privacy Considerations

This tool interfaces with various search providers that may have different privacy practices. While the providers used generally focus on privacy, please review their privacy policies for complete information.