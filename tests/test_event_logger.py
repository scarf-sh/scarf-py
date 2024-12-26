import unittest
import os
from unittest.mock import patch, MagicMock
from scarf import ScarfEventLogger

class TestScarfEventLogger(unittest.TestCase):
    def setUp(self):
        """Reset environment variables before each test."""
        # Store original environment variables
        self.original_env = {
            'DO_NOT_TRACK': os.environ.get('DO_NOT_TRACK'),
            'SCARF_NO_ANALYTICS': os.environ.get('SCARF_NO_ANALYTICS')
        }
        
        # Clear environment variables
        for var in ['DO_NOT_TRACK', 'SCARF_NO_ANALYTICS']:
            if var in os.environ:
                del os.environ[var]

    def tearDown(self):
        """Restore original environment variables after each test."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

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
        
    def test_validate_properties_simple_types(self):
        """Test that simple type properties are accepted."""
        logger = ScarfEventLogger(api_key="test-api-key")
        
        # These should not raise any errors
        logger._validate_properties({
            'string': 'value',
            'integer': 42,
            'float': 3.14,
            'bool': True,
            'none': None
        })
        
    def test_validate_properties_complex_types(self):
        """Test that complex type properties are rejected."""
        logger = ScarfEventLogger(api_key="test-api-key")
        
        invalid_properties = [
            ({'list': [1, 2, 3]}, "list"),
            ({'dict': {'key': 'value'}}, "dict"),
            ({'tuple': (1, 2)}, "tuple"),
            ({'set': {1, 2}}, "set"),
        ]
        
        for props, key in invalid_properties:
            with self.assertRaises(ValueError) as cm:
                logger._validate_properties(props)
            self.assertIn(key, str(cm.exception))
            self.assertIn("simple types are allowed", str(cm.exception))

    @patch('requests.Session')
    def test_empty_properties_allowed(self, mock_session):
        """Test that empty properties dictionary is allowed."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.post.return_value = mock_response
        
        logger = ScarfEventLogger(api_key="test-api-key")
        result = logger.log_event({})
        
        self.assertEqual(result, {"status": "success"})
        mock_session.return_value.post.assert_called_with(
            'https://scarf.sh/api/v1',
            params={}
        )

    def test_check_do_not_track(self):
        """Test the do-not-track pure function with various environment values."""
        test_cases = [
            # (DO_NOT_TRACK, SCARF_NO_ANALYTICS, expected)
            ('1', '', True),
            ('true', '', True),
            ('TRUE', '', True),
            ('0', '', False),
            ('false', '', False),
            ('', '1', True),
            ('', 'true', True),
            ('', 'TRUE', True),
            ('', '0', False),
            ('', 'false', False),
            ('', '', False),
            ('false', 'true', True),
            ('true', 'false', True),
        ]
        
        for dnt, sna, expected in test_cases:
            if dnt:
                os.environ['DO_NOT_TRACK'] = dnt
            elif 'DO_NOT_TRACK' in os.environ:
                del os.environ['DO_NOT_TRACK']
                
            if sna:
                os.environ['SCARF_NO_ANALYTICS'] = sna
            elif 'SCARF_NO_ANALYTICS' in os.environ:
                del os.environ['SCARF_NO_ANALYTICS']
            
            self.assertEqual(
                ScarfEventLogger._check_do_not_track(),
                expected,
                f"Failed with DO_NOT_TRACK={dnt}, SCARF_NO_ANALYTICS={sna}"
            )

    @patch('requests.Session')
    def test_do_not_track_env_var(self, mock_session):
        """Test that DO_NOT_TRACK environment variable disables analytics."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.post.return_value = mock_response
        
        test_cases = [
            ('1', True),
            ('true', True),
            ('TRUE', True),
            ('0', False),
            ('false', False),
            ('', False),
        ]
        
        test_properties = {'event': 'test', 'value': 42}
        
        for value, expected in test_cases:
            os.environ['DO_NOT_TRACK'] = value
            logger = ScarfEventLogger(api_key="test-api-key")
            result = logger.log_event(test_properties)
            
            if expected:
                self.assertIsNone(result)
                mock_session.return_value.post.assert_not_called()
            else:
                self.assertEqual(result, {"status": "success"})
                mock_session.return_value.post.assert_called_with(
                    'https://scarf.sh/api/v1',
                    params=test_properties
                )
            
            # Reset mock for next iteration
            mock_session.return_value.post.reset_mock()

    @patch('requests.Session')
    def test_scarf_no_analytics_env_var(self, mock_session):
        """Test that SCARF_NO_ANALYTICS environment variable disables analytics."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.post.return_value = mock_response
        
        test_cases = [
            ('1', True),
            ('true', True),
            ('TRUE', True),
            ('0', False),
            ('false', False),
            ('', False),
        ]
        
        test_properties = {'event': 'test', 'value': 42}
        
        for value, expected in test_cases:
            os.environ['SCARF_NO_ANALYTICS'] = value
            logger = ScarfEventLogger(api_key="test-api-key")
            result = logger.log_event(test_properties)
            
            if expected:
                self.assertIsNone(result)
                mock_session.return_value.post.assert_not_called()
            else:
                self.assertEqual(result, {"status": "success"})
                mock_session.return_value.post.assert_called_with(
                    'https://scarf.sh/api/v1',
                    params=test_properties
                )
            
            # Reset mock for next iteration
            mock_session.return_value.post.reset_mock()

    @patch('requests.Session')
    def test_env_var_precedence(self, mock_session):
        """Test that either environment variable can disable analytics."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_session.return_value.post.return_value = mock_response
        
        os.environ['DO_NOT_TRACK'] = 'false'
        os.environ['SCARF_NO_ANALYTICS'] = 'true'
        logger = ScarfEventLogger(api_key="test-api-key")
        
        result = logger.log_event({'event': 'test'})
        self.assertIsNone(result)
        mock_session.return_value.post.assert_not_called()

if __name__ == '__main__':
    unittest.main() 