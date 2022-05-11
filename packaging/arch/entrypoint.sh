#!/bin/bash

sudo chown -R builder /build
chmod -R a+rw /build

if [ -d "/rescreen" ]; then
  sudo chown -R builder /rescreen
  chmod -R a+rw /rescreen
fi

su builder -c "python3 create_arch_package.py $*"