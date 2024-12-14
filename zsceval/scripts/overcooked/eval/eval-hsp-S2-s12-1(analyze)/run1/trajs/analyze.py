import pickle

#!usr/env/bin/env python
import pickle, copy, sys, os, csv
import numpy as np
def holding_onion(player_state):
    if player_state["held_object"] is not None and player_state["held_object"]['name'] == "onion":
        return True
    return False
#holding-dish
def holding_dish(player_state):
    if player_state["held_object"] is not None and player_state["held_object"]['name'] == "dish":
        return True
    return False
#holding-soup
def holding_soup(player_state):
    # print(player_state["held_object"])
    if player_state["held_object"] is not None and player_state["held_object"]['name'] == "soup":
        return True
    return False
#onion-on-counter
def onion_on_counter(objs_state, pos):
    for obj in objs_state:
        if obj['name'] == "onion" and list(obj['position']) == pos:
            return True
#dish-on-counter
def dish_on_counter(objs_state, pos):
    for obj in objs_state:
        if obj['name'] == 'dish' and list(obj['position']) == pos:
            return True
#soup-on-counter
def soup_on_counter(objs_state, pos):
    for obj in objs_state:
        if obj['name'] == 'soup' and list(obj['position']) == pos:
            return True
#empty-counter
def counter_empty(objs_state, pos):
    for obj in objs_state:
        if obj['position']==pos: #this makes sense only if only onions in counter are included
           return False
    return True 
#pot-n-onion
def pot_has_n_onions(objs_state, pot_pos):
    for obj in objs_state:
        if obj['name'] == 'onion' and list(obj['position']) == pos:
            count = count + 1
    if count == n:
        return True
    return False
class PredicateList:
    def __init__(self):
        self.layout_list =[ 
                ['X','X','X','P','P','X','X','X'],
                ['X',None,None,2,None,None,None,'X'],
                ['D',None,'X','X','X','X',None,'S'],
                ['X',None,None,1,None,None,None,'X'],
                ['X','X','X','O','O','X','X','X']
                ]
        print(len(self.layout_list[0]))
        print(len(self.layout_list))
        self.counterEmpty = copy.deepcopy(self.layout_list)
        self.onionOnCounter = copy.deepcopy(self.layout_list)
        self.dishOnCounter = copy.deepcopy(self.layout_list)
        self.soupOnCounter = copy.deepcopy(self.layout_list)
        self.counterEmptyChange = copy.deepcopy(self.layout_list)
        self.onionOnCounterChange = copy.deepcopy(self.layout_list)
        self.dishOnCounterChange = copy.deepcopy(self.layout_list)
        self.soupOnCounterChange = copy.deepcopy(self.layout_list)
        # initialize counter predicates
        for j in range(len(self.layout_list)):
            for i in range(len(self.layout_list[0])):
                if self.layout_list[j][i] == 'X':
                    self.counterEmpty[j][i] = False
                    self.onionOnCounter[j][i] = False
                    self.dishOnCounter[j][i] = False
                    self.soupOnCounter[j][i] = False
                    self.counterEmptyChange[j][i] = 0
                    self.onionOnCounterChange[j][i] = 0
                    self.dishOnCounterChange[j][i] = 0
                    self.soupOnCounterChange[j][i] = 0
                else:
                    self.counterEmpty[j][i] = 0
                    self.onionOnCounter[j][i] = 0
                    self.dishOnCounter[j][i] = 0
                    self.soupOnCounter[j][i] = 0
                    self.counterEmptyChange[j][i] = False
                    self.onionOnCounterChange[j][i] = False
                    self.dishOnCounterChange[j][i] = False
                    self.soupOnCounterChange[j][i] = False
        # initialize player predicates
        self.handEmpty = True
        self.holdingOnion = False
        self.holdingDish = False
        self.holdingSoup = False
        # initialize pot predicates
        self.onionInPot = 0
        self.potCooking = False
        self.potReady = False
        # print(self.layout_list)
        

def evaluate(name):
    with open(name, 'rb') as f:
        data = pickle.load(f)
    p1_action_traj = []
    p2_action_traj = []
    p1_state_traj = []
    p2_state_traj = []
    p1_events_traj = []
    p2_events_traj = []
    
    obj_traj = []
    # for giver lists
    p1_effect_list = PredicateList()
    p2_effect_list = PredicateList()
    # for reciever lists, convert found predicates to string and push to list (of strings)
    p1_receiver_list = []
    p2_receiver_list = []
    p1_giver_list = []
    p2_giver_list = []    
    total_subtask_list = []
    potOnions = 0
    flag = 0

    for i in range(0, len(data)):
        if i % 4 == 0 :
            if data[i+1] == 0:
                p1_state_traj.append(data[i]["players"][0])
                p2_state_traj.append(data[i]["players"][1])
                obj_traj.append(data[i]["objects"])
                if i + 2 < len(data):
                    p1_action_traj.append(data[i+2][0])
                    p2_action_traj.append(data[i+2][1])
                if i + 3 < len(data):
                    p1_events_traj.append(data[i+3][0])
                    p2_events_traj.append(data[i+3][1])
            else:
                p1_state_traj.append(data[i]["players"][1])
                p2_state_traj.append(data[i]["players"][0])
                obj_traj.append(data[i]["objects"])
                if i + 2 < len(data):
                    p1_action_traj.append(data[i+2][1])
                    p2_action_traj.append(data[i+2][0])
                if i + 3 < len(data):
                    p1_events_traj.append(data[i+3][1])
                    p2_events_traj.append(data[i+3][0])
    p1_events = copy.deepcopy(p1_events_traj[0])
    p2_events = copy.deepcopy(p2_events_traj[0])
    for key in p1_events.keys():
        p1_events[key] = sum(item[key] for item in p1_events_traj)
    for key in p2_events.keys():
        p2_events[key] = sum(item[key] for item in p2_events_traj)
    # for debugging
    # print(data)
    '''
    dict_keys(['put_onion_on_X',
    'put_dish_on_X',
    'put_soup_on_X', 
    'pickup_onion_from_X',
        'pickup_onion_from_O', 
        'pickup_dish_from_X',
        'pickup_dish_from_D', 
        'pickup_soup_from_X',
            'USEFUL_DISH_PICKUP',
            'SOUP_PICKUP', 
            'PLACEMENT_IN_POT', 
            'delivery', 
            'STAY', 
            'MOVEMENT', 
            'IDLE_MOVEMENT', 
            'IDLE_INTERACT_X',
                'IDLE_INTERACT_EMPTY'])
    '''
    # # for debugging with onion events
    # for timestep,i in enumerate(p1_events_traj):
    #     if i['SOUP_PICKUP']:
    #         print("p1 picks soup from pot", timestep) 
    # for timestep,i in enumerate(p2_events_traj):
    #     if i['pickup_dish_from_X']:
    #         print("p2 picks dish from counter", timestep)
    p1_sub_dep = 0
    p2_sub_dep = 0
    p1_trig_dep_sub = 0
    p2_trig_dep_sub = 0
    p1_giver_trig_dep_sub = 0
    p2_giver_trig_dep_sub = 0
    p1_acc_dep_sub = 0
    p2_acc_dep_sub = 0
    p1_rec_acc_dep_sub = 0
    p2_rec_acc_dep_sub = 0
    


    for i in range(0, len(p1_action_traj)):
        # if it is an interact action, put effects in list.
        p1_action = p1_action_traj[i]
        p2_action = p2_action_traj[i]
        # for p1 INTERACT actions
        if p1_action == "interact":
            
            # for all PICK actions
 
            ''' Pick Onion'''
            if holding_onion(p1_state_traj[i+1]) and not holding_onion(p1_state_traj[i]):
                onion_pick_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation']))) 
                onion_pick_location_test = list(onion_pick_location)
                onion_pick_location = list((onion_pick_location[1], onion_pick_location[0]))
                # counter           
                if onion_on_counter(obj_traj[i], onion_pick_location_test) and p1_effect_list.layout_list[onion_pick_location[0]][onion_pick_location[1]] != 'P': 
                    p1_sub_dep += 1
                    p1_acc_dep_sub += 1
                    # print("p1 just picked an onion from counter at", onion_pick_location, i)
                    onion_pick_location = list(onion_pick_location)
                    if p2_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] == False and p2_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] != 0:
                        p1_rec_acc_dep_sub += 1
                        p2_giver_trig_dep_sub += 1
                       # update giver agent effect predicates 
                        p2_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] = 0
                        # update int. lists
                        p1_receiver_list.append("not counterEmpty@" + str(onion_pick_location))
                        p2_giver_list.append("not counterEmpty@" + str(onion_pick_location))
                    if p2_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[0]] == True and p2_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[0]] != 0:
                        # update giver agent effect lists
                        p2_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                        p2_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[0]] = 0 #reset to 0 and false
                        # update int. lists
                        # print("p2 fulfils p1")
                        p1_receiver_list.append("onionOnCounter@" + str(onion_pick_location))
                        p2_giver_list.append("onionOnCounter@" + str(onion_pick_location))
                    # update effect lists
                    p1_effect_list.handEmpty = False
                    p1_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] = True
                    p1_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] = 1 
                    p1_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                    p1_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[1]] = 1
                # dispenser
                else:
                    p1_effect_list.handEmpty = False
            ''' Pick Dish'''
            if holding_dish(p1_state_traj[i+1]) and not holding_dish(p1_state_traj[i]):
                dish_pick_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                dish_pick_location_test = list(dish_pick_location)
                dish_pick_location = list((dish_pick_location[1], dish_pick_location[0]))
                # counter
                if dish_on_counter(obj_traj[i], dish_pick_location_test):
                    p1_sub_dep += 1
                    p1_acc_dep_sub += 1
                    
                    # print("p1 just picked an dish from counter", i)
                    dish_pick_location = list(dish_pick_location)
                    if p2_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] == False and p2_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] != 0:
                        p1_rec_acc_dep_sub += 1
                        p2_giver_trig_dep_sub += 1
                        # update giver agent predicates
                        p2_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        # update int. lists
                        p1_receiver_list.append("not counterEmpty@" + str(dish_pick_location))
                        p2_giver_list.append("counterEmpty@" + str(dish_pick_location))

                    if p2_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] == True and p2_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] != 0: 
                        # update giver agent predicates
                        p2_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] == False
                        p2_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        # update int. lists
                        # print("p2 fulfils p1")
                        p1_receiver_list.append("dishOnCounter@" + str(dish_pick_location))
                        p2_giver_list.append("dishOnCounter@" + str(dish_pick_location))
                    # update effect lists
                    p1_effect_list.handEmpty = False
                    p1_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] = True
                    p1_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] =1
                    p1_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] = False
                    p1_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] = 1
                # dispenser
                else: 
                    # print("p1 just picked a dish from disp", i)
                    p1_effect_list.handEmpty = False
            ''' Pick Soup'''
            if holding_soup(p1_state_traj[i+1]):
                soup_pick_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                soup_pick_location_test = list(soup_pick_location)
                soup_pick_location = list((soup_pick_location[1], soup_pick_location[0]))
                # counter
                if soup_on_counter(obj_traj[i], soup_pick_location_test) and p1_effect_list.layout_list[soup_pick_location[0]][soup_pick_location[1]] == 'X':
                    p1_sub_dep += 1
                    p1_acc_dep_sub += 1
                    # print("p1 just picked an soup from counter", i) 
                    soup_pick_location = list(soup_pick_location)   
                    if p2_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] == False and p2_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        p1_rec_acc_dep_sub += 1
                        p2_giver_trig_dep_sub += 1
                        # update giver agent effect predicates
                        p2_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        # update int. lists
                        p1_receiver_list.append("not counterEmpty@" + str(soup_pick_location))
                        p2_giver_list.append("not counterEmpty@" + str(soup_pick_location))
                    if p2_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] == True and p2_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        # update giver agent effect predicates
                        p2_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] == False
                        p2_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        # update int. lists
                        p1_receiver_list.append("soupOnCounter@" + str(soup_pick_location))
                        p2_giver_list.append("soupOnCounter@" + str(soup_pick_location))
                    # update effect lists
                    p1_effect_list.handEmpty = False 
                    p1_effect_list.holdingSoup = True
                    p1_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] = True
                    p1_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] = 1
                    p1_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] = False
                    p1_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] = 1
                # pot is already covered in Put Dish (when soup is ready)
             # for all PUT actions
            ''' Put Onion'''
            if holding_onion(p1_state_traj[i]) and not holding_onion(p1_state_traj[i+1]): # player has put down an onion (where)?
                onion_put_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation']))) 
                onion_put_location_test = list(onion_put_location)
                onion_put_location = list((onion_put_location[1], onion_put_location[0]))
                
                # counter
                if onion_on_counter(obj_traj[i+1], onion_put_location_test) and p1_effect_list.layout_list[onion_put_location[0]][onion_put_location[1]] != 'P':
                    p1_sub_dep += 1
                    p1_trig_dep_sub += 1
                    # print("p1 put on counter at",onion_put_location , i)
                    if p2_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] == True and p2_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update effect predicates for giver
                        p2_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                        p2_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('counterEmpty@' + str(onion_put_location))
                        p2_giver_list.append('counterEmpty@' + str(onion_put_location))
                    if p2_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p2_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update effect predicates for giver
                        p2_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] = False
                        p2_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('not onionOnCounter@' + str(onion_put_location))
                        p2_giver_list.append('not onionOnCounter@' + str(onion_put_location))
                    if p2_effect_list.dishOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p2_effect_list.dishOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update effect predicates for giver
                        p2_effect_list.dishOnCounter[onion_put_location[0]][onion_put_location[1]] = False
                        p2_effect_list.dishOnCounterChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('not dishOnCounter@' + str(onion_put_location))
                        p2_giver_list.append('not dishOnCounter@' + str(onion_put_location))
                    if p2_effect_list.soupOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p2_effect_list.soupOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update effect predicates for giver
                        p2_effect_list.soupOnCounter[onion_put_location[0]][onion_put_location[1]] = False
                        p2_effect_list.soupOnCounterChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('not soupOnCounter@' + str(onion_put_location))
                        p2_giver_list.append('not soupOnCounter@' + str(onion_put_location))
                    # update effects
                    p1_effect_list.handEmpty = True
                    p1_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                    p1_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] = 1
                    p1_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] = True
                    p1_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] = 1
                    
                
                # pot
                else:
                    # print("p1 just put onion in pot", i)
                    p1_effect_list.handEmpty = True
                    p1_effect_list.onionInPot +=1
                    potOnions += 1
                    p1_trig_flag = 0
                    if potOnions != 3:
                        if p2_effect_list.onionInPot > 0 :
                            # update p1 dep subtask only if it is part of an interdependence
                            p1_sub_dep += 1
                            p1_acc_dep_sub += 1
                            p1_rec_acc_dep_sub += 1

                            if p2_trig_flag == 0:
                                p2_sub_dep += 1
                                p2_trig_flag = 1
                                p2_trig_dep_sub += 1
                                p2_giver_trig_dep_sub += 1
                            # print("p2 has already put ", p2_effect_list.onionInPot, " at ", i)
                            # if any of the other onions were put by P2
                            p1_receiver_list.append("potOnions@" + str(p2_effect_list.onionInPot))   
                            p2_giver_list.append("potOnions@" + str(p2_effect_list.onionInPot))
                    # if p1 put the last onion in the pot, update effect predicates
                    elif potOnions == 3:
                        # print("p1 gets soup ready at ", i)
                        p1_trig_flag = 0
                        p1_effect_list.potReady = True
                        p1_effect_list.onionInPot = 0
                        p2_effect_list.onionInPot = 0
                        p2_trig_flag = 0
                        potOnions = 0

            ''' Put Dish'''
            if holding_dish(p1_state_traj[i]):
                dish_put_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                dish_put_location_test = list(dish_put_location)
                dish_put_location = list((dish_put_location[1], dish_put_location[0]))
                # counter
                if not holding_dish(p1_state_traj[i+1]) and not holding_soup(p1_state_traj[i+1]):
                    # print("p1 just put an dish on counter", i)
                    p1_sub_dep += 1
                    p1_trig_dep_sub += 1
                    if p2_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] == True and p2_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p2_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                        p2_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('counterEmpty@' + str(dish_put_location))
                        p2_giver_list.append('counterEmpty@' + str(dish_put_location))
                    if p2_effect_list.onionOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p2_effect_list.onionOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p2_effect_list.onionOnCounter[dish_put_location[0]][dish_put_location[1]] = False
                        p2_effect_list.onionOnCounterChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('not onionOnCounter@' + str(dish_put_location))
                        p2_giver_list.append('not onionOnCounter@' + str(dish_put_location))
                    if p2_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p2_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p2_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] == False
                        p2_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('not dishOnCounter@' + str(dish_put_location))
                        p2_giver_list.append('not dishOnCounter@' + str(dish_put_location))
                    if p2_effect_list.soupOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p2_effect_list.soupOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p2_effect_list.soupOnCounter[dish_put_location[0]][dish_put_location[1]] == False
                        p2_effect_list.soupOnCounterChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists                        
                        p1_receiver_list.append('not soupOnCounter@' + str(dish_put_location))
                        p2_giver_list.append('not soupOnCounter@' + str(dish_put_location))
                    # updaye effect lists
                    p1_effect_list.handEmpty = True
                    p1_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                    p1_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] = 1
                    p1_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] = True
                    p1_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] = 1

                # player collected soup
                elif holding_soup(p1_state_traj[i+1]):
                    # print("p1 just picked soup from pot", i)
                    # p1_sub_dep += 1
                    # check for preconditions
                    if p2_effect_list.potReady == True:
                        p1_sub_dep += 1
                        p1_acc_dep_sub += 1
                        p1_rec_acc_dep_sub += 1
                        # if p2 putting onion in soup has not been counted yet, only then it should be counted again
                        if p2_trig_flag == 0:
                            p2_sub_dep += 1
                            p2_trig_flag = 1
                            p2_trig_dep_sub += 1
                            p2_giver_trig_dep_sub += 1
                        p1_effect_list.potReady = False
                        p2_effect_list.potReady == False
                        p1_receiver_list.append("potReady@" + str(i))
                        p2_giver_list.append("potReady@" + str(i))
                    p1_effect_list.handEmpty = False
            ''' Put Soup'''
            if holding_soup(p1_state_traj[i]):
                soup_put_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                soup_put_location_test = list(soup_put_location)
                soup_put_location = list((soup_put_location[1], soup_put_location[0]))
                
                if not p1_events_traj[i]['delivery']:
                    p1_sub_dep += 1
                    p1_trig_dep_sub += 1
                    if p2_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] == True and p2_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p2_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                        p2_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int. lists
                        p1_receiver_list.append('counterEmpty@' + str(soup_put_location))
                        p2_giver_list.append('counterEmpty@' + str(soup_put_location))
                    if p2_effect_list.onionOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p2_effect_list.onionOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p2_effect_list.onionOnCounter[soup_put_location[0]][soup_put_location[1]] == False
                        p2_effect_list.onionOnCounterChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int. lists
                        p1_receiver_list.append('not onionOnCounter@' + str(soup_put_location))
                        p2_giver_list.append('not onionOnCounter@' + str(soup_put_location))
                    if p2_effect_list.dishOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p2_effect_list.dishOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p2_effect_list.dishOnCounter[soup_put_location[0]][soup_put_location[1]] == False
                        p2_effect_list.dishOnCounterChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int. lists
                        p1_receiver_list.append('not dishOnCounter@' + str(soup_put_location))
                        p2_giver_list.append('not dishOnCounter@' + str(soup_put_location))
                    if p2_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p2_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p2_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] == False
                        p2_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int lists
                        p1_receiver_list.append('not soupOnCounter@' + str(soup_put_location))
                        p2_giver_list.append('not soupOnCounter@' + str(soup_put_location))
                    # update effects
                    p1_effect_list.handEmpty = True
                    p1_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                    p1_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] = 1
                    p1_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] = True
                    p1_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] = 1

                # delivery
                else: 
                    # print("soup delivered")
                    flag +=1
                    p1_effect_list.handEmpty = True
                    if flag >5:
                        print("game over")
                        # return p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list, p1_events, p2_events, i

        if p2_action == "interact":
            # for all PICK actions
            ''' Pick Onion'''
            if not holding_onion(p2_state_traj[i]) and holding_onion(p2_state_traj[i+1]):
                onion_pick_location = tuple(map(sum, zip(p2_state_traj[i]['position'], p2_state_traj[i]['orientation'])))
                # this is the location you send
                onion_pick_location_test = list(onion_pick_location)
                onion_pick_location = list((onion_pick_location[1],onion_pick_location[0]))
                # counter
                if onion_on_counter(obj_traj[i], onion_pick_location_test) and p2_effect_list.layout_list[onion_pick_location[0]][onion_pick_location[1]] != 'P': 
                    p2_sub_dep += 1
                    p2_acc_dep_sub += 1
                    # print("p2 picked from counter", onion_pick_location, i )
                    if p1_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] == False and p1_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] != 0:      
                        p2_rec_acc_dep_sub += 1
                        p1_giver_trig_dep_sub += 1
                        # update effect predicates for giver agent
                        p1_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] = False
                        p1_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('not counterEmpty@' + str(onion_pick_location))
                        p1_giver_list.append('not counterEmpty@' + str(onion_pick_location))
                    if p1_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] == True and p1_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[1]] != 0:
                        # update effect predicates for giver agent
                        p1_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                        p1_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[1]]= 0
                        # update int lists
                        p2_receiver_list.append("onionOnCounter@" + str(onion_pick_location))
                        p1_giver_list.append("onionOnCounter@" + str(onion_pick_location))

                    # update effect predicates
                    p2_effect_list.handEmpty = False
                    p2_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] = True
                    p2_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] = 1
                    p2_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                    p2_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[1]] = 1
                    
                # dispenser
                else:
                    # print("p2 just picked an onion from dispenser")
                    p2_effect_list.handEmpty = False

            ''' Pick Dish'''
            if holding_dish(p2_state_traj[i+1]) and not holding_dish(p2_state_traj[i]):
                dish_pick_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                dish_pick_location_test = list(dish_pick_location)
                dish_pick_location = list((dish_pick_location[1], dish_pick_location[0]))
                # print("agent state traj and position", p2_state_traj[i+1], dish_pick_location_test )
                # counter
                if dish_on_counter(obj_traj[i], dish_pick_location_test):
                    p2_sub_dep += 1
                    # print("p2 just picked an dish from counter", i)
                    p2_acc_dep_sub += 1
                    if p1_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] == False and p1_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] != 0:
                        p1_giver_trig_dep_sub += 1
                        p2_rec_acc_dep_sub += 1
                        # update giver agent effect predicates
                        p1_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append('not counterEmpty@' + str(dish_pick_location))
                        p1_giver_list.append('not counterEmpty@' + str(dish_pick_location))
                    if p1_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] == True and p1_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] != 0: 
                        # update giver agent predicates
                        p1_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] == False
                        p1_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append('dishOnCounter@' + str(dish_pick_location))
                        p1_giver_list.append('dishOnCounter@' + str(dish_pick_location))
                    # update effects
                    p2_effect_list.handEmpty = False
                    p2_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] = True
                    p2_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] += 1
                    p2_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] = False
                    p2_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] += 1
                # dispenser
                else: 
                    # print("p2 just picked a dish from disp", i)
                    p2_effect_list.handEmpty = False

            ''' Pick Soup '''
            if holding_soup(p2_state_traj[i+1]):
                soup_pick_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                soup_pick_location_test = list(soup_pick_location)
                soup_pick_location = list((soup_pick_location[1], soup_pick_location[0]))
                # counter
                if soup_on_counter(obj_traj[i], soup_pick_location_test) and p1_effect_list.layout_list[soup_pick_location[0]][soup_pick_location[1]] == 'X':
                    p2_sub_dep += 1
                    p2_acc_dep_sub += 1
                    # print("p2 just picked an soup from counter", i)     
                    if p1_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] == False and p1_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        p1_giver_trig_dep_sub += 1
                        p2_rec_acc_dep_sub += 1
                        # update giver agent effect predicates
                        p2_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append('not counterEmpty@' + str(soup_pick_location))
                        p1_giver_list.append('not counterEmpty@' + str(soup_pick_location))
                    if p1_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] == True and p1_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        # update giver agent effect predicates
                        p1_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] == False
                        p1_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append("soupOnCounter" + str(soup_pick_location))
                        p1_giver_list.append("soupOnCounter" + str(soup_pick_location))
                    # update effects
                    p2_effect_list.handEmpty = False
                    p2_effect_list.holdingSoup = True
                    p2_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] = True
                    p2_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] += 1
                    p2_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] = False
                    p2_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] += 1
                # pot is already covered in Put Dish (when soup is ready)

            ''' PUT ACTIONS '''
            ''' Put Onion'''
            if holding_onion(p2_state_traj[i]) and not holding_onion(p2_state_traj[i+1]): 
                onion_put_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                onion_put_location_test = list(onion_put_location)
                onion_put_location = list((onion_put_location[1], onion_put_location[0]))
                #  counter
                if onion_on_counter(obj_traj[i+1], onion_put_location_test) and p2_effect_list.layout_list[onion_put_location[0]][onion_put_location[1]] != 'P':
                    # print("p2 put onion on the counter",onion_put_location,  i)
                    p2_sub_dep += 1
                    p2_trig_dep_sub += 1
                    if p1_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] == True and p1_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update giver effect list
                        p1_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                        p1_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append('counterEmpty@' + str(onion_put_location))
                        p1_giver_list.append('counterEmpty@' + str(onion_put_location))
                    if p1_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p1_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update giver effect lists
                        p1_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] == False
                        p1_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('not onionOnCounter@' + str(onion_put_location))
                        p1_giver_list.append('not onionOnCounter@' + str(onion_put_location))
                    if p1_effect_list.dishOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p1_effect_list.dishOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update giver effect lists
                        p1_effect_list.dishOnCounter[onion_put_location[0]][onion_put_location[1]] = False
                        p1_effect_list.dishOnCounterChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('not dishOnCounter@' + str(onion_put_location))
                        p1_giver_list.append('not dishOnCounter@' + str(onion_put_location))
                    if p1_effect_list.soupOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p1_effect_list.soupOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        # update giver effect lists
                        p1_effect_list.soupOnCounter[onion_put_location[0]][onion_put_location[1]] = False
                        p1_effect_list.soupOnCounterChange[onion_put_location[0]][onion_put_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('not soupOnCounter@' + str(onion_put_location))
                        p1_giver_list.append('not soupOnCounter@' + str(onion_put_location))
                    # update effect lists
                    p2_effect_list.handEmpty = True
                    p2_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                    p2_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] += 1
                    p2_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] = True
                    p2_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] += 1
                # pot
                else:
                    # print("p2 just put onion in pot ", i)
                    p2_effect_list.handEmpty = True
                    p2_effect_list.onionInPot +=1
                    p2_trig_flag = 0
                    potOnions += 1
                    if potOnions != 3:
                        if p1_effect_list.onionInPot >0 :
                            p2_sub_dep += 1
                            p2_acc_dep_sub += 1
                            p2_rec_acc_dep_sub += 1

                            if p1_trig_flag == 0:
                                p1_sub_dep += 1
                                p1_trig_flag = 1
                                p1_trig_dep_sub += 1
                                p1_giver_trig_dep_sub += 1
                            # print("p1 has already put ", p1_effect_list.onionInPot, " at ", i)
                            # if any of the other onions were put by P1
                            p2_receiver_list.append("potOnions@" + str(p1_effect_list.onionInPot))   
                            p1_giver_list.append("potOnions@" + str(p1_effect_list.onionInPot))
                    # if p1 put the last onion in the pot, update effect predicates
                    elif potOnions == 3:
                        # print("p2 gets soup ready at ", i)
                        p2_effect_list.potReady = True
                        p2_effect_list.onionInPot = 0
                        p2_effect_list.onionInPot = 0
                        p1_trig_flag = 0
                        p2_trig_flag = 0
                        potOnions = 0

            '''Put Dish'''
            if holding_dish(p2_state_traj[i]):
                dish_put_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                dish_put_location_test = list(dish_put_location)
                dish_put_location = list((dish_put_location[1], dish_put_location[0]))
                #  counter
                if not holding_dish(p2_state_traj[i+1]) and not holding_soup(p2_state_traj[i+1]): 
                    p2_sub_dep += 1
                    p2_trig_dep_sub += 1
                    # print("p2 just put dish down on counter", i)
                    if p1_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] == True and p1_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p1_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                        p1_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('counterEmpty@' + str(dish_put_location))
                        p1_giver_list.append('counterEmpty@' + str(dish_put_location))
                    if p1_effect_list.onionOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p1_effect_list.onionOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p1_effect_list.onionOnCounter[dish_put_location[0]][dish_put_location[1]] = False
                        p1_effect_list.onionOnCounterChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('not onionOnCounter@' + str(dish_put_location))
                        p1_giver_list.append('not onionOnCounter@' + str(dish_put_location))
                    if p1_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p1_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p1_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] == False
                        p1_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('not dishOnCounter@' + str(dish_put_location))
                        p1_giver_list.append('not dishOnCounter@' + str(dish_put_location))
                    if p1_effect_list.soupOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p1_effect_list.soupOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        # update giver agent effect predicates
                        p1_effect_list.soupOnCounter[dish_put_location[0]][dish_put_location[1]] == False
                        p1_effect_list.soupOnCounterChange[dish_put_location[0]][dish_put_location[1]] = 0
                        # update int lists       
                        p2_receiver_list.append('not soupOnCounter@' + str(dish_put_location))
                        p1_giver_list.append('not soupOnCounter@' + str(dish_put_location))
                    # update effects
                    p2_effect_list.handEmpty = True
                    p2_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                    p2_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] += 1
                    p2_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] = True
                    p2_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] += 1
                # collect soup from pot
                elif holding_soup(p2_state_traj[i+1]):
                    # print("p2 just picked soup from pot", i)
                    # p2_sub_dep += 1
                    # check for preconditions
                    if p1_effect_list.potReady == True:
                        p2_sub_dep += 1
                        p2_acc_dep_sub += 1
                        p2_rec_acc_dep_sub += 1
                        # if p1 putting onion in soup has not been counted yet, only then it should be counted again
                        if p1_trig_flag == 0:
                            p1_sub_dep += 1
                            p1_trig_flag = 1
                            p1_trig_dep_sub += 1
                            p1_giver_trig_dep_sub += 1
                        p1_effect_list.potReady == False
                        p2_effect_list.potReady = False
                        p2_receiver_list.append("potReady@" + str(i))
                        p1_giver_list.append("potReady@" + str(i))
                    p2_effect_list.handEmpty = False
                    

            ''' Put Soup'''
            if holding_soup(p2_state_traj[i]) and not holding_soup(p2_state_traj[i+1]):
                soup_put_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                soup_put_location_test = list(soup_put_location)
                soup_put_location = list((soup_put_location[1], soup_put_location[0]))
                # counter
                if not p2_events_traj[i]['delivery']:
                    p2_sub_dep += 1
                    p2_trig_dep_sub += 1
                    if p1_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] == True and p1_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p1_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                        p1_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append('counterEmpty@' + str(soup_put_location))
                        p1_giver_list.append('counterEmpty@' + str(soup_put_location))
                    if p1_effect_list.onionOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p1_effect_list.onionOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p1_effect_list.onionOnCounter[soup_put_location[0]][soup_put_location[1]] == False
                        p1_effect_list.onionOnCounterChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append('not onionOnCounter@' + str(soup_put_location))
                        p1_giver_list.append('not onionOnCounter@' + str(soup_put_location))
                    if p1_effect_list.dishOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p1_effect_list.dishOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p1_effect_list.dishOnCounter[soup_put_location[0]][soup_put_location[1]] == False
                        p1_effect_list.dishOnCounterChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int. lists
                        p2_receiver_list.append('not dishOnCounter@' + str(soup_put_location))
                        p1_giver_list.append('not dishOnCounter@' + str(soup_put_location))
                    if p1_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p1_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        # update giver effect predicates
                        p1_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] == False
                        p1_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] = 0
                        # update int lists
                        p2_receiver_list.append('not soupOnCounter@' + str(soup_put_location))
                        p1_giver_list.append('not soupOnCounter@' + str(soup_put_location))
                    # update effects
                    p2_effect_list.handEmpty = True
                    p2_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                    p2_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] += 1
                    p2_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] = True
                    p2_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] += 1

                # deliver
                else: 
                    # print("soup delivered")
                    flag += 1
                    p2_effect_list.handEmpty = True
                    if flag >5:
                        print("game over")
                        # return p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list, p1_events, p2_events, i
        stats = [p1_sub_dep, p1_trig_dep_sub, p1_giver_trig_dep_sub, p1_acc_dep_sub, p1_rec_acc_dep_sub, p2_sub_dep, p2_trig_dep_sub, p2_giver_trig_dep_sub, p2_acc_dep_sub, p2_rec_acc_dep_sub]
    return p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list, p1_events, p2_events, i, stats
def diagnose():
    name = "./random3/traj_115_1.pkl"
    p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list, p1_events, p2_events, time_required, stats = evaluate(name)
    print("p1 giver list:", p1_giver_list)
    # print("p2 receiver list:", p2_receiver_list)
    print("p1 receiver list:", p1_receiver_list)
    # print("p2 giver list:", p2_receiver_list)

def analyse_for_single_run(name):
    # name = "./random3/traj_115_1.pkl"
    p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list, p1_events, p2_events, time_required, stats = evaluate(name)
    # print("p1 giver list:", p1_giver_list)
    # print("p2 receiver list:", p2_receiver_list)
    # print("p1 receiver list:", p1_receiver_list)
    subtask_unique_keys = [
        'put_onion_on_X',
        'put_dish_on_X',
        'put_soup_on_X', 
        'pickup_onion_from_X',
        'pickup_onion_from_O', 
        'pickup_dish_from_X',
        'pickup_dish_from_D', 
        'pickup_soup_from_X',
        'SOUP_PICKUP', 
        'PLACEMENT_IN_POT', 
        'delivery'
            ]
    subtask_non_dep_keys = [
        'pickup_onion_from_O',
        'pickup_dish_from_D', 
        'delivery' # put dish/soup on serving station
        'SOUP_PICKUP', #pick soup from pot 
    ]
    subtask_dep_keys = [
        'pickup_onion_from_X',
        'put_onion_on_X',
        'pickup_dish_from_X',
        'put_dish_on_X',     
        'pickup_soup_from_X',
        'put_soup_on_X', 
        'PLACEMENT_IN_POT'
        ] 
    subtask_trigger_keys = [
        'put_onion_on_X',
        'PLACEMENT_IN_POT', # put onion in pot
        'put_dish_on_X',     
        'put_soup_on_X', 
        ] 
    subtask_accept_keys = [
        'pickup_onion_from_X',
        'pickup_dish_from_X',
        'pickup_soup_from_X',
        ] 
    p1_events_total = sum(p1_events.values())
    p2_events_total = sum(p2_events.values())
    # total amount of subtasks done by the agent (all events which involve interact)
    p1_sub_events = {key:p1_events[key] for key in subtask_unique_keys}
    p2_sub_events = {key:p2_events[key] for key in subtask_unique_keys}
    # how many of dep vs non-dep events did the agent do ?    
    p1_dep_events = {key:p1_sub_events[key] for key in subtask_dep_keys}
    p2_dep_events = {key:p2_sub_events[key] for key in subtask_dep_keys}
    # print(p2_dep_events)
    # how many trigger and accept actions
    # p1_trigger_events = {key:p1_dep_events[key] for key in subtask_trigger_keys}
    # p1_accept_events = {key:p1_dep_events[key] for key in subtask_accept_keys}
    # p2_trigger_events = {key:p2_dep_events[key] for key in subtask_trigger_keys}
    # p2_accept_events = {key:p2_dep_events[key] for key in subtask_accept_keys}
    # print("Total | Subtasks | Dep |", 
    #       p1_events_total, sum(p1_sub_events.values()), sum(p1_dep_events.values()), stats[0])
    # print("Trigger | Trigger-giver | Accept | Accept-receiver", stats[1], stats[2], stats[3], stats[4])
    # print("Total | Subtasks | Dep |", 
    #       p2_events_total, sum(p2_sub_events.values()), sum(p2_dep_events.values()), stats[5] )
    # print("Trigger | Trigger-giver | Accept | Accept-receiver", stats[6], stats[7], stats[8], stats[9])
    val = check_sanity_for_one_run(name,stats)
    # print("number of incorrect", val)
    return val

def check_sanity_for_one_run(str, stats):
    if stats[2] > stats[1] or stats[4] > stats[3] or stats[0] != (stats[1]+stats[3]) :
        print(str)
        return 1
    if stats[7] > stats[6] or stats[9] > stats[8] or stats[5] != (stats[6]+stats[8]) :
        print(str)
        return 1
    return 0

def test_on_all():
    # name = "traj_9_1.pkl"
    agent0 = sys.argv[1]
    agent1 = sys.argv[2]
    layout = sys.argv[3]
    seed = int(sys.argv[4])
    p1_receiver_list_sum = 0
    p2_receiver_list_sum = 0
    p1_giver_list_sum = 0 
    p2_giver_list_sum = 0 
    p1_events_total = []
    p2_events_total = []

    subtask_unique_keys = ['put_onion_on_X',
    'put_dish_on_X',
    'put_soup_on_X', 
    'pickup_onion_from_X',
        'pickup_onion_from_O', 
        'pickup_dish_from_X',
        'pickup_dish_from_D', 
        'pickup_soup_from_X',
            'SOUP_PICKUP', 
            'PLACEMENT_IN_POT', 
            'delivery'
            ]
    subtask_non_dep_keys = [
        'pickup_onion_from_O',
        'pickup_dish_from_D', 
        'delivery' # put dish/soup on serving station
        'SOUP_PICKUP', #pick soup from pot 
    ]
    subtask_dep_keys = [
        'pickup_onion_from_X',
        'put_onion_on_X',
        'PLACEMENT_IN_POT', # put onion in pot
        'pickup_dish_from_X',
        'put_dish_on_X',     
        'pickup_soup_from_X',
        'put_soup_on_X', 
        'SOUP_PICKUP', #pick soup from pot
        ] 
    subtask_trigger_keys = [
        'put_onion_on_X',
        'PLACEMENT_IN_POT', # put onion in pot
        'put_dish_on_X',     
        'put_soup_on_X', 
        ] 
    subtask_accept_keys = [
        'pickup_onion_from_X',
        'pickup_dish_from_X',
        'pickup_soup_from_X',
        ] 
    time_required_total = 0
    runs = 0
    for i in range (1,seed+1):
        # print("here")
        if agent1 == 'cole':
            n = 75
        else:
            n = 36
        dir = "/home/local/ASUAD/ubiswas2/ZSC-Eval/zsceval/scripts/overcooked/eval/traj_eval/" + str(layout) +"/" + str(agent0) + "/" + str(agent1) + "/eval-" + str(agent1) + "-S2-s" + str(n) +"-" + str(i)+ "/run1/trajs/"+ layout +"/"
        print(dir)
        for name in os.scandir(dir) :
            if name.is_file() and runs<=11:
                # print(name)
                p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list, p1_events, p2_events, time_required = evaluate(name)
                p1_events_total_int = sum(p1_events.values())
                p2_events_total_int = sum(p2_events.values())
                # total amount of subtasks done by the agent
                p1_events = {key:p1_events[key] for key in subtask_unique_keys}
                p2_events = {key:p2_events[key] for key in subtask_unique_keys}
                # how many of dep vs non-dep events did the agent do ?    
                p1_dep_events = {key:p1_events[key] for key in subtask_dep_keys}
                p2_dep_events = {key:p2_events[key] for key in subtask_dep_keys}
                # we can get the trigger and accept list from here by just extracting outside the loop, the put and pick actions
                p1_trigger_events = {key:p1_dep_events[key] for key in subtask_trigger_keys}
                p1_accept_events = {key:p1_dep_events[key] for key in subtask_accept_keys}
                p2_trigger_events = {key:p2_dep_events[key] for key in subtask_trigger_keys}
                p2_accept_events = {key:p2_dep_events[key] for key in subtask_accept_keys}
                print("P1 total events,",sum(p1_events.values()))
                print("P1 dep events,", sum(p1_dep_events.values()))
                print("P1 trigger events,", sum(p1_trigger_events.values()))
                print("P1 accept events,", sum(p1_accept_events.values()))
                print("P1 trigger events which got accepted,", len(p1_giver_list))
                print("P1 accepted which trigger events,", len(p1_receiver_list))
                print("P2 total events,",sum(p2_events.values()))
                print("P2 dep events,", sum(p2_dep_events.values()))
                print("P2 trigger events,", sum(p2_trigger_events.values()))
                print("P2 accept events,", sum(p2_accept_events.values()))
                print("P2 trigger events which got accepted,", len(p2_giver_list))
                print("P2 accepted which trigger events,",len(p2_receiver_list))
                p1_receiver_list_sum += len(p1_receiver_list)
                p2_receiver_list_sum += len(p2_receiver_list)
                p1_giver_list_sum += len(p1_giver_list)
                p2_giver_list_sum += len(p2_giver_list)
                p1_events_total.append(p1_events)
                p2_events_total.append(p2_events)
                time_required_total += time_required
                if len(p1_giver_list) >=sum(p1_trigger_events.values()):
                    continue
                if len(p2_giver_list) >= sum(p2_trigger_events.values()):
                    continue
                with open("HA_subj_results.csv", 'a', newline = '') as file:
                    writer = csv.writer(file)
                    row = [layout,
                        agent0, 
                        agent1, 
                        sum(p1_events.values()), 
                        round(float(sum(p1_dep_events.values())*100)/float(sum(p1_events.values())),2), 
                        round(float(sum(p1_trigger_events.values())*100)/float(sum(p1_dep_events.values())),2), 
                        round(float(len(p1_giver_list)*100)/float(sum(p1_trigger_events.values())),2), 
                        sum(p2_events.values()), 
                        round(float(sum(p2_dep_events.values())*100)/float(sum(p2_events.values())),2), 
                        round(float(sum(p2_trigger_events.values())*100)/float(sum(p2_dep_events.values())),2),
                        round(float(len(p2_giver_list)*100)/float(sum(p2_trigger_events.values())),2),
                        time_required
                    ]
                    writer.writerow(row)
                runs += 1
    p1_events_over_runs = copy.deepcopy(p1_events)
    p2_events_over_runs = copy.deepcopy(p2_events)
    for key in p1_events.keys():
        p1_events_over_runs[key] = float(sum(item[key] for item in p1_events_total))/float(runs)
    for key in p2_events.keys():
        p2_events_over_runs[key] = float(sum(item[key] for item in p2_events_total))/float(runs)
    print(str(agent0), " receives ", round(float(p1_receiver_list_sum)/ float(runs)))
    print(str(agent1), " gives ", round(float(p2_giver_list_sum)/ float(runs)))
    print(str(agent1), " receives ", round(float(p2_receiver_list_sum)/ float(runs)))
    print(str(agent0), " gives ", round(float(p1_giver_list_sum)/ float(runs)))
    print(str(agent0), " list of events ", p1_events_over_runs)
    print(str(agent1), " list of events ", p2_events_over_runs)
    print("Avg time for run:", float(time_required_total)/float(runs))
    print(runs)
    with open("HA_obj_results.csv", 'a', newline = '') as file:
        writer = csv.writer(file)
        # row = ['p1_r', 'p1_g', 'p2_r', 'p2_g', 'p1_events', 'p2_events' ]
        row = [layout, agent0, agent1, float(p1_receiver_list_sum)/ float(runs), float(p1_giver_list_sum)/ float(runs), float(p2_receiver_list_sum)/ float(runs), float(p2_giver_list_sum)/ float(runs), p1_events_over_runs, p2_events_over_runs, float(time_required_total)/float(runs)]
        writer.writerow(row)

def main():
    dir = "/home/local/ASUAD/ubiswas2/ZSC/results/Overcooked/random3/population/eval-hsp-S2-s12-1/run1/trajs/random3/"
    val = 0
    for name in os.scandir(dir) :
        if name.is_file():
            val += analyse_for_single_run(name)
    print("incorrect,", val)

if __name__=="__main__":
    main()
'''
dict_keys(['put_onion_on_X',
 'put_dish_on_X',
   'put_soup_on_X', 
   'pickup_onion_from_X',
     'pickup_onion_from_O', 
     'pickup_dish_from_X',
       'pickup_dish_from_D', 
       'pickup_soup_from_X',
         'USEFUL_DISH_PICKUP',
           'SOUP_PICKUP', 
           'PLACEMENT_IN_POT', 
           'delivery', 
           'STAY', 
           'MOVEMENT', 
           'IDLE_MOVEMENT', 
           'IDLE_INTERACT_X',
             'IDLE_INTERACT_EMPTY'])

'''