"""Budget and transaction helpers used across world/economy reporting."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass(frozen=True)
class Transaction:
    """Immutable record of a budget transaction."""

    time: str
    reason: str
    delta: int
    balance: int

    def to_dict(self) -> dict:
        """Return the transaction as a serialisable dictionary."""
        return asdict(self)


def adjust_budget(balance: int, delta: int, *, allow_negative: bool = False) -> int:
    """Return a new balance after applying delta, preventing overdraft by default."""
    new_balance = balance + delta
    if not allow_negative and new_balance < 0:
        raise ValueError("Insufficient budget for transaction.")
    return new_balance


def record_transaction(
    history: List[Transaction],
    *,
    time: str,
    reason: str,
    delta: int,
    balance: int,
    limit: int = 10,
) -> None:
    """Append a transaction to history, trimming the list to the rolling limit."""
    history.append(Transaction(time=time, reason=reason, delta=delta, balance=balance))
    if limit and len(history) > limit:
        del history[:-limit]


def serialise_history(history: List[Transaction]) -> List[dict]:
    """Return the transaction history as serialisable dictionaries."""
    return [entry.to_dict() for entry in history]


def restore_history(payload: Optional[List[dict]]) -> List[Transaction]:
    """Rebuild a list of Transaction objects from a persisted payload."""
    history: List[Transaction] = []
    if not payload:
        return history
    for entry in payload:
        if not isinstance(entry, dict):
            continue
        try:
            history.append(
                Transaction(
                    time=str(entry.get("time", "")),
                    reason=str(entry.get("reason", "")),
                    delta=int(entry.get("delta", 0)),
                    balance=int(entry.get("balance", 0)),
                )
            )
        except (TypeError, ValueError):
            continue
    return history
