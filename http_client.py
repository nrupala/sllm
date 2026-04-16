"""Production: Async HTTP Client with Retry"""
import aiohttp
import asyncio
from typing import Optional, Dict, Any

class AsyncHTTPClient:
    def __init__(self, base_url: str = "", timeout: int = 30, retries: int = 3):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.retries = retries
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session
    
    async def _request_with_retry(self, method: str, url: str, **kwargs) -> Dict[Any, Any]:
        for attempt in range(self.retries):
            try:
                async with await self._get_session() as session:
                    async with session.request(method, url, **kwargs) as resp:
                        resp.raise_for_status()
                        return await resp.json()
            except Exception as e:
                if attempt == self.retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        return {}
    
    async def get(self, path: str, **kwargs) -> Dict[Any, Any]:
        url = f"{self.base_url}{path}" if not path.startswith("http") else path
        return await self._request_with_retry("GET", url, **kwargs)
    
    async def post(self, path: str, **kwargs) -> Dict[Any, Any]:
        url = f"{self.base_url}{path}" if not path.startswith("http") else path
        return await self._request_with_retry("POST", url, **kwargs)
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

# Usage: client = AsyncHTTPClient("https://api.example.com")