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

from requests.exceptions import RequestException

from scarf import ScarfEventLogger


def main():
    try:
        # Initialize the logger using environment variables
        logger = ScarfEventLogger()

        # Send a test event with two fields
        response = logger.log_event({
            "test_field_1": "hello from scarf-py",
            "test_field_2": 42
        })

        print(f"Response from Scarf: {response}")

    except ValueError as e:
        print(f"Configuration error: {e}")
    except RequestException as e:
        print(f"Error sending event to Scarf: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
