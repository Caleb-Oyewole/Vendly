#!/usr/bin/env python3
"""
Posts a Meta-shaped webhook body straight to the local API, so the frontend
team (or you) can test the "vendor taps YES" path without a phone, Meta, or
ngrok. Requires WEBHOOK_SKIP_SIGNATURE=true in your local .env -- never set
that true anywhere internet-facing.

Usage:
    python scripts/simulate_reply.py --vendor 11 --answer YES
    python scripts/simulate_reply.py --vendor 11 --answer NO --base-url http://127.0.0.1:8000
"""
import argparse
import sys

import requests


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate a vendor's WhatsApp button reply.")
    parser.add_argument("--vendor", type=int, required=True, help="Vendor id, e.g. 11")
    parser.add_argument("--answer", choices=["YES", "NO"], required=True)
    parser.add_argument("--phone", default="2348012345671", help="Digits only, no '+'")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    body = {
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "messages": [{
                "from": args.phone,
                "id": f"simulated.{args.vendor}.{args.answer}",
                "type": "button",
                "button": {"payload": f"{args.answer}:{args.vendor}", "text": args.answer},
            }],
        }}]}],
    }

    resp = requests.post(f"{args.base_url}/api/v1/webhook/whatsapp", json=body, timeout=5)
    print(f"HTTP {resp.status_code}: {resp.text}")
    return 0 if resp.status_code == 200 else 1


if __name__ == "__main__":
    sys.exit(main())
