import unittest
from unittest.mock import patch, Mock
from sellermagnet_api import SellerMagnetClient

class TestAmazonSearchEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = SellerMagnetClient(api_key="test-api-key")

    @patch("requests.Session.request")
    def test_search_amazon_products_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {"searchResults": [{"asin": "B0D1N3V2FF"}]}}
        mock_request.return_value = mock_response

        result = self.client.search_amazon_products("raspberry pi", "A1PA6795UKMFR9", count=10)
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["searchResults"][0]["asin"], "B0D1N3V2FF")

    def test_search_amazon_products_invalid_count(self):
        with self.assertRaises(InvalidParameterError):
            self.client.search_amazon_products("raspberry pi", "A1PA6795UKMFR9", count=51)

if __name__ == "__main__":
    unittest.main()