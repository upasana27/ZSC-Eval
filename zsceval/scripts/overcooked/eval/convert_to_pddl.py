'''
We have the joint policy with (s_t,a_t). Map the a_t's to PDDL type actions with list of preconditions, additions and deletions.

Agent1, Agent 2 (state) - Location, orientation, object

def up(agent):
    current_loc = agent[loc]
    next_loc = current_loc + up_action
    preconditions - next_loc is valid and empty
    if all preconditions are true:
        agent.state[loc] = next_loc
        grid[next_loc] = A
        grid[current_loc] = E
    return pre, effects

no_of_agents = agent_1, agent_2
no_of_objects = has-object?,onion_dispenser, dish_dispenser, onion, dish, soup_dish, serving_station
no_of_oven_states = is_oven, oven_empty, oven_1_onion, oven_2_onion, oven_3-onion, oven_cooking, oven_soup

--------- movement actions -------------
def up(current state):
    loc_all = current_state.grid where loc_all is a 2D grid/array of feature-loc's at each location of the grid
    preconditions - (loc_all[i+1][j] is a valid square) and (loc_all[i+1][j].is_empty) )
    if preconditions(loc_all) = True ; record each of the feature_loc checked as pre
        effects - (loc_all[i+1][j].has_agent[k] == True) and (loc_all[i][j].has_agent[k] == False) and (loc_all[i][j].is_empty == True) and (loc_all[i+1][j].is_empty == False)
        new_loc = effects(current_state) ; this is where we modify current state's grid of loc's, record all the features changed here in eff  
    return pre, eff
---------interact actions ---------------
def interact(current_state):
    agent = current_state.agents[k]
    loc_all = current_state.grid
    interact_with_y, interact_with_x = agent.loc + agent.facing

    ----- pick actions --------
    preconditions - (agent.holding[0] == True) and (loc_all[interact_with_y][interact_with_x].has-object[0] == True)
    object = objects[j] where j is the index such that loc_all[interact_with_y][interact_with_x].has-object[j] == 1
    if preconditions(agent,loc_all): ;record the conditions checked in pre
        effects - (agent.hand-empty = False) and (loc_all[interact_with_y][interact_with_x].has-object[0 and object-th] = False) and (agent.holding[0 and object-th] == True) 
        update agent and loc_all in current state ; record all the features changed in eff
        validate with next_state
        return pre, eff

        
    ------ put actions ---------
    put_object = agent.holding[j] where j is the index such that agent.holding[j] == 1
    ------ put on counter -------
    preconditions - (agent.holding[0] == True) and (loc_all[interact_with_y][interact_with_x].has-object[0] == False) and (loc_all[interact_with_y][interact_with_x].is-counter == True)
    if preconditions(agent,loc_all) = True ; record all the features checked
        effects - (agent.holding[0] = False) and (loc_all[interact_with_y][interact_with_x].has-object[0] == True) and (loc_all[interact_with_y][interact_with_x].has-object[put_object-th] == True)
        update agent and loc_all in current state ; record all the features changed in eff
        validate with next_state
        return pre, eff
    ------ put onion into oven ------
    preconditions - (agent.holding[0] == True) and (put_object == onion) and (loc_all[interact_with_y][interact_with_x].has-object[0] == True) 
                    and (loc_all[interact_with_y][interact_with_x].is-oven[0] == True) and (loc_all[interact_with_y][interact_with_x].is-oven[1/2/3] == True)
    if preconditions(agent, loc_all): ;record all features checked
        j = oven-state
        effects - (agent.hand_empty = False) and  (loc_all[interact_with_y][interact_with_x].is-oven[j] == False) and (loc_all[interact_with_y][interact_with_x].is-oven[j+1] == True) : 
        update agent and loc_all in current state 
        validate with next_state
        return pre, eff
    ------ put dish into oven with soup -----
    ------ deliver soup -------    
    '''