import os
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class ContentDownloader:
    def __init__(self, file_path='./'):
        # Directory to save downloaded contents
        self.file_path = file_path

    def download_contents(self, result_links, query):
        # Marker for images in the filename
        image_marker = '_images' if self.only_images else ''
        
        # Directory names
        query_dir = f"{query.replace(' ', '_')}{image_marker}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        raw_image_dir = 'raw_images'
        raw_html_dir = 'raw_html'

        # Create directories
        # exist_ok=True allows the creation of directories if they don't already exist
        try:
            os.makedirs(os.path.join(self.file_path, query_dir, raw_image_dir), exist_ok=True)
            os.makedirs(os.path.join(self.file_path, query_dir, raw_html_dir), exist_ok=True)
        except Exception as e:
            print(f"Error creating directories: {e}")
            return

        for link in result_links:
            # Parse the link to get the filename
            parsed_url = urlparse(link)
            filename = os.path.basename(parsed_url.path)
            
            try:
                # Send a GET request to the link
                response = requests.get(link)
            except Exception as e:
                print(f"Error getting {link}: {e}")
                continue

            if self.only_images:
                # For images, save the raw content of the response in binary mode
                try:
                    with open(os.path.join(self.file_path, query_dir, raw_image_dir, filename), 'wb') as out_file:
                        out_file.write(response.content)
                except Exception as e:
                    print(f"Error writing to {filename}: {e}")
                    continue
            else:
                # For HTML, format the HTML with BeautifulSoup before saving
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    with open(os.path.join(self.file_path, query_dir, raw_html_dir, f"{filename}.html"), 'w') as out_file:
                        out_file.write(soup.prettify())
                except Exception as e:
                    print(f"Error writing to {filename}.html: {e}")
                    continue

        print(f"Contents downloaded to {os.path.join(self.file_path, query_dir)}")
