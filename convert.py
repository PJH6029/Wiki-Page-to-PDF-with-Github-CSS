import os
import requests
import pdfkit
from urllib.parse import urlparse, quote, unquote
from dotenv import load_dotenv

# Load GitHub token from .env file
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

def is_url_encoded(url):
    # Check if the URL is already encoded
    if '%' in url:
        try:
            decoded_url = unquote(url)
            return quote(decoded_url) == url
        except Exception:
            return False
    return False

def get_markdown_url(wiki_page_url):
    # Parse the URL
    parsed_url = urlparse(wiki_page_url)
    
    # Extract the repository path and wiki page name
    path_parts = parsed_url.path.split("/wiki/")
    
    # Handle case where the URL doesn't match the expected format
    if len(path_parts) != 2:
        raise ValueError("Invalid wiki page URL format")
    
    repo_path = path_parts[0]
    page_name = path_parts[1]
    
    # Encode the page name to handle non-ASCII characters
    if not is_url_encoded(page_name):
        encoded_page_name = quote(page_name)
        decoded_page_name = page_name
    else:
        encoded_page_name = page_name
        decoded_page_name = unquote(page_name)
    
    # Construct the markdown URL
    markdown_url = f"https://raw.githubusercontent.com/wiki{repo_path}/{encoded_page_name}.md"
    return markdown_url, decoded_page_name


def fetch_markdown_content(markdown_url):
    # Get the markdown content
    response = requests.get(markdown_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Failed to fetch markdown content")

def convert_markdown_to_html(markdown_content):
    # Prepare the payload and headers
    payload = {"text": markdown_content}
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Send the request to GitHub's Markdown API
    response = requests.post(
        "https://api.github.com/markdown", json=payload, headers=headers
    )
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Failed to convert markdown to HTML")

def save_html(html_content, filename):
    # HTML template
    html_template = f"""
    <html>
    <head>
    <link
        rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown-light.min.css"
        integrity="sha512-zb2pp+R+czM7GAemdSUQt6jFmr3qCo6ikvBgVU6F5GvwEDR0C2sefFiPEJ9QUpmAKdD5EqDUdNRtbOYnbF/eyQ=="
        crossorigin="anonymous"
        referrerpolicy="no-referrer"
    />
    </head>
    <body>
        <div class="markdown-body">
            {html_content}
        </div>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_template)

def convert_to_pdf(html_filename, pdf_filename):
    pdfkit.from_file(html_filename, pdf_filename)

def main(wiki_page_url):
    # Get markdown URL and fetch the markdown content
    markdown_url, page_name = get_markdown_url(wiki_page_url)
    markdown_content = fetch_markdown_content(markdown_url)

    # Convert markdown content to GitHub-flavored HTML
    html_content = convert_markdown_to_html(markdown_content)

    # Save HTML content
    html_filename = f"{page_name}.html"
    save_html(html_content, html_filename)
    print(f"Converted {wiki_page_url} to {html_filename}")
    
    # pdf_filename = f"{page_name}.pdf"
    # convert_to_pdf(html_filename, pdf_filename)
    # print(f"Converted {wiki_page_url} to {pdf_filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python convert.py <wiki-page-url>")
    else:
        wiki_page_url = sys.argv[1]
        main(wiki_page_url)
