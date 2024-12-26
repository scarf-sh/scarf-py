import json
import os
import requests
from typing import Dict, Any, Optional, Union
from urllib.parse import urlencode

class ScarfEventLogger:
    """A client for sending telemetry events to Scarf."""
    
    SIMPLE_TYPES = (str, int, float, bool, type(None))
    
    def __init__(self, api_key: str, base_url: str = "https://scarf.sh/api/v1"):
        """Initialize the Scarf event logger.
        
        Args:
            api_key: Your Scarf API key
            base_url: The base URL for the Scarf API (optional)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
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

    def log_event(self, event_type: str, properties: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Log a telemetry event to Scarf.
        
        Args:
            event_type: The type of event being logged
            properties: Additional properties to include with the event (optional).
                       All values must be simple types (str, int, float, bool, None).
            
        Returns:
            The response from the Scarf API as a dictionary, or None if analytics are disabled
            
        Raises:
            ValueError: If any property value is not a simple type
            requests.exceptions.RequestException: If the request fails
        """
        if self._check_do_not_track():
            return None
            
        if not isinstance(event_type, str):
            raise ValueError("event_type must be a string")
            
        params = {'type': event_type}
        if properties:
            self._validate_properties(properties)
            params.update(properties)
        
        response = self.session.post(
            f'{self.base_url}/events',
            params=params
        )
        response.raise_for_status()
        return response.json()