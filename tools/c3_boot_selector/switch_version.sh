#!/usr/bin/bash
set -u

ROOT=/data/c3_boot_selector
STATE_FILE="$ROOT/active_version"
ACTIVE_PATH=/data/openpilot
STABLE_INACTIVE=/data/openpilot-current-0.9.7
LEGACY_INACTIVE=/data/openpilot-gm-0.9.6-backup-20260716
SWAP_PATH=/data/.openpilot-version-swap

desired="${1:-}"
if [[ "$desired" != "stable" && "$desired" != "legacy" ]]; then
  echo "usage: $0 stable|legacy" >&2
  exit 2
fi

active="$(cat "$STATE_FILE" 2>/dev/null || echo stable)"
if [[ "$active" != "stable" && "$active" != "legacy" ]]; then
  echo "invalid active version: $active" >&2
  exit 3
fi

if [[ "$desired" == "$active" ]]; then
  exit 0
fi

if pgrep -x ui >/dev/null && [[ "${C3_SWITCH_AT_BOOT:-0}" != "1" ]]; then
  echo "refusing to switch while the openpilot UI is running" >&2
  exit 4
fi

if [[ "$active" == "stable" ]]; then
  incoming="$LEGACY_INACTIVE"
  outgoing="$STABLE_INACTIVE"
else
  incoming="$STABLE_INACTIVE"
  outgoing="$LEGACY_INACTIVE"
fi

for launcher in "$ACTIVE_PATH/launch_openpilot.sh" "$incoming/launch_openpilot.sh"; do
  if [[ ! -x "$launcher" ]]; then
    echo "missing launcher: $launcher" >&2
    exit 5
  fi
done

if [[ -e "$outgoing" || -e "$SWAP_PATH" ]]; then
  echo "version swap destination already exists" >&2
  exit 6
fi

mv "$ACTIVE_PATH" "$SWAP_PATH" || exit 7
if ! mv "$incoming" "$ACTIVE_PATH"; then
  mv "$SWAP_PATH" "$ACTIVE_PATH"
  exit 8
fi
if ! mv "$SWAP_PATH" "$outgoing"; then
  mv "$ACTIVE_PATH" "$incoming"
  mv "$SWAP_PATH" "$ACTIVE_PATH"
  exit 9
fi

printf '%s\n' "$desired" > "$STATE_FILE.tmp"
mv "$STATE_FILE.tmp" "$STATE_FILE"
sync
