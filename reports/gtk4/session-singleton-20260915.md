# Modern Space session ownership — 2026-09-15

The GTK4 runner now serializes ownership of the private Casilda compositor with
`$GTK4_RUNTIME_ROOT/gtk4-session.lock`.

Live guest verification:

    primary runner: started
    secondary runner: exit code 1
    secondary output: GTK4 preview session already running
    shell count after refusal: 1

This prevents duplicate modern shells from competing for the same fullscreen
Activity surface, which was the cause of the observed loading-placeholder
state during earlier Count retests.
