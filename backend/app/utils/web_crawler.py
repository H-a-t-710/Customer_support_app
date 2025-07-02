import requests
import logging
import time
import os
import json
from typing import List, Dict, Any, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.core.config import settings
from app.utils.preprocessor import clean_html

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebCrawler:
    """
    Web crawler for extracting content from Angel One support pages.
    """
    
    def __init__(self, 
                 base_url: str = "https://www.angelone.in/support",
                 rate_limit: float = 1.0,
                 output_dir: str = None):
        """
        Initialize the web crawler.
        
        Args:
            base_url (str): Base URL to start crawling from
            rate_limit (float): Time to wait between requests in seconds
            output_dir (str): Directory to save crawled data
        """
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.output_dir = output_dir or os.path.join(settings.PROCESSED_PATH, "web_content")
        self.visited_urls: Set[str] = set()
        self.queue: List[str] = [self.base_url]
        self.content_data: List[Dict[str, Any]] = []
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize headers for requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid for crawling.
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if URL is valid
        """
        # Parse URL
        parsed_url = urlparse(url)
        
        # Check if URL is from Angel One support
        if "angelone.in" not in parsed_url.netloc:
            return False
        
        # Check if URL is a support page
        if "/support" not in parsed_url.path and not url == self.base_url:
            return False
        
        # Skip URLs with query parameters
        if parsed_url.query:
            return False
        
        # Skip social media and login links
        skip_patterns = [
            "/login", 
            "facebook", 
            "twitter", 
            "linkedin", 
            "instagram",
            "javascript:",
            "#",
            "tel:",
            "mailto:"
        ]
        
        if any(pattern in url.lower() for pattern in skip_patterns):
            return False
        
        return True
    
    def extract_content(self, url: str, html: str) -> Dict[str, Any]:
        """
        Extract content from HTML.
        
        Args:
            url (str): URL of the page
            html (str): HTML content
            
        Returns:
            Dict[str, Any]: Extracted content
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract title
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "No Title"
        
        # Try to find the main content
        content_selectors = [
            "main", 
            "article", 
            ".content", 
            "#content",
            ".main-content",
            ".container"
        ]
        
        main_content = None
        for selector in content_selectors:
            content = soup.select(selector)
            if content:
                main_content = content[0]
                break
        
        if not main_content:
            main_content = soup.body
        
        # Extract text content
        if main_content:
            # Remove navigation, footer, scripts, and styles
            for element in main_content.select("nav, footer, script, style, .footer, .header, .navigation"):
                element.decompose()
            
            # Extract headings
            headings = [h.text.strip() for h in main_content.find_all(["h1", "h2", "h3"])]
            
            # Extract paragraphs
            paragraphs = [p.text.strip() for p in main_content.find_all("p") if p.text.strip()]
            
            # Extract lists
            list_items = [li.text.strip() for li in main_content.find_all("li") if li.text.strip()]
            
            # Clean the full text
            full_text = clean_html(main_content.get_text(separator="\n", strip=True))
            
            # Check if page has FAQ content
            faq_content = []
            faq_selectors = [".faq", "#faq", ".faqs", "#faqs", ".accordion"]
            
            for selector in faq_selectors:
                faq_elements = soup.select(selector)
                if faq_elements:
                    for faq in faq_elements:
                        # Try to extract question-answer pairs
                        questions = faq.find_all(["h3", "h4", "dt", ".question", ".accordion-header"])
                        answers = faq.find_all(["p", "dd", ".answer", ".accordion-body"])
                        
                        # Match questions with answers
                        for i, question in enumerate(questions):
                            if i < len(answers):
                                q_text = question.text.strip()
                                a_text = answers[i].text.strip()
                                
                                if q_text and a_text:
                                    faq_content.append({
                                        "question": q_text,
                                        "answer": a_text
                                    })
            
            return {
                "url": url,
                "title": title,
                "headings": headings,
                "paragraphs": paragraphs,
                "list_items": list_items,
                "full_text": full_text,
                "faq_content": faq_content,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        return {
            "url": url,
            "title": title,
            "full_text": "No content extracted",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def extract_links(self, url: str, html: str) -> List[str]:
        """
        Extract links from HTML.
        
        Args:
            url (str): URL of the page
            html (str): HTML content
            
        Returns:
            List[str]: List of extracted links
        """
        soup = BeautifulSoup(html, "html.parser")
        links = []
        
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            
            # Normalize URL
            absolute_url = urljoin(url, href)
            
            # Check if URL is valid
            if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                links.append(absolute_url)
        
        return links
    
    def crawl(self) -> List[Dict[str, Any]]:
        """
        Crawl the support pages.
        
        Returns:
            List[Dict[str, Any]]: List of crawled content
        """
        page_count = 0
        
        while self.queue:
            # Get next URL from queue
            url = self.queue.pop(0)
            
            # Skip if already visited
            if url in self.visited_urls:
                continue
            
            # Mark as visited
            self.visited_urls.add(url)
            
            try:
                logger.info(f"Crawling page {page_count + 1}: {url}")
                
                # Fetch page
                response = requests.get(url, headers=self.headers, timeout=10)
                
                # Check if request was successful
                if response.status_code == 200:
                    html = response.text
                    
                    # Extract content
                    content = self.extract_content(url, html)
                    self.content_data.append(content)
                    
                    # Extract links
                    links = self.extract_links(url, html)
                    
                    # Add new links to queue
                    for link in links:
                        if link not in self.visited_urls and link not in self.queue:
                            self.queue.append(link)
                    
                    # Increment page count
                    page_count += 1
                else:
                    logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                
                # Rate limiting
                time.sleep(self.rate_limit)
                
            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
        
        # Save crawled data
        self._save_crawled_data()
        
        logger.info(f"Crawling completed. Crawled {len(self.content_data)} pages.")
        return self.content_data
    
    def _save_crawled_data(self) -> None:
        """
        Save crawled data to file.
        """
        output_path = os.path.join(self.output_dir, "angel_one_support.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.content_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved crawled data to {output_path}")
    
    def get_crawled_data(self) -> List[Dict[str, Any]]:
        """
        Get crawled data from file.
        
        Returns:
            List[Dict[str, Any]]: Crawled data
        """
        output_path = os.path.join(self.output_dir, "angel_one_support.json")
        
        if not os.path.exists(output_path):
            logger.warning(f"Crawled data file not found: {output_path}")
            return []
        
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            logger.info(f"Loaded {len(data)} crawled pages from {output_path}")
            return data
        except Exception as e:
            logger.error(f"Error loading crawled data: {str(e)}")
            return []
            
# Function to process web content into a format suitable for the RAG system
def process_web_content(web_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process web content for RAG system.
    
    Args:
        web_data (List[Dict[str, Any]]): Web content data
        
    Returns:
        List[Dict[str, Any]]: Processed document chunks
    """
    processed_docs = []
    
    for page in web_data:
        url = page.get("url", "")
        title = page.get("title", "")
        full_text = page.get("full_text", "")
        faq_content = page.get("faq_content", [])
        
        # Create document from full text
        if full_text and full_text != "No content extracted":
            doc = {
                "content": full_text,
                "metadata": {
                    "source": url,
                    "title": title,
                    "source_type": "web",
                    "timestamp": page.get("timestamp", "")
                }
            }
            processed_docs.append(doc)
        
        # Create documents from FAQ content
        for faq in faq_content:
            question = faq.get("question", "")
            answer = faq.get("answer", "")
            
            if question and answer:
                doc = {
                    "content": f"Q: {question}\nA: {answer}",
                    "metadata": {
                        "source": url,
                        "title": title,
                        "source_type": "web_faq",
                        "timestamp": page.get("timestamp", "")
                    }
                }
                processed_docs.append(doc)
    
    return processed_docs 