#!/usr/bin/bash

ROOT=/data/c3_boot_selector
sleep 180

[[ "$(cat "$ROOT/active_version" 2>/dev/null)" == "legacy" ]] || exit 0
pgrep -x ui >/dev/null && exit 0

echo "legacy UI did not start; restoring stable version" >&2
C3_SWITCH_AT_BOOT=1 "$ROOT/switch_version.sh" stable || exit 1
sudo reboot
