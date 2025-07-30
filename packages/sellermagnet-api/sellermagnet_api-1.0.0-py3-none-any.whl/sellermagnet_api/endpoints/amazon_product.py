from typing import Dict, Any, Optional
from ..client import SellerMagnetClient


class AmazonProductEndpoints:
    """Handles Amazon product-related API endpoints."""

    def __init__(self, client: SellerMagnetClient):
        self.client = client

    def statistics(self, asin: str, marketplace_id: str, graphs: bool = False) -> Dict[str, Any]:
        return self.client.get_amazon_product_statistics(asin, marketplace_id, graphs)

    def lookup(self, asin: str, marketplace_id: str) -> Dict[str, Any]:
        return self.client.get_amazon_product(asin, marketplace_id)

    def offers(self, asin: str, marketplace_id: str, geo_location: Optional[str] = None) -> Dict[str, Any]:
        return self.client.get_amazon_product_offers(asin, marketplace_id, geo_location)

    def estimated_sales(self, asin: str, marketplace_id: str) -> Dict[str, Any]:
        return self.client.get_amazon_product_estimated_sales(asin, marketplace_id)

    def convert_asin(self, identifier: str, marketplace_id: str, conversion_direction: str) -> Dict[str, Any]:
        return self.client.convert_amazon_asin(identifier, marketplace_id, conversion_direction)