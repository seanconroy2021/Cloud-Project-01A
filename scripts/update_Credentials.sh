#!/bin/bash
# Open the credentials file in VSCode
# code $HOME/.aws/credentials

# Run the script 10 times and measure the execution time
for ((i=1; i<=10; i++))
do
    echo "Running acs_1.py - Iteration $i"
    time python ./src/acs_1.py
done
