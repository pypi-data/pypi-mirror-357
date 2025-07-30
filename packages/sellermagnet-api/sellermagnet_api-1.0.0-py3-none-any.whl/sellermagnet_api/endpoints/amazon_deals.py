from typing import Dict, Any
from ..client import SellerMagnetClient


class AmazonDealsEndpoints:
    """Handles Amazon deals-related API endpoints."""

    def __init__(self, client: SellerMagnetClient):
        self.client = client

    def bestsellers(self, category_id: str, marketplace_id: str, count: int = 30) -> Dict[str, Any]:
        return self.client.get_amazon_bestsellers(category_id, marketplace_id, count)

    def categories(self, marketplace_id: str) -> Dict[str, Any]:
        return self.client.get_amazon_deals_categories(marketplace_id)