# FULL PORT receipts and GTK4 default — 2026-10-22

## Image

- ISO `aspartame-2026.10.22-x86_64.iso`, sha256 `8d18f445…`.
- Runtime export `gtk4-preview-standalone-20261022b`, sha256 `ccce1187…`.
- It adds three changes to the earlier runtime:
  - the 0301 accessible name for `ActivityToolbarButton`;
  - the Pippy Ctrl+Tab fix;
  - GTK4 as the default Space.
- The VM was booted headless in snapshot mode with no dev share.

## Default Space

After boot, `sugar-gtk4-space.sh status` reported `current=1` (GTK4).
`/tmp/aspartame-gtk4-space.log` reported `Sugar Spaces ready: F8 = GTK4
(default), F7 = GTK3 recovery`. Recovery round trip:

```text
runtime-check=ok target=gtk3 pid=784 desktop=0 ...
runtime-check=ok target=gtk4 pid=1387 desktop=1 ...
```

## Receipts

Command: `scripts/sugar-gtk4-fullport-receipt.py <candidate>`. Keystrokes go
through QEMU's virtual keyboard; focus moves only with Tab and Ctrl+Tab.

```text
markdown-input=PASS keys=qemu focus=tab
markdown-persist=PASS object=e57409b9-200e-4d69-bcc5-6bedd6c12aa3
markdown-guard=PASS sha256=ea9c7024785a
markdown-a11y=PASS checked=4
fullport-receipt=PASS candidate=markdown
pippy-input=PASS keys=qemu focus=tab,ctrl+tab
pippy-persist=PASS object=3043b7a4-714e-48ab-9e29-b6675e3a457f
pippy-guard=PASS sha256=ea9c7024785a
pippy-a11y=PASS checked=10
fullport-receipt=PASS candidate=pippy
```

What each workflow did:
- **Markdown:** typed `# Field notes`, a blank line and `Typed through QEMU.`
  The rendered preview showed the heading.
- **Pippy:** typed `print(6*7)`, moved focus to Run with Ctrl+Tab, and
  pressed Space. The output showed `42`.

Found and fixed by these receipts on the earlier image:
- `ActivityToolbarButton` had no accessible name. This affected every
  GTK4 Activity.
- Pippy's editor turned Ctrl+Tab into an indent, a keyboard trap.
- The QMP macro could not type spaces, dots or punctuation.

## Regression on the same image

| Check | Result |
| --- | --- |
| Runtime check gtk3 (after F7) / gtk4 | ok / ok |
| Settings probe | 3 close/reopen PASS, `settings-aboutcomputer=PASS refresh=PASS` |
| GTK4 / GTK3 lifecycle, 3 cycles each | PASS / PASS |
| Activity matrix, 1 cycle | `activity-matrix=PASS` |

## Retirement gate

`gtk4-retirement=BLOCKED blocker=full-parity`. Markdown and Pippy are now
FULL PORT. The other six candidates fail the core-workflow comparison; see
the verdicts in `ACTIVITY_PORT_CLASSIFICATION.md`. GTK3 packages stay
installed. GTK3 now serves only as the F7 recovery Space.
