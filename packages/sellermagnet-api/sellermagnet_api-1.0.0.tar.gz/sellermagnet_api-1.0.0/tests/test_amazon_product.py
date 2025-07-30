import unittest
from unittest.mock import patch, Mock
from sellermagnet_api import SellerMagnetClient

class TestAmazonProductEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = SellerMagnetClient(api_key="test-api-key")

    @patch("requests.Session.request")
    def test_get_amazon_product_success(self, mock_request):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": {"productInfo": {"asin": "B0CL61F39H"}}}
        mock_request.return_value = mock_response

        result = self.client.get_amazon_product("B0CL61F39H", "ATVPDKIKX0DER")
        self.assertTrue(result["success"])
        self.assertEqual(result["data"]["productInfo"]["asin"], "B0CL61F39H")

if __name__ == "__main__":
    unittest.main()