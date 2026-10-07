#!/bin/sh
# luced-photo's checks: every module's tests, Luce and Base (luc test), then the test
# programs in tests/<name>/main, each with HOME in a scratch folder as luc will give
# them: presets in a fresh catalog; an import done twice on luce-raw's sample raws
# (skipped without them); the app drawing three frames on a fresh library. Until luc
# test runs tests/<name>/main itself (LUCE_LANG); then this file goes.
set -eu
cd "$(dirname "$0")"
luc test
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
for name in presets import; do
    luce-base build "tests/$name/main.lucb" --native -o "$work/$name"
    mkdir "$work/home-$name"
    HOME="$work/home-$name" "$work/$name"
done
luce build tests/smoke/main.luc -o "$work/smoke"
mkdir "$work/home-smoke"
HOME="$work/home-smoke" "$work/smoke"
