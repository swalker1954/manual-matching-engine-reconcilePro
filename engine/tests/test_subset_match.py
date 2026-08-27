"""Tests for the Tier 2 (many-to-one) matching core in subset_match.py.

Includes a differential test against a naive reference implementation of
the *same* algorithm (full resort of the pending list on every iteration,
recomputing each target's candidate pool from scratch every time) to
guard against the incremental/heap-based Tier 2 in subset_match.py ever
silently changing which matches get found. The naive version is
correct-but-slow by construction (that slowness, at real data volumes
like a ~21k-row Oracle Receivables export, is exactly the bug the
incremental version fixes) -- it exists here only as a trusted oracle for
small randomized cases, not as production code.
"""

import random
from datetime import date, timedelta

import pytest

from subset_match import MatchResult, _feasible, _lookup, build_dp, match_all, to_cents


def make_item(prefix, i, amount, day, base=date(2025, 8, 1)):
    return {"id": f"{prefix}{i}", "amount_cents": to_cents(amount),
            "date": base + timedelta(days=day)}


def test_exact_1to1_prefers_earliest_date_on_tie():
    gl = [make_item("GL", 1, 100, day=5), make_item("GL", 2, 100, day=1)]
    bank = [make_item("BK", 1, 100, day=3)]
    results = match_all(gl, bank, date_window_days=15)
    r = results["BK1"]
    assert r.status == "exact_1to1"
    assert r.group_ids == ["GL2"]  # earlier-date candidate wins


def test_many_to_one_finds_combination():
    gl = [make_item("GL", 1, 30, day=1), make_item("GL", 2, 70, day=2),
          make_item("GL", 3, 999, day=1)]
    bank = [make_item("BK", 1, 100, day=1)]
    results = match_all(gl, bank, date_window_days=15)
    r = results["BK1"]
    assert r.status == "exact_many"
    assert sorted(r.group_ids) == ["GL1", "GL2"]


def test_date_window_excludes_out_of_range_candidates():
    gl = [make_item("GL", 1, 50, day=0)]
    bank = [make_item("BK", 1, 50, day=20)]  # 20 days > default window
    results = match_all(gl, bank, date_window_days=15)
    assert results["BK1"].status == "not_allocated"


def test_each_gl_item_used_at_most_once():
    gl = [make_item("GL", 1, 50, day=1)]
    bank = [make_item("BK", 1, 50, day=1), make_item("BK", 2, 50, day=1)]
    results = match_all(gl, bank, date_window_days=15)
    matched = [r for r in results.values() if r.group_ids]
    assert len(matched) == 1
    assert {gid for r in results.values() for gid in r.group_ids} == {"GL1"}


# --- differential test against a naive reference implementation ---

def _naive_match_all(gl_items, bank_items, max_items=10, date_window_days=15,
                      cap_entries=200_000):
    """Same algorithm, deliberately re-sorting and rescanning from scratch
    on every iteration -- O(targets^2 x pool size), fine for the small
    cases used here, unusable at production scale. Reference oracle only."""
    available = {item["id"]: (item["amount_cents"], item["date"]) for item in gl_items}
    results = {}

    def pool_for(b):
        target_date = b["date"]
        return [(gid, amt) for gid, (amt, d) in available.items()
                if abs((d - target_date).days) <= date_window_days]

    ordered = sorted(bank_items, key=lambda b: (b["amount_cents"], b["date"]))
    still = []
    for b in ordered:
        target_cents = b["amount_cents"]
        candidates = [(gid, d) for gid, (amt, d) in available.items()
                      if amt == target_cents and abs((d - b["date"]).days) <= date_window_days]
        if candidates:
            candidates.sort(key=lambda x: x[1])
            gid = candidates[0][0]
            del available[gid]
            results[b["id"]] = MatchResult(b["id"], "exact_1to1", [gid], target_cents)
        else:
            still.append(b)

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
        else:
            dp, complete = build_dp(pool, max_items, cap_entries)
            combo = _lookup(dp, target_cents)
            if combo is None:
                status = "not_allocated" if complete else "search_incomplete"
                results[b["id"]] = MatchResult(b["id"], status)
            else:
                for gid in combo:
                    del available[gid]
                results[b["id"]] = MatchResult(b["id"], "exact_many", list(combo), target_cents)
    return results


def _gen_case(seed, n_gl=25, n_bank=15, amount_scale=500, date_span=60):
    rnd = random.Random(seed)
    base = date(2025, 8, 1)
    gl_items = []
    for i in range(n_gl):
        amt = rnd.randint(-amount_scale, amount_scale) or 1
        gl_items.append(make_item("GL", i, amt / 100, rnd.randint(0, date_span), base))
    bank_items = []
    for i in range(n_bank):
        if rnd.random() < 0.5 and gl_items:
            picks = rnd.sample(gl_items, min(rnd.randint(1, 3), len(gl_items)))
            amt_cents = sum(p["amount_cents"] for p in picks)
        else:
            amt_cents = rnd.randint(-amount_scale * 3, amount_scale * 3)
        bank_items.append({"id": f"BK{i}", "amount_cents": amt_cents,
                            "date": base + timedelta(days=rnd.randint(0, date_span))})
    return gl_items, bank_items


def _summarize(results):
    return {bid: (r.status, tuple(sorted(r.group_ids)), r.matched_sum_cents)
            for bid, r in results.items()}


@pytest.mark.parametrize("seed", range(40))
def test_matches_naive_reference(seed):
    gl_items, bank_items = _gen_case(seed)
    ref = _naive_match_all([dict(x) for x in gl_items], [dict(x) for x in bank_items],
                            date_window_days=15, cap_entries=200_000)
    new = match_all([dict(x) for x in gl_items], [dict(x) for x in bank_items],
                     date_window_days=15, cap_entries=200_000)
    assert _summarize(new) == _summarize(ref)
