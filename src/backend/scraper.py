import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_website_content(url: str) -> dict:
    """
    Extract content from a website.
    
    Args:
        url: The URL of the website to scrape
        
    Returns:
        dict: A dictionary containing the extracted content
    """
    try:
        logger.info(f"Fetching content from {url}")
        response = requests.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract relevant information
        title = soup.title.string if soup.title else "Untitled"
        
        # Extract text content
        paragraphs = [p.text for p in soup.find_all('p')]
        headings = [h.text for h in soup.find_all(['h1', 'h2', 'h3'])]
        
        # Extract images
        images = [img.get('src') for img in soup.find_all('img') if img.get('src')]
        
        # Extract links
        links = [{'text': a.text, 'href': a.get('href')} 
                 for a in soup.find_all('a') if a.get('href')]
        
        # Return structured content
        return {
            "title": title,
            "headings": headings,
            "paragraphs": paragraphs,
            "images": images,
            "links": links,
            "raw_html": response.text  # Include raw HTML for more advanced processing
        }
    
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        raise Exception(f"Failed to extract content: {str(e)}")