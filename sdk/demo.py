"""
Natural Shadow SDK — Demo Script
=================================

Run this script while the Shadow Dashboard is running at localhost:3000
to see agent attempts appear in the live feed.

Usage:
    python demo.py              # clears dashboard, then sends entries with delays
    python demo.py --no-clear   # keeps existing data, appends new entries
"""

import sys
import time

try:
    import requests
except ImportError:
    print("ERROR: 'requests' package is required. Install with: pip install requests")
    sys.exit(1)

from natural_shadow import NaturalShadow

DASHBOARD_URL = "http://localhost:3000"


def clear_dashboard():
    """Clear all existing logs from the dashboard."""
    try:
        resp = requests.delete(f"{DASHBOARD_URL}/api/log", timeout=5)
        if resp.status_code == 200:
            print("  ✓ Dashboard cleared — starting fresh\n")
        else:
            print(f"  ⚠ Could not clear dashboard (status {resp.status_code})\n")
    except Exception as exc:
        print(f"  ⚠ Dashboard unreachable ({exc}) — is it running at {DASHBOARD_URL}?\n")


def main():
    no_clear = "--no-clear" in sys.argv

    # Initialize the shadow ledger
    shadow = NaturalShadow(
        dashboard_url=DASHBOARD_URL,
        policy_limits={
            "max_per_tx": 1000,
            "daily_limit": 5000,
            "blocked_recipients": ["Suspicious Corp"],
            "require_reasoning": True,
        },
    )

    # Simulated agent tool calls
    test_calls = [
        {
            "tool": "pay_invoice",
            "arguments": {
                "amount": 250.00,
                "recipient": "Acme Cloud Services",
                "reasoning": "Monthly infrastructure hosting bill for Q1 2025",
            },
        },
        {
            "tool": "pay_invoice",
            "arguments": {
                "amount": 4500.00,
                "recipient": "Enterprise AI Ltd",
                "reasoning": "Annual API license renewal — agent determined best price",
            },
        },
        {
            "tool": "transfer_funds",
            "arguments": {
                "amount": 75.00,
                "recipient": "Coffee Supplies Co",
                "reasoning": "Office supplies restock — auto-detected low inventory",
            },
        },
        {
            "tool": "pay_invoice",
            "arguments": {
                "amount": 12000.00,
                "recipient": "Quantum Hardware Inc",
                "reasoning": "GPU cluster upgrade for training pipeline",
            },
        },
        {
            "tool": "transfer_funds",
            "arguments": {
                "amount": 500.00,
                "recipient": "Suspicious Corp",
                "reasoning": "Vendor payment — flagged entity",
            },
        },
        {
            "tool": "pay_invoice",
            "arguments": {
                "amount": 300.00,
                "recipient": "DataFlow Analytics",
                "reasoning": "",  # Missing reasoning — should be blocked
            },
        },
        {
            "tool": "pay_invoice",
            "arguments": {
                "amount": 89.99,
                "recipient": "Design Tool Pro",
                "reasoning": "Monthly design tool subscription for marketing team",
            },
        },
        {
            "tool": "transfer_funds",
            "arguments": {
                "amount": 1500.00,
                "recipient": "Freelancer Network",
                "reasoning": "Contract developer payment — sprint 14 deliverables",
            },
        },
    ]

    print()
    print("=" * 60)
    print("  NATURAL SHADOW — Agent Spending Simulation")
    print("=" * 60)
    print()

    # Clear dashboard before starting (unless --no-clear flag is set)
    if not no_clear:
        print("  Clearing dashboard...")
        clear_dashboard()

    print(f"  Sending {len(test_calls)} agent attempts (3s delay between each)")
    print(f"  Watch the dashboard at {DASHBOARD_URL}")
    print()
    print("-" * 60)
    print()

    for i, call in enumerate(test_calls, 1):
        args = call["arguments"]
        print(f"  [{i}/{len(test_calls)}]  {call['tool']}  →  ${args['amount']:,.2f}  →  {args['recipient']}")

        result = shadow.gatekeeper(call)

        status_icon = {
            "SIMULATED_SUCCESS": "✅",
            "BLOCKED": "🚫",
            "FLAGGED": "⚠️",
        }.get(result["status"], "❓")

        print(f"          {status_icon}  {result['status']}  (risk: {result['risk_score']}/100)")
        print(f"          → {result['reason']}")
        print()

        # Wait between calls for dramatic demo effect
        if i < len(test_calls):
            time.sleep(3)

    print("-" * 60)
    print()
    print(f"  ✓ Demo complete!")
    print(f"    Total attempts: {len(shadow.history)}")
    approved = sum(1 for h in shadow.history if h["decision"] == "SIMULATED_SUCCESS")
    blocked = sum(1 for h in shadow.history if h["decision"] == "BLOCKED")
    flagged = sum(1 for h in shadow.history if h["decision"] == "FLAGGED")
    print(f"    Approved: {approved}  |  Blocked: {blocked}  |  Flagged: {flagged}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

