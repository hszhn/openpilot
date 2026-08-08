#!/usr/bin/bash

ROOT=/data/c3_boot_selector
SELECTOR="$ROOT/c3-version-selector"

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/var/tmp/weston}"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-wayland-egl}"

"$SELECTOR"
selection=$?

case "$selection" in
  20) desired=legacy ;;
  10) desired=stable ;;
  *)
    echo "version selector failed with status $selection; using stable" >&2
    desired=stable
    ;;
esac

C3_SWITCH_AT_BOOT=1 "$ROOT/switch_version.sh" "$desired" || {
  echo "unable to select $desired; attempting stable fallback" >&2
  C3_SWITCH_AT_BOOT=1 "$ROOT/switch_version.sh" stable
}

if [[ "$(cat "$ROOT/active_version" 2>/dev/null)" == "legacy" ]]; then
  "$ROOT/legacy_watchdog.sh" >/tmp/c3_legacy_watchdog.log 2>&1 &
fi
