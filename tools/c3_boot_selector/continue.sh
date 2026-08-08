#!/usr/bin/bash

/data/c3_boot_selector/boot_select.sh

cd /data/openpilot
exec ./launch_openpilot.sh
