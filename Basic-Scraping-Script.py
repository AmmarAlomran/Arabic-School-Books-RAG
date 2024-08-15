import requests
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# URL of the webpage containing the books
url = "https://beadaya.com/section/1098"

# Directory to save the downloaded books
download_dir = "books"

# Create the directory if it doesn't exist
os.makedirs(download_dir, exist_ok=True)

# Function to download a file
def download_file(file_url, file_name):
    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Raise HTTPError for bad responses
        file_path = os.path.join(download_dir, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded: {file_name}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {file_name}: {e}")

# Request the page
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all the links to the books
book_links = soup.select('div.file-item-2 a')

# Prepare a list of download tasks
download_tasks = []

for link in book_links:
    book_url = link['href']
    book_title = link['title']
    
    # Make a request to the book page to find the download link
    try:
        book_page_response = requests.get(book_url)
        book_page_response.raise_for_status()  # Raise HTTPError for bad responses
        book_page_soup = BeautifulSoup(book_page_response.content, 'html.parser')
        download_link = book_page_soup.select_one('div.download-section a.download-file')['href']
        
        # Add the download task to the list
        download_tasks.append((download_link, book_title + '.pdf'))
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve download link for {book_title}: {e}")
    except Exception as e:
        print(f"An error occurred while processing {book_title}: {e}")

# Use ThreadPoolExecutor to download files concurrently
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_file = {executor.submit(download_file, link, name): name for link, name in download_tasks}
    for future in as_completed(future_to_file):
        file_name = future_to_file[future]
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred while downloading {file_name}: {e}")

print("All downloads completed.")