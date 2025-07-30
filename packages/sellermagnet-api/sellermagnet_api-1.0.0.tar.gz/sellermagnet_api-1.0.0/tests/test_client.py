import unittest
from unittest.mock import patch, Mock
from sellermagnet_api import SellerMagnetClient, AuthenticationError, InvalidParameterError, APIError

class TestSellerMagnetClient(unittest.TestCase):
    def setUp(self):
        self.client = SellerMagnetClient(api_key="test-api-key")

    @patch("requests.Session.request")
    def test_get_amazon_product_statistics_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {"asin": "B0CLTBHXWQ"}}
        mock_request.return_value = mock_response

        result = self.client.get_amazon_product_statistics("B0CLTBHXWQ", "A1PA6795UKMFR9")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["asin"], "B0CLTBHXWQ")

    @patch("requests.Session.request")
    def test_get_amazon_product_statistics_auth_error(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"success": False, "error": "Unauthorized", "message": "Invalid API key"}
        mock_request.return_value = mock_response

        with self.assertRaises(AuthenticationError):
            self.client.get_amazon_product_statistics("B0CLTBHXWQ", "A1PA6795UKMFR9")

    def test_invalid_api_key(self):
        with self.assertRaises(ValueError):
            SellerMagnetClient(api_key="")

if __name__ == "__main__":
    unittest.main()