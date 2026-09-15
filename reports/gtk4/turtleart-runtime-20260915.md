# TurtleBlocks GTK4 runtime evidence — 2026-09-15

The guest round-trip probe `scripts/sugar-gtk4-turtleart-roundtrip.py` passed
against the running GTK4 preview:

```text
turtleart-roundtrip=PASS resume=PASS cleanup=PASS
```

The probe launches `org.laptop.TurtleArtActivity` through the Journal/Shell
services, finds the activity in the guest AT-SPI tree by its real process ID,
stops it, seeds a JSON Journal object containing turtle position, heading, and
line data, relaunches that object, verifies the restored visible status text,
and confirms process/bus cleanup. This establishes a FUNCTIONAL PORT for the
bounded drawing workflow; it does not claim full upstream TurtleBlocks parity.

The root cause fixed in this pass was a property collision: `SimpleActivity`
already owns the `canvas` property, so the drawing widget now uses the private
`_drawing_area` name and the activity root remains the Casilda canvas.
