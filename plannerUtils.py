'''
Defines the classes leveraged in Planner. Mostly used for the A* algorithm
'''

import heapq

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
        return heapq.heappop(self.heap)[2]
    
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
                          "pre": {f'r{i}{j}' : True},
                          "eff": {f'r{i}{j}' : False,
                                  f'r{i+d_i}{j}': True}}
                    domain['operators'].append(op)
            for d_j in [-1,1]:
                if 1 <= j + d_j <= board_dim:
                    op = {"name": f'move-{i}{j}-{i}{j+d_j}',
                          "pre": {f'r{i}{j}' : True},
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

def load_few_shot_examples(ex_file : str = ''):
    if not os.path.exists(ex_file):
            raise FileNotFoundError(f'Cannot load domain: {dom_file} does not exist')
    
    with open(ex_file, 'r') as fin:
        j_obj = json.JSONDecoder().decode(fin.read())

    examples = []
    for ex in j_obj['examples']:
        examples.append({"prompt": ex['prompt'], "story" : ex['story']})

    return examples
