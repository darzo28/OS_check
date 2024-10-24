import sys
import csv
import os
import subprocess
import networkx as nx
from enum import Enum

DELIMITER = '/'
EMPTY = '-'
IN_SIGNAL = 'in_signal'
OUT_SIGNAL = 'out_signal'

class Types(str, Enum):
    Mealy = 'mealy'
    Moore = 'moore'

def read_mealy(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.MultiDiGraph()
        states = [EMPTY if state == '' else state for state in reader.__next__()[1:]]
        graph.add_nodes_from(states)
        for line in reader:
            in_signal = line[0]  
            transitions = line[1:]
            for transition, from_state in zip(transitions, states):
                split_result = [EMPTY] if transition == '' else transition.split(DELIMITER)
                to_state, out_signal = split_result if len(split_result) == 2 else [split_result[0], DELIMITER.join(split_result[1:])]
                out_signal = EMPTY if out_signal == '' else out_signal
                graph.add_edge(from_state, to_state, in_signal=in_signal, out_signal=out_signal)
        return graph

def read_moore(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.MultiDiGraph()
        out_signals = [EMPTY if signal == '' else signal for signal in reader.__next__()[1:]]
        states = [EMPTY if state == '' else state for state in reader.__next__()[1:]]
        for state, out_signal in zip(states, out_signals):
            graph.add_node(state, out_signal=out_signal)
        for line in reader:
            in_signal = line[0]
            to_states = [EMPTY if state == '' else state for state in line[1:]]
            for from_state, to_state in zip(states, to_states):
                graph.add_edge(from_state, to_state, in_signal=in_signal)
        return graph

def read_sequence(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        return [signal for signal in reader.__next__() if signal != '']

def print_sequence(file, in_signals, out_signals):
    with open(file, newline='\n', mode='w') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(in_signals)
        writer.writerow(out_signals)
    
    print(f'Completed: {out_sequence}')

def process(graph, in_signals, option):
    current_state = list(graph.nodes)[0]
    output_sequence = []

    for symbol in in_signals:
        next_state = None
        for neighbor in graph.neighbors(current_state):
            edge_data = graph.get_edge_data(current_state, neighbor)
            for edge in edge_data.values():
                if edge[IN_SIGNAL] == symbol:
                    next_state = neighbor
                    out_signal = edge[OUT_SIGNAL] if option == Types.Mealy.value else graph.nodes[next_state][OUT_SIGNAL]
                    output_sequence.append(out_signal)
                    break
        
        if next_state == None:
            output_sequence.append(EMPTY)
            print(f'Invalid input sequence or final state reached')
            break
            
        current_state = next_state
        
    return output_sequence

def exit_help():
    print('sequence_generate.py (mealy|moore) <graph filename> <sequence filename>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) != 3:
        exit_help()

    if args[0] == Types.Mealy.value:
        mealy = read_mealy(args[1])
        in_sequence = read_sequence(args[2])
        out_sequence = process(mealy, in_sequence, args[0])
        print_sequence(args[2], in_sequence, out_sequence)
        
    elif args[0] == Types.Moore.value:
        moore = read_moore(args[1])
        in_sequence = read_sequence(args[2])
        out_sequence = process(moore, in_sequence, args[0])
        print_sequence(args[2], in_sequence, out_sequence)

    else:
        exit_help()
