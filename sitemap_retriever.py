#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sitemap Retriever

This script retrieves and parses XML sitemaps from a given URL. It searches for sitemaps
in common locations, parses robots.txt files, and attempts to find sitemap references
in the website's HTML.

Usage:
    python sitemap_retriever.py [-h] [-t THRESHOLD] url

Arguments:
    url         The base URL of the website to check for sitemaps
    -t, --threshold THRESHOLD
                Maximum number of URLs to display per sitemap (default: 50)
    -h, --help  Show this help message and exit
"""

import requests
import time
import argparse
import logging
from typing import List, Dict, Union
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET
import gzip

SITEMAP_INDICATORS = [
    "sitemap.xml",
    "sitemap_index.xml",
    "sitemap-index.xml",
    "sitemap_index.xml.gz",
    "sitemap.xml.gz",
    "robots.txt",
]


def get_sitemaps_from_url(
    base_url: str, threshold: int
) -> List[Dict[str, Union[str, Dict[str, List[str]]]]]:
    headers = {
        "User-Agent": "SitemapRetriever/1.0 (+https://github.com/yourusername/sitemap-retriever)"
    }

    session = requests.Session()
    all_results = []

    for spath in SITEMAP_INDICATORS:
        full_path = urljoin(base_url, spath)
        logging.info(f"Checking {full_path}")
        try:
            response = session.get(
                full_path, headers=headers, allow_redirects=True, timeout=10
            )
            logging.info(f"Got response {response.status_code}")

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
                alt_scheme = "https" if urlparse(base_url).scheme == "http" else "http"
                alt_base_url = f"{alt_scheme}://{urlparse(base_url).netloc}"
                alt_full_path = urljoin(alt_base_url, spath)
                logging.info(f"Trying alternative protocol: {alt_full_path}")
                alt_response = session.get(
                    alt_full_path, headers=headers, allow_redirects=True, timeout=10
                )
                if alt_response.status_code == 200:
                    result = get_sitemap_content(alt_full_path, session, headers)
                    if result:
                        all_results.append({"url": alt_full_path, "content": result})
        except requests.RequestException as e:
            logging.error(f"Error requesting {full_path}: {str(e)}")

        time.sleep(0.3)  # 0.3 second delay between requests

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
            logging.error(f"Error requesting homepage: {str(e)}")

    return all_results


def get_sitemap_content(
    url: str, session: requests.Session, headers: Dict[str, str]
) -> Union[Dict[str, Union[str, List[str]]], None]:
    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = response.content
            if (
                url.endswith(".gz")
                or response.headers.get("Content-Type") == "application/x-gzip"
            ):
                content = gzip.decompress(content)

            root = ET.fromstring(content)

            if root.tag.endswith("sitemapindex"):
                sitemaps = [
                    sitemap.text
                    for sitemap in root.findall(
                        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                    )
                ]
                return {"type": "index", "sitemaps": sitemaps}
            else:
                urls = [
                    url.text
                    for url in root.findall(
                        ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
                    )
                ]
                return {"type": "sitemap", "urls": urls}
    except Exception as e:
        logging.error(f"Error processing sitemap at {url}: {str(e)}")

    return None


def parse_robots_txt(robots_txt_content: str) -> List[str]:
    return [
        line.split(": ")[1].strip()
        for line in robots_txt_content.split("\n")
        if line.lower().startswith("sitemap:")
    ]


def find_sitemaps_in_html(html_content: str, base_url: str) -> List[str]:
    sitemap_urls = []
    for line in html_content.split("\n"):
        for indicator in SITEMAP_INDICATORS:
            if indicator in line:
                start = line.find("http")
                if start != -1:
                    end = line.find('"', start)
                    if end != -1:
                        sitemap_urls.append(line[start:end])
                else:
                    start = line.find(indicator)
                    if start != -1:
                        end = line.find('"', start)
                        if end != -1:
                            sitemap_urls.append(urljoin(base_url, line[start:end]))
    return sitemap_urls


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Retrieve and parse XML sitemaps from a given URL."
    )
    parser.add_argument("url", help="The base URL of the website to check for sitemaps")
    parser.add_argument(
        "-t",
        "--threshold",
        type=int,
        default=50,
        help="Maximum number of URLs to display per sitemap",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    base_url = args.url
    threshold = args.threshold

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    results = get_sitemaps_from_url(base_url, threshold)

    if results:
        print(f"\nFound {len(results)} sitemap(s):")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Sitemap URL: {result['url']}")
            content = result["content"]
            if content["type"] == "index":
                print(f"   Sitemap index with {len(content['sitemaps'])} sitemaps:")
                for sitemap in content["sitemaps"][:threshold]:
                    print(f"   - {sitemap}")
                if len(content["sitemaps"]) > threshold:
                    print(
                        f"   ... and {len(content['sitemaps']) - threshold} more sitemaps"
                    )
            else:
                print(f"   Sitemap with {len(content['urls'])} URLs:")
                for url in content["urls"][:threshold]:
                    print(f"   - {url}")
                if len(content["urls"]) > threshold:
                    print(f"   ... and {len(content['urls']) - threshold} more URLs")
    else:
        print("No sitemaps found")


if __name__ == "__main__":
    main()
