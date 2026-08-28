"""Receipt-based matching for engines with a natural grouping key (e.g.
Oracle Receivables' Receipt Number), where "many" side items sharing that
key have their amounts summed (a subtotal) and matched exact-to-the-cent
against a single Bank deposit.

Unlike the combinatorial subset-sum engine (subset_match.py), this is a
direct lookup, not a search: the grouping is given by the data itself (the
Receipt Number), not assembled by trying combinations. There is no
item-count limit, no date-window restriction, and no "search incomplete"
outcome -- a group either finds its one matching Bank row or it doesn't.

GL rows with a blank/missing Receipt Number are each treated as their own
singleton group rather than being lumped together, since a blank value
isn't a real shared receipt.

On a tie (more than one receipt group -- or more than one Bank row --
sharing the same amount), the earliest-date group is matched first,
consistent with the tie-break rule used elsewhere in this engine.
"""

from subset_match import MatchResult


def match_by_receipt(gl_items: list, bank_items: list) -> dict:
    """gl_items: list of dicts with 'id', 'amount_cents', 'date', and
    'group_key' (the Receipt Number).
    bank_items: list of dicts with 'id', 'amount_cents', 'date'.
    Returns dict of bank_id -> MatchResult.
    """
    groups = {}
    for item in gl_items:
        key = item.get("group_key")
        if key is None or (isinstance(key, str) and key.strip() == ""):
            key = ("__blank__", item["id"])
        groups.setdefault(key, []).append(item)

    # subtotal_cents -> list of (earliest_date, [gl_ids]), earliest first
    available = {}
    for members in groups.values():
        subtotal = sum(m["amount_cents"] for m in members)
        earliest = min(m["date"] for m in members)
        available.setdefault(subtotal, []).append((earliest, [m["id"] for m in members]))
    for candidates in available.values():
        candidates.sort(key=lambda x: x[0])

    results = {}
    ordered_bank = sorted(bank_items, key=lambda b: (b["amount_cents"], b["date"]))
    for b in ordered_bank:
        candidates = available.get(b["amount_cents"])
        if candidates:
            _, gl_ids = candidates.pop(0)
            results[b["id"]] = MatchResult(b["id"], "exact_receipt", gl_ids, b["amount_cents"])
        else:
            results[b["id"]] = MatchResult(b["id"], "not_allocated")

    return results
