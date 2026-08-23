"""Exact-cent, many-to-one subset-sum matching core.

Given a pool of "many" side items (e.g. GL lines) and a list of "one" side
targets (e.g. Bank transactions), finds, for each target, a subset of
1..max_items pool items whose amounts sum exactly to the target amount.
Each pool item is consumed by at most one target across the whole run
(global uniqueness).

Approach: for each target, in descending amount-magnitude order (largest,
rarest amounts get first claim on shared items), restrict candidates to
GL items within `date_window_days` of the target's date, build a
bounded-item-count subset-sum DP over just that window (dp[k] = {sum ->
combo of ids achieving it with exactly k items}), and take the smallest-k
match. Committed items are removed from the pool before the next target.
Restricting to a date window keeps each DP build small even though the
full (unrestricted) pool is too large to search exhaustively.

All amounts are handled as integer cents to avoid floating point drift.
"""

from dataclasses import dataclass, field
from datetime import date
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
    list of dicts (index 0..max_items) mapping achieved sum -> tuple of ids,
    and `complete` is False if the entry cap was hit before all items were
    folded in (results are then a partial/best-effort index, not exhaustive)."""
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
    order = sorted(bank_items, key=lambda b: -abs(b["amount_cents"]))
    results = {}

    for b in order:
        target_date = b["date"]
        target_cents = b["amount_cents"]
        pool = [
            (gid, amt) for gid, (amt, d) in available.items()
            if abs((d - target_date).days) <= date_window_days
        ]
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
        status = "exact_1to1" if len(combo) == 1 else "exact_many"
        results[b["id"]] = MatchResult(b["id"], status, list(combo), target_cents)

    return results
