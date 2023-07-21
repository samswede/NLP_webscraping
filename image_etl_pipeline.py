import csv
import os
from respectful_duckduckgo_search import RespectfulDuckDuckGoSearch
from content_downloader import ContentDownloader
from image_classifier import ImageClassifier


def etl_pipeline(query, num_search_results, only_images):
    # Extract
    ddg_search = RespectfulDuckDuckGoSearch(num_search_results=num_search_results, only_images=only_images)
    result_links = ddg_search.search(query)
    ddg_search.save_results(result_links, query)

    # Load
    result_links = ddg_search.load_results(query)

    # Download contents
    downloader = ContentDownloader()
    downloader.download_contents(result_links, query)

    # Classify and annotate images
    classifier = ImageClassifier()
    image_dir = os.path.join(downloader.file_path, f"{query.replace(' ', '_')}_images")
    
    # Prepare to save image labels
    with open(f"{query.replace(' ', '_')}_labels.csv", 'w', newline='') as csvfile:
        fieldnames = ['image_name', 'labels']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()

        for filename in os.listdir(image_dir):
            labels = classifier.classify(os.path.join(image_dir, filename))
            
            # Write the labels for each image to the CSV file
            writer.writerow({'image_name': filename, 'labels': labels})

    print("Image labels saved.")
