import os
import time
from typing import Any, Dict, Optional

import requests

from .version import __version__


class ScarfEventLogger:
    """A client for sending telemetry events to Scarf."""

    SIMPLE_TYPES = (str, int, float, bool, type(None))
    DEFAULT_TIMEOUT = 3.0  # 3 seconds

    def __init__(
        self,
        endpoint_url: str,
        timeout: Optional[float] = None,
        verbose: Optional[bool] = None,
    ):
        """Initialize the Scarf event logger.

        Args:
            endpoint_url: The endpoint URL for the Scarf API
            timeout: Default timeout in seconds for API calls (optional, default: 3.0)
            verbose: Enable verbose logging (optional, defaults to SCARF_VERBOSE env var)

        Raises:
            ValueError: If endpoint_url is not provided or is empty
        """
        if not endpoint_url:
            raise ValueError("endpoint_url must be provided")

        self.endpoint_url = endpoint_url.rstrip('/')
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        self.verbose = (
            verbose if verbose is not None
            else os.environ.get('SCARF_VERBOSE', '').lower() in ('1', 'true')
        )
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'scarf-py/{__version__}'
        })

        if self.verbose:
            print("Scarf Logger Configuration:")
            print(f"  Endpoint URL: {self.endpoint_url}")
            print(f"  Timeout: {self.timeout}s")
            print(f"  User-Agent: {self.session.headers['User-Agent']}")

    @staticmethod
    def _check_do_not_track() -> bool:
        """Check if analytics are disabled via environment variables.

        Returns:
            bool: True if analytics should be disabled, False otherwise
        """
        dnt = os.environ.get('DO_NOT_TRACK', '').lower()
        scarf_no_analytics = os.environ.get('SCARF_NO_ANALYTICS', '').lower()

        return (
            dnt in ('1', 'true') or
            scarf_no_analytics in ('1', 'true')
        )

    def _validate_properties(self, properties: Dict[str, Any]) -> None:
        """Validate that all property values are simple types.

        Args:
            properties: Dictionary of properties to validate

        Raises:
            ValueError: If any property value is not a simple type
        """
        for key, value in properties.items():
            if not isinstance(value, self.SIMPLE_TYPES):
                type_names = ', '.join(t.__name__ for t in self.SIMPLE_TYPES)
                raise ValueError(
                    f"Property '{key}' has invalid type {type(value)}. "
                    f"Only simple types are allowed: {type_names}"
                )

    def log_event(
        self,
        properties: Dict[str, Any],
        timeout: Optional[float] = None,
    ) -> bool:
        """Log a telemetry event to Scarf.

        Args:
            properties: Properties to include with the event.
                All values must be simple types (str, int, float, bool, None).
                Example: {'event': 'download', 'package': 'scarf', 'version': '1.0.0'}
            timeout: Optional timeout in seconds for this specific API call.
                Overrides the default timeout set in the constructor.

        Returns:
            True if the event was sent successfully, False if analytics are disabled

        Raises:
            ValueError: If any property value is not a simple type
            requests.exceptions.RequestException: If the request fails or times out
        """
        if self._check_do_not_track():
            if self.verbose:
                print("Analytics are disabled via environment variables")
            return False

        if properties:
            self._validate_properties(properties)

        if self.verbose:
            print("\nSending event:")
            print(f"  Properties: {properties}")
            print(f"  Timeout: {timeout if timeout is not None else self.timeout}s")

        start_time = time.time()
        try:
            response = self.session.post(
                self.endpoint_url,
                params=properties,
                timeout=timeout if timeout is not None else self.timeout
            )
            response.raise_for_status()

            if self.verbose:
                elapsed = time.time() - start_time
                print(f"\nResponse received in {elapsed:.3f}s:")
                print(f"  Status: {response.status_code}")
                print(f"  URL: {response.url}")
                if response.text:
                    print(f"  Body: {response.text[:1000]}")

            return True

        except Exception as e:
            if self.verbose:
                elapsed = time.time() - start_time
                print(f"\nError after {elapsed:.3f}s:")
                print(f"  {type(e).__name__}: {str(e)}")
            raise
