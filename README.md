# Scarf-py

Python bindings for [Scarf](https://scarf.sh) telemetry. This package provides a simple and ergonomic way to send telemetry events to Scarf.

## Installation

```bash
pip install scarf
```

## Usage

```python
from scarf import ScarfEventLogger

# Initialize the logger with your API key
logger = ScarfEventLogger(api_key="your-api-key", base_url="https://your-scarf-endpoint.com/your-endpoint-id")

# Log an event with properties
logger.log_event({
    "event": "package_download",
    "version": "1.0.0",
    "platform": "linux"
})

# Log a simple event with no properties
logger.log_event({})
```

## API Reference

### ScarfEventLogger

#### `__init__(api_key: str, base_url: str = "https://api.scarf.sh/api/v1")`

Initialize a new Scarf event logger.

- `api_key`: Your Scarf API key
- `base_url`: The base URL for the Scarf API (optional)

#### `log_event(properties: Dict[str, Any]) -> Optional[Dict[str, Any]]`

Log a telemetry event to Scarf.

- `properties`: Dictionary of properties to include with the event. All values must be simple types (str, int, float, bool, None).

Returns the response from the Scarf API as a dictionary. Returns None if analytics are disabled via environment variables.

### Environment Variables

Analytics can be disabled by setting either of these environment variables:
- `DO_NOT_TRACK=1` or `DO_NOT_TRACK=true`
- `SCARF_NO_ANALYTICS=1` or `SCARF_NO_ANALYTICS=true`

## License

MIT License 