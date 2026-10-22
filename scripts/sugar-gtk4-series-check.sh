#!/usr/bin/env bash
set -euo pipefail

# Apply the GTK4 preview patch series to a pristine tree built from the
# pinned baseline SHAs and report how it lands. This answers a question the
# ordinary build cannot: sugar-gtk4-build.sh works against a checkout that
# previous runs already mutated, and treats a patch as satisfied when it
# reverse-applies, so it can report success while the series itself no
# longer reconstructs the preview.
#
# Guest-only: it needs the source checkouts that sugar-gtk4-init.sh made.

if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This check is guest-only; run it inside the Aspartame development VM.' >&2
    exit 2
fi

repo=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
root=${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}
patch_dir=${GTK4_PATCH_DIR:-$repo/patches/gtk4-preview}
work=${GTK4_SERIES_WORK:-$(mktemp -d)}
trap '[ -n "${GTK4_SERIES_WORK:-}" ] || rm -rf "$work"' EXIT

echo 'Aspartame GTK4 preview series check'

# Mirror sugar-gtk4-build.sh's routing table so the two cannot drift.
route() {
    case "$(basename "$1")" in
        0002-*) echo sugar-ext ;;
        0014-*|0170-*) echo sugar-datastore ;;
        0029-*|0171-*) echo log-activity ;;
        0137-*|0138-*) echo casilda ;;
        0300-*) echo sugar ;;
        0301-*) echo sugar-toolkit-gtk4 ;;
        0003-*) echo SKIP ;;
        *) echo UNROUTED ;;
    esac
}

for name in sugar sugar-toolkit-gtk4 sugar-ext sugar-datastore log-activity casilda; do
    src="$root/sources/$name"
    test -d "$src/.git" || { echo "missing checkout: $src" >&2; exit 2; }
    mkdir -p "$work/$name"
    git -C "$src" archive HEAD | tar -xf - -C "$work/$name"
    (cd "$work/$name" && git init -q && git add -A &&
        git -c user.email=series@check -c user.name=series commit -qm baseline)
    printf 'baseline %-22s %s\n' "$name" "$(git -C "$src" rev-parse --short HEAD)"
done

exact=0; fuzzed=0; failed=0; skipped=0
for patch in "$patch_dir"/*.patch; do
    [ -f "$patch" ] || continue
    name=$(basename "$patch")
    target=$(route "$patch")
    if [ "$target" = UNROUTED ]; then
        echo "  FAIL: $name is not routed"; failed=$((failed + 1)); continue
    fi
    if [ "$target" = SKIP ]; then
        skipped=$((skipped + 1)); continue
    fi
    dir="$work/$target"
    if git -C "$dir" apply --check "$patch" 2>/dev/null; then
        git -C "$dir" apply "$patch"; exact=$((exact + 1))
    elif (cd "$dir" && patch -p1 --dry-run --fuzz=5 <"$patch" >/dev/null 2>&1); then
        (cd "$dir" && patch -p1 --fuzz=5 <"$patch" >/dev/null 2>&1)
        echo "  fuzz: $name"
        fuzzed=$((fuzzed + 1))
    else
        echo "  FAIL: $name -> $target"
        failed=$((failed + 1))
    fi
done

broken=0
while IFS= read -r file; do
    python3 -m py_compile "$file" 2>/dev/null || {
        echo "  DOES NOT COMPILE: ${file#$work/}"; broken=$((broken + 1)); }
done < <(find "$work/sugar/src" "$work/sugar-toolkit-gtk4/src" -name '*.py')

echo "exact=$exact fuzz=$fuzzed failed=$failed skipped=$skipped uncompilable=$broken"
if [ "$broken" -ne 0 ]; then
    echo 'Result: FAIL (a clean rebuild would not import)'
    exit 1
fi
if [ "$fuzzed" -ne 0 ] || [ "$failed" -ne 0 ]; then
    echo 'Result: FAIL (the series must apply exactly; regenerate 0300/0301)'
    exit 1
fi
echo 'Result: PASS (the series reconstructs the preview exactly)'
