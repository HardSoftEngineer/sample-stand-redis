#!/usr/bin/env bash
set -e

#
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
OUTPUT="$SCRIPT_DIR/../docs/stand-state.md"
DATE=$(date -u +"%Y-%m-%d")


# 
if ! [[ -e "$OUTPUT" ]]; then 
    echo "Error, not exist path OUTPUT: $OUTPUT"
    exit -1 
fi


#
echo "# Stand state" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "This file captures the environment state at the time of last verification." >> "$OUTPUT"


# 
echo "" >> "$OUTPUT"
echo "## Host system" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "Generated at: $DATE" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "- OS: $(uname -s)" >> "$OUTPUT"
echo "- Kernel: $(uname -r)" >> "$OUTPUT"
echo "- Architecture: $(uname -m)" >> "$OUTPUT"

if [[ -f /etc/os-release ]]; then
  . /etc/os-release
  echo "- Distribution: $NAME $VERSION" >> "$OUTPUT"
fi


# 
echo "" >> "$OUTPUT"
echo "## Tooling" >> "$OUTPUT"

if command -v docker >/dev/null 2>&1; then
  echo "- Docker Engine: $(docker version --format '{{.Server.Version}}')" >> "$OUTPUT"
else
  echo "- Docker Engine: not installed" >> "$OUTPUT"
fi

if docker compose version >/dev/null 2>&1; then
  echo "- Docker Compose: $(docker compose version --short)" >> "$OUTPUT"
else
  echo "- Docker Compose: not available" >> "$OUTPUT"
fi
