import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class MedicalGuidelineScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Configure Chrome options for headless scraping
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Define source configurations
        self.sources = {
            'WHO': {
                'url': 'https://www.who.int/publications/guidelines',
                'type': 'selenium',
                'selectors': {
                    'guideline_links': 'a[href*="/publications/"]',
                    'title': 'h1, h2, h3',
                    'date': '.date, .published-date',
                    'content': '.content, .description'
                }
            },
            'CDC': {
                'url': 'https://www.cdc.gov/mmwr/index.html',
                'type': 'requests',
                'selectors': {
                    'guideline_links': 'a[href*="/mmwr/"]',
                    'title': 'h1, h2, h3',
                    'date': '.date, .published-date',
                    'content': '.content, .description'
                }
            },
            'NICE': {
                'url': 'https://www.nice.org.uk/guidance/published',
                'type': 'selenium',
                'selectors': {
                    'guideline_links': 'a[href*="/guidance/"]',
                    'title': 'h1, h2, h3',
                    'date': '.date, .published-date',
                    'content': '.content, .description'
                }
            },
            'AHA': {
                'url': 'https://www.heart.org/en/professional/quality-improvement/clinical-guidance',
                'type': 'selenium',
                'selectors': {
                    'guideline_links': 'a[href*="/professional/"]',
                    'title': 'h1, h2, h3',
                    'date': '.date, .published-date',
                    'content': '.content, .description'
                }
            },
            'ADA': {
                'url': 'https://diabetesjournals.org/care/issue',
                'type': 'requests',
                'selectors': {
                    'guideline_links': 'a[href*="/care/"]',
                    'title': 'h1, h2, h3',
                    'date': '.date, .published-date',
                    'content': '.content, .description'
                }
            },
            'IDSA': {
                'url': 'https://www.idsociety.org/practice-guideline/',
                'type': 'selenium',
                'selectors': {
                    'guideline_links': 'a[href*="/practice-guideline/"]',
                    'title': 'h1, h2, h3',
                    'date': '.date, .published-date',
                    'content': '.content, .description'
                }
            }
        }
    
    def get_selenium_driver(self):
        """Get a configured Selenium WebDriver"""
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.set_page_load_timeout(30)
            return driver
        except Exception as e:
            logger.error(f"Failed to initialize Selenium driver: {e}")
            return None
    
    def scrape_who_guidelines(self):
        """Scrape WHO guidelines"""
        guidelines = []
        try:
            driver = self.get_selenium_driver()
            if not driver:
                return guidelines
            
            driver.get(self.sources['WHO']['url'])
            time.sleep(5)
            
            # Wait for content to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find guideline links
            links = soup.find_all('a', href=re.compile(r'/publications/'))
            
            for link in links[:10]:  # Limit to 10 most recent
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    href = link.get('href')
                    if href.startswith('/'):
                        href = f"https://www.who.int{href}"
                    
                    # Try to extract date from parent elements
                    date_element = link.find_parent().find(class_=re.compile(r'date|published'))
                    date = date_element.get_text(strip=True) if date_element else datetime.now().strftime('%Y-%m-%d')
                    
                    guidelines.append({
                        'title': title,
                        'source': 'WHO',
                        'link': href,
                        'date': date,
                        'content': title  # Use title as content for now
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing WHO guideline: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping WHO guidelines: {e}")
        
        return guidelines
    
    def scrape_cdc_guidelines(self):
        """Scrape CDC MMWR guidelines"""
        guidelines = []
        try:
            response = self.session.get(self.sources['CDC']['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find MMWR articles
            links = soup.find_all('a', href=re.compile(r'/mmwr/'))
            
            for link in links[:10]:  # Limit to 10 most recent
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    href = link.get('href')
                    if href.startswith('/'):
                        href = f"https://www.cdc.gov{href}"
                    
                    # Try to extract date
                    date_element = link.find_parent().find(class_=re.compile(r'date|published'))
                    date = date_element.get_text(strip=True) if date_element else datetime.now().strftime('%Y-%m-%d')
                    
                    guidelines.append({
                        'title': title,
                        'source': 'CDC',
                        'link': href,
                        'date': date,
                        'content': title
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing CDC guideline: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping CDC guidelines: {e}")
        
        return guidelines
    
    def scrape_nice_guidelines(self):
        """Scrape NICE guidelines"""
        guidelines = []
        try:
            driver = self.get_selenium_driver()
            if not driver:
                return guidelines
            
            driver.get(self.sources['NICE']['url'])
            time.sleep(5)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find guideline links
            links = soup.find_all('a', href=re.compile(r'/guidance/'))
            
            for link in links[:10]:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    href = link.get('href')
                    if href.startswith('/'):
                        href = f"https://www.nice.org.uk{href}"
                    
                    date_element = link.find_parent().find(class_=re.compile(r'date|published'))
                    date = date_element.get_text(strip=True) if date_element else datetime.now().strftime('%Y-%m-%d')
                    
                    guidelines.append({
                        'title': title,
                        'source': 'NICE',
                        'link': href,
                        'date': date,
                        'content': title
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing NICE guideline: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping NICE guidelines: {e}")
        
        return guidelines
    
    def scrape_aha_guidelines(self):
        """Scrape American Heart Association guidelines"""
        guidelines = []
        try:
            driver = self.get_selenium_driver()
            if not driver:
                return guidelines
            
            driver.get(self.sources['AHA']['url'])
            time.sleep(5)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find guideline links
            links = soup.find_all('a', href=re.compile(r'/professional/'))
            
            for link in links[:10]:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    href = link.get('href')
                    if href.startswith('/'):
                        href = f"https://www.heart.org{href}"
                    
                    date_element = link.find_parent().find(class_=re.compile(r'date|published'))
                    date = date_element.get_text(strip=True) if date_element else datetime.now().strftime('%Y-%m-%d')
                    
                    guidelines.append({
                        'title': title,
                        'source': 'AHA',
                        'link': href,
                        'date': date,
                        'content': title
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing AHA guideline: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping AHA guidelines: {e}")
        
        return guidelines
    
    def scrape_ada_guidelines(self):
        """Scrape American Diabetes Association guidelines"""
        guidelines = []
        try:
            response = self.session.get(self.sources['ADA']['url'], timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find ADA Care articles
            links = soup.find_all('a', href=re.compile(r'/care/'))
            
            for link in links[:10]:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    href = link.get('href')
                    if href.startswith('/'):
                        href = f"https://diabetesjournals.org{href}"
                    
                    date_element = link.find_parent().find(class_=re.compile(r'date|published'))
                    date = date_element.get_text(strip=True) if date_element else datetime.now().strftime('%Y-%m-%d')
                    
                    guidelines.append({
                        'title': title,
                        'source': 'ADA',
                        'link': href,
                        'date': date,
                        'content': title
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing ADA guideline: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error scraping ADA guidelines: {e}")
        
        return guidelines
    
    def scrape_idsa_guidelines(self):
        """Scrape IDSA practice guidelines"""
        guidelines = []
        try:
            driver = self.get_selenium_driver()
            if not driver:
                return guidelines
            
            driver.get(self.sources['IDSA']['url'])
            time.sleep(5)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find guideline links
            links = soup.find_all('a', href=re.compile(r'/practice-guideline/'))
            
            for link in links[:10]:
                try:
                    title = link.get_text(strip=True)
                    if not title or len(title) < 10:
                        continue
                    
                    href = link.get('href')
                    if href.startswith('/'):
                        href = f"https://www.idsociety.org{href}"
                    
                    date_element = link.find_parent().find(class_=re.compile(r'date|published'))
                    date = date_element.get_text(strip=True) if date_element else datetime.now().strftime('%Y-%m-%d')
                    
                    guidelines.append({
                        'title': title,
                        'source': 'IDSA',
                        'link': href,
                        'date': date,
                        'content': title
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing IDSA guideline: {e}")
                    continue
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"Error scraping IDSA guidelines: {e}")
        
        return guidelines
    
    def scrape_all_sources(self):
        """Scrape guidelines from all sources"""
        all_guidelines = []
        
        logger.info("Starting to scrape all medical guideline sources...")
        
        # Scrape each source
        sources_to_scrape = [
            ('WHO', self.scrape_who_guidelines),
            ('CDC', self.scrape_cdc_guidelines),
            ('NICE', self.scrape_nice_guidelines),
            ('AHA', self.scrape_aha_guidelines),
            ('ADA', self.scrape_ada_guidelines),
            ('IDSA', self.scrape_idsa_guidelines)
        ]
        
        for source_name, scrape_function in sources_to_scrape:
            try:
                logger.info(f"Scraping {source_name} guidelines...")
                guidelines = scrape_function()
                all_guidelines.extend(guidelines)
                logger.info(f"Found {len(guidelines)} guidelines from {source_name}")
                
                # Add small delay between sources to be respectful
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")
                continue
        
        logger.info(f"Total guidelines scraped: {len(all_guidelines)}")
        return all_guidelines
    
    def get_guideline_content(self, url):
        """Get detailed content from a guideline URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:2000]  # Limit content length
            
        except Exception as e:
            logger.error(f"Error getting content from {url}: {e}")
            return "" 