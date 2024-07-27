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

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sitemap-retriever.git
   cd sitemap-retriever
   ```

2. (Optional but recommended) Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Make the script executable (on Unix-based systems):
   ```
   chmod +x sitemap_retriever.py
   ```

## Usage

Run the script from the command line, providing the base URL of the website you want to check:

```
python sitemap_retriever.py [-h] [-t THRESHOLD] url
```

or, if you made the script executable:

```
./sitemap_retriever.py [-h] [-t THRESHOLD] url
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

You can modify the `SITEMAP_INDICATORS` list in the script to adjust which sitemap filenames are checked. Open `sitemap_retriever.py` in a text editor and locate the following lines near the top of the file:

```python
SITEMAP_INDICATORS = [
    "sitemap.xml",
    "sitemap_index.xml",
    "sitemap-index.xml",
    "sitemap_index.xml.gz",
    "sitemap.xml.gz",
    "robots.txt",
]
```

Add or remove entries as needed for your use case.

## Troubleshooting

1. If you encounter a "Permission denied" error when trying to run the script, ensure you've made it executable:
   ```
   chmod +x sitemap_retriever.py
   ```

2. If you get a "ModuleNotFoundError", make sure you've activated your virtual environment and installed the requirements:
   ```
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. If the script isn't finding sitemaps for a website you know has them, try running with verbose logging:
   ```
   python -u sitemap_retriever.py https://example.com
   ```
   This will show more detailed information about the script's progress.

## Contributing

Contributions are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

Please make sure to update tests as appropriate and adhere to the existing coding style.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped to improve this project.
- Special thanks to the Python community for providing excellent libraries like `requests` that make projects like this possible.

## Contact

If you have any questions, feel free to open an issue or contact the maintainer directly.

Happy sitemap retrieving!