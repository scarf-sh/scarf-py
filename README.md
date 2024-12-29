# scarf-py

A Python client for sending telemetry events to Scarf.

## Installation

```bash
pip install scarf-sdk
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
- `SCARF_VERBOSE=1`: Enable verbose logging

## Features

- Simple API for sending telemetry events
- Environment variable configuration
- Configurable timeouts (default: 3 seconds)
- Support for empty payloads
- Automatic User-Agent header (`scarf-sdk/VERSION`)
- Respects Do Not Track settings
- Verbose logging mode for debugging

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

## Publishing

To publish a new version:

1. Update version in `setup.py`
2. Create and push a new tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

The CI workflow will automatically build and publish to PyPI when a new version tag is pushed.

## License

Apache 2.0