#!/usr/bin/env bash
set -e

#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


f_uv_init() {
  echo "uv init"
  return_install=0

  curl -LsSf https://astral.sh/uv/install.sh | sh
  return_install=$?
  echo "return_install: $return_install"
  
  echo "update"
  source ~/.bashrc

  if ! uv2 --version >/dev/null 2>&1; then
    echo "error, after install not find uv"
    return_install=-1
  fi

  return "$return_install"
}


# 
if uv --version >/dev/null 2>&1; then
  echo "uv version: $(uv --version --short)"
else
  echo "uv tool not find, start install"
  f_uv_init
fi

