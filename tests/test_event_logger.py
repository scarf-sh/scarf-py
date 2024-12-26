import unittest
from scarf import ScarfEventLogger

class TestScarfEventLogger(unittest.TestCase):
    def test_initialization(self):
        """Test that we can create a ScarfEventLogger instance."""
        logger = ScarfEventLogger(api_key="test-api-key")
        self.assertIsInstance(logger, ScarfEventLogger)
        self.assertEqual(logger.api_key, "test-api-key")
        self.assertEqual(logger.base_url, "https://scarf.sh/api/v1")

    def test_custom_base_url(self):
        """Test that we can initialize with a custom base URL."""
        custom_url = "https://custom.scarf.sh/api/v1"
        logger = ScarfEventLogger(api_key="test-api-key", base_url=custom_url)
        self.assertEqual(logger.base_url, custom_url)

if __name__ == '__main__':
    unittest.main() 