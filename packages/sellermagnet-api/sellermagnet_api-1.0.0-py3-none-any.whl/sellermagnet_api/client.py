import requests
from typing import Dict, Any, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .exceptions import SellerMagnetException, AuthenticationError, InvalidParameterError, APIError

logger = logging.getLogger(__name__)


class SellerMagnetClient:
    """Client for interacting with the SellerMagnet API for Amazon data and pipeline management."""

    BASE_URL = "https://sellermagnet-api.com/api"  # Official API base URL from sellermagnet-api.com

    def __init__(self, api_key: str, base_url: Optional[str] = None, timeout: int = 30, retries: int = 3):
        """
        Initialize the SellerMagnet API client.

        Args:
            api_key (str): The API key for authentication.
            base_url (str, optional): The base URL for the API. Defaults to BASE_URL.
            timeout (int): Request timeout in seconds. Defaults to 30.
            retries (int): Number of retry attempts for failed requests. Defaults to 3.

        Raises:
            ValueError: If api_key is empty or None.
        """
        if not api_key:
            raise ValueError("API key is required")
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "SellerMagnetClient/1.0.0"})

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None,
                 data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the SellerMagnet API with retry logic.

        Args:
            method (str): HTTP method (GET, POST, etc.).
            endpoint (str): API endpoint path (e.g., '/amazon-product-lookup').
            params (Dict[str, Any], optional): Query parameters.
            data (Dict[str, Any], optional): Request body data.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            AuthenticationError: If the API key is invalid or insufficient credits.
            InvalidParameterError: If required parameters are missing or invalid.
            APIError: For other API-related errors.
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key

        try:
            response = self.session.request(method, url, params=params, json=data, timeout=self.timeout)
            response.raise_for_status()
            result = response.json()

            if not result.get("success"):
                error_message = result.get("message", "Unknown error")
                error_code = result.get("error", "Unknown")
                if response.status_code == 401:
                    raise AuthenticationError(error_message)
                elif response.status_code == 400:
                    raise InvalidParameterError(error_message)
                else:
                    raise APIError(f"{error_code}: {error_message}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise APIError(f"Request failed: {str(e)}")

    # Amazon Product-related methods
    def get_amazon_product_statistics(self, asin: str, marketplace_id: str, graphs: bool = False) -> Dict[str, Any]:
        """
        Retrieve detailed statistics for an Amazon product.

        Args:
            asin (str): Product ASIN (e.g., 'B08N5WRWNW').
            marketplace_id (str): Marketplace ID (e.g., 'A1PA6795UKMFR9').
            graphs (bool): Whether to generate visual graphs for history data.

        Returns:
            Dict[str, Any]: Product statistics data.
        """
        params = {"asin": asin, "marketplaceId": marketplace_id}
        if graphs:
            params["graph_generation"] = True
        return self._request("GET", "/amazon-product-statistics", params=params)

    def get_amazon_product(self, asin: str, marketplace_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed product information for a given ASIN.

        Args:
            asin (str): Product ASIN.
            marketplace_id (str): Marketplace ID.

        Returns:
            Dict[str, Any]: Product details.
        """
        params = {"asin": asin, "marketplaceId": marketplace_id}
        return self._request("GET", "/amazon-product-lookup", params=params)

    def get_amazon_product_offers(self, asin: str, marketplace_id: str, geo_location: Optional[str] = None) -> Dict[
        str, Any]:
        """
        List offers for an Amazon product.

        Args:
            asin (str): Product ASIN.
            marketplace_id (str): Marketplace ID.
            geo_location (str, optional): Geo location ZIP code.

        Returns:
            Dict[str, Any]: Product offers data.
        """
        params = {"asin": asin, "marketplaceId": marketplace_id}
        if geo_location:
            params["geo_location"] = geo_location
        return self._request("GET", "/amazon-product-offers", params=params)

    def get_amazon_product_estimated_sales(self, asin: str, marketplace_id: str) -> Dict[str, Any]:
        """
        Retrieve estimated sales data for an Amazon product.

        Args:
            asin (str): Product ASIN.
            marketplace_id (str): Marketplace ID.

        Returns:
            Dict[str, Any]: Estimated sales data.
        """
        params = {"asin": asin, "marketplaceId": marketplace_id}
        return self._request("GET", "/amazon-product-search-estimated-sells", params=params)

    def convert_amazon_asin(self, identifier: str, marketplace_id: str, conversion_direction: str) -> Dict[str, Any]:
        """
        Convert between ASIN and EAN identifiers.

        Args:
            identifier (str): ASIN or EAN to convert.
            marketplace_id (str): Marketplace ID.
            conversion_direction (str): 'asin-to-ean' or 'ean-to-asin'.

        Returns:
            Dict[str, Any]: Conversion result.
        """
        if conversion_direction not in ["asin-to-ean", "ean-to-asin"]:
            raise InvalidParameterError("Invalid conversion_direction. Must be 'asin-to-ean' or 'ean-to-asin'")
        params = {"asin": identifier, "marketplaceId": marketplace_id, "conversion_direction": conversion_direction}
        return self._request("GET", "/amazon-asin-converter", params=params)

    # Amazon Seller-related methods
    def get_amazon_seller_reviews(self, seller_id: str, marketplace_id: str) -> Dict[str, Any]:
        """
        Fetch review details for a specific Amazon seller.

        Args:
            seller_id (str): Seller ID.
            marketplace_id (str): Marketplace ID.

        Returns:
            Dict[str, Any]: Seller review data.
        """
        params = {"sellerId": seller_id, "marketplaceId": marketplace_id}
        return self._request("GET", "/amazon-seller-review", params=params)

    # Amazon Search-related methods
    def search_amazon_products(self, query: str, marketplace_id: str, count: int = 30) -> Dict[str, Any]:
        """
        Search Amazon products by keyword.

        Args:
            query (str): Search query (e.g., 'phone').
            marketplace_id (str): Marketplace ID.
            count (int): Number of results (max 50, default 30).

        Returns:
            Dict[str, Any]: Search results.
        """
        if count > 50:
            raise InvalidParameterError("Count must not exceed 50")
        params = {"q": query, "marketplaceId": marketplace_id, "count": count}
        return self._request("GET", "/amazon-search", params=params)

    # Amazon Deals-related methods
    def get_amazon_bestsellers(self, category_id: str, marketplace_id: str, count: int = 30) -> Dict[str, Any]:
        """
        Fetch top-selling products in a specific Amazon category.

        Args:
            category_id (str): Category ID (e.g., 'electronics').
            marketplace_id (str): Marketplace ID.
            count (int): Number of results (max 50, default 30).

        Returns:
            Dict[str, Any]: Bestseller data.
        """
        if count > 50:
            raise InvalidParameterError("Count must not exceed 50")
        params = {"category_id": category_id, "marketplaceId": marketplace_id, "count": count}
        return self._request("GET", "/amazon-bestsellers", params=params)

    def get_amazon_deals_categories(self, marketplace_id: str) -> Dict[str, Any]:
        """
        List categories with active Amazon deals.

        Args:
            marketplace_id (str): Marketplace ID.

        Returns:
            Dict[str, Any]: Deals categories.
        """
        params = {"marketplaceId": marketplace_id}
        return self._request("GET", "/amazon-deals-categories", params=params)

    # Amazon Marketplace-related methods
    def get_amazon_marketplaces(self) -> Dict[str, Any]:
        """
        Retrieve a list of supported Amazon marketplaces.

        Returns:
            Dict[str, Any]: Marketplaces data.
        """
        return self._request("GET", "/amazon-get-marketplaces")

    # Pipeline-related methods
    def create_pipeline(self, pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new data pipeline.

        Args:
            pipeline_data (Dict[str, Any]): Pipeline configuration data.

        Returns:
            Dict[str, Any]: Pipeline creation response.
        """
        return self._request("POST", "/api/pipelines", data=pipeline_data)

    def get_pipelines(self) -> Dict[str, Any]:
        """
        Retrieve all pipelines for the authenticated user.

        Returns:
            Dict[str, Any]: List of pipelines.
        """
        return self._request("GET", "/api/pipelines")

    def update_pipeline(self, pipeline_id: str, active: bool) -> Dict[str, Any]:
        """
        Update a pipeline's active status.

        Args:
            pipeline_id (str): Pipeline ID.
            active (bool): Whether the pipeline should be active.

        Returns:
            Dict[str, Any]: Update response.
        """
        data = {"active": active}
        return self._request("PATCH", f"/api/pipelines/{pipeline_id}", data=data)

    def delete_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Delete a pipeline.

        Args:
            pipeline_id (str): Pipeline ID.

        Returns:
            Dict[str, Any]: Deletion response.
        """
        return self._request("DELETE", f"/api/pipelines/{pipeline_id}")

    def get_pipeline_logs(self, pipeline_id: str) -> Dict[str, Any]:
        """
        Retrieve logs for a specific pipeline.

        Args:
            pipeline_id (str): Pipeline ID.

        Returns:
            Dict[str, Any]: Pipeline logs.
        """
        return self._request("GET", f"/api/pipeline-logs/{pipeline_id}")