from planner import *

def run_tests():
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
    b = State({'R2Clean' : True, 'inR1':True,'inR2':True,})
    c = State({'inR1':True,'inR2':False,'R1Clean':False,'R2Clean':False})

    d = State({'r23': True, 'w24': True, 'w14': True})
    e = State({'r25': True})
    f = State({'r25': True})
    g = State({'r51': True, 'b44': True})

    #State Equality tests
    #assert a == c
    assert a != b
    # gen_del_rob_ex()
    #tmp = load_few_shot_examples('./domain_examples/few-shot-examples.json')
    gen_block_ex()
    P.load_domain('./domain_examples/block-domain.json')

    #solve and print
    P.make_plan_astar([d,e])
    P.print_sol()
    sol_str = P.sol_to_string()
    '''
    gen_openai_story([{'genre'   : "histrical fiction",
                       'subject' : "John Muir",
                       'details' : "The main character dies",
                       'plan'   : sol_str}])
    '''

if __name__ == '__main__': run_tests()
