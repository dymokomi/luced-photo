#!/bin/sh
# luced-photo's checks: every module's tests, Luce and Base (luc test); presets saved,
# replaced, renamed and deleted in a fresh catalog (tests/presets_check.lucb); the app
# built and drawing three frames on a fresh library (--smoke); and, when luce-raw's
# sample raws are checked out beside it, an import of a Leica DNG and a Fuji RAF
# twice, the second finding both already in the library (tests/import_check.lucb).
# Everything is made in a scratch folder, HOME included, so no real library or the
# remembered last library is touched.
set -eu
cd "$(dirname "$0")"
luc test
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
luce-base build tests/presets_check.lucb --native -o "$work/presets_check"
"$work/presets_check" "$work/presets"
luce build src/main.luc -o "$work/luced-photo"
HOME="$work" "$work/luced-photo" --library "$work/Smoke.library" --smoke
echo "PASS smoke: the app drew three frames"
samples=../luce-raw/build/samples
if [ -f "$samples/leica_m240.dng" ]; then
    luce-base build tests/import_check.lucb --native -o "$work/import_check"
    "$work/import_check" "$work/Import.library" "$samples/leica_m240.dng" "$samples/fuji_xt2_xtrans_14c.raf" > "$work/import.txt"
    grep -q "^2 photos" "$work/import.txt" || { cat "$work/import.txt"; echo "FAIL import: expected 2 photos"; exit 1; }
    grep -q "skipped" "$work/import.txt" || { cat "$work/import.txt"; echo "FAIL import: the second import added duplicates"; exit 1; }
    echo "PASS import: 2 photos, the second import skipped both"
else
    echo "import skipped: no sample raws in $samples"
fi
