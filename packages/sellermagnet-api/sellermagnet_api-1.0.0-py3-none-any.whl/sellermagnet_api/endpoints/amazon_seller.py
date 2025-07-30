from typing import Dict, Any
from ..client import SellerMagnetClient


class AmazonSellerEndpoints:
    """Handles Amazon seller-related API endpoints."""

    def __init__(self, client: SellerMagnetClient):
        self.client = client

    def reviews(self, seller_id: str, marketplace_id: str) -> Dict[str, Any]:
        return self.client.get_amazon_seller_reviews(seller_id, marketplace_id)