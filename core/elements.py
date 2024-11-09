import json
import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt



class Signal_information(object):
    def __init__(self, signal_power: float, path: list):
        self._signal_power = signal_power
        self._noise_power = 0.0
        self._latency = 0.0
        self._path = path



    @property
    def signal_power(self):
        return self._signal_power

    def update_signal_power(self, delta_signal_power):
        self._signal_power += delta_signal_power


    @property
    def noise_power(self):
        return self._noise_power

    @noise_power.setter
    def noise_power(self, new_noise_power):
        self._noise_power = new_noise_power

    def update_noise_power(self, delta_noise_power):
        self._noise_power += delta_noise_power


    @property
    def latency(self):
        return self._latency

    @latency.setter
    def latency(self, new_latency):
        self._latency = new_latency

    def update_latency(self, delta_latency):
        self._latency += delta_latency



    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, new_path):
        self._path = new_path

    def update_path(self):
        self._path.pop(0)





class Node(object):
    def __init__(self, data_input: dict):
        self._label = data_input['label']
        self._position = tuple(data_input['position'])
        self._connected_nodes = data_input['connected_nodes']
        self._successive = {}


    @property
    def label(self):
        return self._label


    @property
    def position(self):
        return self._position


    @property
    def connected_nodes(self):
        return self._connected_nodes


    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, new_successive):
        self._successive.update(new_successive)


    def propagate(self, signal_information: Signal_information):

        # Check if there are nodes left in the path and if the first node in the signal's path matches the current node
        if signal_information.path and signal_information.path[0] == self.label:

            # Remove the current node
            signal_information.update_path()

            # Check if there are more nodes to visit
            if signal_information.path:
                next_node_label = signal_information.path[0]

                # Only propagate if the next node exists in _successive dictionary
                if next_node_label in self._successive:
                    self._successive[next_node_label].propagate(signal_information)






class Line(object):
    def __init__(self, label_line:str, length_line: float):
        self._label_line = label_line
        self._length_line = length_line
        self._successive = {}


    @property
    def label(self):
        return self._label_line

    @property
    def length(self):
        return self._length_line


    @property
    def successive(self):
        return self._successive

    @successive.setter
    def successive(self, new_successive):
        self._successive.update(new_successive)


    def latency_generation(self):
        speed_of_light = 3e8 # [m]/[s]
        latency =  self._length_line / ((2/3) * speed_of_light)
        return latency

    def noise_generation(self, signal_power: float):
        noise = 1e-9 * self._length_line * signal_power
        return noise


    def propagate(self, signal_information: Signal_information):

        # Update the signal information with latency and noise
        signal_information.update_latency(self.latency_generation())
        signal_information.update_noise_power(self.noise_generation(signal_information.signal_power))

        # Retrieve the next node from the path, if available, and propagate if it exists in `successive`
        if signal_information.path:
            next_node_label = signal_information.path[0]
            if next_node_label in self._successive:
                self._successive[next_node_label].propagate(signal_information)



class Network(object):
    def __init__(self, file='nodes.json'):
        self._nodes = {}
        self._lines = {}

        with open(file, 'r') as file:
            data = json.load(file)

            # Create Node instances and add them to the _nodes dictionary
            for label, node_information in data.items():
                node_data = {
                    'label': label,
                    'position': tuple(node_information['position']),
                    'connected_nodes': node_information['connected_nodes']
                }
                node = Node(node_data)
                self.nodes[label] = node


            # Create Line instances between connected nodes and add them to the _lines dictionary
            for node_label, node in self._nodes.items():
                for connected_node_label in node.connected_nodes:
                    if connected_node_label in self._nodes:
                        pos1, pos2 = node.position, self._nodes[connected_node_label].position
                        line_length = math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
                        line_label = f"{node_label}{connected_node_label}"
                        line = Line(line_label, line_length)
                        self._lines[line_label] = line

    @property
    def nodes(self):
        return self._nodes

    @property
    def lines(self):
        return self._lines



    def draw(self):
        for node_label, node in self._nodes.items():
            # Plot the node
            plt.plot(node.position[0], node.position[1], 'bo', markersize=8)

            # Add the label next to the node
            plt.text(node.position[0] + 0.1, node.position[1] + 0.1, node_label, fontsize=15, ha='left', color='black', fontweight='bold')

            # Connections to other nodes
            for next_node_label in node.connected_nodes:
                pos1 = node.position
                pos2 = self._nodes[next_node_label].position
                plt.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 'k-', lw=1)

        plt.title('Network Topology')
        plt.xlabel('X Position')
        plt.ylabel('Y Position')
        plt.grid(True)
        plt.show()


    # find_paths: given two node labels, returns all paths that connect the 2 nodes
    # as a list of node labels. Admissible path only if cross any node at most once

    def find_paths(self, start_label, end_label, visited=None):

        if visited is None:
            visited = []

        visited.append(start_label)
        paths = []

        if start_label == end_label:
            return [visited]

        for next_node in self._nodes[start_label].connected_nodes:
            if next_node not in visited:
                new_paths = self.find_paths(next_node, end_label, visited.copy())
                for path in new_paths:
                    #paths.append([start_label] + path)
                    paths.append(path)

        return paths




    # connect function set the successive attributes of all NEs as dicts
    # each node must have dict of lines and viceversa
    def connect(self):
        for node_label, node in self._nodes.items():
            for connected_label in node.connected_nodes:
                line_label = f"{node_label}{connected_label}"

                if line_label in self._lines:
                    node.successive[connected_label] = self._lines[line_label]
                    self._lines[line_label].successive[connected_label] = self._nodes[connected_label]



    # propagate signal_information through path specified in it
    # and returns the modified spectral information
    def propagate(self, signal_information: Signal_information):
        start_node = signal_information.path[0]
        if start_node in self._nodes:
            self._nodes[start_node].propagate(signal_information)

        return signal_information






