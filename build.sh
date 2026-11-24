#!/bin/bash
set -e
cd "$(dirname "$0")/simplesim-3.0"
sed -i "s|#include <termio.h>|#include <termios.h>|" target-pisa/syscall.c
make clean || true
make config-pisa
make sim-outorder CC="gcc -fcommon" OFLAGS="-O2"
ls -l sim-outorder
