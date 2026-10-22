"""The GTK4 preview series after the 2026-10-22 upstream re-pin.

Sugar and the toolkit each carry one rebased downstream delta (0300/0301).
The individual history lives in patches/gtk4-preview/folded/ for provenance;
these tests keep that history honest about what still ships.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = ROOT / "patches/gtk4-preview"
FOLDED = PATCH_DIR / "folded"
BUILD = (ROOT / "scripts/sugar-gtk4-build.sh").read_text()
INIT = (ROOT / "scripts/sugar-gtk4-init.sh").read_text()
SHIPPED = "\n".join(
    path.read_text(errors="ignore") for path in sorted(PATCH_DIR.glob("030*.patch"))
)

# Folded lines that the rebase removed on purpose, with the reason.
SUPERSEDED = {
    # Upstream style.apply_css_to_widget now scopes CSS itself (0301 header).
    "0026-toolkit-global-css.patch",
    # Upstream CellRendererIcon carries real GObject properties (0301 header).
    "0005-home-cell-renderer-api.patch",
    "0007-home-renderer-signal-compat.patch",
    "0015-toolkit-cell-renderer-props-compat.patch",
    "0016-toolkit-cell-renderer-gobject.patch",
    "0020-toolkit-cell-renderer-scrolling.patch",
    # Upstream palette/palettewindow/palettemenu rewrite was taken whole.
    "0028-toolkit-sugar-interactions.patch",
    "0033-toolkit-palette-menu-activation.patch",
    # Retired by the old build before the re-pin: 0039 (registry filtering
    # superseded), 0063-0065 (forced close superseded by the shell's own
    # Activity close), 0096 (lookup workaround superseded by 0124).
    "0039-home-filter-missing-activities.patch",
    "0063-shell-stop-activity-closes-surface.patch",
    "0064-shell-stop-activity-terminates-process.patch",
    "0065-shell-stop-activity-pid-fallback.patch",
    "0096-registry-get-bundle-modern-override.patch",
}


def _routes(text):
    return set(re.findall(r"^\s+(0\d{3})-\*(?:\|0\d{3}-\*)*\)", text, re.M)) | set(
        re.findall(r"\|(0\d{3})-\*", text)
    )


def test_every_top_level_patch_is_routed_by_the_build():
    ids = {path.name[:4] for path in PATCH_DIR.glob("*.patch")}
    assert ids <= _routes(BUILD), ids - _routes(BUILD)


def test_build_applies_exactly_or_reports_drift():
    assert "--fuzz=0" in BUILD
    assert "--fuzz=5" not in BUILD.split("for patch in")[1].split("\ndone")[0]
    assert "GTK4 preview patch drift" in BUILD
    assert "unrouted GTK4 preview patch" in BUILD


def test_pins_follow_upstream_heads_named_by_the_rebased_patches():
    assert "refs/pull/1106/head|beaae56c23acab8781525319d4da2884082ab0e7" in INIT
    assert "sugar-toolkit-gtk4.git|refs/heads/main|9d86a31862f6d676840ed755f109d4cd5bc7c2c6" in INIT
    assert (PATCH_DIR / "0300-sugar-downstream-on-beaae56.patch").exists()
    assert (PATCH_DIR / "0301-toolkit-downstream-on-9d86a31.patch").exists()


def test_repin_preserves_and_replaces_a_dirty_checkout():
    assert "pre-repin-" in INIT
    assert "checkout --force --detach" in INIT
    assert "clean -fdq" in INIT


def _added_lines(patch_text):
    for line in patch_text.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            body = line[1:].strip()
            if len(body) > 24 and not body.startswith("#"):
                yield body


def test_folded_intent_still_ships():
    """Most substantive lines added by folded patches survive in 0300/0301.

    Later folded patches legitimately rewrite earlier ones, so this is a
    ratio, not an identity: it catches a rebase that silently drops a
    patch's work wholesale.
    """
    shipped = {line[1:].strip() for line in SHIPPED.splitlines()
               if line[:1] in "+ "}
    lost = []
    for patch in sorted(FOLDED.glob("*.patch")):
        if patch.name in SUPERSEDED:
            continue
        added = list(_added_lines(patch.read_text(errors="ignore")))
        if len(added) < 3:
            continue
        kept = sum(1 for line in added if line in shipped)
        if kept / len(added) < 0.25:
            lost.append((patch.name, kept, len(added)))
    assert lost == [], lost


def _class_duplicates(source):
    import ast
    found = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ClassDef):
            seen = set()
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    if item.name in seen and not any(
                            "setter" in ast.unparse(d) or "getter" in ast.unparse(d)
                            for d in item.decorator_list):
                        found.append(f"{node.name}.{item.name}")
                    seen.add(item.name)
    return found


def test_shell_service_defines_each_navigation_action_once():
    """A trailing duplicate silently replaced ShowNeighborhood/ShowGroup with
    versions that neither closed Settings nor cleared the active Activity."""
    patch = (PATCH_DIR / "0300-sugar-downstream-on-beaae56.patch").read_text()
    service = patch.split("+++ b/src/jarabe/view/service.py", 1)[1].split("\ndiff --git", 1)[0]
    for action in ("ShowNeighborhood", "ShowGroup", "ShowControlPanel"):
        assert service.count(f"def {action}(self):") <= 1, action


def test_overlay_and_activities_have_no_shadowed_methods():
    offenders = []
    for path in [*(ROOT / "gtk4-overlay/src").rglob("*.py"),
                 *ROOT.glob("packages/gtk4-*-activity/*.py")]:
        offenders += [f"{path.name}:{name}" for name in
                      _class_duplicates(path.read_text(encoding="utf-8-sig"))]
    assert offenders == [], offenders
