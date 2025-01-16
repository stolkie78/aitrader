#!/bin/bash
#
# Shell script to run a Docker container with a specified config
#
# Usage: ./run_scalper.sh <config_name>
#

CONFIG="${1}"

if [ -z "$CONFIG" ]; then
  echo "Usage: $0 <config_name>"
  exit 1
fi

echo "Running Docker container with configuration: $CONFIG"

mkdir -p $(pwd)/data/${CONFIG}
touch $(pwd)/data/${CONFIG}/bot_status.json
touch $(pwd)/data/${CONFIG}/transactions.json

docker run --name scalper_${CONFIG} -d \
  -v $(pwd)/config/config.json:/app/config.json \
  -v $(pwd)/config/${CONFIG}.json:/app/scalper.json \
  -v $(pwd)/config/slack.json:/app/slack.json \
  bitvavo-scalper:latest
sleep 30
docker logs scalper_${CONFIG}
