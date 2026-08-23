# manual-matching-engine-reconcilePro

A many-to-one exact-cent matching engine for reconciling GL and Bank
transaction exports that don't fit the automated business-rule engines.
Given a two-tab workbook (GL / Bank), it finds groups of 1-10 GL items
whose amounts sum exactly to a single Bank amount, writes a group code
back onto both sides, and produces Match Report / Match Inputs tabs
summarizing what it found.

This is explicitly a **first-pass tool, not a complete solution**: it
catches the "obvious" combinations so a human doesn't have to hunt for
them by hand. Whatever's left over needs manual review -- that's expected,
not a bug.

## How matching works

1. **Exact 1:1 matches first.** Every target is checked for a single GL
   item at the exact same amount before any many-to-one search runs. On a
   tie (multiple same-amount candidates within the date window), the
   earliest-date GL item wins.
2. **Then many-to-one, most-constrained target first.** Remaining Bank
   targets are searched in order of fewest candidate GL items in their
   date window -- a target with few options is searched (and gets first
   claim on shared items) before one with many alternatives. Within a
   single target's search, the fewest-item (simplest) combination wins.
3. **Ties on duplicate amounts** are broken by earliest date.
4. Every GL item is used in at most one group, globally.

Candidates for a target are restricted to GL items within a date window
(default ±15 days) of the target's date. This isn't just a performance
shortcut -- at real data volume (hundreds of GL lines), proving no exact
combination exists is combinatorially expensive without it, and it
doubles as a plausibility filter against coincidental amount matches.

## Usage

```
cd engine
python3 match_workbook.py \
  --input SAP_202512_Unmatched.xlsx \
  --output SAP_202512_Matched.xlsx \
  --id-col "Matching/Group ID" \
  --engine-col "Matched By Engine" --engine-tag Manual \
  --status-col "Match Status" --status-value Matched \
  --prefix SAP --period 2025-12 \
  --max-items 10 --date-window 15 --cap-entries 2000000
```

Key flags (all have defaults suited to the ReconcilePro export format --
run `--help` for the full list):

- `--gl-sheet` / `--bank-sheet`: tab names (default `GL` / `Bank`)
- `--amount-col` / `--date-col`: source columns (default `Matching Amount`
  / `Transaction Date`)
- `--id-col`: where the group code is written on both sides (varies by
  export version -- `Match ID or Group ID` in one, `Matching/Group ID` in
  another; check the actual column header)
- `--prefix` / `--period`: group codes are `{prefix}-{period}-{seq:03d}`,
  e.g. `SAP-2025-12-001`, sequential in Bank-row order so the sheet sorts
  back into matched groups
- `--cap-entries`: how much search effort per target before giving up and
  marking it `search_incomplete` rather than a confirmed `Not allocated`.
  Real matches tend to require exploring deep into the search space, so
  lowering this trades away real matches for speed -- don't lower it just
  to make a test run finish faster; ~2,000,000 took about 12 minutes on
  451 GL x 636 Bank rows and is the validated setting.

## Repeating for other engines

Work Order #1 describes 7-8 separate SAP/Oracle/etc. engines, each with
its own worksheet export. The script is parameterized (sheet names,
column names, prefix, period) specifically so the same tool can be
pointed at each one -- it does not need to be rewritten per engine, only
re-invoked with the right `--gl-sheet`/`--bank-sheet`/column-name/`--prefix`
arguments for that export's layout.

## Known limitations (first iteration)

- Exact-cent matching only; no tolerance/rounding slack.
- Pure amount + date-window search; no use of description, reference, or
  other business-context fields that a human reviewer would use to
  disambiguate coincidental amount matches.
- `search_incomplete` (as opposed to `Not allocated`) means the search
  gave up before proving no combination exists -- it is not a confirmed
  negative. At real data volume, most unresolved targets will land here
  rather than a proven "no match."
- Real financial data should never be committed to this repo (see
  `.gitignore`) -- only the engine code.
