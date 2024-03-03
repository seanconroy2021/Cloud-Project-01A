#!/bin/bash
# This script is used to clean up the workspace after running the program.
rm -f ./data/*.pem
rm -f ./data/*.jpeg
rm -f ./data/index.html
rm -f ./data/setupConfig.json
rm -f ./data/url.txt
rm -rf logs
mkdir logs
