import httpx
from bs4 import BeautifulSoup
from typing import List
import time

class ImageScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_images(self, item_name: str, category: str = 'General') -> List[str]:
        """Scrape images based on category and item name"""
        try:
            if category.lower() == 'sneakers':
                return self._scrape_stockx(item_name)
            elif category.lower() == 'electronics':
                return self._scrape_ebay(item_name)
            else:
                return self._scrape_generic(item_name)
        except Exception as e:
            print(f"Scraping error: {e}")
            return []
    
    def _scrape_stockx(self, item_name: str) -> List[str]:
        """Scrape StockX for sneaker images"""
        try:
            search_url = f"https://stockx.com/search?s={item_name.replace(' ', '%20')}"
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=10) as client:
                response = client.get(search_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                images = []
                for img in soup.find_all('img', limit=15):
                    src = img.get('src') or img.get('data-src')
                    if src and ('stockx' in src.lower() or 'cloudinary' in src.lower()):
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif src.startswith('/'):
                            src = 'https://stockx.com' + src
                        if src not in images:
                            images.append(src)
                
                return images[:15]
        except:
            return self._scrape_generic(item_name)
    
    def _scrape_ebay(self, item_name: str) -> List[str]:
        """Scrape eBay for electronics images"""
        try:
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={item_name.replace(' ', '+')}"
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=10) as client:
                response = client.get(search_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                images = []
                for img in soup.find_all('img', limit=15):
                    src = img.get('src') or img.get('data-src')
                    if src and 'ebayimg' in src.lower():
                        if src.startswith('//'):
                            src = 'https:' + src
                        if src not in images and src.startswith('http'):
                            images.append(src)
                
                return images[:15]
        except:
            return self._scrape_generic(item_name)
    
    def _scrape_generic(self, item_name: str) -> List[str]:
        """Generic image scraping fallback"""
        try:
            search_url = f"https://www.google.com/search?q={item_name.replace(' ', '+')}&tbm=isch"
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=10) as client:
                response = client.get(search_url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                images = []
                for img in soup.find_all('img', limit=15):
                    src = img.get('src') or img.get('data-src')
                    if src and src.startswith('http'):
                        if src not in images:
                            images.append(src)
                
                return images[:15]
        except:
            return []
    
    def download_image(self, url: str, save_path: str) -> bool:
        """Download an image from URL to local path"""
        try:
            with httpx.Client(headers=self.headers, timeout=15) as client:
                response = client.get(url)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    return True
        except:
            pass
        return False
