import requests
from bs4 import BeautifulSoup
import html2text
from urllib.parse import urljoin, urlparse
import tiktoken
import os
from dotenv import load_dotenv
from openai import OpenAI
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_page(url):
    """Fetches the HTML content of a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def extract_internal_links(html, base_url):
    """Extracts and returns a list of internal links from the given HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        # Only include links from the same domain
        if urlparse(full_url).netloc == urlparse(base_url).netloc:
            links.add(full_url)
    return list(links)

def html_to_text(html):
    """Converts HTML to plain text using html2text."""
    converter = html2text.HTML2Text()
    converter.ignore_links = True  # Optionally, adjust settings; e.g., to preserve links
    return converter.handle(html)

def merge_texts_remove_duplicates(texts):
    """
    Merge a list of texts into one string while removing duplicate lines.
    Splits texts by newline, removes duplicates while preserving order.
    """
    seen = set()
    merged_lines = []
    for text in texts:
        # Add heading to indicate a new page
        merged_lines.append("### New Page ###")
        for line in text.splitlines():
            stripped_line = line.strip()
            if stripped_line and stripped_line not in seen:
                seen.add(stripped_line)
                merged_lines.append(stripped_line)
    return merged_lines

def process_website_to_md(website, num_subpages=5, llm_model="gpt-4o-mini"):
    """
    Processes a website by fetching its main page and a number of internal subpages,
    extracts the text content, and sends a prompt to an OpenAI model to extract
    useful information for recreating the site.

    Parameters:
        website (str): The URL of the website to process.
        num_subpages (int): Number of internal subpages to process.
        llm_model (str): The language model to use for the extraction.

    Returns:
        str: The markdown output from the OpenAI model.
    """
    logging.info(f"Fetching main page: {website}")
    main_html = fetch_page(website)
    if not main_html:
        logging.error("Failed to fetch the main page.")
        return None

    # Convert main page HTML to text
    main_text = html_to_text(main_html)

    # Extract internal links from the main page
    links = extract_internal_links(main_html, website)
    logging.info(f"Found {len(links)} internal links. Processing first {num_subpages} subpages:")

    # Process subpages and store text content
    subpages_text = []
    for subpage in links[:num_subpages]:
        subpage = subpage.replace("\n", "").strip()
        logging.info(f"Fetching subpage: {subpage}")
        sub_html = fetch_page(subpage)
        if sub_html:
            sub_text = html_to_text(sub_html)
            subpages_text.append(sub_text)
        else:
            logging.error(f"Failed to fetch {subpage}")

    # Merge texts from subpages and remove duplicate lines
    lines = merge_texts_remove_duplicates(subpages_text)

    # Initialize the tokenizer for the given model and count tokens
    tokenizer = tiktoken.encoding_for_model(llm_model)
    num_of_tokens = len(tokenizer.encode("\n".join(lines)))
    logging.info(f"Number of tokens: {num_of_tokens}")

    merged_text = '\n'.join(lines)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Compose the prompt
    prompt = f"""Given the content of the website ({website}), please extract useful information to recreate the site. Focus on the following sections:

1. **General Information**: Provide a brief overview of the website's purpose and main features.  
2. **Opening Hours**: List the opening hours of the business or service.  
3. **Contact Information**: Include all relevant contact details such as phone numbers, email addresses, and physical addresses.  
4. **Website Content**: Extract key content that should be included on the website, such as descriptions, services offered, or any other pertinent information.  
5. **Images**: Identify and list prominent images, including logos and other important visuals, along with their URLs.  

Structure the output as markdown for clarity and easy reading.

This is IMPORTANT! Output only markdown, no comments, no explanations, just the extracted information in markdown format. Also keep original  language.

Website Content:
{merged_text}
"""

    response = client.chat.completions.create(
        model=llm_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    output = response.choices[0].message.content
    logging.info(output)
    return output

if __name__ == "__main__":
    website = "https://www.knihovna.roztoky.cz/web/"
    process_website_to_md(website, num_subpages=5, llm_model="gpt-4o-mini")