# GTK4 Write formatting pass — 2026-10-05

Write now has a bounded formatting workflow: Bold, Italic, and Heading
actions, an explicit Select all action for keyboard/accessibility-friendly
button operation, and Clear formatting. The document model keeps raw UTF-8 for
unformatted objects. Once formatting is used, the Journal payload becomes a
stable `aspartame-write-v1` JSON object containing the UTF-8 text and spans.

Read accepts that payload and displays its text, preserving the object model
across the two GTK4 Activities. Existing raw text objects and the Chirality
UTF-8 object path remain unchanged.

Real guest qualification:

```text
write-format-roundtrip=PASS bold-persist=PASS read-interoperability=PASS cleanup=PASS
```

The follow-up host sweep also found and fixed a GTK4 callback crash when
`Clear formatting` was activated with no selection: GTK4 can return an empty
selection tuple, which is now handled as a normal whole-document fallback.
The GTK4 host suite passes `470` tests after the fix.

This is bounded rich-text progress, not a FULL PORT claim. ODT/AbiWord
document-format breadth, media embedding, and collaboration remain open.
