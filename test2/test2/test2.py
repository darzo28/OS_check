import sys
import csv
import os
import subprocess
import networkx as nx
import pygraphviz as pgv
from enum import Enum

class Types(str, Enum):
    Mealy = 'mealy'
    Moore = 'moore'

def read_mealy(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.DiGraph()
        states = reader.__next__()[1:]
        for line in reader:
            in_signal = line[0]  
            transitions = line[1:]
            for transition, from_state in zip(transitions, states):
                to_state, out_signal = transition.split('/')
                graph.add_edge(from_state, to_state, in_signal=in_signal, out_signal=out_signal)
        return graph

def read_moore(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        graph = nx.DiGraph()
        out_signals = reader.__next__()[1:]
        states = reader.__next__()[1:]
        for state, out_signal in zip(states, out_signals):
            graph.add_node(state, out_signal=out_signal)
        for line in reader:
            in_signal = line[0]
            to_states = line[1:]
            for from_state, to_state in zip(states, to_states):
                graph.add_edge(from_state, to_state, in_signal=in_signal)
        return graph

def read_state_machine(option, file):
    if option == Types.Mealy.value:
        return read_mealy(file)
    else:
        return read_moore(file)

def read_sequence(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        in_signals = reader.__next__()
        out_signals = reader.__next__()
        return in_signals, out_signals

def draw_graph(path, graph, option):
    for state_from, state_to, signals in graph.edges(data=True):
        in_signal = signals.get('in_signal')
        out_signal = signals.get('out_signal') if option == Types.Mealy.value else graph.nodes[state_to]['out_signal']
        signals['label'] = f'{in_signal}/{out_signal}' if option == Types.Mealy.value else in_signal

    if option == Types.Moore.value:
        states_mapping = {}
        for state, out in graph.nodes(data=True):
            out_signal = out['out_signal']
            states_mapping.update({state: f'{state}/{out_signal}'})
        graph = nx.relabel_nodes(graph, states_mapping)

    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw(path)

def process(graph, in_signals, option):
    current_state = list(graph.nodes)[0]
    output_sequence = []

    for symbol in in_signals:
        next_state = None
        for neighbor in graph.neighbors(current_state):
            edge_data = graph.get_edge_data(current_state, neighbor)
            if edge_data['in_signal'] == symbol:
                next_state = neighbor
                out_signal = edge_data['out_signal'] if option == Types.Mealy.value else graph.nodes[next_state]['out_signal']
                output_sequence.append(out_signal)
                break
            
        current_state = next_state
        
    return output_sequence

def check(sequence, graph, option, order):
    in_signals, out_signals = read_sequence(sequence)
    out_sequence = process(graph, in_signals, option)
       
    if out_signals == out_sequence:
        print(f'Test {order} passed')
    else:
        print(f'Test {order} failed')

def execute(execute_file, option):
    i = 0
    command = ['python3', execute_file] if execute_file.endswith('py') else [execute_file]

    for input_file in os.listdir(f'..\{option}\sequence'): 
        sequence = f'..\{option}\sequence\{input_file}'
        in_path = f'..\{option}\input\{input_file}'
        output = f'..\{option}\output\output{i}.csv'

        input_path = f'..\{option}\graphs\input{i}.png'
        input_graph = read_state_machine(option, in_path)
        draw_graph(input_path, input_graph, option)

        subprocess.check_call(command + [option, in_path, output])
        
        output_path = f'..\{option}\graphs\output{i}.png'
        output_graph = read_state_machine(option, output)

        check(sequence, output_graph, option, i)
        draw_graph(output_path, output_graph, option)
        i += 1

def exit_help():
    print('lab2.py <execute file> <mealy|moore>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) == 2:
        execute(args[0], args[1])
    elif len(args) == 1:
        execute(args[0], Types.Mealy.value)
        execute(args[0], Types.Moore.value)
    else:
        exit_help()      
