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

## Workspace

Drop raw source workbooks into `workspace/` (gitignored, along with every
`.xlsx`/`.xlsm` anywhere in the repo -- real financial data never gets
committed no matter where you put it). `workspace/output/` is a reasonable
place to let the pipeline write its results.

## Double-click launcher (non-command-line use)

`Run_SAP_Matching.bat` (project root) is meant to be run via a Desktop
shortcut, no command line needed. The engine code stays wherever this
project folder lives; the DATA lives separately, organized by period, at
a fixed external location (currently
`C:\users\swalk\documents\ReconcilePro\Operating_files\Periods\<period>\`
-- edit `DATA_ROOT` near the top of the `.bat` if this ever moves):

```
Periods\<period>\raw\Manual Matching\
  <raw export>.xlsx   <- input: exactly one .xlsx here
  output\              <- results land here (auto-created; safe to
                          delete to reset)
```

1. Put exactly one raw export `.xlsx` in that period's `raw\Manual
   Matching\` folder.
2. Double-click the shortcut (or the `.bat` itself).
3. It prompts for the period (e.g. type `2025-12` and press Enter) --
   deliberate, not auto-picked, so an old unprocessed period folder can
   never get silently skipped or the wrong month run by accident.
4. Results land in that period's `raw\Manual Matching\output\` as
   `matched.xlsx` and `matched_analysis.xlsx`.

It auto-detects the processing period *label used in match codes* from
the data itself (no need to edit the file each month for that part) and
auto-finds the one `.xlsx` sitting in the raw folder -- if it finds none
or more than one, it stops with a clear message rather than guessing.
Uses the same validated SAP defaults as `run_sap.ps1`/`run_sap.sh`.

A `.bat` file downloaded from the internet may be Windows-blocked the
same way `.ps1` files are -- if double-clicking it does nothing or shows
a security warning, run `Unblock-File -Path .\Run_SAP_Matching.bat` once
in PowerShell.

## Quick start: run_sap.sh

For the SAP GL/Bank export format (validated on the December 2025 data),
`engine/run_sap.sh` chains matching + the Analysis tab in one command:

```
cd engine
./run_sap.sh ../workspace/ReconcilePro_Matching_202512.xlsx SAP 2025-12 ../workspace/output
```

Produces `<name>_matched.xlsx` (matching engine only) and
`<name>_matched_analysis.xlsx` (with the Analysis dashboard tab added) in
the output directory. This is the SAP-specific defaults baked in --
`Matching ID` as the primary code column, `Matching/Group ID` mirrored,
`Match Status` flipped to `Matched`, 15-day date window, 10-item cap,
2,000,000-entry search budget. For a different engine's export, call the
two scripts directly (see below) with that export's own column/sheet
names.

## Usage (calling the scripts directly)

```
cd engine
python3 match_workbook.py \
  --input SAP_202512_Unmatched.xlsx \
  --output SAP_202512_Matched.xlsx \
  --id-col "Matching ID" --secondary-id-col "Matching/Group ID" \
  --engine-col "Matched By Engine" --engine-tag Manual \
  --status-col "Match Status" --status-value Matched \
  --prefix SAP --period 2025-12 \
  --max-items 10 --date-window 15 --cap-entries 2000000

python3 build_analysis_tab.py \
  --input SAP_202512_Matched.xlsx \
  --output SAP_202512_Matched_Analysis.xlsx \
  --bank-sheet Bank --source-label SAP
```

Key `match_workbook.py` flags (all have defaults suited to the
ReconcilePro export format -- run `--help` for the full list):

- `--gl-sheet` / `--bank-sheet`: tab names (default `GL` / `Bank`)
- `--amount-col` / `--date-col`: source columns (default `Matching Amount`
  / `Transaction Date`)
- `--id-col`: primary column the group code is written into on both sides
  (varies by export version -- check the actual column header). Defaults
  to `Matching ID`.
- `--secondary-id-col`: optional second column to also receive the code,
  e.g. `Matching/Group ID` on exports that carry both.
- `--prefix` / `--period` / `--seq-digits`: group codes are
  `{prefix}-{period}-{seq padded to seq-digits}`, e.g. `SAP-2025-12-01`
  (default 2-digit padding), sequential in Bank-row order so the sheet
  sorts back into matched groups. Bump `--seq-digits` if a run exceeds the
  digit count's capacity (2 digits -> 99 matches) or padding will break
  sort order past that count.
- `--cap-entries`: how much search effort per target before giving up and
  marking it `search_incomplete` rather than a confirmed `Not allocated`.
  Real matches tend to require exploring deep into the search space, so
  lowering this trades away real matches for speed -- don't lower it just
  to make a test run finish faster; ~2,000,000 took about 12 minutes on
  451 GL x 636 Bank rows and is the validated setting.

`build_analysis_tab.py` adds a KPI/story/chart "Analysis" dashboard tab
computed live (via SUMIFS formulas) from a Bank-style sheet -- see
`--help` for its flags.

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
