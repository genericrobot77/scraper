import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL
base_url = "https://www.healthdirect.gov.au"

# Lists to hold results
results = []

# Function to fetch IDs from a single page
def fetch_h2_ids(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # Use 'lxml' or 'html.parser' for HTML content
        soup = BeautifulSoup(response.content, 'lxml')

        # Find all <h2> tags that have an 'id' attribute
        h2_tags_with_id = soup.find_all('h2', id=True)
        # Extract the 'id' values
        ids = [tag['id'] for tag in h2_tags_with_id]

        return ids
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

# Main script execution
def main():
    # Define a list of test URLs
    test_urls = [
        "https://www.healthdirect.gov.au/fever",   # Example URL with known IDs
        "https://www.healthdirect.gov.au/cough",   # Another example
        # Add more URLs as needed
    ]

    print(f"Total test URLs: {len(test_urls)}")

    # Extract H2 IDs from each URL
    for idx, url in enumerate(test_urls, 1):
        print(f"Processing ({idx}/{len(test_urls)}): {url}")
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
