# CEN4908C - Computer Engineering Design 2
# Project: Parking Availability System 
#
# Last modified: 04/08/25
#
# Arguments:
#   [1] absolute path to folder containing .csv file with data
#   Optional:
#   'start=': 0-indexed entry point to read data, inclusive
#   'end=': 0-indexed termination point to read data, not inclusive
#
# Description:
#   Takes in path to folder containing '.csv' file with hardware benchmark data.
#	Assumes hardware benchmark data is formatted properly from a given hw_benchmark .csv file (see hw_benchmark.sh). 
#   Stores plots in the corresponding folder path.
#   Prints basic statistical information: data timespan, min, max, average, 
#   

import os, sys, argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()