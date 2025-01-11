#!/bin/bash

# Number of tries
tries=100

# Output file to store timings
output_file="timing_results.txt"
> "$output_file"  # Clear the file

# Run the command and collect timings
for ((i=1; i<=tries; i++))
do
    echo "Run $i:" >> "$output_file"
    (/usr/bin/time -f "%e" ./bin/hqc-256) 2>> "$output_file"
done

# Calculate the average time
echo "Calculating average..."
awk '/^[0-9]+(\.[0-9]+)?$/ {sum += $1; count++} END {if (count > 0) print "Average Time:", sum / count}' "$output_file"

