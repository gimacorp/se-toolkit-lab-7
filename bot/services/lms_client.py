"""HTTP client for the LMS backend API.

This module provides a simple interface to query the LMS backend endpoints.
All requests use Bearer token authentication.
"""

import httpx
from typing import Any


class LMSClient:
    """Client for the LMS backend API.
    
    Attributes:
        base_url: Base URL of the LMS API (e.g., http://localhost:42002)
        api_key: API key for authentication
        timeout: Request timeout in seconds
    """
    
    def __init__(self, base_url: str, api_key: str, timeout: float = 5.0):
        """Initialize the LMS client.
        
        Args:
            base_url: Base URL of the LMS API
            api_key: API key for Bearer authentication
            timeout: Request timeout in seconds (default: 5.0)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for authenticated requests.
        
        Returns:
            Headers dict with Authorization and Content-Type.
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def get_items(self) -> list[dict[str, Any]]:
        """Fetch all items (labs and tasks) from the backend.
        
        Returns:
            List of items from the backend.
            
        Raises:
            httpx.RequestError: If the request fails (connection error, timeout, etc.)
            httpx.HTTPStatusError: If the server returns an error response (4xx, 5xx)
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/items/",
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()
    
    async def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Fetch pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., "lab-04")
            
        Returns:
            List of pass rate data for each task in the lab.
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the server returns an error response
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()
    
    async def health_check(self) -> dict[str, Any]:
        """Check if the backend is healthy by fetching items.
        
        Returns:
            Dict with health status and item count.
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the server returns an error response
        """
        items = await self.get_items()
        return {"healthy": True, "item_count": len(items)}
