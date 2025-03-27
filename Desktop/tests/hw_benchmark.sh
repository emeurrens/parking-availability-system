#!/bin/bash

# CEN4908C - Computer Engineering Design 2
# Project: Parking Availability System 
#
# Last modified: 03/27/25
#
# Description:
#	Benchmark polling system commands to read core temperature, voltage, frequency, and throttle state over time.
#   Saves results in folder ./hw_benchmark/HW_TEST_[DateTime]
#   See https://github.com/emeurrens/parking-availability-system/issues/83 for documentation on this feature
#
# Resources:
# - Very useful bash scripting guide: https://mywiki.wooledge.org/BashGuide

REPO_NAME="parking-availability-system"
LOCAL_PATH="$HOME/$REPO_NAME/Desktop/tests"
TEST_NAME="HW_TEST_$(date +%y%m%d%H%M%S)"
CSV_HEADER="TIME,TEMP,CORE_FREQ,CORE_VOLT,THROTTLE_STATE"

end_benchmark() {
    exit 0
    # TODO: Implement python3 script to plot data
    # python3 
}

run_benchmark() {
    echo
    echo "Running benchmark. Press 'Ctrl+C' to stop logging and generate plots."
    echo

    count=0
    while true
    do  
        # Store data entry into .csv
        TIME=$(date +%s)
        TEMP=$(vcgencmd measure_temp | grep -o -E [0-9.]+)          # temp celsius
        VOLT=$(vcgencmd measure_volts core | grep -o -E [0-9.]+)    # volts
        FREQ=$(vcgencmd measure_clock arm | grep -o -E [0-9.]+$)     # hertz
        THROTTLE=$(vcgencmd get_throttled | grep -o -E 0x[0-9.]+)    # hex string representing throttle flags

        echo "$TIME,$TEMP,$FREQ,$VOLT,$THROTTLE" >> "$TEST_NAME.csv"
        
        # Show loading bar to demonstrate to users that the script is running
        if (( $count == 5 ))
        then
            echo -ne "\r                              \r"
            count=0
        else
            echo -n ". "
            ((count++))
        fi

        sleep 1
    done
}

make_results_files() {
    if [[ ! -e "hw_benchmark_results" ]]
    then
        mkdir hw_benchmark_results
    fi
    cd hw_benchmark_results
    mkdir $TEST_NAME
    cd $TEST_NAME
    touch "$TEST_NAME.csv"
    echo $CSV_HEADER > "$TEST_NAME.csv"
}

main() {
    cd $LOCAL_PATH
    echo
    echo "Running Pi hardware benchmark test . . ."
    echo "Results can be found in folder '$LOCAL_PATH/hw_benchmark_results/$TEST_NAME'"
    make_results_files
    run_benchmark
}

trap 'cd $LOCAL_PATH; end_benchmark; exit 0' SIGINT
main