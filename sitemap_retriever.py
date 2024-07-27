#!/usr/bin/env python3

import sys
import requests
import time
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
import gzip
import io

SITEMAP_INDICATORS = [
    "sitemap.xml",
    "sitemap_index.xml",
    "sitemap-index.xml",
    "sitemap_index.xml.gz",
    "sitemap.xml.gz",
    "robots.txt",
]
THRESHOLD = 50


def get_sitemaps_from_url(base_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    session = requests.Session()
    all_results = []

    for spath in SITEMAP_INDICATORS:
        full_path = urljoin(base_url, spath)
        print(f"Checking {full_path}")
        try:
            response = session.get(
                full_path, headers=headers, allow_redirects=True, timeout=10
            )
            print(f"Got response {response.status_code}")

            if response.status_code == 200:
                if spath == "robots.txt":
                    sitemap_urls = parse_robots_txt(response.text)
                    for sitemap_url in sitemap_urls:
                        result = get_sitemap_content(sitemap_url, session, headers)
                        if result:
                            all_results.append({"url": sitemap_url, "content": result})
                else:
                    result = get_sitemap_content(full_path, session, headers)
                    if result:
                        all_results.append({"url": full_path, "content": result})
            elif response.status_code == 403:
                # Try alternative protocol (http/https)
                alt_scheme = "https" if urlparse(base_url).scheme == "http" else "http"
                alt_base_url = f"{alt_scheme}://{urlparse(base_url).netloc}"
                alt_full_path = urljoin(alt_base_url, spath)
                print(f"Trying alternative protocol: {alt_full_path}")
                alt_response = session.get(
                    alt_full_path, headers=headers, allow_redirects=True, timeout=10
                )
                if alt_response.status_code == 200:
                    result = get_sitemap_content(alt_full_path, session, headers)
                    if result:
                        all_results.append({"url": alt_full_path, "content": result})
        except requests.RequestException as e:
            print(f"Error requesting {full_path}: {str(e)}")

        time.sleep(0.3)  # 1 second delay between requests

    # If no sitemap found, try scraping the homepage
    if not all_results:
        try:
            homepage_response = session.get(
                base_url, headers=headers, allow_redirects=True, timeout=10
            )
            if homepage_response.status_code == 200:
                sitemap_urls = find_sitemaps_in_html(homepage_response.text, base_url)
                for sitemap_url in sitemap_urls:
                    result = get_sitemap_content(sitemap_url, session, headers)
                    if result:
                        all_results.append({"url": sitemap_url, "content": result})
        except requests.RequestException as e:
            print(f"Error requesting homepage: {str(e)}")

    return all_results


def get_sitemap_content(url, session, headers):
    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.content
            if (
                url.endswith(".gz")
                or response.headers.get("Content-Type") == "application/x-gzip"
            ):
                content = gzip.decompress(content)

            # Try parsing as XML
            try:
                root = ET.fromstring(content)
            except ET.ParseError:
                # If XML parsing fails, try decoding as UTF-8 and remove any invalid characters
                content = content.decode("utf-8", "ignore").encode("utf-8")
                root = ET.fromstring(content)

            # Check if it's a sitemap index
            if root.tag.endswith("sitemapindex"):
                sitemaps = []
                for sitemap in root.findall(
                    ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                ):
                    sitemaps.append(sitemap.text)
                return {"type": "index", "sitemaps": sitemaps}
            else:
                urls = []
                for url in root.findall(
                    ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                ):
                    urls.append(url.text)
                return {"type": "sitemap", "urls": urls}
    except Exception as e:
        print(f"Error processing sitemap at {url}: {str(e)}")

    return None


def parse_robots_txt(robots_txt_content):
    sitemap_urls = []
    for line in robots_txt_content.split("\n"):
        if line.lower().startswith("sitemap:"):
            sitemap_urls.append(line.split(": ")[1].strip())
    return sitemap_urls


def find_sitemaps_in_html(html_content, base_url):
    sitemap_urls = []

    for line in html_content.split("\n"):
        for indicator in SITEMAP_INDICATORS:
            if indicator in line:
                # Extract URL - this is a simplified approach
                start = line.find("http")
                if start != -1:
                    end = line.find('"', start)
                    if end != -1:
                        sitemap_urls.append(line[start:end])
                else:
                    # Handle relative URLs
                    start = line.find(indicator)
                    if start != -1:
                        end = line.find('"', start)
                        if end != -1:
                            sitemap_urls.append(urljoin(base_url, line[start:end]))
    return sitemap_urls


def main():
    if len(sys.argv) != 2:
        print("Usage: python sitemap_retriever.py <base_url>")
        print("Example: python sitemap_retriever.py https://example.com")
        sys.exit(1)

    base_url = sys.argv[1]
    results = get_sitemaps_from_url(base_url)

    if results:
        print(f"\nFound {len(results)} sitemap(s):")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Sitemap URL: {result['url']}")
            content = result["content"]
            if content["type"] == "index":
                print(f"   Sitemap index with {len(content['sitemaps'])} sitemaps:")
                for sitemap in content["sitemaps"][:THRESHOLD]:
                    print(f"   - {sitemap}")
                if len(content["sitemaps"]) > THRESHOLD:
                    print(
                        f"   ... and {len(content['sitemaps']) - THRESHOLD} more sitemaps"
                    )
            else:
                print(f"   Sitemap with {len(content['urls'])} URLs:")
                for url in content["urls"][:THRESHOLD]:
                    print(f"   - {url}")
                if len(content["urls"]) > THRESHOLD:
                    print(f"   ... and {len(content['urls']) - THRESHOLD} more URLs")
    else:
        print("No sitemaps found")


if __name__ == "__main__":
    main()
