# Side-by-side parity: {{NAME}}

- **Bundle ID:** `{{BUNDLE_ID}}`
- **Date:** {{DATE}}
- **GTK3 reference (F7):** `{{GTK3}}`
- **GTK4 candidate (F8):** `{{GTK4}}`
- **Class at start:** {{CLASS}}
- **Tester:** (person or agent; agents also name the image/build they used)
- **Image / preview build:** (ISO name or `STANDALONE-MANIFEST` hash)

Do each step in the classic Space (F7) first, then repeat it in the modern
Space (F8). Write what you actually saw in both columns, not what should
happen. Score only the GTK4 side, on the Activity Manager's six-face scale:
how much does the F8 version hurt compared with F7?

| Score | Meaning |
| --- | --- |
| 0 | No hurt: same or better than GTK3 |
| 2 | Hurts a little bit: cosmetic difference only |
| 4 | Hurts a little more: works, but slower or clumsier |
| 6 | Hurts even more: part of the step is missing |
| 8 | Hurts a whole lot: the step mostly fails |
| 10 | Hurts worst: the step is impossible |

Leave the score cell empty until the step has been done in both Spaces. The
report's score is its worst step, and any empty cell keeps it "in progress".

| Step | What to do | F7 (GTK3) observed | F8 (GTK4) observed | Score |
| --- | --- | --- | --- | --- |
| S1 | Launch from Home Favorites; note time to a usable surface | | | |
| S2 | First view: layout, toolbar, title, icons, colours | | | |
| S3 | Core workflow (name it here): | | | |
| S4 | Keyboard only: Tab, Shift+Tab, Enter/Space, Escape | | | |
| S5 | Palettes, toolbar buttons, and the Stop button | | | |
| S6 | Stop, then resume the same object from the Journal | | | |
| S7 | Edge case: empty input, very large input, or rapid clicks | | | |
| S8 | Accessible names: every control reads sensibly over AT-SPI | | | |

## Differences found

- (One bullet per difference. Link a `BLOCKERS.md` entry or a commit when one exists.)

## Evidence

- Screenshots: (paths under `reports/gtk4/`, F7 and F8 at the same step)
- Logs/commands: (probe scripts or key sequences used)

## Verdict

(Keep, repair, or promote. A move to FULL PORT also needs the classification
ledger updated with this report linked.)
