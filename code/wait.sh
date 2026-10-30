#!/bin/bash
set -a; . ~/neuro/keys.env; set +a
sleep 60
for i in $(seq 1 120); do s=$(kaggle kernels status $1 2>&1 | tail -1); echo "$(date +%T) $s"; case "$s" in *COMPLETE*|*ERROR*|*CANCEL*) break;; esac; sleep 45; done
rm -rf ~/neuro/out/$2; mkdir -p ~/neuro/out/$2; cd ~/neuro/out/$2; kaggle kernels output $1 -p . >/dev/null 2>&1; ls -R | head -30
