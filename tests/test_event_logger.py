import os
import re
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from requests.exceptions import ReadTimeout, Timeout

from scarf import ScarfEventLogger, __version__


class TestScarfEventLogger(unittest.TestCase):
    DEFAULT_ENDPOINT = "https://scarf.sh/api/v1"

    def setUp(self):
        """Reset environment variables before each test."""
        # Store original environment variables
        self.original_env = {
            'DO_NOT_TRACK': os.environ.get('DO_NOT_TRACK'),
            'SCARF_NO_ANALYTICS': os.environ.get('SCARF_NO_ANALYTICS'),
            'SCARF_VERBOSE': os.environ.get('SCARF_VERBOSE'),
        }

        # Clear environment variables
        for var in ['DO_NOT_TRACK', 'SCARF_NO_ANALYTICS', 'SCARF_VERBOSE']:
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
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
        self.assertIsInstance(logger, ScarfEventLogger)
        self.assertEqual(logger.endpoint_url, self.DEFAULT_ENDPOINT)
        self.assertEqual(logger.timeout, ScarfEventLogger.DEFAULT_TIMEOUT)
        self.assertFalse(logger.verbose)

    def test_initialization_validation(self):
        """Test that initialization fails with invalid endpoint_url."""
        with self.assertRaises(ValueError):
            ScarfEventLogger(endpoint_url="")
        with self.assertRaises(ValueError):
            ScarfEventLogger(endpoint_url=None)

    def test_verbose_from_env(self):
        """Test that verbose mode can be enabled via environment variable."""
        os.environ['SCARF_VERBOSE'] = '1'
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
        self.assertTrue(logger.verbose)

        os.environ['SCARF_VERBOSE'] = 'true'
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
        self.assertTrue(logger.verbose)

        os.environ['SCARF_VERBOSE'] = '0'
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
        self.assertFalse(logger.verbose)

    def test_verbose_override(self):
        """Test that verbose parameter overrides environment variable."""
        os.environ['SCARF_VERBOSE'] = '1'
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, verbose=False)
        self.assertFalse(logger.verbose)

        os.environ['SCARF_VERBOSE'] = '0'
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, verbose=True)
        self.assertTrue(logger.verbose)

    def test_custom_timeout(self):
        """Test that we can initialize with a custom timeout."""
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, timeout=5.0)
        self.assertEqual(logger.timeout, 5.0)

    def test_custom_endpoint_url(self):
        """Test that we can initialize with a custom endpoint URL."""
        custom_url = "https://custom.scarf.sh/api/v1"
        logger = ScarfEventLogger(endpoint_url=custom_url)
        self.assertEqual(logger.endpoint_url, custom_url)

    def test_validate_properties_simple_types(self):
        """Test that simple type properties are accepted."""
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)

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
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)

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
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response

        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
        result = logger.log_event({})

        self.assertTrue(result)
        mock_session.return_value.post.assert_called_with(
            self.DEFAULT_ENDPOINT,
            params={},
            timeout=3.0
        )

    @patch('requests.Session')
    def test_request_timeout(self, mock_session):
        """Test that requests timeout after the specified duration."""
        mock_session.return_value.post.side_effect = Timeout("Request timed out")

        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, timeout=1)

        with self.assertRaises(Timeout):
            logger.log_event({"event": "test"})

        mock_session.return_value.post.assert_called_with(
            self.DEFAULT_ENDPOINT,
            params={"event": "test"},
            timeout=1
        )

    @patch('requests.Session')
    def test_request_timeout_override(self, mock_session):
        """Test that per-request timeout overrides the default."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response

        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, timeout=3.0)
        result = logger.log_event({"event": "test"}, timeout=1.0)

        self.assertTrue(result)
        mock_session.return_value.post.assert_called_with(
            self.DEFAULT_ENDPOINT,
            params={"event": "test"},
            timeout=1.0
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
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response

        test_cases = [
            ('1', False),
            ('true', False),
            ('TRUE', False),
            ('0', True),
            ('false', True),
            ('', True),
        ]

        test_properties = {'event': 'test', 'value': 42}

        for value, should_send in test_cases:
            os.environ['DO_NOT_TRACK'] = value
            logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
            result = logger.log_event(test_properties)

            if should_send:
                self.assertTrue(result)
                mock_session.return_value.post.assert_called_with(
                    self.DEFAULT_ENDPOINT,
                    params=test_properties,
                    timeout=3.0
                )
            else:
                self.assertFalse(result)
                mock_session.return_value.post.assert_not_called()

            # Reset mock for next iteration
            mock_session.return_value.post.reset_mock()

    @patch('requests.Session')
    def test_scarf_no_analytics_env_var(self, mock_session):
        """Test that SCARF_NO_ANALYTICS environment variable disables analytics."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response

        test_cases = [
            ('1', False),
            ('true', False),
            ('TRUE', False),
            ('0', True),
            ('false', True),
            ('', True),
        ]

        test_properties = {'event': 'test', 'value': 42}

        for value, should_send in test_cases:
            os.environ['SCARF_NO_ANALYTICS'] = value
            logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
            result = logger.log_event(test_properties)

            if should_send:
                self.assertTrue(result)
                mock_session.return_value.post.assert_called_with(
                    self.DEFAULT_ENDPOINT,
                    params=test_properties,
                    timeout=3.0
                )
            else:
                self.assertFalse(result)
                mock_session.return_value.post.assert_not_called()

            # Reset mock for next iteration
            mock_session.return_value.post.reset_mock()

    @patch('requests.Session')
    def test_env_var_precedence(self, mock_session):
        """Test that either environment variable can disable analytics."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.post.return_value = mock_response

        os.environ['DO_NOT_TRACK'] = 'false'
        os.environ['SCARF_NO_ANALYTICS'] = 'true'
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)

        result = logger.log_event({'event': 'test'})
        self.assertFalse(result)
        mock_session.return_value.post.assert_not_called()

    @patch('requests.Session')
    def test_request_timeout_behavior(self, mock_session):
        """Test that requests actually time out after the specified duration."""
        def mock_post(*args, **kwargs):
            if kwargs.get('timeout', float('inf')) < 2:
                raise ReadTimeout("Request timed out")
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        mock_session.return_value.post.side_effect = mock_post

        # Should timeout (1s timeout, requires 2s)
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, timeout=1)
        with self.assertRaises(ReadTimeout):
            logger.log_event({"event": "test"})

        # Should succeed (3s timeout, requires 2s)
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, timeout=3)
        result = logger.log_event({"event": "test"})
        self.assertTrue(result)

        # Should timeout with per-request override (3s default, 1s override)
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT, timeout=3)
        with self.assertRaises(ReadTimeout):
            logger.log_event({"event": "test"}, timeout=1)

        # Verify the last timeout value was passed correctly
        mock_session.return_value.post.assert_called_with(
            self.DEFAULT_ENDPOINT,
            params={"event": "test"},
            timeout=1
        )

    @patch('requests.Session')
    @patch('builtins.print')
    def test_verbose_output(self, mock_print, mock_session):
        """Test that verbose mode logs the expected information."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = self.DEFAULT_ENDPOINT
        mock_response.text = "Success"
        mock_session.return_value.post.return_value = mock_response

        logger = ScarfEventLogger(
            endpoint_url=self.DEFAULT_ENDPOINT,
            timeout=1.0,
            verbose=True
        )

        # Check initialization logging
        mock_print.assert_any_call("Scarf Logger Configuration:")
        mock_print.assert_any_call(f"  Endpoint URL: {self.DEFAULT_ENDPOINT}")
        mock_print.assert_any_call("  Timeout: 1.0s")

        # Reset mock for event logging
        mock_print.reset_mock()

        # Log an event
        test_properties = {"test": "value"}
        logger.log_event(test_properties)

        # Check event logging
        mock_print.assert_any_call("\nSending event:")
        mock_print.assert_any_call("  Properties: {'test': 'value'}")
        mock_print.assert_any_call("  Timeout: 1.0s")

        # Check response logging - using regex to match elapsed time
        elapsed_pattern = re.compile(r"\nResponse received in \d+\.\d+s:")
        elapsed_calls = [
            call for call in mock_print.call_args_list
            if call[0] and isinstance(call[0][0], str) and elapsed_pattern.match(call[0][0])
        ]
        self.assertEqual(len(elapsed_calls), 1, "Expected one elapsed time log")

        mock_print.assert_any_call("  Status: 200")
        mock_print.assert_any_call("  URL: https://scarf.sh/api/v1")
        mock_print.assert_any_call("  Body: Success")

    def test_version_consistency(self):
        """Test that version is consistent with pyproject.toml."""
        # Read version from pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            version_match = re.search(r'version\s*=\s*"(.*?)"', content)
            self.assertIsNotNone(version_match, "Could not find version in pyproject.toml")
            version = version_match.group(1)

        # Check that __version__ matches
        self.assertEqual(__version__, version)

        # Check that User-Agent header uses correct version
        logger = ScarfEventLogger(endpoint_url=self.DEFAULT_ENDPOINT)
        self.assertEqual(
            logger.session.headers['User-Agent'],
            f'scarf-py/{version}'
        )

if __name__ == '__main__':
    unittest.main()
