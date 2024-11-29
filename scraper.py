import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
import time

# Base URL
base_url = "https://www.healthdirect.gov.au"
sitemap_url = "https://www.healthdirect.gov.au/sitemap-content.xml"

# Lists to hold results
results = []

# Function to fetch IDs from a single page
def fetch_h2_ids(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # Use 'lxml' for HTML parsing
        soup = BeautifulSoup(response.content, 'lxml')

        # Find all <h2> tags that have an 'id' attribute
        h2_tags_with_id = soup.find_all('h2', id=True)
        # Extract the 'id' values
        ids = [tag['id'] for tag in h2_tags_with_id]

        return ids
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

# Function to parse the sitemap and extract URLs
def parse_sitemap(sitemap_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()
        # Use 'lxml-xml' for XML parsing
        soup = BeautifulSoup(response.content, 'lxml-xml')

        # Extract all <loc> tags
        urls = [loc.text for loc in soup.find_all('loc')]
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

# Main script execution
def main():
    # Parse the sitemap to get all URLs
    all_urls = parse_sitemap(sitemap_url)

    # Filter URLs to include only those in the first directory level
    filtered_urls = []
    for url in all_urls:
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.strip('/').split('/')
        if len(path_parts) == 1 and path_parts[0]:
            filtered_urls.append(url)

    print(f"Total URLs in first directory level: {len(filtered_urls)}")

    # Extract H2 IDs from each URL
    for idx, url in enumerate(filtered_urls[:1705], 1):
        print(f"Processing ({idx}/{len(filtered_urls[:5])}): {url}")
        ids = fetch_h2_ids(url)
        results.append({'URL': url, 'IDs': ids})
        time.sleep(1)  # Polite delay between requests

    # Save results to a CSV file
    df = pd.DataFrame(results)
    # Check if DataFrame is not empty and contains the 'IDs' column
    if not df.empty and 'IDs' in df.columns:
        # Convert the list of IDs to a comma-separated string
        df['IDs'] = df['IDs'].apply(lambda ids: ', '.join(ids))
        df.to_csv('h2_ids.csv', index=False)
        print("Scraping complete. Results saved to h2_ids.csv.")
    else:
        print("No data to save. DataFrame is empty.")

if __name__ == "__main__":
    main()
