from plannerUtils import *
from pipelines    import *
from enum import Enum
import json
class PlannerType(Enum):
    del_rob = 0
    block = 1

class Planner:

    def __init__(self, type : PlannerType = None, name : str = None, dom_file : str = None) -> None:
        self.name = name
        self.ops = {}
        self.sol = []
        self.type = None
        if type is not None:
            self.set_type(type)
        else:
            self.set_type(PlannerType.del_rob)

        self.type = type
        if dom_file is not None:
            self.load_domain(dom_file)

    def calc_h(self, x: State, y: State) -> int:
        '''
            calculates hamming distance
        '''
        distance = 0
        for var, val in x.dbase.items():
            if val:
                if var not in y.dbase or not y.dbase[var]:
                    distance += 1
            else:
                if var in y.dbase and y.dbase[var]:
                    distance += 1
        return distance

    def make_plan_astar(self, milestones : list[State]) -> list[Operation]:
        '''
            Add the initial state to the opened list
            While open is not empty
                state_analyzed = first in open.
                if state is final_state, return state.
        '''

        #initalize
        milestones    = self.handle_input(milestones)
        open_states   = PriorityQueue()
        closed_states = list()
        visited       = {}
        start         = milestones[0]
        goal          = milestones[1]
        g = 0
        c = 0
        open_states.put(start, self.calc_h(start, goal), c)
        c += 1

        #main loop
        while not open_states.empty():

            current = open_states.get()[2]
            if self.compare_goal(current, goal):
                visited.update({goal : current})
                self.sol = self.getPath(visited, goal, start)[::-1]
                if len(milestones) != 2:
                    #self.sol[-1].op += " |m| " #Uncomment to track milestones in plan print
                    self.sol += self.make_plan_astar(milestones[1:])
                return self.sol
            
            closed_states.append(current)
            g += 1
            for name,op in self.ops.items():
                if op.check(current):
                    new_state = op.apply(current)
                    if new_state not in closed_states and new_state not in open_states.states():    
                        open_states.put(new_state, g + self.calc_h(goal, new_state), c)
                        c += 1
                        new_state.op = name
                        visited.update({new_state : current})
        self.sol = []
        return self.sol

    def getPath(self, visited: dict[State:State], goal:State, start:State):
        '''
            generates for a given state-to-state dictionary after A* is run
        '''
        current = goal
        path = list()
        current = visited[current]
        while not current == start:
            path.append(current)
            current = visited[current]
        return path

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
        # if self.name is None:
        #     self.name = j_obj.get('name', None)

        for op in j_obj['operators']:
            op_name = op.get('name', None)
            self.ops.update({op_name : Operation(op['pre'], op['eff'], op_name)})

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

    def compare_goal(self, current: State, goal: State) -> bool:
        for var, val in goal.dbase.items():
            if val:
                if var not in current.dbase or not current.dbase[var]:
                    return False
            else:
                if var in current.dbase and current.dbase[var]:
                    return False
        return True
    
    def print_sol(self):
        if self.sol:
            print(*[(self.format_sol(var.op), var.dbase) for var in self.sol], sep = "\n")
        else:
            print("No Solution")

    def format_sol(self, op):
        if self.type is PlannerType.block:
            res = op[0]
            c = 0
            i = 0
            while c < 4:
                i+=1
                if op[i] == "-": c+=1
                res += op[i]
            op = res[:-1]
            return op
        return op


    def sol_to_string(self) -> str:
        if self.sol:
            sol_str = ""
            for var in self.sol: sol_str += (" " + var.op) 
            return sol_str
        else:
            print("No Solution")
            return None

    def generate_block_props(self, piles: list[list[str]]) -> dict:
        props = {}
        i = 1
        #generate top propositions
        for var in piles:
            if var:
                props.update({f'{var[0].lower()}t{i}' : True})
                l = len(var)
                for j in range(0, l-1):
                    props.update({f'{var[j].lower()}{var[j+1].lower()}' : True})
                props.update({f'{var[l-1].lower()}`' : True})
            else:
                props.update({f'`t{i}': True})
            i += 1
        return props

    def set_type(self, new_type):

        if new_type is PlannerType.block and (self.type is None or self.type is not PlannerType.block):
            self.load_domain('./domain_examples/block-domain.json')
            self.type = PlannerType.block
            return

        if new_type is PlannerType.del_rob and (self.type is None or self.type is not PlannerType.del_rob):
            self.load_domain('./domain_examples/del-robot-domain.json')
            self.type = PlannerType.del_rob
            return

    def handle_input(self, input) -> list[State]:
        if isinstance(input[0], list): #handles the case where the user inputs a lisst for block domain
            if self.type is PlannerType.block:
                block_props = []
                for var in input:
                    block_props.append(State(self.generate_block_props(var)))
                return block_props
        else: return input



    
