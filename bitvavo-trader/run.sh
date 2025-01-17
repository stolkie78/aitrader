#!/bin/bash
#
# Shell script to run a Docker container with a specified config
#
# Usage: ./run_trader.sh <config_name>
#

CONFIG="${1}"

if [ -z "$CONFIG" ]; then
  echo "Usage: $0 <config_name>"
  exit 1
fi

echo "Running Docker container with configuration: $CONFIG"

docker run --name trader_${CONFIG} -d \
  -v $(pwd)/config/config.json:/app/config.json \
  -v $(pwd)/config/${CONFIG}.json:/app/trader.json \
  -v $(pwd)/config/slack.json:/app/slack.json \
  bitvavo-trader:latest
sleep 30
docker logs trader_${CONFIG}
