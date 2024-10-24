import sys
import csv
import os
import networkx as nx
from enum import Enum

DELIMITER = '/'
EMPTY = '-'
IN_SIGNAL = 'in_signal'
OUT_SIGNAL = 'out_signal'
OUT_FORMATS = [
    'bmp', 'fig', 'gif', 'jpe', 'jpeg', 
    'jpg', 'json', 'pdf', 'pic', 'plain',
    'png', 'svg', 'tif', 'tiff'
]

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

def read_state_machine(option, file):
    if option == Types.Mealy.value:
        return read_mealy(file)
    else:
        return read_moore(file)

def draw_graph(path, graph, option):
    for state_from, state_to, signals in graph.edges(data=True):
        in_signal = signals.get(IN_SIGNAL)
        out_signal = signals.get(OUT_SIGNAL) if option == Types.Mealy.value else graph.nodes[state_to][OUT_SIGNAL]
        signals['label'] = f'{in_signal}/{out_signal}' if option == Types.Mealy.value else in_signal
    
    if option == Types.Moore.value:
        states_mapping = {}
        for state, out in graph.nodes(data=True):
            out_signal = out[OUT_SIGNAL]
            states_mapping.update({state: f'{state}/{out_signal}'})
        graph = nx.relabel_nodes(graph, states_mapping)
        

    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw(path)

def exit_help():
    print('Invalid arguments')
    print('draw.py <mealy|moore> <input file> <output file>')
    sys.exit(0)

def execute(args):
    if not os.path.isfile(args[1]):
        print(f'No such file: "{args[1]}"')
        sys.exit(0)

    if not args[2].endswith(tuple(OUT_FORMATS)):
        out_formats = ', '.join(OUT_FORMATS)
        print(f'Output format not recognized. Use one of: {out_formats}')
        sys.exit(0)

    graph = read_state_machine(args[0], args[1])
    draw_graph(args[2], graph, args[0])

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) == 3 and (args[0] == Types.Mealy.value or args[0] == Types.Moore.value):
        execute(args)
        os.startfile(args[2])
    else:
        exit_help()   
