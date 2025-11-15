from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass(frozen=True)
class Transaction:
    time: str
    reason: str
    delta: int
    balance: int

    def to_dict(self) -> dict:
        return asdict(self)


def adjust_budget(balance: int, delta: int, *, allow_negative: bool = False) -> int:
    """
    Return the new balance after applying delta. Raises ValueError if funds would drop
    below zero and `allow_negative` is False.
    """
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
    """
    Append a transaction to `history` and enforce the optional rolling limit.
    """
    history.append(Transaction(time=time, reason=reason, delta=delta, balance=balance))
    if limit and len(history) > limit:
        del history[:-limit]


def serialise_history(history: List[Transaction]) -> List[dict]:
    return [entry.to_dict() for entry in history]


def restore_history(payload: Optional[List[dict]]) -> List[Transaction]:
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
