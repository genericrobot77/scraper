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

# Function to fetch content from <h1>, <h2> tags and their child elements
def fetch_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # Use 'lxml' for HTML parsing
        soup = BeautifulSoup(response.content, 'lxml')

        # Find the <h1> tag for the page title
        h1_tag = soup.find('h1')
        page_name = h1_tag.get_text(strip=True) if h1_tag else ""

        # Find all <h2> tags that have an 'id' attribute
        h2_tags_with_id = soup.find_all('h2', id=True)
        
        content_list = []

        for tag in h2_tags_with_id:
            h2_id = tag['id']
            h2_text = tag.get_text(strip=True)
            
            # Extract content from child <p> and <ul> tags under the respective <h2> tag
            combined_content = []
            next_tag = tag.find_next_sibling()
            while next_tag and next_tag.name in ['p', 'ul']:
                if next_tag.name == 'p':
                    combined_content.append(next_tag.get_text(strip=True))
                elif next_tag.name == 'ul':
                    list_items = [li.get_text(strip=True) for li in next_tag.find_all('li')]
                    combined_content.extend(list_items)
                next_tag = next_tag.find_next_sibling()
            
            content_list.append({
                'ID': h2_id,
                'H2_Text': h2_text,
                'Content': ' | '.join(combined_content)
            })
        
        return page_name, content_list
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return "", []

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
    # Option to use a specific URL for testing
    test_urls = [
        "https://www.healthdirect.gov.au/abdominal-pain"
    ]

    if test_urls:
        filtered_urls = test_urls
    else:
        # Parse the sitemap to get all URLs
        all_urls = parse_sitemap(sitemap_url)

        # Filter URLs to include only those in the first directory level
        filtered_urls = []
        for url in all_urls:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip('/').split('/')
            if len(path_parts) == 1 and path_parts[0]:
                filtered_urls.append(url)

    print(f"Total URLs to process: {len(filtered_urls)}")

    # Extract content from the filtered URLs
    for idx, url in enumerate(filtered_urls[:5], 1):
        print(f"Processing ({idx}/{len(filtered_urls)}): {url}")
        page_name, content = fetch_content(url)
        results.append({'URL': url, 'H1': page_name, 'Content': content})
        time.sleep(1)  # Polite delay between requests

    # Save results to a CSV file
    rows = []
    for result in results:
        url = result['URL']
        page_name = result['H1']
        for content in result['Content']:
            rows.append({
                'URL': url,
                'H1': page_name,
                'H2_ID': content['ID'],
                'H2_Text': content['H2_Text'],
                'Content': content['Content']
            })

    df = pd.DataFrame(rows)
    # Check if DataFrame is not empty and contains the necessary columns
    if not df.empty:
        df.to_csv('h2_content.csv', index=False)
        print("Scraping complete. Results saved to h2_content.csv.")
    else:
        print("No data to save. DataFrame is empty.")

if __name__ == "__main__":
    main()
