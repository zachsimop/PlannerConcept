import json
import os

class State:
    def __init__(self, dbase: dict[str, bool]) -> None:
        self.dbase = {var: val for var,val in dbase.items()}
    
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
            new_state[var] = val

class Planner:
    def __init__(self, name : str = None, dom_file : str = None) -> None:
        self.name = name
        self.ops = []

        if dom_file is not None:
            self.load_domain(dom_file)
            

    def load_domain(self, dom_file : str = '') -> None:
        '''
            Loads operations from a file and adds all operations to the calling object's list of
            operations. Initially only expected to accept purely propositional operations written
            in JSON. Future extensions should successfully parse predicate operations as well, but
            that is outside the scope of this project. When extended to allow for predicate logic,
            JSON should be replaced with PDDL format. Extensions for this project may include
            supporting PPDDL (probabilistic PDDL) if determined to facilitate exploration, MA-PDDL
            (Multi-Agent PDDL) if generated narratives should follow multiple agents (characters)
        '''
        if not os.path.exists(dom_file):
            raise FileNotFoundError(f'Cannot load domain: {dom_file} does not exist')
        
        with open(dom_file, 'r') as fin:
            j_obj = json.JSONDecoder().decode(fin.read())

        #File sourced name should be overridden by name given to instance at creation
        if self.name is None:
            self.name = j_obj.get('name', None)

        for op in j_obj['operators']:
            op_name = op.get('name', None)
            self.ops.append(Operation(op['pre'], op['eff'], op_name))

    def save_domain(self, dom_file : str = '') -> None:
        j_obj = {}
        if self.name is not None:
            j_obj['name'] = self.name

        j_obj['operators'] = []
        for op in self.ops:
            op_obj = {}
            if op.name is not None:
                op_obj['name'] = op.name
            op_obj['pre'], op_obj['eff'] = op.pre, op.eff
            j_obj['operators'].append(op_obj)

        with open(dom_file, 'w') as fout:
            fout.write(json.JSONEncoder().encode(j_obj))
        

    def make_plan_astar(self, milestones : list[State]) -> list[Operation]:
        pass

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
    
if __name__ == '__main__':
    '''
        main function for testing purposes
    '''
    x = State({'p': True, 'q': False})
    y = State({'p': True, 'q': True})
    op1 = Operation({'p': True, 'q': False, 'r': False}, dict())
    op2 = Operation({'q': False}, dict())

    assert op1.check(x) == True
    assert op1.check(y) == False

    assert op1.check_strict(x) == False
    assert op1.check_strict(y) == False
    assert op2.check_strict(x) == True
    assert op2.check_strict(y) == False
