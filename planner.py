class State:
    def __init__(self, dbase: dict[str, bool]) -> None:
        self.dbase = {var: val for var,val in dbase.items()}
    
class Operation:
    def __init__(self, preconditions: dict[str, bool], effects: dict[str, bool]) -> None:
        pass

    def check(self, x: State) -> bool:
        '''
            Apple the operation, requiring only that all True variables in self.pre
            are present and True in State x. If a variable p is False in self.pre,
            x may either not explicitly list p or it may list p as False.
        '''
        pass
                
    def check_strict(self, x: State) -> bool:
        '''
            Apply the operation, requiring that all False variables in self.pre are
            explicitly False in State x
        '''
        pass
    
    def apply(self, x: State) -> State:
        pass

class Planner:
    def __init__(self, pddl_file : str = '') -> None:
        pass

    def make_plan_astar(self, milestones : list[State]) -> list[Operation]:
        pass
    

    