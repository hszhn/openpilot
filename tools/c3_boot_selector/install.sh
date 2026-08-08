#!/usr/bin/bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR=/data/c3_boot_selector
LEGACY_DIR=/data/openpilot-gm-0.9.6-backup-20260716

if [[ ! -x "$LEGACY_DIR/launch_openpilot.sh" ]]; then
  echo "legacy openpilot backup is missing" >&2
  exit 1
fi

mkdir -p "$INSTALL_DIR"
cp "$SOURCE_DIR/main.cpp" "$SOURCE_DIR/c3_boot_selector.pro" "$INSTALL_DIR/"
cp "$SOURCE_DIR/boot_select.sh" "$SOURCE_DIR/switch_version.sh" "$SOURCE_DIR/legacy_watchdog.sh" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR"/*.sh

cd "$INSTALL_DIR"
/usr/lib/qt5/bin/qmake c3_boot_selector.pro
make -j2

if [[ ! -f "$LEGACY_DIR/launch_env.sh.c3-original" ]]; then
  cp "$LEGACY_DIR/launch_env.sh" "$LEGACY_DIR/launch_env.sh.c3-original"
fi
sed -i 's/export AGNOS_VERSION="[^"]*"/export AGNOS_VERSION="10.1"/' "$LEGACY_DIR/launch_env.sh"

printf 'stable\n' > "$INSTALL_DIR/active_version"
if [[ ! -f /data/continue.sh.before-c3-selector ]]; then
  cp /data/continue.sh /data/continue.sh.before-c3-selector
fi
cp "$SOURCE_DIR/continue.sh" /data/continue.sh
chmod +x /data/continue.sh

echo "C3 boot selector installed; it will appear after the next reboot."
