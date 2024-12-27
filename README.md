# Scarf-py

Python bindings for [Scarf](https://scarf.sh) telemetry. This package provides a simple and ergonomic way to send telemetry events to Scarf.

## Installation

```bash
pip install scarf
```

## Usage

```python
from scarf import ScarfEventLogger

# Initialize the logger with your API key and optional timeout
logger = ScarfEventLogger(
    api_key="your-api-key",
    base_url="https://your-scarf-endpoint.com/your-endpoint-id",
    timeout=3.0  # Optional: default timeout of 3 seconds
)

# Log an event with properties
logger.log_event({
    "event": "package_download",
    "version": "1.0.0",
    "platform": "linux"
})

# Log a simple event with no properties
logger.log_event({})

# Log an event with a custom timeout
logger.log_event(
    {"event": "slow_operation"},
    timeout=5.0  # Override timeout for this specific call
)
```

## API Reference

### ScarfEventLogger

#### `__init__(api_key: str, base_url: str = "https://api.scarf.sh/api/v1", timeout: Optional[float] = None)`

Initialize a new Scarf event logger.

- `api_key`: Your Scarf API key
- `base_url`: The base URL for the Scarf API (optional)
- `timeout`: Default timeout in seconds for API calls (optional, default: 3.0)

#### `log_event(properties: Dict[str, Any], timeout: Optional[float] = None) -> Optional[Dict[str, Any]]`

Log a telemetry event to Scarf.

- `properties`: Dictionary of properties to include with the event. All values must be simple types (str, int, float, bool, None).
- `timeout`: Optional timeout in seconds for this specific API call. Overrides the default timeout set in the constructor.

Returns the response from the Scarf API as a dictionary. Returns None if analytics are disabled via environment variables.

### Environment Variables

Analytics can be disabled by setting either of these environment variables:
- `DO_NOT_TRACK=1` or `DO_NOT_TRACK=true`
- `SCARF_NO_ANALYTICS=1` or `SCARF_NO_ANALYTICS=true`

## License

MIT License 