#!/bin/bash
#
# Run example
if [ -z "$1"]; then
    echo "Welke config wil gebruiken?"
else
    CONFIG="${1}"
fi

docker run -d -v $(pwd)/config/config.json:/app/config.json -v $(pwd)/config/${CONFIG}.json:/app/trader.json -n scalper_${CONFIG} bitvavo-trader:latest
docker logs trader_${CONFIG}
