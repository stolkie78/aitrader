#!/bin/bash
#
# Run example
docker run -d -v $(pwd)/config/config.json:/app/config.json  -v $(pwd)/config/SOL-EUR.json:/app/trader.json bitvavo-aiscalper:0.1 

