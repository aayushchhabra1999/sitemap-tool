# Sitemap Retriever

Sitemap Retriever is a Python script that helps you find and parse XML sitemaps for any given website. It searches for sitemaps in common locations, parses robots.txt files, and even attempts to find sitemap references in the website's HTML.

## Features

- Checks multiple common sitemap locations
- Parses robots.txt for sitemap URLs
- Handles both sitemap indices and regular sitemaps
- Supports gzipped sitemaps
- Attempts to use alternative protocols (http/https) if initial requests fail
- Scrapes the homepage for sitemap references as a last resort
- Configurable output threshold for large sitemaps

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sitemap-retriever.git
   cd sitemap-retriever
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script from the command line, providing the base URL of the website you want to check:

```
python sitemap_retriever.py [-h] [-t THRESHOLD] url
```

Arguments:
- `url`: The base URL of the website to check for sitemaps
- `-t, --threshold THRESHOLD`: Maximum number of URLs to display per sitemap (default: 50)
- `-h, --help`: Show the help message and exit

Example:
```
python sitemap_retriever.py https://example.com -t 100
```

The script will output the found sitemaps and their contents (up to the specified threshold per sitemap).

## Configuration

You can modify the `SITEMAP_INDICATORS` list in the script to adjust which sitemap filenames are checked.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.