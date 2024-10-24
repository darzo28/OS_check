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

def read_state_machine(option, file):
    if option == Types.Mealy.value:
        return read_mealy(file)
    else:
        return read_moore(file)

def read_sequence(file):
    with open(file, newline='\n') as f:
        reader = csv.reader(f, delimiter=';')
        in_signals = [signal for signal in reader.__next__() if signal != '']
        out_signals = [signal for signal in reader.__next__() if signal != '']
        return in_signals, out_signals

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

def check(sequence, graph, option, order):
    in_signals, out_signals = read_sequence(sequence)
    out_sequence = process(graph, in_signals, option)
       
    if out_signals == out_sequence:
        print(f'Test {order} passed')
    else:
        print(f'Test {order} failed')

def execute(execute_file, option):
    folder_name = option.split('-')[0]
    output_type = option.split('-')[2]
    command = ['python3', execute_file] if execute_file.endswith('py') else [execute_file]

    print(f'Option {option} testing')

    for i in range(len(os.listdir(f'..\{folder_name}\sequence'))): 
        sequence = f'..\{folder_name}\sequence\input{i}.csv'
        in_path = f'..\{folder_name}\input\input{i}.csv'
        output = f'..\{folder_name}\output\output{i}.csv'

        input_path = f'..\{folder_name}\graphs\input{i}.png'
        input_graph = read_state_machine(folder_name, in_path)
        draw_graph(input_path, input_graph, folder_name)

        subprocess.check_call(command + [option, in_path, output])
        
        output_path = f'..\{folder_name}\graphs\output{i}.png'
        output_graph = read_state_machine(output_type, output)

        draw_graph(output_path, output_graph, output_type)
        check(sequence, output_graph, output_type, i)

def exit_help():
    print('lab1.py <execute file> <mealy-to-moore|moore-to-mealy>')
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]

    if len(args) == 2:
        execute(args[0], args[1])
    elif len(args) == 1:
        execute(args[0], 'mealy-to-moore')
        execute(args[0], 'moore-to-mealy')
    else:
        exit_help()      
