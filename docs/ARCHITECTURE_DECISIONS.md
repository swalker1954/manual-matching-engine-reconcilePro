# ReconcilePro Architecture Decision Log

A running record of fundamental, hard-to-reverse decisions about the
cloud ReconcilePro build, kept so each one survives past whichever chat
session it was made in. One entry per decision. Entries are not edited
after acceptance — a changed decision gets a new entry that supersedes
the old one and says so explicitly.

---

## ADR-001 — Data storage: cloud Postgres, not the local drive

**Status:** Accepted — September 22, 2026
**Decided by:** Project Owner, in this session, confirming the approach
already implemented under WO-0145.

### Context

The local ReconcilePro system stores raw files, report files, and its
SQL database entirely on the local machine. The Project Owner asked
whether the cloud-hosted app could run while still reading/writing data
on the local drive, given that maintaining and testing the cloud system
implies the cloud side needs its own real data to test against.

### Decision

**No.** The cloud app does not, and will not, read or write to the local
drive. It has its own separate database:

- **Hosting:** Google Cloud Platform — Cloud Run (the app container) +
  Cloud SQL for Postgres (the database), connected via the Cloud SQL
  Auth Proxy.
- **Why Postgres specifically:** SQLite's single-file, single-writer
  model cannot support isolated, concurrently-accessed organizations —
  required for the project's eventual multi-tenant goal, not adopted
  only for testing convenience.
- **How data gets in:** raw files (GL exports, bank files, and — once
  WO-0201 lands — the PowerBI export) are uploaded through the Control
  Center's Utilities screen into Cloud Storage / Postgres. Nothing is
  read directly from `C:\Users\swalk\...` or any local path.
- **Relationship to the local database:** two independent databases, not
  one shared store. The local SQLite database remains the system of
  record for the desktop line. The cloud Postgres database is separate.
  "Functionality matches" is established by running the same test data
  through both and comparing output (per the project's existing
  side-by-side verification governance), not by the two systems sharing
  storage.

### Condition attached by the Project Owner

Moving data into the cloud must not create meaningful operator burden.
Acceptable shape: **identify the raw file(s), click one button**, as
part of (or an added button alongside) Data Prep — not a multi-step or
manual process.

### Verification against the condition

Checked against the actual code on `cloud-foundation-wo-0145`
(`operating_files/src/control_center/prototype.py`,
`handle_cloud_storage_upload_period_page`, WO-0151): the existing
"Upload Raw Files for a Period" screen already matches this bar exactly
— a period field, a GL file picker, a Bank file picker, and a single
"Upload" button. It is an explicitly one-time-per-period step; Data
Prep, Zero Clear, and every engine run afterward reuse that upload
without asking again.

**Consequence for WO-0201:** adding the PowerBI export fits this same
pattern — one more `<input type="file">` field on this same form, not a
new workflow. No condition violation; no design gap to close.

### Rejected alternative

Reaching into the local drive from the cloud container (e.g., a VPN
tunnel plus a network file share) was considered and rejected: two
physically separate networks with no natural shared filesystem, a real
security exposure (opening a local drive to a cloud service), fragile,
and defeats the purpose of a cloud deployment (availability independent
of the local machine being on).
