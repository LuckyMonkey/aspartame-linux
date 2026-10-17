# GTK4 About my Computer inventory — 2026-10-17

The GTK4 preview now has a native `AboutComputer` control-panel section. It
uses a small read-only inventory provider for `/etc/os-release`, `/proc`, DMI,
`lspci`, environment, and Python/platform metadata. Optional probes fail closed
to `Not available`, and the view exposes a refresh action without dumping
terminal output into the UI.

## Evidence

- Focused GTK4/About/standalone tests: `21 passed`.
- Full host gate: `578 passed`.
- ISO: `aspartame-2026.10.17-x86_64.iso`.
- ISO SHA-256: `ebff439e18fb7709dadd6965c7bd74b1a2e5e059d8a81f990b43637fa8509302`.
- Embedded squashfs SHA-256 matches the build staging squashfs:
  `b5e4c3030a890b3693918fa9288ffbb1c319114d79f76fc261ae063f02cceffb`.
- Packaged preview archive SHA-256:
  `5e196b1ef3908fb17054e279f3a6b4cdbf39c4958133977aa1bbf28a990f4978`.
- Final staged source contains `import cpsection.aboutcomputer` and the four
  native overlay files under `gtk4-overlay/src/cpsection/aboutcomputer/`.

The guest-side preview rebuild was not claimed in this pass because the
development VM's passwordless `aspartame` account rejects SSH password login;
the ISO staging step applies the same checked-in registration patch to the
exported source before packaging. A fresh guest visual capture of Settings →
About my Computer remains the next runtime acceptance step.
