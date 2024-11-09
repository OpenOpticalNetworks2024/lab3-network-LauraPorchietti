import json
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from core.elements import Signal_information, Network
import math


# Exercise Lab3: Network

ROOT = Path(__file__).parent.parent
INPUT_FOLDER = ROOT / 'resources'
file_input = INPUT_FOLDER / 'nodes.json'


# Load the Network from the JSON file, connect nodes and lines in Network.
# Then propagate a Signal Information object of 1mW in the network and save the results in a dataframe.
# Convert this dataframe in a csv file called 'weighted_path' and finally plot the network.
# Follow all the instructions in README.md file

# Initialize the network from the provided JSON file
network = Network(file_input)

# Connect all nodes and lines within the network
network.connect()

paths_results = []
signal_power = 1e-3 # [W]

# Loop over all pairs of nodes in the network, we only consider paths between different nodes
for source in network.nodes:
    for destination in network.nodes:
        if source != destination:

            paths = network.find_paths(source, destination)
            print(f"All possible paths from {source} to {destination}:")

            for path in paths:
                # Print all possible paths between all possible node couples
                print(" -> ".join(path))
                string_path = '->'.join(path)

                # Signal_information object instance
                signal_information = Signal_information(signal_power, path)
                # Signal propagation through the network along the specified path
                signal = network.propagate(signal_information)

                total_latency = signal.latency
                total_noise = signal.noise_power
                snr_db = 10 * math.log10(signal.signal_power / total_noise)
                paths_results.append({
                    'Path': string_path,
                    'Total Latency (s)': total_latency,
                    'Total Noise (W)': total_noise,
                    'SNR (dB)': snr_db
                })

# Creating dataframes from the results and converting to a CSV file
df = pd.DataFrame(paths_results)
df.to_csv('weighted_path.csv', index=False)

# Network topology plot
network.draw()

