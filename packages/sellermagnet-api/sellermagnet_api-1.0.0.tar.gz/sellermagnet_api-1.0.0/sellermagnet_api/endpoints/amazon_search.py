from typing import Dict, Any
from ..client import SellerMagnetClient


class AmazonSearchEndpoints:
    """Handles Amazon search-related API endpoints."""

    def __init__(self, client: SellerMagnetClient):
        self.client = client

    def products(self, query: str, marketplace_id: str, count: int = 30) -> Dict[str, Any]:
        return self.client.search_amazon_products(query, marketplace_id, count)