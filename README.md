# scarf-py

Python bindings for [Scarf](https://scarf.sh) telemetry. This package provides a simple and ergonomic way to send telemetry events to Scarf.

## Installation

```bash
pip install scarf-py
```

## Usage

```python
from scarf_py import ScarfEventLogger

# Initialize the logger with your API key
logger = ScarfEventLogger(api_key="your-api-key")

# Log a simple event
logger.log_event("package_download")

# Log an event with additional properties
logger.log_event("package_install", {
    "package_name": "my-package",
    "version": "1.0.0",
    "platform": "linux"
})
```

## API Reference

### ScarfEventLogger

#### `__init__(api_key: str, base_url: str = "https://api.scarf.sh/api/v1")`

Initialize a new Scarf event logger.

- `api_key`: Your Scarf API key
- `base_url`: The base URL for the Scarf API (optional)

#### `log_event(event_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

Log a telemetry event to Scarf.

- `event_type`: The type of event being logged
- `properties`: Additional properties to include with the event (optional)

Returns the response from the Scarf API as a dictionary. Raises `requests.exceptions.RequestException` if the request fails.

## License

MIT License 