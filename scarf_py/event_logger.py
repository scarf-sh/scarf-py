import json
import requests
from typing import Dict, Any, Optional

class ScarfEventLogger:
    """A client for sending telemetry events to Scarf."""
    
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
            'Content-Type': 'application/json'
        })

    def log_event(self, event_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log a telemetry event to Scarf.
        
        Args:
            event_type: The type of event being logged
            properties: Additional properties to include with the event (optional)
            
        Returns:
            The response from the Scarf API as a dictionary
            
        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        payload = {
            'type': event_type,
            'properties': properties or {}
        }
        
        response = self.session.post(
            f'{self.base_url}/events',
            data=json.dumps(payload)
        )
        response.raise_for_status()
        return response.json()