#!/usr/bin/env bash
set -e

#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

docker compose -f "$SCRIPT_DIR/../docker/docker-compose.yml" up -d 
