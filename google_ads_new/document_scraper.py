"""
Google Ads Documentation Scraper
Scrapes official Google Ads API documentation and creates language-ready chunks
"""

import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import time
import logging
from typing import List, Dict, Any
from .constants import GOOGLE_ADS_API_DOCS_URLS

logger = logging.getLogger(__name__)

class GoogleAdsDocsScraper:
    """Scraper for Google Ads API documentation"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_text(self, url: str) -> str:
        """Fetch and clean text from a URL"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='devsite-content')
            if main_content:
                text = main_content.get_text(" ", strip=True)
            else:
                text = soup.get_text(" ", strip=True)
            
            # Clean up text
            text = self._clean_text(text)
            return text
            
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common Google Docs artifacts
        text = text.replace('Skip to main content', '')
        text = text.replace('Skip to navigation', '')
        text = text.replace('Google Cloud', '')
        
        return text.strip()
    
    def extract_metadata(self, url: str, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from the page"""
        metadata = {
            'source': url,
            'title': '',
            'version': '',
            'section': ''
        }
        
        try:
            # Extract title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text().strip()
            
            # Extract version if available
            version_elem = soup.find('span', class_='devsite-version')
            if version_elem:
                metadata['version'] = version_elem.get_text().strip()
            
            # Extract section based on URL
            if '/get-started/' in url:
                metadata['section'] = 'getting_started'
            elif '/oauth/' in url:
                metadata['section'] = 'oauth'
            elif '/concepts/' in url:
                metadata['section'] = 'concepts'
            elif '/mutating/' in url:
                metadata['section'] = 'mutating'
            elif '/account-management/' in url:
                metadata['section'] = 'account_management'
            else:
                metadata['section'] = 'general'
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from {url}: {e}")
        
        return metadata
    
    def scrape_documents(self, urls: List[str] = None) -> List[Document]:
        """Scrape all documents and create chunks"""
        if urls is None:
            urls = GOOGLE_ADS_API_DOCS_URLS
        
        all_docs = []
        
        for i, url in enumerate(urls):
            try:
                logger.info(f"Processing {i+1}/{len(urls)}: {url}")
                
                # Fetch text
                text = self.fetch_text(url)
                if not text:
                    logger.warning(f"No text extracted from {url}")
                    continue
                
                # Split into chunks
                chunks = self.splitter.split_text(text)
                
                # Create documents
                for j, chunk in enumerate(chunks):
                    if len(chunk.strip()) > 50:  # Only include substantial chunks
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                'source': url,
                                'chunk': j,
                                'total_chunks': len(chunks),
                                'url_index': i
                            }
                        )
                        all_docs.append(doc)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(all_docs)} document chunks")
        return all_docs

def scrape_google_ads_docs() -> List[Document]:
    """Main function to scrape Google Ads documentation"""
    scraper = GoogleAdsDocsScraper(chunk_size=1000, chunk_overlap=200)
    return scraper.scrape_documents()
