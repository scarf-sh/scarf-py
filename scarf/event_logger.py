import os
import requests
from typing import Dict, Any, Optional
from .version import __version__

class ScarfEventLogger:
    """A client for sending telemetry events to Scarf."""
    
    SIMPLE_TYPES = (str, int, float, bool, type(None))
    DEFAULT_TIMEOUT = 3.0  # 3 seconds
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: Optional[float] = None):
        """Initialize the Scarf event logger.
        
        Args:
            api_key: Your Scarf API key (optional, defaults to SCARF_API_KEY environment variable)
            base_url: The base URL for the Scarf API (optional, defaults to SCARF_BASE_URL environment variable)
            timeout: Default timeout in seconds for API calls (optional, default: 3.0)
            
        Raises:
            ValueError: If neither api_key parameter nor SCARF_API_KEY environment variable is set
        """
        self.api_key = api_key or os.environ.get('SCARF_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either through api_key parameter or SCARF_API_KEY environment variable")
            
        self.base_url = (base_url or os.environ.get('SCARF_BASE_URL', "https://scarf.sh/api/v1")).rstrip('/')
        self.timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': f'scarf-py/{__version__}'
        })

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
                raise ValueError(
                    f"Property '{key}' has invalid type {type(value)}. "
                    f"Only simple types are allowed: {', '.join(t.__name__ for t in self.SIMPLE_TYPES)}"
                )

    def log_event(self, properties: Dict[str, Any], timeout: Optional[float] = None) -> Optional[bool]:
        """Log a telemetry event to Scarf.
        
        Args:
            properties: Properties to include with the event.
                       All values must be simple types (str, int, float, bool, None).
                       For example: {'event': 'package_download', 'package': 'scarf', 'version': '1.0.0'}
            timeout: Optional timeout in seconds for this specific API call.
                    Overrides the default timeout set in the constructor.
            
        Returns:
            True if the event was sent successfully, None if analytics are disabled
            
        Raises:
            ValueError: If any property value is not a simple type
            requests.exceptions.RequestException: If the request fails or times out
        """
        if self._check_do_not_track():
            return None
            
        if properties:
            self._validate_properties(properties)
        
        response = self.session.post(
            f'{self.base_url}',
            params=properties,
            timeout=timeout if timeout is not None else self.timeout
        )
        response.raise_for_status()
        return True