#!/usr/bin/env python3

"""
Example script for sending test events to Scarf.

To run this example:
1. Install the package in development mode:
   pip install -e .

2. Run this script:
   python examples/send_test_event.py

Environment variables:
    SCARF_VERBOSE=1: Enable verbose logging
"""

from requests.exceptions import RequestException

from scarf import ScarfEventLogger


def main():
    try:
        # Initialize the logger with a test endpoint and verbose mode
        logger = ScarfEventLogger(
            endpoint_url="https://avi.gateway.scarf.sh/test-scarf-py",
            verbose=True  # Enable verbose logging
        )

        # Send a test event with two fields
        success = logger.log_event({
            "test_field_1": "hello from scarf-py",
            "test_field_2": 42
        })

        if not success:
            print("Analytics are disabled via environment variables")
            return 0

        print("Successfully sent event to Scarf")
        return 0

    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1
    except RequestException as e:
        print(f"Error sending event to Scarf: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
