#!/bin/sh
# luced-photo's checks: every module's tests, Luce and Base (luc test); the test
# programs in tests/<name>/main (presets in a fresh catalog; an import done twice on
# luce-raw's sample raws, skipped without them); and the app built and drawing three
# frames on a fresh library (--smoke), with HOME in a scratch folder so the
# remembered last library is not touched. Until luc test runs tests/<name>/main
# itself (LUCE_LANG).
set -eu
cd "$(dirname "$0")"
luc test
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
for name in presets import; do
    luce-base build "tests/$name/main.lucb" --native -o "$work/$name"
    "$work/$name"
done
luce build src/main.luc -o "$work/luced-photo"
HOME="$work" "$work/luced-photo" --library "$work/Smoke.library" --smoke
echo "PASS smoke: the app drew three frames"
