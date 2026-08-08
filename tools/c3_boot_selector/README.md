# C3 boot selector

This device-specific selector switches between the current 0.9.7 tree and the
preserved 0.9.6 tree before openpilot starts. It is intended only for the 2015
Buick Envision C3 installation described in the project handoff.

The stable version is selected automatically after 10 seconds. A legacy boot
that does not start the UI within 180 seconds is rolled back to the stable tree.

Install from the active openpilot tree:

```bash
cd /data/openpilot/tools/c3_boot_selector
./install.sh
```
