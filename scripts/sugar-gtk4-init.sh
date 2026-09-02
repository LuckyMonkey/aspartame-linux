#!/usr/bin/env bash
set -euo pipefail

if ! grep -qx 'IMAGE_ID=aspartame' /etc/os-release; then
    echo 'This launcher is guest-only; run it inside the Aspartame development VM.' >&2
    exit 2
fi

root=${1:-${GTK4_ROOT:-/home/aspartame/Development/gtk4-preview}}
mkdir -p "$root/sources" "$root/build" "$root/logs"

clone_at() {
    local name=$1 url=$2 ref=$3 sha=$4
    local path="$root/sources/$name"
    if [ -e "$path" ] && [ ! -d "$path/.git" ]; then
        echo "refusing non-git path: $path" >&2
        exit 1
    fi
    if [ ! -d "$path/.git" ]; then
        git clone --filter=blob:none --no-checkout "$url" "$path"
    fi
    git -C "$path" fetch --depth=1 origin "$ref" >/dev/null
    git -C "$path" checkout --detach "$sha" >/dev/null
    printf '%s\t%s\t%s\t%s\n' "$name" "$url" "$ref" \
        "$(git -C "$path" rev-parse HEAD)"
}

pins_tmp=$(mktemp)
printf '# name\turl\trequested-ref\tresolved-sha\tdate\n' > "$pins_tmp"
printf '# name\turl\trequested-ref\tresolved-sha\tdate\n'

declare -a specs=(
    'sugar|https://github.com/sugarlabs/sugar.git|refs/pull/1106/head|f84a2d514dbbcab6e30c810b00088f47870e04a5'
    'sugar-toolkit-gtk4|https://github.com/sugarlabs/sugar-toolkit-gtk4.git|refs/pull/35/head|74f6a05a4921c27d0892bc22845fd4d4a60f4119'
    'sugar-artwork|https://github.com/sugarlabs/sugar-artwork.git|refs/heads/master|3c4854d3eec0ba9b02a9ad139462fd559e6c027d'
    'sugar-ext|https://github.com/sugarlabs/sugar-ext.git|refs/heads/main|563760e726fb33443dba5a9ce2c67b005da897d2'
    'sugar-datastore|https://github.com/sugarlabs/sugar-datastore.git|refs/heads/master|7aa97e791432d26007a9f16d4214b2085380edec'
    'casilda|https://gitlab.gnome.org/jpu/casilda.git|refs/heads/main|cecb869ce390e13ebdecdca9953731d3a3f3aa73'
    'calculate-activity|https://github.com/rythmlongia/calculate-activity.git|refs/heads/gtk4-layout-fix|1ff50e724dc1d53f685cbe2bd54295ff04f8795f'
    'log-activity|https://github.com/Inuth0603/log-activity.git|refs/heads/port-to-gtk4-dev|b4c43c4dee10f4e52677ec367276e847a0b4edb7'
    'browse-activity|https://github.com/Inuth0603/browse-activity.git|refs/heads/testing|c4489279fe7631d972ba110ff7e0d04a27e645c4'
    'imageviewer-activity|https://github.com/Inuth0603/imageviewer-activity.git|refs/heads/gtk4-port|87fedc07a2d15416b8f450db3f727eeb22de1b09'
    'terminal-activity|https://github.com/Inuth0603/terminal-activity.git|refs/heads/gtk4-port|1425071905ece054b039205ae70b7f7208fe367e'
)

for spec in "${specs[@]}"; do
    IFS='|' read -r name url ref sha <<< "$spec"
    line=$(clone_at "$name" "$url" "$ref" "$sha")
    printf '%s\t%s\n' "$line" "$(date -u +%Y-%m-%d)" >> "$pins_tmp"
    printf '%s\t%s\n' "$line" "$(date -u +%Y-%m-%d)"
done
mv "$pins_tmp" "$root/PINS.tsv"
