from typing import Dict, Any
from ..client import SellerMagnetClient


class AmazonMarketplaceEndpoints:
    """Handles Amazon marketplace-related API endpoints."""

    def __init__(self, client: SellerMagnetClient):
        self.client = client

    def list(self) -> Dict[str, Any]:
        return self.client.get_amazon_marketplaces()