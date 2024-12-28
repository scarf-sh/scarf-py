#!/usr/bin/env python3

"""
Example script for sending test events to Scarf.

To run this example:
1. Install the package in development mode:
   pip install -e .

2. Set environment variables:
   export SCARF_API_KEY="your-api-key"
   export SCARF_BASE_URL="https://your-scarf-endpoint.com"

3. Run this script:
   python examples/send_test_event.py
"""

import os
from scarf import ScarfEventLogger
from requests.exceptions import RequestException

def main():
    try:
        # Initialize the logger (will use environment variables)
        logger = ScarfEventLogger()

        test_payload = {
            "test_field_1": "hello from scarf-py",
            "test_field_2": 43
        }

        # Send a test event with two fields
        success = logger.log_event(test_payload)
        
        if success:
            print("Successfully sent event to Scarf", test_payload)
        else:
            print("Analytics are disabled via environment variables")
        
    except ValueError as e:
        print(f"Configuration error: {e}")
    except RequestException as e:
        print(f"Error sending event to Scarf: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main() 