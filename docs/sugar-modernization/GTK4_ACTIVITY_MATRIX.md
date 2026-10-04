# GTK4 Activity matrix

This matrix separates runtime coverage from behavioral parity. The lifecycle
probe proves that a registered bundle can launch through Journal/Casilda,
register its private Activity service, become active in the shell, and stop
without an orphan process. It does not by itself prove a complete port.

| Activities | Runtime coverage | Parity classification |
|---|---|---|
| Help, Count, Calculate, Clock, JAMClock, Image Viewer, Terminal, Browse, Log | 3-cycle Casilda launch/activate/stop evidence | FUNCTIONAL PORT (bounded workflows) |
| Write | 3-cycle launch plus UTF-8 Journal save/resume and save-failure cancellation/retry | FUNCTIONAL PORT |
| Read | 2-cycle launch plus seeded UTF-8 Journal object resume and visible page restoration | FUNCTIONAL PORT |
| Stopwatch | 2-cycle launch plus seeded JSON Journal object resume and visible elapsed-time restoration | FUNCTIONAL PORT |
| Calculate | 2-cycle launch plus seeded Journal expression resume and visible result restoration | FUNCTIONAL PORT |
| Level | 2-cycle launch plus seeded JSON Journal inclination resume and visible readout restoration | FUNCTIONAL PORT |
| Markdown | 2-cycle launch plus seeded UTF-8 Journal source resume and visible editor restoration | FUNCTIONAL PORT |
| Finance | 2-cycle launch plus seeded JSON transaction resume and visible balance restoration | FUNCTIONAL PORT |
| Words | 2-cycle launch plus seeded JSON word resume and visible lookup restoration | FUNCTIONAL PORT |
| Portfolio | 2-cycle launch plus seeded JSON title/body resume and visible title restoration | FUNCTIONAL PORT |
| Jukebox | 2-cycle launch plus seeded JSON playlist resume and visible track restoration | FUNCTIONAL PORT |
| Grid Paint | 2-cycle launch plus seeded JSON cell-selection resume and visible summary restoration | FUNCTIONAL PORT |
| Abacus | 2-cycle launch plus seeded JSON rod-value resume and visible value restoration | FUNCTIONAL PORT |
| Pippy | 2-cycle launch plus seeded UTF-8 source resume and visible editor restoration | FUNCTIONAL PORT |
| Typing Turtle | 2-cycle launch plus seeded JSON exercise-index resume and visible prompt restoration | FUNCTIONAL PORT |
| Moon | 2-cycle launch plus seeded JSON phase resume and visible phase restoration | FUNCTIONAL PORT |
| Planets | 2-cycle launch plus seeded JSON selected-planet resume and visible selection restoration | FUNCTIONAL PORT |
| Color My World | 2-cycle launch plus seeded JSON color resume and visible selection restoration | FUNCTIONAL PORT |
| Get Books | 2-cycle launch plus seeded JSON catalog selection resume and visible title restoration | FUNCTIONAL PORT |
| Game Of Life | 2-cycle launch plus seeded JSON live-cell/generation resume and visible summary restoration | FUNCTIONAL PORT |
| Paint | 2-cycle launch plus seeded JSON stroke/color resume and visible status restoration | FUNCTIONAL PORT |
| FotoToon | 2-cycle launch plus seeded JSON caption-canvas resume and visible caption restoration | FUNCTIONAL PORT |
| Mastermind | 2-cycle launch plus seeded JSON guess history resume and visible guess-progress restoration | FUNCTIONAL PORT |
| Poll | 2-cycle launch plus seeded JSON question/choice/vote resume and visible count restoration | FUNCTIONAL PORT |
| Mancala | 2-cycle launch plus seeded JSON board/store/turn resume and visible store restoration | FUNCTIONAL PORT |
| Reversi | 2-cycle launch plus seeded JSON board/player resume and visible score restoration | FUNCTIONAL PORT |
| Jumble | 2-cycle launch plus seeded JSON puzzle-index/answer resume and visible prompt restoration | FUNCTIONAL PORT |
| NumberRush | 2-cycle launch plus seeded JSON round/score resume and visible score restoration | FUNCTIONAL PORT |
| Across and Down | 2-cycle launch plus seeded JSON clue/letters resume and visible clue restoration | FUNCTIONAL PORT |
| IQ | 2-cycle launch plus seeded JSON round resume and visible puzzle-status restoration | FUNCTIONAL PORT |
| Appel Haken | 2-cycle launch plus seeded JSON colour configuration resume and visible solved-state restoration | FUNCTIONAL PORT |
| BallAndBrick | 2-cycle launch plus seeded JSON brick-count resume and visible status restoration | FUNCTIONAL PORT |
| Implode | 2-cycle launch plus seeded JSON block-grid resume and visible remaining-block restoration | FUNCTIONAL PORT |
| PlayGo | 2-cycle launch plus seeded JSON board/turn resume and visible turn restoration | FUNCTIONAL PORT |
| BlockParty | 2-cycle launch plus seeded JSON arrangement resume and visible ordering restoration | FUNCTIONAL PORT |
| Memorize | 2-cycle launch plus seeded JSON card/match resume and visible pair-count restoration | FUNCTIONAL PORT |
| Maze | 2-cycle launch plus seeded JSON position resume and visible position restoration | FUNCTIONAL PORT |
| Last One Loses | 2-cycle launch plus seeded JSON pile resume and visible token-count restoration | FUNCTIONAL PORT |
| Gears | 2-cycle launch plus seeded JSON rotation resume and visible rotation restoration | FUNCTIONAL PORT |
| Connect the Dots | 2-cycle launch plus seeded JSON connection-progress resume and visible prompt restoration | FUNCTIONAL PORT |
| Diamond Fusion | 2-cycle launch plus seeded JSON board/score resume and visible score restoration | FUNCTIONAL PORT |
| TurtleBlocks | 2-cycle launch plus seeded JSON Journal turtle position/heading/lines resume, visible status restoration, and clean stop | FUNCTIONAL PORT |
| Color My World, Level | 3-cycle matrix evidence | COVERAGE IMPLEMENTATION |
| Get Things Done | 2-cycle launch plus seeded JSON Journal task-list resume and clean stop | FUNCTIONAL PORT |

The authoritative class definitions and per-Activity boundaries live in
[`ACTIVITY_PORT_CLASSIFICATION.md`](ACTIVITY_PORT_CLASSIFICATION.md). No
Activity is currently a FULL PORT, and no implemented bundle is being counted
as a PLACEHOLDER merely because it has reduced behavior.

## Porting gate

Use [GTK4_ACTIVITY_RUNBOOK.md](GTK4_ACTIVITY_RUNBOOK.md) for each Activity.
Promotion requires evidence appropriate to the claimed class:

- import/build at the pinned source state;
- Home activation in the running GTK4 preview;
- private Activity D-Bus service and intended surface path;
- real input and accessible controls for the claimed workflow;
- canonical Stop action, process exit, and bus-name release;
- Journal relaunch/resume when the Activity owns persistent state;
- comparison with the stable GTK3 behavior before claiming parity.

The full matrix is a coverage instrument, not a retirement gate. On
2026-10-04, peer presence and Neighborhood rendering were qualified with two
clean packaged headless guests; the remaining collaboration gate is shared
Activity join/action behavior. Other highest-value work is continued
per-Activity parity promotion and the remaining physical-input boundaries.

## UX qualification and first retirement candidates

On 2026-10-03, a headless 1920×1080 QEMU visual pass qualified Portfolio,
Markdown, and Finance after correcting collapsed editor surfaces and the
centered narrow Finance layout. Each passed the visual sweep and two Journal
launch/resume/stop cycles with the GTK4 process, Activity service, accessible
surface, and datastore payload intact. See
[`gtk4-activity-ux-pass-20261003.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261003.md).

These are the first **modern-space retirement candidates**. The GTK4 registry
may hide their GTK3 duplicate from the modern Home view, but the GTK3 bundles
remain installed as fallback/reference. Package removal is deliberately still
blocked on full feature parity, collaboration, and physical-input evidence.

The second UX batch qualified Write, Pippy, Jukebox, and Color My World on the
same date and resolution. Their editor, output, playlist, and color-preview
surfaces now have clear bounds and fill the available Activity area; Pippy,
Jukebox, and Color My World also passed two Journal roundtrip cycles, while
Write passed three launch/activate/stop cycles. They are the next
modern-Space retirement candidates under the same fallback-preserving boundary.

The third UX batch qualified Gears, Moon, Paint, FotoToon, Game Of Life, and
Abacus at 1920×1080. Canvas surfaces now expand into the Activity area with
explicit labels, visible boundaries where useful, and controls placed beside
the work surface. Each passed two Journal roundtrip cycles; the full headless
visual sweep completed 50/50. The roundtrip harnesses also gained a packaged
interpreter fallback instead of depending on a developer-only absolute path.
See [`gtk4-activity-ux-pass-20261004-canvas.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-canvas.md).

The fourth UX batch qualified IQ, Jumble, Appel Haken, and Across and Down at
1920×1080. Their learning tasks now sit in labeled responsive panels rather
than presenting controls as isolated top-aligned widgets; Appel Haken also
uses visible color semantics for its region controls. All four passed two
Journal roundtrip cycles and the full headless sweep remained 50/50. See
[`gtk4-activity-ux-pass-20261004-games.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-games.md).

The fifth UX batch qualified Number Rush, Stopwatch, BlockParty, and Memorize
at 1920×1080. Compact interaction Activities now have labeled expanding work
surfaces, centered controls, and a prominent Stopwatch readout instead of
isolated top-aligned widgets. All four passed two Journal roundtrip cycles and
the full headless sweep remained 50/50. See
[`gtk4-activity-ux-pass-20261004-games2.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-games2.md).

The sixth UX batch qualified Get Things Done at 1920×1080. Its task entry and
task list now have explicit hierarchy and an expanding labeled surface; its
two-cycle Journal probe and the full headless visual sweep remained green.
See [`gtk4-activity-ux-pass-20261004-tasks.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-tasks.md).

The seventh UX batch qualified Log at 1920×1080. Its GTK4 ListBox-based file
browser now preserves a stable detail viewport through a pinned build patch;
the full visual sweep stayed 50/50 and `sugar-gtk4-runtime-check.sh gtk4`
returned `runtime-check=ok`. See
[`gtk4-activity-ux-pass-20261004-log.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-log.md).

The eighth UX batch qualified Get Books, Jukebox, and Words at 1920×1080.
Get Books and Jukebox now use explicit side-by-side content/player regions;
Words uses a centered bounded task card. All three passed the targeted
Journal/D-Bus visual launch/paint/stop sweep (`3/3`) and their focused source
tests. This improves the modern-space presentation while leaving GTK3
fallback/reference bundles in place pending full behavior-parity gates. See
[`gtk4-activity-ux-pass-20261004-library.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-library.md).

The ninth UX batch qualified Markdown and Pippy at 1920×1080. Both now use
explicit side-by-side editing/output workspaces with visible boundaries, and
both passed the targeted visual sweep plus two Journal resume/stop cycles
with seeded payloads. See
[`gtk4-activity-ux-pass-20261004-editors.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-editors.md).

The tenth UX batch qualified PlayGo, Mancala, and Mastermind in the GTK4
development runtime at 1920×1080. Their primary boards now occupy labeled,
expanding Activity work areas with centered game controls; each passed a
Journal resume/cleanup roundtrip and a headless QMP screenshot macro. This is
development-share evidence pending the next packaged ISO rebuild. See
[`gtk4-activity-ux-pass-20261004-games3.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-games3.md).

The packaged follow-up rebuild also fixed a GTK4 ListBox placeholder cleanup
regression in Get Things Done. Two GTD Journal cycles and the complete
catalog visual sweep passed `50/50` shareless at 1920×1080. See
[`packaged-shareless-qualification-20261004-rerun.md`](../../reports/gtk4/packaged-shareless-qualification-20261004-rerun.md).

On 2026-10-04, the packaged/shareless qualification booted the rebuilt ISO
without `/mnt/aspartame-dev`. The complete GTK4 catalog visual sweep passed
`50/50` at 1920×1080, Get Books and Pippy passed two Journal lifecycle cycles
each, and the AT-SPI Spaces action passed with GTK3/GTK4 comparison geometry
of `960+960`. The same image also passed the Sugar health check after carrying
the malformed Journal metadata guard into the system datastore service. See
[`packaged-shareless-qualification-20261004.md`](../../reports/gtk4/packaged-shareless-qualification-20261004.md).

The next source UX batch qualified BallAndBrick, Implode, Last One Loses, Maze,
Poll, Reversi, Clock, JAMClock, and Read for explicit expanding work surfaces
and centered compact controls. Focused source tests and compilation pass; the
rebuilt headless development guest and the final shareless standalone image
both passed the targeted visual sweep (`8/8`, 1920×1080), and the six Journal
roundtrip probes passed on each runtime. The final image also passed the
complete catalog regression sweep `50/50` at 1920×1080. See
[`gtk4-activity-ux-pass-20261004-games4.md`](../../reports/gtk4/gtk4-activity-ux-pass-20261004-games4.md).
