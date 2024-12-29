#!/usr/bin/env python3

"""
Example script for sending test events to Scarf.

To run this example:
1. Set environment variables:
   export SCARF_API_KEY="your-api-key"
   export SCARF_BASE_URL="https://avi.gateway.scarf.sh/test-scarf-py"  # Optional

2. Install the package in development mode:
   pip install -e .

3. Run this script:
   python examples/send_test_event.py
"""

import os

from requests.exceptions import RequestException

from scarf import ScarfEventLogger


def main():
    try:
        # Check for required environment variable
        if not os.environ.get('SCARF_API_KEY'):
            print("Error: SCARF_API_KEY environment variable is not set")
            return 1

        # Initialize the logger using environment variables
        logger = ScarfEventLogger()

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
