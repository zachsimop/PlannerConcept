from planner import *
from plannerUtils import del_rob_state_format, block_state_format

#Block Example
P = Planner(PlannerType.block)

#States
a = [['A', 'C', 'B'], [], []]
b = [[], [], ['A', 'C', 'B']]
c = [[], ['B', 'C'], ['A']]

#Solve and Print
P.make_plan_astar([a,b])
print("-------------* BLOCK *-------------\n")
P.print_sol()
gen_openai_story([], True, PlannerType.block)
#Delivery Robot
P.set_type(PlannerType.del_rob)

a = State({'r11': True, 'w24': True, 'w14': True})
b = State({'r31': True})
c = State({'r29': True})

#Solve and Print
P.make_plan_astar([a,b])
print("\n\n-------------* DELIVERY ROBOT *-------------\n")

P.print_sol()
print(P.format_plan(del_rob_state_format, False))
print(P.format_plan(del_rob_state_format))
