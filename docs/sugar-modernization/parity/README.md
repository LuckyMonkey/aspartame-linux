# Side-by-side parity workflow (F7 GTK3 ↔ F8 GTK4)

This is how an Activity earns a parity score, and eventually FULL PORT. It
turns the README's "Spaces are an executable oracle" idea into a repeatable
record.

## The pieces

| Piece | Path | Role |
| --- | --- | --- |
| Pairing table | `PAIRS.tsv` (generated) | Every GTK4 Activity, its GTK3 reference, its current port class |
| Report template | `TEMPLATE.md` | Eight standard steps, each scored on the six-face scale |
| Reports | `reports/gtk4/parity/<activity>-<date>.md` | One per comparison session; never overwritten |
| Tool | `scripts/sugar-parity.py` (`make parity-*`) | `pairs`, `new`, `export`, `check` |
| Activity Manager data | `gtk4-overlay/src/cpsection/activities/port_status.json` (generated) | Shown on each row in the modern Settings → Activity Manager |

GTK3 references come from, in order: the pinned source in
`packages/upstream-activities/`, a native row in
`docs/activity-reviews/REVIEWS.tsv`, an Arch `sugar-activity-*` package, or
`sugarizer-web:` when no GTK3 bundle ever existed (compare against the web
Activity's behaviour instead, and say so in the report).

## Running a comparison

1. `make parity-new BUNDLE=org.sugarlabs.Write` creates a prefilled report.
2. In the guest, press **F7**, do step S1 in the classic GTK3 Activity, write
   what you saw. Press **F8**, repeat in GTK4, write what you saw.
3. Score the GTK4 side for that step: 0 (no hurt) … 10 (impossible). Leave the
   cell empty until both sides were actually done.
4. Repeat for every step. Name the core workflow in S3.
5. `make parity-export` and commit the report plus the regenerated
   `port_status.json` together. The Activity Manager now shows the result.

Scoring rules (enforced by the tool):

- A report's score is its **worst** step. One painful step is the score.
- Any unscored step keeps the report **in progress**; it shows as such.
- Only 0, 2, 4, 6, 8, 10 are valid. Anything else counts as unscored.
- The newest dated report for an Activity is the one shown.

## Two ratings, kept separate

The Activity Manager shows two different things on each row, and they must
not be merged:

- **Port class and side-by-side score**: evidence, from the ledger and from
  these reports. Read-only in the UI.
- **The user's face rating**: an opinion, stored per user in
  `~/.config/aspartame/activity-ratings-wong-baker.json`. The classic
  five-level answers in `activity-ratings.json` are read as a fallback
  (Perfect→0, Good→2, Needs work→4, Bad→8, Broken→10) and never rewritten.

## Promotion

A report scoring 0 or 2 on every step is the evidence a FULL PORT promotion
needs; the ledger (`ACTIVITY_PORT_CLASSIFICATION.md`) still has to be edited
by hand with the report linked, then `make parity-pairs parity-export`.

## When Chirality arrives

F7/F8 here means "classic Space, then modern Space". When the Spaces become
the Left Hand / Right Hand (`ASPARTAME_CHIRALITY.md`), keep this workflow
until GTK3 is retired: the reports stay valid evidence and only the
"press F7, then F8" instructions change. Do not delete reports; a later
re-test is a new dated report.
