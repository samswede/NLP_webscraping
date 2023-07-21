import requests
from bs4 import BeautifulSoup
import time
import json
import os
from datetime import datetime
from urllib.parse import urlparse, urljoin
from robotexclusionrulesparser import RobotExclusionRulesParser

class RespectfulDuckDuckGoSearch:
    def __init__(self, num_search_results=10, only_images=False, delay=1.0, file_path='./'):
        # Number of search results to retrieve
        self.num_search_results = num_search_results
        
        # Whether to only return images
        self.only_images = only_images
        
        # Delay between requests to respect server load
        self.delay = delay
        
        # Directory to save and load results
        self.file_path = file_path

        # Base search URLs
        self.search_url = "https://duckduckgo.com/html/?q={}"
        self.image_search_url = "https://duckduckgo.com/?iar=images&iax=images&ia=images&q={}"

        # Parser for robots.txt
        self.parser = RobotExclusionRulesParser()

        # Base URL for checking robots.txt
        self.base_url = "https://duckduckgo.com"

    def search(self, query):
        # Get the robots.txt file
        response = requests.get(urljoin(self.base_url, 'robots.txt'))
        
        # Parse the robots.txt
        self.parser.parse(response.text)
        
        result_links = []

        if self.only_images:
            # Check robots.txt for image search URL
            if self.parser.is_allowed("*", self.image_search_url):
                time.sleep(self.delay)
                response = requests.get(self.image_search_url.format(query))
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all image links up to the set limit
                results = soup.find_all('a', class_='tile--img__img', href=True, limit=self.num_search_results)
                for result in results:
                    result_links.append(result['href'])
        else:
            # Check robots.txt for standard search URL
            if self.parser.is_allowed("*", self.search_url):
                time.sleep(self.delay)
                response = requests.get(self.search_url.format(query))
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all result links up to the set limit
                results = soup.find_all('a', class_='result__url', href=True, limit=self.num_search_results)
                for result in results:
                    result_links.append('https://duckduckgo.com' + result['href'])

        return result_links

    def save_results(self, result_links, query):
        # Marker for images in the filename
        image_marker = '_images' if self.only_images else ''
        
        # Filename includes the query, image marker and timestamp
        filename = f"{query.replace(' ', '_')}{image_marker}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        
        # Save result links to a JSON file
        with open(os.path.join(self.file_path, filename), 'w') as f:
            json.dump(result_links, f)
        print(f"Results saved to {os.path.join(self.file_path, filename)}")
    
    def load_results(self, query):
        # Marker for images in the filename
        image_marker = '_images' if self.only_images else ''
        
        # Look for a file that starts with the query and image marker and ends with .json
        for file in os.listdir(self.file_path):
            if file.startswith(f"{query.replace(' ', '_')}{image_marker}") and file.endswith(".json"):
                
                # Load result links from the file
                with open(os.path.join(self.file_path, file), 'r') as f:
                    result_links = json.load(f)
                    return result_links
        return None
