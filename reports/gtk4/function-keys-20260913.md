# GTK4 function-key routing — 2026-09-13

The live GTK4 guest initially ignored F1–F6 while an Activity surface had
focus. The shell's controller was attached only to the top-level window, while
Casilda's compositor widget owned the focused event route. Patch `0070` attaches
the existing semantic `KeyHandler` at capture phase to that compositor widget.

Runtime evidence after restarting the GTK4 shell:

- F1 produced Neighborhood (`sugar-20260912-233439-v0.0.31.png`).
- F2, F3, F4, F5, and F6 were accepted in sequence; the shell log recorded
  `GTK4 semantic key event: F1` through `F6`.
- F6 visibly revealed the Sugar Frame (`sugar-20260912-233450-v0.0.31.png`).

This preserves Activity focus for normal input while restoring Sugar's global
semantic navigation actions. GTK3 remains a separate process/Space.

The follow-up `0071` patch dismisses the Frame overlay before F1–F4 changes the
desktop level. A live F6→F3 sequence now returns to a clear GTK4 Home ring in
`sugar-20260912-234523-v0.0.31.png`.
