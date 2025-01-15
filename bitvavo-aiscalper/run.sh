#!/bin/bash
#
# Run example
docker run  -v $(pwd)/config/config.json:/app/config.json  -v $(pwd)/config/SOL-EUR.json:/app/scalper.json bitvavo-scalper:latest

