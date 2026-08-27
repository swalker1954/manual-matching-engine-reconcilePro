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

import heapq
import time
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
              date_window_days: int = 15, cap_entries: int = 2_000_000,
              progress_every: int = 10) -> dict:
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

    print(f"  Tier 1 (1:1): {len(ordered) - len(still)} matched, "
          f"{len(still)} remain for many-to-one search", flush=True)

    # Tier 2: many-to-one, most-constrained target (fewest date-window
    # candidates) searched first; ties broken by (amount, date). Each
    # target gets one full DP build over its current candidate pool and
    # takes the fewest-item combo it offers.
    #
    # A target's date-window candidate *ids* never change (GL dates are
    # fixed) -- only how many of those ids are still available does. So
    # each target's candidate id list is computed once, and its "still
    # available" count is maintained incrementally (decremented only when
    # a match consumes one of its candidates) instead of being rescanned
    # from every pending target's full window on every iteration -- that
    # rescan is what made this stage O(targets^2 x GL pool size) and
    # unusable once the GL pool reaches real-world size (tens of
    # thousands of rows for engines like Oracle Receivables, vs. the ~450
    # rows this was originally tuned against).
    #
    # Priority order is still "true current global most-constrained
    # first": a heap is kept in (count, amount, date, seq) order, and a
    # stale entry (pushed before a later decrement) is detected and
    # discarded at pop time rather than eagerly removed, since removing
    # an arbitrary heap entry isn't cheap -- this is the standard
    # lazy-deletion/decrease-key pattern and yields identical results to
    # resorting from scratch every time.
    pending = still
    total = len(pending)
    seq = {b["id"]: i for i, b in enumerate(pending)}
    by_id = {b["id"]: b for b in pending}
    window_ids = {}
    gl_to_targets = {}
    for b in pending:
        ids = [gid for gid, _ in pool_for(b)]
        window_ids[b["id"]] = ids
        for gid in ids:
            gl_to_targets.setdefault(gid, []).append(b["id"])

    remaining_count = {bid: len(ids) for bid, ids in window_ids.items()}
    heap = []
    for b in pending:
        bid = b["id"]
        heapq.heappush(heap, (remaining_count[bid], b["amount_cents"], b["date"], seq[bid], bid))

    done = 0
    start = time.time()
    finalized = set()
    while len(finalized) < total:
        count, _, _, _, bid = heapq.heappop(heap)
        if bid in finalized or count != remaining_count[bid]:
            continue  # already processed, or a fresher entry supersedes this one
        finalized.add(bid)
        b = by_id[bid]
        target_cents = b["amount_cents"]
        pool = [(gid, available[gid][0]) for gid in window_ids[bid] if gid in available]
        if not pool or not _feasible(pool, target_cents, max_items):
            results[bid] = MatchResult(bid, "not_allocated")
        else:
            dp, complete = build_dp(pool, max_items, cap_entries)
            combo = _lookup(dp, target_cents)
            if combo is None:
                status = "not_allocated" if complete else "search_incomplete"
                results[bid] = MatchResult(bid, status)
            else:
                for gid in combo:
                    del available[gid]
                    for other_id in gl_to_targets.get(gid, ()):
                        if other_id in finalized:
                            continue
                        remaining_count[other_id] -= 1
                        other = by_id[other_id]
                        heapq.heappush(heap, (remaining_count[other_id], other["amount_cents"],
                                               other["date"], seq[other_id], other_id))
                results[bid] = MatchResult(bid, "exact_many", list(combo), target_cents)

        done += 1
        if total and (done % progress_every == 0 or done == total):
            elapsed = time.time() - start
            rate = done / elapsed if elapsed > 0 else 0
            remaining = (total - done) / rate if rate > 0 else 0
            print(f"  Tier 2: {done}/{total} targets searched "
                  f"({elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining)", flush=True)

    return results
