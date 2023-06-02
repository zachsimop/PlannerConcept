'''
Defines the classes leveraged in Planner. Mostly used for the A* algorithm
'''

import heapq
import json
import os
from enum import Enum
class PlannerType(Enum):
    del_rob = 0
    block = 1

class State:
    def __init__(self, dbase: dict[str, bool]) -> None:
        self.dbase = {var: val for var,val in dbase.items()}
        self.op = None

    def __hash__(self):
        # there's probably a better option than this hash, but it should work and ensure that
        # multiple State objects with the same database are treated as equivalent
        return hash(tuple(self.dbase.items()))

    def __eq__(self, rhs):
        try:
            assert isinstance(rhs, State)
        except AssertionError as e:
            print(rhs)
            raise e
        return self.dbase == rhs.dbase
        
class Operation:
    def __init__(self, preconditions: dict[str, bool], effects: dict[str, bool], name : str = None) -> None:
        self.name = name
        self.pre = {var: val for var,val in preconditions.items()}
        self.eff = {var: val for var,val in effects.items()}

    def check(self, x: State) -> bool:
        '''
            Check whether the operation can be applied to State x, requiring only that all True
            variables in self.pre are present and True in State x. If a variable p is False in
            self.pre, x may either not explicitly list p or it may list p as False.
        '''
        for var, val in self.pre.items():
            if val:
                if var not in x.dbase or not x.dbase[var]:
                    return False
            else:
                if var in x.dbase and x.dbase[var]:
                    return False
        return True
                
    def check_strict(self, x: State) -> bool:
        '''
            Check whether the operation can be applied to State x, requiring that all False
            variables in self.pre are explicitly False in State x
        '''
        return all(var in x.dbase and x.dbase[var] == val for var, val in self.pre.items())
    
    def apply(self, x: State) -> State:
        new_state = State(x.dbase)
        for var, val in self.eff.items():
            new_state.dbase[var] = val
        return new_state
    
class PriorityQueue:
    def __init__(self):
        self.heap =  list()
    
    def empty(self) -> bool:
        return not self.heap
    
    def put(self, state: State, priority: int, c: int):
        heapq.heappush(self.heap, [priority, c, state])
    
    def get(self) -> State:
        return heapq.heappop(self.heap)
    
    def states(self) -> list():
        '''
            Return a list of the states in the priority queue
        '''
        return [val[2] for val in self.heap]

def gen_del_rob_ex(output_file='./domain_examples/del-robot-domain.json'):
    domain = {"name": "delivery-robot",
              "operators": []
              }
    
    board_dim = 5
    for i in range(1, board_dim+1):
        for j in range(1, board_dim+1):
            # movement operators for square i,j
            for d_i in [-1,1]:
                if 1 <= i + d_i <= board_dim:
                    op = {"name": f'move-{i}{j}-{i+d_i}{j}',
                          "pre": {f'r{i}{j}' : True, f'w{i+d_i}{j}' : False},
                          "eff": {f'r{i}{j}' : False,
                                  f'r{i+d_i}{j}': True}}
                    domain['operators'].append(op)
            for d_j in [-1,1]:
                if 1 <= j + d_j <= board_dim:
                    op = {"name": f'move-{i}{j}-{i}{j+d_j}',
                          "pre": {f'r{i}{j}' : True, f'w{i}{j+d_j}' : False},
                          "eff": {f'r{i}{j}' : False,
                                  f'r{i}{j+d_j}': True}}
                    domain['operators'].append(op)

            # pickup and dropoff operators for square i,j
            op = {"name": f'pickup-{i}{j}',
                  "pre": {f'r{i}{j}' : True,
                          f'b{i}{j}' : True,
                          'h' : False},
                  "eff": {f'b{i}{j}' : False,
                          'h': True}}
            domain['operators'].append(op)
            op = {"name": f'dropoff-{i}{j}',
                  "pre": {f'r{i}{j}' : True,
                          f'b{i}{j}' : False,
                          'h' : True},
                  "eff": {f'b{i}{j}' : True,
                          'h': False}}
            domain['operators'].append(op)


    with open(output_file, 'w') as fout:
        fout.write(json.JSONEncoder().encode(domain))

def del_rob_state_format(state : State) -> str:
    output = ''
    output += 'Present Location: '
    for var, is_true in state.dbase.items():
        if var.startswith('r') and is_true:
            output += f'({var[1]},{var[2]})' + ' ; '
            break

    output += f"{'' if state.dbase.get('h', False) else 'not '}holding an object ; "

    output += 'Object locations: '
    for var, is_true in state.dbase.items():
        if var.startswith('b') and is_true:
            output += f'({var[1]},{var[2]})' + ','
    output = output[:-1] + ' ; '

    output += 'Wall locations: '
    for var, is_true in state.dbase.items():
        if var.startswith('w') and is_true:
            output += f'({var[1]},{var[2]})' + ','
    output = output[:-1]

    return output

def gen_block_ex(output_file='./domain_examples/block-domain.json'):
    domain = {"name": "block",
              "operators": []
              }
    ascii_offset = 96
    uid = 0
    num_of_piles = 3
    block_dim = 5
    # for each block type
    for i in range(1, block_dim + 1):
        # for each pile move combo
        for j in range(1, num_of_piles + 1):
            for k in range(1, num_of_piles + 1):
                # Do not generate moves from pile j to itself
                if j != k:
                    # for possible block combos at pile(k)
                    # 0 included to incoperate the possibility of no blocks
                    # being in the pile
                    for l in range(0, block_dim + 1):
                        if i != l:
                            for m in range(0, block_dim + 1):
                                b1 = chr(i + ascii_offset)
                                b2 = chr(l + ascii_offset)
                                b3 = chr(m + ascii_offset)
                                op = {"name": f'move-{b1}-{j}-{k}-{uid}',
                                      "pre": {f'{b1}t{j}' : True,            # does block a cap pile j
                                              f'{b1}{b2}' : True,            # is block a on block b
                                              f'{b3}t{k}' : True,            # does block c cap pile k
                                              },
                                      "eff": {f'{b2}t{j}' : True,            # block b becomes top of pile j
                                              f'{b1}t{j}' : False,           # block a no longer caps pile j
                                              f'{b1}t{k}' : True,            # block a now caps pile k
                                              f'{b1}{b2}' : False,           # a is no longer on b
                                              f'{b1}{b3}' : True,            # a is now on c
                                              f'{b3}t{k}' : False,           # c is no longer on top
                                              }}
                                domain['operators'].append(op)
                                uid += 1

    with open(output_file, 'w') as fout:
        fout.write(json.JSONEncoder().encode(domain))

def block_state_format(state : State) -> str:
    output = ''
    for i in range(1, 4):
        output += f'Pile {i}: '
        for var, is_true in state.dbase.items():
            if f't{i}' in var and is_true:
                b = var[0]
                if b == "`":
                    output += "Empty "
                else:
                    output += var[0] + ","
                    while b != '`':
                        for val, is_true in state.dbase.items():
                            if b == val[0] and val[1] != 't' and is_true:
                                b = val[1]
                                output += val[1] + ","
                    output = output[:-3] + " "
    return output

def load_few_shot_examples(ex_file : str = ''):
    if not os.path.exists(ex_file):
            raise FileNotFoundError(f'Cannot load domain: {ex_file} does not exist')

    with open(ex_file, 'r', encoding="utf8") as fin:
        j_obj = json.JSONDecoder().decode(fin.read())

    return j_obj['examples']
