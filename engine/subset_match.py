"""Exact-cent, many-to-one subset-sum matching core.

Given a pool of "many" side items (e.g. GL lines) and a list of "one" side
targets (e.g. Bank transactions), finds, for each target, a subset of
1..max_items pool items whose amounts sum exactly to the target amount.
Each pool item is consumed by at most one target across the whole run
(global uniqueness).

Priority order:
  1. Exact 1:1 matches are resolved first, for every target, before any
     many-to-one search is attempted.
  2. Remaining targets are then attempted at group size 2, then 3, ... up
     to `max_items` -- i.e. the simplest (fewest-item) explanation wins
     globally across all targets before anyone is allowed a larger group.
  3. Whenever multiple targets share the same amount (a tie), the one
     with the earlier date is processed first.

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


def build_dp(pool: list, size: int, cap_entries: int = 2_000_000):
    """pool: list of (id, amount_cents). Returns (dp, complete) where dp is a
    list of dicts (index 0..size) mapping achieved sum -> tuple of ids for
    a combo of exactly that many items, and `complete` is False if the
    entry cap was hit before all pool items were folded in (dp[size] is
    then a partial index, not an exhaustive one)."""
    dp = [dict() for _ in range(size + 1)]
    dp[0][0] = ()
    total_entries = 1
    for pid, amt in pool:
        for k in range(size - 1, -1, -1):
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


def _feasible(pool: list, target_cents: int, size: int) -> bool:
    """Cheap reachability check: is target_cents within the range spanned
    by the most extreme achievable sum of exactly `size` pool items?
    Rules out amounts far outside the pool's scale before paying for a DP
    build (e.g. a multi-million dollar target against a pool of GL lines
    each under $150k)."""
    if len(pool) < size:
        return False
    amts = sorted(amt for _, amt in pool)
    min_reach = sum(amts[:size])
    max_reach = sum(amts[-size:])
    return min_reach <= target_cents <= max_reach


def match_all(gl_items: list, bank_items: list, max_items: int = 10,
              date_window_days: int = 15, cap_entries: int = 2_000_000) -> dict:
    """gl_items / bank_items: list of dicts with keys 'id', 'amount_cents',
    and 'date' (a datetime.date). Returns dict of bank_id -> MatchResult.
    """
    available = {item["id"]: (item["amount_cents"], item["date"]) for item in gl_items}
    unresolved = sorted(bank_items, key=lambda b: (b["amount_cents"], b["date"]))
    results = {}
    incomplete_ids = set()

    def pool_for(b):
        target_date = b["date"]
        return [
            (gid, amt) for gid, (amt, d) in available.items()
            if abs((d - target_date).days) <= date_window_days
        ]

    # Tier 1: exact 1:1 matches, earliest-date GL candidate wins ties.
    still = []
    for b in unresolved:
        target_cents = b["amount_cents"]
        candidates = [
            (gid, d) for gid, amt, d in
            ((gid, amt, d) for gid, (amt, d) in available.items())
            if amt == target_cents
        ]
        candidates = [(gid, d) for gid, d in candidates
                      if abs((d - b["date"]).days) <= date_window_days]
        if candidates:
            candidates.sort(key=lambda x: x[1])
            gid = candidates[0][0]
            del available[gid]
            results[b["id"]] = MatchResult(b["id"], "exact_1to1", [gid], target_cents)
        else:
            still.append(b)
    unresolved = still

    # Tier 2: group sizes 2..max_items, smallest first, globally.
    for size in range(2, max_items + 1):
        if not unresolved:
            break
        still = []
        for b in unresolved:
            target_cents = b["amount_cents"]
            pool = pool_for(b)
            if not _feasible(pool, target_cents, size):
                still.append(b)
                continue
            dp, complete = build_dp(pool, size, cap_entries)
            if not complete:
                incomplete_ids.add(b["id"])
            combo = dp[size].get(target_cents)
            if combo is None:
                still.append(b)
                continue
            for gid in combo:
                del available[gid]
            results[b["id"]] = MatchResult(b["id"], "exact_many", list(combo), target_cents)
        unresolved = still

    for b in unresolved:
        status = "search_incomplete" if b["id"] in incomplete_ids else "not_allocated"
        results[b["id"]] = MatchResult(b["id"], status)

    return results
