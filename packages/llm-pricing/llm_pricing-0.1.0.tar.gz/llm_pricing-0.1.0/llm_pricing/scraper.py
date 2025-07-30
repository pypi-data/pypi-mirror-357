"""
Extended scraper module to manage HTTP requests and parse HTML content using BeautifulSoup.

Give a star to the repository from [here](https://github.com/fswair/llm-pricing) if you find it useful!
"""

from aiohttp import ClientSession
from user_agent import generate_user_agent

import bs4

class RequestManager:
    """
    Manages HTTP requests with predefined headers for web scraping.
    """
    
    def __init__(self, session: ClientSession):
        """Initialize the RequestManager with an aiohttp session.
        
        Args:
            session: An aiohttp ClientSession instance for making requests.
        """
        self.session = session
    
    @property
    def headers(self) -> dict:
        """
        Get standard headers for requests to anthropic.com.
        
        Returns:
            Dictionary containing HTTP headers mimicking a browser request.
        """
        return {
            'Host': 'www.anthropic.com',
            'Sec-Ch-Ua-Platform': 'macOS',
            'Accept-Language': 'tr-TR,tr;q=0.9',
            'Sec-Ch-Ua': '"Chromium";v="133", "Not(A:Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            "User-Agent": generate_user_agent(),
            'Accept': '*/*',
            'Origin': 'https://www.anthropic.com/',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.anthropic.com/pricing#api',
            'Accept-Encoding': 'gzip, deflate, br',
            'Priority': 'u=1, i'
        }

    async def get(self, url: str, params: dict = None) -> bytes:
        """
        Make an HTTP GET request to the specified URL.
        
        Args:
            url: The URL to request.
            params: Optional query parameters for the request.
            
        Returns:
            The response content as bytes.
            
        Raises:
            aiohttp.ClientResponseError: If the request fails.
        """
        async with self.session.get(url, params=params, headers=self.headers) as response:
            response.raise_for_status()
            return await response.content.read()


class Scraper(bs4.BeautifulSoup):
    """
    A web scraper that extends BeautifulSoup for parsing HTML content.
    """
    
    def __init__(self, url: str, session: ClientSession, **request_params):
        """Initialize the scraper with URL and session.
        
        Args:
            url: The URL to scrape.
            session: An aiohttp ClientSession for making requests.
            **request_params: Additional parameters for the request.
        """
        self.url = url
        self.session = session
        self._request_params = request_params
    
    async def init(self) -> None:
        """
        Initialize the scraper by fetching and parsing the content.
        
        This method must be called after instantiation to populate the
        BeautifulSoup object with the scraped content.
        """
        self._manager = RequestManager(self.session)
        self.content = await self._manager.get(self.url, params=self._request_params)
        super().__init__(self.content, 'html.parser')