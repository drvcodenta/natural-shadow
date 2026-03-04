"""
Natural Shadow SDK
==================

A lightweight Python wrapper that intercepts AI agent spending calls,
enforces mock policies, and logs every attempt to the Natural Shadow Dashboard.

Usage:
    from natural_shadow import NaturalShadow

    shadow = NaturalShadow(
        dashboard_url="http://localhost:3000",
        policy_limits={"max_per_tx": 1000, "daily_limit": 5000}
    )

    result = shadow.gatekeeper({
        "tool": "pay_invoice",
        "arguments": {
            "amount": 500,
            "recipient": "Vendor A",
            "reasoning": "Monthly SaaS subscription payment"
        }
    })

    print(result)
    # {"status": "SIMULATED_SUCCESS", "risk_score": 12, ...}
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    requests = None  # type: ignore


class NaturalShadow:
    """Shadow ledger gateway for AI agent spending simulation.

    Intercepts agent tool calls that involve financial transactions,
    evaluates them against configurable policy limits, computes a
    simulated risk score, and logs every attempt to the Natural
    Shadow Dashboard.

    Args:
        dashboard_url: Base URL of the Shadow Dashboard (e.g. ``http://localhost:3000``).
        policy_limits: Dict with policy thresholds. Supported keys:
            - ``max_per_tx`` (float): Maximum allowed amount per transaction.
            - ``daily_limit`` (float): Maximum cumulative daily spend.
            - ``blocked_recipients`` (list[str]): Recipients that are always blocked.
            - ``require_reasoning`` (bool): Whether a reasoning string is required.
    """

    DECISION_APPROVED = "SIMULATED_SUCCESS"
    DECISION_BLOCKED = "BLOCKED"
    DECISION_FLAGGED = "FLAGGED"

    # Risk thresholds
    _HIGH_RISK_THRESHOLD = 75
    _MEDIUM_RISK_THRESHOLD = 40

    def __init__(
        self,
        dashboard_url: str = "http://localhost:3000",
        policy_limits: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.dashboard_url = dashboard_url.rstrip("/")
        self.policy_limits = policy_limits or {
            "max_per_tx": 1000,
            "daily_limit": 5000,
            "blocked_recipients": [],
            "require_reasoning": False,
        }
        self._daily_spend: float = 0.0
        self._daily_reset: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self._history: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def gatekeeper(self, agent_tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Intercept an agent tool call, evaluate policy, and log the result.

        Args:
            agent_tool_call: A dict with at minimum:
                - ``arguments.amount`` (float)
                - ``arguments.recipient`` (str)
                - ``arguments.reasoning`` (str, optional)

        Returns:
            A dict with ``status``, ``risk_score``, ``reason``, and ``id``.
        """
        intent = agent_tool_call.get("arguments", agent_tool_call)
        amount = float(intent.get("amount", 0))
        recipient = str(intent.get("recipient", "unknown"))
        reasoning = str(intent.get("reasoning", ""))
        tool_name = agent_tool_call.get("tool", "unknown_tool")

        # Reset daily counter if new day
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if today != self._daily_reset:
            self._daily_spend = 0.0
            self._daily_reset = today

        # Compute risk
        risk_score = self._compute_risk_score(intent)

        # Evaluate policy
        decision, reason = self._evaluate_policy(
            amount, recipient, reasoning, risk_score
        )

        # Build log entry
        entry_id = self._generate_id(intent)
        log_entry: Dict[str, Any] = {
            "id": entry_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool_name,
            "amount": amount,
            "recipient": recipient,
            "reasoning": reasoning,
            "decision": decision,
            "reason": reason,
            "risk_score": risk_score,
        }

        # Track daily spend for approved transactions
        if decision == self.DECISION_APPROVED:
            self._daily_spend += amount

        # Persist
        self._history.append(log_entry)
        self._send_to_dashboard(log_entry)

        return {
            "status": decision,
            "risk_score": risk_score,
            "reason": reason,
            "id": entry_id,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evaluate_policy(
        self,
        amount: float,
        recipient: str,
        reasoning: str,
        risk_score: int,
    ) -> tuple[str, str]:
        """Check the intent against all policy rules.

        Returns:
            A tuple of (decision, reason).
        """
        max_per_tx = self.policy_limits.get("max_per_tx", float("inf"))
        daily_limit = self.policy_limits.get("daily_limit", float("inf"))
        blocked_recipients = self.policy_limits.get("blocked_recipients", [])
        require_reasoning = self.policy_limits.get("require_reasoning", False)

        # Hard blocks
        if amount > max_per_tx:
            return (
                self.DECISION_BLOCKED,
                f"Amount ${amount:,.2f} exceeds per-transaction limit of ${max_per_tx:,.2f}",
            )

        if self._daily_spend + amount > daily_limit:
            return (
                self.DECISION_BLOCKED,
                f"Would exceed daily limit of ${daily_limit:,.2f} "
                f"(current: ${self._daily_spend:,.2f})",
            )

        if recipient.lower() in [r.lower() for r in blocked_recipients]:
            return (
                self.DECISION_BLOCKED,
                f"Recipient '{recipient}' is on the blocked list",
            )

        if require_reasoning and not reasoning.strip():
            return (
                self.DECISION_BLOCKED,
                "Transaction reasoning is required but not provided",
            )

        # Soft flags
        if risk_score >= self._HIGH_RISK_THRESHOLD:
            return (
                self.DECISION_FLAGGED,
                f"High risk score ({risk_score}/100) — manual review recommended",
            )

        if risk_score >= self._MEDIUM_RISK_THRESHOLD:
            return (
                self.DECISION_FLAGGED,
                f"Elevated risk score ({risk_score}/100) — flagged for review",
            )

        return (self.DECISION_APPROVED, "Transaction within policy limits")

    def _compute_risk_score(self, intent: Dict[str, Any]) -> int:
        """Compute a simulated risk score between 0-100.

        The score is deterministic for the same input (seeded from a hash)
        but takes into account heuristic factors:
        - Higher amounts → higher risk
        - Missing reasoning → +15
        - Unusual recipients → variable bump
        """
        amount = float(intent.get("amount", 0))
        recipient = str(intent.get("recipient", ""))
        reasoning = str(intent.get("reasoning", ""))

        # Deterministic seed from intent content
        seed_str = f"{amount}{recipient}{reasoning}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed)

        # Base score from amount (logarithmic scale)
        if amount <= 0:
            base = 5
        elif amount < 100:
            base = rng.randint(5, 20)
        elif amount < 500:
            base = rng.randint(15, 35)
        elif amount < 1000:
            base = rng.randint(25, 50)
        elif amount < 5000:
            base = rng.randint(40, 65)
        else:
            base = rng.randint(55, 85)

        # Reasoning penalty
        if not reasoning.strip():
            base += 15

        # Recipient entropy (unusual names score higher)
        if len(recipient) < 3:
            base += 10

        return min(base, 100)

    def _send_to_dashboard(self, log_entry: Dict[str, Any]) -> bool:
        """POST the log entry to the Shadow Dashboard API.

        Returns True on success, False on failure (non-blocking).
        """
        if requests is None:
            print(f"[NaturalShadow] requests not installed — log skipped: {log_entry['id']}")
            return False

        try:
            resp = requests.post(
                f"{self.dashboard_url}/api/log",
                json=log_entry,
                timeout=5,
            )
            return resp.status_code == 200
        except Exception as exc:
            print(f"[NaturalShadow] Dashboard unreachable ({exc}) — log stored locally")
            return False

    @staticmethod
    def _generate_id(intent: Dict[str, Any]) -> str:
        """Generate a short unique ID for the log entry."""
        raw = json.dumps(intent, sort_keys=True) + str(time.time())
        return hashlib.sha256(raw.encode()).hexdigest()[:12]

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    @property
    def history(self) -> List[Dict[str, Any]]:
        """Return the local history of all logged attempts."""
        return list(self._history)

    def reset(self) -> None:
        """Clear local history and daily spend counter."""
        self._history.clear()
        self._daily_spend = 0.0
