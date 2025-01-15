#!/bin/bash
#
# Run example
docker run -d -v $(pwd)/config/config.json:/app/config.json -v $(pwd)/config/BIG3.json:/app/trader.json bitvavo-aitrader:0.1 

