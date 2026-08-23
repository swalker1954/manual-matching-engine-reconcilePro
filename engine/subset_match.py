"""Exact-cent, many-to-one subset-sum matching core.

Given a pool of "many" side items (e.g. GL lines) and a list of "one" side
targets (e.g. Bank transactions), finds, for each target, a subset of
1..max_items pool items whose amounts sum exactly to the target amount.
Each pool item is consumed by at most one target across the whole run
(global uniqueness).

Priority order:
  1. Exact 1:1 matches are resolved first, for every target, before any
     many-to-one search is attempted. On a tie (multiple available GL
     items at the same amount within the date window), the earliest-date
     GL item wins.
  2. Remaining targets are then searched for a many-to-one group, most
     constrained target first: the target with the fewest candidate GL
     items in its date window is searched before one with more
     candidates, since it has less room to be satisfied another way and
     fewer alternative combinations to compete over. Within that search,
     the fewest-item (simplest) combo is preferred automatically.
  3. Whenever two targets have the same dollar amount, the one with the
     earlier date is processed first.

Candidates for a target are restricted to GL items within
`date_window_days` of the target's date -- this keeps each search small
even though the full (unrestricted) pool is too large to search
exhaustively, and doubles as a plausibility filter against coincidental
matches.

All amounts are handled as integer cents to avoid floating point drift.
"""

from dataclasses import dataclass, field
from typing import Optional


def to_cents(amount: float) -> int:
    """Round a dollar amount to integer cents."""
    return round(amount * 100)


@dataclass
class MatchResult:
    target_id: object
    status: str  # "exact_1to1" | "exact_many" | "not_allocated" | "search_incomplete"
    group_ids: list = field(default_factory=list)
    matched_sum_cents: Optional[int] = None


def build_dp(pool: list, max_items: int, cap_entries: int = 2_000_000):
    """pool: list of (id, amount_cents). Returns (dp, complete) where dp is a
    list of dicts (index 0..max_items) mapping achieved sum -> tuple of ids
    achieving it with exactly that many items, and `complete` is False if
    the entry cap was hit before all pool items were folded in."""
    dp = [dict() for _ in range(max_items + 1)]
    dp[0][0] = ()
    total_entries = 1
    for pid, amt in pool:
        for k in range(max_items - 1, -1, -1):
            if not dp[k]:
                continue
            for s, combo in list(dp[k].items()):
                new_s = s + amt
                bucket = dp[k + 1]
                if new_s not in bucket:
                    bucket[new_s] = combo + (pid,)
                    total_entries += 1
            if total_entries > cap_entries:
                return dp, False
    return dp, True


def _lookup(dp: list, target_cents: int) -> Optional[tuple]:
    """Smallest-item-count combo achieving target_cents, or None."""
    for k in range(1, len(dp)):
        combo = dp[k].get(target_cents)
        if combo is not None:
            return combo
    return None


def _feasible(pool: list, target_cents: int, max_items: int) -> bool:
    """Cheap reachability check: is target_cents within the range spanned
    by the most extreme achievable sum of up to max_items pool items?
    Rules out amounts far outside the pool's scale before paying for a DP
    build (e.g. a multi-million dollar target against a pool of GL lines
    each under $150k)."""
    amts = sorted(amt for _, amt in pool)
    neg = [a for a in amts if a < 0]
    pos = [a for a in amts if a > 0]
    min_reach = sum(neg[:max_items])
    max_reach = sum(sorted(pos, reverse=True)[:max_items])
    return min_reach <= target_cents <= max_reach


def match_all(gl_items: list, bank_items: list, max_items: int = 10,
              date_window_days: int = 15, cap_entries: int = 2_000_000) -> dict:
    """gl_items / bank_items: list of dicts with keys 'id', 'amount_cents',
    and 'date' (a datetime.date). Returns dict of bank_id -> MatchResult.
    """
    available = {item["id"]: (item["amount_cents"], item["date"]) for item in gl_items}
    results = {}

    def pool_for(b):
        target_date = b["date"]
        return [
            (gid, amt) for gid, (amt, d) in available.items()
            if abs((d - target_date).days) <= date_window_days
        ]

    # Tier 1: exact 1:1 matches. Process targets in (amount, date) order so
    # duplicate-amount ties are resolved earliest-date-target first; within
    # each, the earliest-date GL candidate wins.
    ordered = sorted(bank_items, key=lambda b: (b["amount_cents"], b["date"]))
    still = []
    for b in ordered:
        target_cents = b["amount_cents"]
        candidates = [
            (gid, d) for gid, (amt, d) in available.items()
            if amt == target_cents and abs((d - b["date"]).days) <= date_window_days
        ]
        if candidates:
            candidates.sort(key=lambda x: x[1])
            gid = candidates[0][0]
            del available[gid]
            results[b["id"]] = MatchResult(b["id"], "exact_1to1", [gid], target_cents)
        else:
            still.append(b)

    # Tier 2: many-to-one, most-constrained target (fewest date-window
    # candidates) searched first; ties broken by (amount, date). Each
    # target gets one full DP build over its current candidate pool and
    # takes the fewest-item combo it offers.
    def sort_key(b):
        return (len(pool_for(b)), b["amount_cents"], b["date"])

    pending = still
    while pending:
        pending.sort(key=sort_key)
        b = pending.pop(0)
        target_cents = b["amount_cents"]
        pool = pool_for(b)
        if not pool or not _feasible(pool, target_cents, max_items):
            results[b["id"]] = MatchResult(b["id"], "not_allocated")
            continue
        dp, complete = build_dp(pool, max_items, cap_entries)
        combo = _lookup(dp, target_cents)
        if combo is None:
            status = "not_allocated" if complete else "search_incomplete"
            results[b["id"]] = MatchResult(b["id"], status)
            continue
        for gid in combo:
            del available[gid]
        results[b["id"]] = MatchResult(b["id"], "exact_many", list(combo), target_cents)

    return results
