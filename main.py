from planner import *
from plannerUtils import del_rob_state_format, block_state_format
from pipelines import gen_openai_story, gen_llama_story
import pickle

# Pickle data formated as:
# [ [Plan1 w/ state, Plan1 w/out state] [Plan2 w/ state, Plan2 w/out state] ]
file = open('./finalPlans.pkl', 'wb')
plans =[]

#Block Example
print("-------------* BLOCK *-------------\n")
P = Planner(PlannerType.block)

# Ex1
a = [['A', 'B', 'C', 'D'], [], []]
b = [[], [], ['A', 'B', 'C', 'D']]
P.make_plan_astar([a,b])
new_plan = P.format_plan(block_state_format)
print(new_plan)
plans.append([new_plan, P.format_plan(block_state_format, False)])

# Ex2
a = [['A', 'B'], [], ['C', 'D']]
b = [[], [], ['C', 'D', 'A', 'B']]
P.make_plan_astar([a,b])
new_plan = P.format_plan(block_state_format)
print(new_plan)
plans.append([new_plan, P.format_plan(block_state_format, False)])

# Ex3
a = [['A', 'B', 'C'], [], []]
b = [[], ['A', 'B', 'C'], []]
c = [[], [], ['A', 'B', 'C']]
P.make_plan_astar([a,b,c])
new_plan = P.format_plan(block_state_format)
print(new_plan)
plans.append([new_plan, P.format_plan(block_state_format, False)])

# Ex4
a = [['A', 'B', 'C'], [], []]
b = [['A'], ['B'], ['C']]
P.make_plan_astar([a,b])
new_plan = P.format_plan(block_state_format)
print(new_plan)
plans.append([new_plan, P.format_plan(block_state_format, False)])

# Ex5
a = [['A', 'B', 'C'], [], []]
b = [['A'], ['B'], ['C']]
c = [[], [], ['A', 'B', 'C']]
P.make_plan_astar([a,b,c])
new_plan = P.format_plan(block_state_format)
print(new_plan)
plans.append([new_plan, P.format_plan(block_state_format, False)])

#Delivery Robot
print("\n\n-------------* DELIVERY ROBOT *-------------\n")
P.set_type(PlannerType.del_rob)

# Ex 1
a = State({'r11': True, 'w24': True, 'w14': True, 'w34':True, 'w44': True})
b = State({'r51': True})
P.make_plan_astar([a,b])
new_plan = P.format_plan(del_rob_state_format)
print(new_plan + "\n")
plans.append([new_plan, P.format_plan(del_rob_state_format, False)])

# Ex 2
a = State({'r34': True, 'b21': True})
b = State({'r33': True, 'b33': True})
P.make_plan_astar([a,b])
P.print_sol()
new_plan = P.format_plan(del_rob_state_format)
print(new_plan + "\n")
plans.append([new_plan, P.format_plan(del_rob_state_format, False)])

# Ex 3
a = State({'r21': True, 'w22': True, 'w34': True, 'w23':True, 'w36': True, 'b11': True})
b = State({'r35': True, 'b35': True})
P.make_plan_astar([a,b])
new_plan = P.format_plan(del_rob_state_format)
print(new_plan + "\n")
plans.append([new_plan, P.format_plan(del_rob_state_format, False)])

# Ex 4
a = State({'r11': True, 'w24': True, 'w14': True, 'w34':True, 'w44': True})
b = State({'r13': True})
c = State({'r22': True})
d = State({'r54': True})
P.make_plan_astar([a,b,c,d])
new_plan = P.format_plan(del_rob_state_format)
print(new_plan + "\n")
plans.append([new_plan, P.format_plan(del_rob_state_format, False)])

# Ex 5
a = State({'r11': True,
           'w22': True, 'w23': True, 'w24':True,
           'w32': True, 'w33': True, 'w34':True,  })
b = State({'r54': True})
c = State({'r11': True})
P.make_plan_astar([a,b,c])
new_plan = P.format_plan(del_rob_state_format)
print(new_plan + "\n")
plans.append([new_plan, P.format_plan(del_rob_state_format, False)])

# Ex 6
a = State({'r11': True, 'b51': True, 'b15': True,
           'w22': True, 'w23': True, 'w24':True,
           'w32': True, 'w33': True, 'w34':True,  })
b = State({'r11': True, 'b31': True, 'b35': True, })
P.make_plan_astar([a,b])
new_plan = P.format_plan(del_rob_state_format)
print(new_plan)
plans.append([new_plan, P.format_plan(del_rob_state_format, False)])

pickle.dump(plans, file)
file.close()
