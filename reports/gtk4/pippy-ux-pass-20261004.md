# GTK4 Pippy UX pass — 2026-10-04

## Result

The packaged GTK4 sweep showed Pippy's editor and output workspace collapsed
into an effectively blank surface. The activity already had a bounded runner,
examples, input, and cancellation controls, but the nested body container
prevented the primary panes from receiving the available height.

Pippy now places its title, side-by-side editor/output grid, and status
directly in the expanding Activity root. The code editor and output frame
therefore occupy the workspace at normal Sugar dimensions, with Run, Stop,
example selection, reset, and program input kept beneath the editor.

## Verification

The pushed change was syntax-checked and the GTK4 preview was rebuilt:

```text
GTK4 toolkit, Casilda, sugar-ext, Jarabe, and datastore preview build: PASS
```

Pippy launched through the real Journal D-Bus path in the headless GTK4 shell.
The initial 1920x1080 capture showed the expanded editor and output panes; its
SHA-256 was
`5573611906ed4f7c15d79ee779f9ce6f655ce52684ffe438ce84f30137eae911`.

A headless QEMU click on `Run` executed the default Python program. The
follow-up 1920x1080 capture showed:

```text
Hello from Pippy!
Python number 1
Python number 2
Python number 3
Finished
```

Its SHA-256 was
`04922260e2f52297e491e15ccd25f7e97d16c213df9b51352018f180ade8e7b1`.

## Boundary

Pippy remains a `FUNCTIONAL PORT`, not a `FULL PORT`. The bounded local
runner is not a security sandbox, and full upstream editor/runtime breadth
remains open. No GTK3 package was removed.
