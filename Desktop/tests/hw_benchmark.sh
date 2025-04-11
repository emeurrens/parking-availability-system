#!/bin/bash

# CEN4908C - Computer Engineering Design 2
# Project: Parking Availability System 
#
# Last modified: 04/08/25
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
START_TIME="$(date +%y%m%d%H%M%S)"
TEST_NAME="HW_TEST_${START_TIME}"
CSV_HEADER="TIME,TEMP,CORE_FREQ,CORE_VOLT,THROTTLE_STATE"

end_benchmark() {
    python3 hw_plot.py "${LOCAL_PATH}/hw_benchmark_results/${TEST_NAME}/data.csv"
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

        echo "$TIME,$TEMP,$FREQ,$VOLT,$THROTTLE" >> "data.csv"

        # Print current data
        if (( $count > 0))
        then
            echo -ne "\033[5A"
        fi
        echo -e "\rTemperature: ${TEMP}'C        \nCore Frequency: ${FREQ} Hz     \nVoltage: ${VOLT}V              \nThrottle State: ${THROTTLE}    "
        echo

        # Show loading bar to demonstrate to users that the script is running
        # if (( $count == 5 ))
        # then
        #     echo -ne "\r                              \r"
        #     count=0
        # else
        #     echo -ne "\033[$(($count*2))C. "
        #     ((count++))
        # fi

        ((count++))
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
    touch "data.csv"
    echo $CSV_HEADER > "data.csv"
}

main() {
    cd $LOCAL_PATH
    echo
    echo "Running Pi hardware benchmark test . . ."
    echo "Results can be found in folder '$LOCAL_PATH/hw_benchmark_results/$TEST_NAME'"
    make_results_files
    run_benchmark
}

trap 'echo; cd $LOCAL_PATH; end_benchmark; exit 0' SIGINT
main