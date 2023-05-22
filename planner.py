import heapq

class State:
    def __init__(self, dbase: dict[str, bool]) -> None:
        self.dbase = {var: val for var,val in dbase.items()}
    
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
    def __init__(self, preconditions: dict[str, bool], effects: dict[str, bool]) -> None:
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
    
    def put(self, item: State, priority: int, tiebreaker: int):
        heapq.heappush(self.heap, [priority, tiebreaker, item])
    
    def get(self) -> State:
        return heapq.heappop(self.heap)[2]

class Planner:
    def __init__(self, pddl_file : str = '') -> None:
        self.ops = {}
        pass

    def calc_h(self, x: State, y: State) -> int:
        '''
            calculates the hamming distance of two lists
            it assumes that the lists are not in order. 
        '''
        return self.calc_h_helper(x,y) + self.calc_h_helper(y,x)

    def calc_h_helper(self, x: State, y: State) -> int:
        '''
            returns the number of propositions that are not
            the same between two given states. It counts a difference
            if the proposition in x is either not in y or labled as false in y.
            It will not evaulate a proposition of x if labled as false.
        '''
        distance = 0
        for var, val in x.dbase.items():
            if val:
                if var not in y.dbase or not y.dbase[var]:
                    distance = distance + 1
        return distance

    def make_plan_astar(self, milestones : list[State]) -> list[Operation]:
        '''
            Add the initial state to the opened list
            While open is not empty
                state_analyzed = first in open.
                if state is final_state, return state.
        '''
        #initalize
        start = milestones[0]
        goal = milestones[-1]
        g = 0
        h = self.calc_h(start, goal)
        open_states = PriorityQueue()
        open_states.put(start, h, 0)
        closed_states = list()
        visited : dict[State, State] = {} 
        c = 1

        while not open_states.empty():
            current = open_states.get()
            if all(var in current.dbase and current.dbase[var] == val for var, val in goal.dbase.items()):
                return self.getPath(visited, goal, start)
            
            closed_states.append(current)
            for name,op in self.ops.items():
                if op.check(current):
                    print("applying" , name)
                    new_state = op.apply(current)
                    if new_state not in closed_states and new_state not in [s[2] for s in open_states.heap]:
                        g = g + 1
                        if name == 'moveToR2': g = g + 1
                        h = self.calc_h(new_state, goal)
                        open_states.put(new_state, g + h, c)
                        c += 1
                        visited.update({new_state : current})
        return []

    def getPath(self, visited: dict[State:State], goal:State, start:State):
        '''
            generates for a given state-to-state dictionary after A* is run
        '''
        current = goal
        path = list()
        while not all(var in current.dbase and current.dbase[var] == val for var, val in start.dbase.items()):
            path.append(current)
            current = visited[current]
        path.append(current)
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
    
if __name__ == '__main__':
    '''
        main function for testing purposes
    '''
    x = State({'p': True, 'q': False})
    y = State({'p': True, 'q': True})
    P = Planner()
    op1 = Operation({'p': True, 'q': False, 'r': False}, dict())
    op2 = Operation({'q': False}, dict())

    assert op1.check(x) == True
    assert op1.check(y) == False

    # operation-dev
    assert op1.check_strict(x) == False
    assert op1.check_strict(y) == False
    assert op2.check_strict(x) == True
    assert op2.check_strict(y) == False

    #heuristic-dev
    '''      
    S1 {p}
    S2 {p, q}
    '''
    assert P.calc_h(x,y) == 1

    '''
    S1 {p, x}
    S2 {p, q}
    '''
    x.dbase.update({'r': True})
    assert P.calc_h(x,y) == 2

    '''
    Ensures that the function will handle the case where even if the state is strictly
    represented, it will not count the value
    S1 {p, x}
    S2 {p, q}
    '''
    y.dbase.update({'s': False})
    assert P.calc_h(x,y) == 2

    '''
    Ensures that if a state is represented as true in one state and false in the other,
    it will be counted.
    S1 {p, x, s}
    S2 {p, q}
    '''
    x.dbase.update({'s': True})
    assert P.calc_h(x,y) == 3

    #A*-dev
    P.init_test()

    a = State({'inR1':True,'inR2':False,'R1Clean':False,'R2Clean':False})
    b = State({'inR1':False,'inR2':True,'R1Clean':True,'R2Clean':True})
    c = State({'inR1':True,'inR2':False,'R1Clean':False,'R2Clean':False})
    sol = P.make_plan_astar([a,b])

    #print out solution
    print(*[var.dbase for var in sol], sep = "\n")
'''
                    if new_state in open_states:
                        if new_cost <= new_state in open_states:
                            open_states.remove(new_state)
                    if new_state in closed:
                        if new_cost <= new_state in closed:
                            closed_states.'''

    
