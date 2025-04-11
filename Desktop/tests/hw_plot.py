# CEN4908C - Computer Engineering Design 2
# Project: Parking Availability System 
#
# Last modified: 04/11/25
#
# Arguments:
#   [1] absolute path to .csv file with data
#   Optional:
#   'start=': 0-indexed entry point to read data, inclusive
#   'end=': 0-indexed termination point to read data, not inclusive
#
# Description:
#   Takes in path to .csv file with hardware benchmark data.
#	Assumes hardware benchmark data is formatted properly from a given hw_benchmark .csv file (see hw_benchmark.sh). 
#   Stores plots in the corresponding folder path.
#   Prints basic statistical information: data timespan, min, max, average, 
#   

import os, argparse
import pandas as pd
import matplotlib.pyplot as plt

"""
Prepare parser for parsing arguments
"""
parser = argparse.ArgumentParser(description="Creates plots of and prints statistics from hardware benchmark data")
parser.add_argument('-s', '--start', help="0-indexed entry point to read data starting from the first data entry after the header, inclusive")
parser.add_argument('-e', '--end', help="0-indexed termination point to stop data reading, exclusive")
parser.add_argument('filepath', help="Filepath for .csv")

"""
Parse arguments from script input
"""
args = parser.parse_args()

"""
Find first valid hardware benchmark data files to read
"""
HEADERS = {
    'TIME': "Time (s)", 
    'TEMP': "Temperature (°C)", 
    'CORE_FREQ': "Core Frequency (Hz)", 
    'CORE_VOLT': "Core Voltage (V)", 
    'THROTTLE_STATE': "Throttle State Code"
}

# results=[]
# for root, dirs, files in os.walk(args.filepath):
#     for name in files:
#         if fnmatch.fnmatch(name, '*.csv'):
#             data = pd.read_csv(os.path.join(root,name))
#             if (set(data.columns)==HEADERS.keys()):
#                 results.append(data)

df = pd.read_csv(args.filepath)
if (set(df.columns) != HEADERS.keys()):
    print("Date headers do not match expected values. Terminating script . . . ")
    exit(1)

print(f"Current File Accessed: {args.filepath}\n")

# Adjust entry range according to script args
if (args.start != None):
    df = df[int(args.start):]

if (args.end != None):
    df = df[:int(args.end)]

# Preprocess data for plotting
df['TIME'] = df['TIME'] - df['TIME'][0]
for i in range(df['THROTTLE_STATE'].size):
    df.at[i, 'THROTTLE_STATE'] = int(df['THROTTLE_STATE'][i], 0)

# Plot data and save them in provided path
for column in df.columns[1:df.columns.size-1]:
    plt.figure()
    plt.plot(df['TIME'], df[column], label = column)
    plt.xlabel(HEADERS['TIME'])
    plt.ylabel(HEADERS[column])
    plt.title(f"{HEADERS[column]} over Time")
    plt.grid()
    plt.savefig(f"{os.path.dirname(args.filepath)}/{column}_PLOT.png")
    plt.close()

print("Plots saved successfully.\n")
    
# Print statistics
print("Printing stats . . . \n")
for column in df.columns[1:df.columns.size-1]:
    print(f"{HEADERS[column]}:")
    print(f"    Minimum: {df[column].min()}")
    print(f"    Average: {df[column].mean()}")
    print(f"    Maximum: {df[column].max()}")

# Terminate program
exit(0)