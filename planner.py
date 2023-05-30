from plannerUtils import *
from pipelines    import *
import json

class Planner:

    def __init__(self, name : str = None, dom_file : str = None) -> None:
        self.name = name
        self.ops = {}
        self.sol = []
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

            current = open_states.get()
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
    
    def init_test(self):
        
        #TEST OPS DEFINITION
        #cleanRl
        self.ops.update({'cleanR1':
                         Operation(
                             #precondictions
                             {'inR1' : True, 'R1Clean': False},
                             #effects
                             {'R1Clean' : True})
                         })

        #cleanR2
        self.ops.update({'cleanR2':
                         Operation(
                             {'inR2' : True, 'R2Clean': False},
                             {'R2Clean' : True})
                         })

        #MoveR1
        self.ops.update({'moveToR1':
                         Operation(
                             {'inR2' : True},
                             {'inR2' : False, 'inR1' : True})
                         })
        

        #MoveR2
        self.ops.update({'moveToR2':
                             Operation(
                                 {'inR1' : True},
                                 {'inR1' : False, 'inR2' : True})
                         })
                         
        #self.ops.append()
        
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
            #self.sol[0].op += " |s| " #uncomment to mark start and ends in plan
            #self.sol[-1].op += " |g| "
            print(*[var.op for var in self.sol], sep = "\n")
        else:
            print("No Solution")
    def sol_to_string(self) -> str:
        if self.sol:
            sol_str = ""
            for var in self.sol: sol_str += (" " + var.op) 
            return sol_str
        else:
            print("No Solution")
            return None


    
