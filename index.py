import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import time

def download_file(url, folder_path):
    local_filename = os.path.join(folder_path, os.path.basename(urlparse(url).path))
    with requests.get(url, stream=True) as response:
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 KB
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(local_filename))

        with open(local_filename, 'wb') as file:
            for data in response.iter_content(chunk_size=block_size):
                progress_bar.update(len(data))
                file.write(data)

        progress_bar.close()

    return local_filename

def download_resources(base_url, html_content, folder_path):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract and download CSS files
    css_links = [urljoin(base_url, link.get('href')) for link in soup.find_all('link', {'rel': 'stylesheet'})]
    for css_link in css_links:
        download_file(css_link, folder_path)

    # Extract and download JavaScript files
    js_links = [urljoin(base_url, script.get('src')) for script in soup.find_all('script', {'src': True})]
    for js_link in js_links:
        download_file(js_link, folder_path)

    # Download other resources (images, fonts, etc.)
    other_links = [urljoin(base_url, resource.get('src') or resource.get('href')) for resource in soup.find_all(['img', 'audio', 'video', 'source', 'link', 'object', 'embed', 'track', 'use'])]
    for other_link in other_links:
        download_file(other_link, folder_path)

def save_website(url, folder_path):
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Download HTML content
    response = requests.get(url)
    html_content = response.text

    # Save HTML file
    html_filename = os.path.join(folder_path, 'index.html')
    with open(html_filename, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

    # Download and save resources
    download_resources(url, html_content, folder_path)

if __name__ == "__main__":
    website_url = input("Enter the website URL: ")
    folder_path = input("Enter the folder path to save the files: ")

    start_time = time.time()

    save_website(website_url, folder_path)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nProcess completed in {elapsed_time:.2f} seconds.")