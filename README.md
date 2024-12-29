# scarf-py

A Python client for sending telemetry events to Scarf.

## Installation

```bash
pip install scarf
```

## Usage

```python
from scarf import ScarfEventLogger

# Initialize with required endpoint URL
logger = ScarfEventLogger(
    endpoint_url="https://your-scarf-endpoint.com",
    timeout=5.0  # Optional: Set default timeout in seconds (default: 3.0)
)

# Send an event with properties
success = logger.log_event({
    "event": "package_download",
    "package": "scarf",
    "version": "1.0.0"
})

# Send an event with a custom timeout
success = logger.log_event(
    properties={"event": "custom_event"},
    timeout=1.0  # Override default timeout for this call
)

# Empty properties are allowed
success = logger.log_event({})
```

## Configuration

The client can be configured through environment variables:

- `DO_NOT_TRACK=1`: Disable analytics
- `SCARF_NO_ANALYTICS=1`: Disable analytics (alternative)

## Features

- Simple API for sending telemetry events
- Environment variable configuration
- Configurable timeouts (default: 3 seconds)
- Automatically reespects Do Not Track settings

## Development

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT