import pickle

#!usr/env/bin/env python
import pickle, json, copy
import numpy as np
import re
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
    if player_state["held_object"] is not None and player_state["held_object"]['name'] == "soup":
        return True
    return False
#onion-on-counter
def onion_on_counter(objs_state, pos):
    for obj in objs_state:
        if obj['name'] == 'onion' and obj['position'] == pos:
            return True
#dish-on-counter
def dish_on_counter(objs_state, pos):
    for obj in objs_state:
        if obj['name'] == 'dish' and obj['position'] == pos:
            return True
#soup-on-counter
def soup_on_counter(objs_state, pos):
    for obj in objs_state:
        if obj['name'] == 'soup' and obj['position'] == pos:
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
        if obj['name'] == 'onion' and obj['position'] == pos:
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
                ['X','X','X','O','O','X','X','X']]
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
        self.potOnions = 0
        self.potCooking = False
        self.potReady = False
        # print(self.layout_list)
        

def evaluate():
    name = "traj_9_1.pkl"
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
    potOnions = 0
    flag = 0
    # data is of type list, 1,
    for i in range(0, len(data)):
        if i % 3 == 0 :
            p1_state_traj.append(data[i]["players"][0])
            p2_state_traj.append(data[i]["players"][1])
            obj_traj.append(data[i]["objects"])
            if i + 1 < len(data):
                p1_action_traj.append(data[i+1][0])
                p2_action_traj.append(data[i+1][1])
            if i+2 < len(data):
                p1_events_traj.append(data[i+2][0])
                p2_events_traj.append(data[i+2][1])

    # for debugging
    # for timestep,i in enumerate(p1_events_traj):
    #     if i['pickup_dish_from_X']:
    #         print("p2 picks dish from counter", timestep)
    
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
                # counter           
                if onion_on_counter(obj_traj[i], onion_pick_location) and p1_effect_list.layout_list[onion_put_location[0]][onion_put_location[1]] != 'P': 
                    # print("p1 just picked an onion from counter at", i)
                    onion_pick_location = list(onion_pick_location)
                    if p2_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] == False and p2_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] != 0:
                        p2_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] = True
                        p2_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] = 0
                        p1_receiver_list.append("counterEmpty@" + str(onion_pick_location))
                        p2_giver_list.append("counterEmpty@" + str(onion_pick_location))
                    if p2_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[0]] == True and p2_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[0]] != 0:
                        p2_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                        p2_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[0]] = 0 #reset to 0 and false
                        p1_receiver_list.append("onionOnCounter@" + str(onion_pick_location))
                        p2_giver_list.append("onionOnCounter@" + str(onion_pick_location))
                    p1_effect_list.handEmpty = False
                    p1_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] = True
                    p1_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] += 1 
                    p1_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                    p1_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[1]] += 1
                # dispenser
                else:
                    # print("p1 just picked an onion from dispenser at",i)
                    p1_effect_list.handEmpty = False
            ''' Pick Dish'''
            if holding_dish(p1_state_traj[i+1]):
                dish_pick_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                # counter
                if dish_on_counter(obj_traj[i], dish_pick_location):
                    # print("p1 just picked an dish from counter", i)
                    dish_pick_location = list(dish_pick_location)
                    if p2_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] == False and p2_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] != 0:
                        p2_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] = True
                        p2_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        p1_receiver_list.append("counterEmpty@" + str(dish_pick_location))
                        p2_giver_list.append("counterEmpty@" + str(dish_pick_location))

                    if p2_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] == True and p2_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] != 0: 
                        p2_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] == False
                        p2_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        p1_receiver_list.append("dishOnCounter@" + str(dish_pick_location))
                        p2_giver_list.append("dishOnCounter@" + str(dish_pick_location))
                    p1_effect_list.handEmpty = False
                    p1_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] = True
                    p1_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] +=1
                    p1_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] = False
                    p1_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] += 1
                # dispenser
                else: 
                    # print("p1 just picked a dish from disp", i)
                    p1_effect_list.handEmpty = False
            ''' Pick Soup'''
            if holding_soup(p1_state_traj[i+1]):
                soup_pick_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                # counter
                if soup_on_counter(obj_traj[i], soup_pick_location) and p1_effect_list.layout_list[soup_pick_location[0]][soup_pick_location[1]] == 'X':
                    # print("p1 just picked an soup from counter", i) 
                    soup_pick_location = list(soup_pick_location)   
                    if p2_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] == False and p2_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        p2_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] = True
                        p2_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        p1_receiver_list.append("counterEmpty@" + str(soup_pick_location))
                        p2_giver_list.append("counterEmpty@" + str(soup_pick_location))
                    if p2_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] == True and p2_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        p2_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] == False
                        p2_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        p1_receiver_list.append("soupOnCounter@" + str(soup_pick_location))
                        p2_giver_list.append("soupOnCounter@" + str(soup_pick_location))
                    p1_effect_list.handEmpty = False 
                    p1_effect_list.holdingSoup = True
                    p1_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] = True
                    p1_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] += 1
                    p1_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] = False
                    p1_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] += 1
                # pot
                else:
                    # print("p1 just picked a soup from pot", i)
                    #check for preconditions
                    if p2_effect_list.potReady == True:
                        p2_effect_list.potReady = False
                        p1_receiver_list.append('potReady@', i)
                        p2_giver_list.append('potReady@', i)
                    # update effect predicates
                    p1_effect_list.handEmpty = False
                    p1_effect_list.potOnions = 0

             # for all PUT actions
            ''' Put Onion'''
            if holding_onion(p1_state_traj[i]) and not holding_onion(p1_state_traj[i+1]): # player has put down an onion (where)?
                onion_put_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation']))) 
                # counter
                if onion_on_counter(obj_traj[i+1], onion_put_location) and p1_effect_list.layout_list[onion_put_location[0]][onion_put_location[1]] != 'P':
                    if p2_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] == True and p2_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p2_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                        p2_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] = 0
                        p1_receiver_list.append('counterEmpty@' + str(onion_put_location))
                        p2_giver_list.append('counterEmpty@' + str(onion_put_location))
                    if p2_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p2_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p1_receiver_list.append('not onionOnCounter@' + str(onion_put_location))
                        p2_giver_list.append('not onionOnCounter@' + str(onion_put_location))
                    if p2_effect_list.dishOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p2_effect_list.dishOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p1_receiver_list.append('not dishOnCounter@' + str(onion_put_location))
                        p2_giver_list.append('not dishOnCounter@' + str(onion_put_location))
                    if p2_effect_list.soupOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p2_effect_list.soupOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p1_receiver_list.append('not soupOnCounter@' + str(onion_put_location))
                        p2_giver_list.append('not soupOnCounter@' + str(onion_put_location))

                    p1_effect_list.handEmpty = True
                    p1_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                    p1_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] += 1
                    p1_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] = True
                    p1_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] += 1

                # pot
                else:
                    # update effect predicates
                    p1_effect_list.handEmpty = True
                    if potOnions < 3:
                        p1_effect_list.potOnions += 1
                        potOnions += 1
                        if p2_effect_list.potOnions < 3 and p2_effect_list.potOnions > 0:
                            p1_receiver_list.append('potOnions@' + str(p1_effect_list.potOnions))
                            p2_giver_list.append('potOnions@' + str(p1_effect_list.potOnions))
                    # if number of onions in the pot equals 3, update predicate to indicate pot is ready
                    if potOnions == 3:
                        p1_effect_list.potReady = True
                        p1_effect_list.potOnions = 0
                        p2_effect_list.potOnions = 0
                        potOnions = 0

            ''' Put Dish'''
            if holding_dish(p1_state_traj[i-1]):
                dish_put_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                # counter
                if not holding_dish(p2_state_traj[i+1]) and not holding_soup(p2_state_traj[i+1]):
                    if p2_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] == True and p2_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p2_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                        p2_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] = 0
                        p1_receiver_list.append('counterEmpty@' + str(dish_put_location))
                        p2_giver_list.append('counterEmpty@' + str(dish_put_location))
                    if p2_effect_list.onionOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p2_effect_list.onionOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p1_receiver_list.append('not onionOnCounter@' + str(dish_put_location))
                        p2_giver_list.append('not onionOnCounter@' + str(dish_put_location))
                    if p2_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p2_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p1_receiver_list.append('not dishOnCounter@' + str(dish_put_location))
                        p2_giver_list.append('not dishOnCounter@' + str(dish_put_location))
                    if p2_effect_list.soupOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p2_effect_list.soupOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p1_receiver_list.append('not soupOnCounter@' + str(dish_put_location))
                        p2_giver_list.append('not soupOnCounter@' + str(dish_put_location))

                    p1_effect_list.handEmpty = True
                    p1_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                    p1_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] += 1
                    p1_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] = True
                    p1_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] += 1

                # player collected soup
                elif holding_soup(p2_state_traj[i+1]):
                    # print("p2 pick soup from pot", i)
                    # check for preconditions
                    if p2_effect_list.potReady == True:
                        p2_effect_list.potReady == False
                        p1_receiver_list.append("potReady@" + str(dish_put_location))
                        p2_giver_list.append("potReady@" + str(dish_put_location))
                    p1_effect_list.handEmpty = False
                    p1_effect_list.potReady = False

            ''' Put Soup'''
            if holding_soup(p1_state_traj[i]):
                soup_put_location = tuple(map(sum, zip(p1_state_traj[i]['position'],p1_state_traj[i]['orientation'])))
                # counter
                if not p1_events_traj[i]['delivery']:
                    if p2_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] == True and p2_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p2_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                        p2_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] = 0
                        p1_receiver_list.append('counterEmpty@' + str(soup_put_location))
                        p2_giver_list.append('counterEmpty@' + str(soup_put_location))
                    if p2_effect_list.onionOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p2_effect_list.onionOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p1_receiver_list.append('not onionOnCounter@' + str(soup_put_location))
                        p2_giver_list.append('not onionOnCounter@' + str(soup_put_location))
                    if p2_effect_list.dishOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p2_effect_list.dishOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p1_receiver_list.append('not dishOnCounter@' + str(soup_put_location))
                        p2_giver_list.append('not dishOnCounter@' + str(soup_put_location))
                    if p2_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p2_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p1_receiver_list.append('not soupOnCounter@' + str(soup_put_location))
                        p2_giver_list.append('not soupOnCounter@' + str(soup_put_location))

                    p1_effect_list.handEmpty = True
                    p1_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                    p1_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] += 1
                    p1_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] = True
                    p1_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] += 1

                # delivery
                else: 
                    print("soup delivered")
                    flag +=1
                    p1_effect_list.handEmpty = True
                    if flag >5:
                        print("game over")
                        return p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list

        if p2_action == "interact":
            # for all PICK actions
            ''' Pick Onion'''
            if holding_onion(p1_state_traj[i]) and not holding_onion(p2_state_traj[i+1]):
                onion_pick_location = tuple(map(sum, zip(p2_state_traj[i]['position'], p2_state_traj[i]['orientation'])))
                # counter
                if onion_on_counter(obj_traj[i+1], onion_put_location) and p1_effect_list.layout_list[onion_put_location[0]][onion_put_location[1]] != 'P': 
                    if p1_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] == False and p1_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] != 0:      
                        p1_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] = True
                        p1_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] = 0
                        p2_receiver_list.append('counterEmpty@' + str(onion_pick_location))
                        p1_giver_list.append('counterEmpty@' + str(onion_pick_location))
                    if p1_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[0]] == True and p1_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[0]] != 0:
                        p1_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                        p1_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[0]]= 0
                        p2_receiver_list.append("onionOnCounter@" + str(onion_pick_location))
                        p1_giver_list.append("onionOnCounter@" + str(onion_pick_location))
                    p2_effect_list.handEmpty = False
                    p2_effect_list.counterEmpty[onion_pick_location[0]][onion_pick_location[1]] = True
                    p2_effect_list.counterEmptyChange[onion_pick_location[0]][onion_pick_location[1]] += 1
                    p2_effect_list.onionOnCounter[onion_pick_location[0]][onion_pick_location[1]] = False
                    p2_effect_list.onionOnCounterChange[onion_pick_location[0]][onion_pick_location[1]] += 1
                # dispenser
                else:
                    # print("p1 just picked an onion from dispenser")
                    p2_effect_list.handEmpty = False

            ''' Pick Dish'''
            if holding_dish(p2_state_traj[i+1]):
                dish_pick_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                # counter
                if dish_on_counter(obj_traj[i], dish_pick_location):
                    # print("p1 just picked an dish from counter", i)
                    if p1_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] == False and p1_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] != 0:
                        p1_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] = True
                        p1_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        p2_receiver_list.append('counterEmpty@' + str(dish_pick_location))
                        p1_giver_list.append('counterEmpty@' + str(dish_pick_location))
                    if p1_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] == True and p1_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] != 0: 
                        p1_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] = False
                        p1_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] = 0
                        p2_receiver_list.append('dishOnCounter@' + str(dish_pick_location))
                        p1_giver_list.append('dishOnCounter@' + str(dish_pick_location))
                    p2_effect_list.handEmpty = False
                    p2_effect_list.counterEmpty[dish_pick_location[0]][dish_pick_location[1]] = True
                    p2_effect_list.counterEmptyChange[dish_pick_location[0]][dish_pick_location[1]] += 1
                    p2_effect_list.dishOnCounter[dish_pick_location[0]][dish_pick_location[1]] = False
                    p2_effect_list.dishOnCounterChange[dish_pick_location[0]][dish_pick_location[1]] += 1
                # dispenser
                else: 
                    # print("p1 just picked a dish from disp", i)
                    p2_effect_list.handEmpty = False

            ''' Pick Soup '''
            if holding_soup(p2_state_traj[i+1]):
                soup_pick_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                # counter
                if soup_on_counter(obj_traj[i], soup_pick_location) and p1_effect_list.layout_list[soup_pick_location[0]][soup_pick_location[1]] == 'X':
                    # print("p2 just picked an soup from counter", i)     
                    if p1_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] == False and p1_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        p1_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] = True
                        p1_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        p2_receiver_list.append('counterEmpty@' + str(soup_pick_location))
                        p1_giver_list.append('counterEmpty@' + str(soup_pick_location))
                    if p1_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] == True and p1_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] != 0:
                        p1_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] = False
                        p1_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] = 0
                        p2_receiver_list.append("soupOnCounter" + str(soup_pick_location))
                        p1_giver_list.append("soupOnCounter" + str(soup_pick_location))
                    p2_effect_list.handEmpty = False
                    p2_effect_list.holdingSoup = True
                    p2_effect_list.counterEmpty[soup_pick_location[0]][soup_pick_location[1]] = True
                    p2_effect_list.counterEmptyChange[soup_pick_location[0]][soup_pick_location[1]] += 1
                    p2_effect_list.soupOnCounter[soup_pick_location[0]][soup_pick_location[1]] = False
                    p2_effect_list.soupOnCounterChange[soup_pick_location[0]][soup_pick_location[1]] += 1
                # pot
                else:
                    if p1_effect_list.potReady == True:
                        p1_effect_list.potReady = False
                        p2_receiver_list.append("potReady@", i)
                        p1_giver_list.append("potReady@", i)
                    # update effect predicates
                    # print("p2 just picked a soup from pot", i)
                    p2_effect_list.handEmpty = False

            ''' PUT ACTIONS '''
            ''' Put Onion'''
            if holding_onion(p2_state_traj[i]) and not holding_onion(p2_state_traj[i+1]): 
                onion_put_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                #  counter
                if onion_on_counter(obj_traj[i+1], onion_put_location) and p1_effect_list.layout_list[onion_put_location[0]][onion_put_location[1]] != 'P':
                    # print("p2 put onion on the counter", i)
                    # check for preconditions
                    if p1_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] == True and p1_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p1_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                        p1_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] = 0
                        p2_receiver_list.append('counterEmpty@' + str(onion_put_location))
                        p1_giver_list.append('counterEmpty@' + str(onion_put_location))
                    if p1_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p1_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p2_receiver_list.append('not onionOnCounter@' + str(onion_put_location))
                        p1_giver_list.append('not onionOnCounter@' + str(onion_put_location))
                    if p1_effect_list.dishOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p1_effect_list.dishOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p2_receiver_list.append('not dishOnCounter@' + str(onion_put_location))
                        p1_giver_list.append('not dishOnCounter@' + str(onion_put_location))
                    if p1_effect_list.soupOnCounter[onion_put_location[0]][onion_put_location[1]] == False and p1_effect_list.soupOnCounterChange[onion_put_location[0]][onion_put_location[1]] != 0:
                        p2_receiver_list.append('not soupOnCounter@' + str(onion_put_location))
                        p1_giver_list.append('not soupOnCounter@' + str(onion_put_location))
                    p2_effect_list.handEmpty = True
                    p2_effect_list.counterEmpty[onion_put_location[0]][onion_put_location[1]] = False
                    p2_effect_list.counterEmptyChange[onion_put_location[0]][onion_put_location[1]] += 1
                    p2_effect_list.onionOnCounter[onion_put_location[0]][onion_put_location[1]] = True
                    p2_effect_list.onionOnCounterChange[onion_put_location[0]][onion_put_location[1]] += 1
                    # print(p2_receiver_list)
                    # print(p1_giver_list)
                # pot
                else:
                    p2_effect_list.handEmpty = True
                    if potOnions < 3:
                        p2_effect_list.potOnions += 1
                        potOnions += 1
                        if p1_effect_list.potOnions < 3 and p1_effect_list.potOnions > 0:
                            p2_receiver_list.append('potOnions@' + str(p1_effect_list.potOnions))
                            p1_giver_list.append('potOnions@' + str(p1_effect_list.potOnions))
                    # if number of onions in the pot equals 3, update predicate to indicate pot is ready
                    if potOnions == 3:
                        p2_effect_list.potReady = True
                        p1_effect_list.potOnions = 0
                        p2_effect_list.potOnions = 0
                        potOnions = 0

            '''Put Dish'''
            if holding_dish(p2_state_traj[i]):
                dish_put_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                #  counter
                if not holding_dish(p2_state_traj[i+1]) and not holding_soup(p2_state_traj[i+1]): 
                    # print("p2 put dish down on counter", i)
                    if p1_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] == True and p1_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p1_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                        p1_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] = 0
                        p2_receiver_list.append('counterEmpty@' + str(dish_put_location))
                        p1_giver_list.append('counterEmpty@' + str(dish_put_location))
                    if p1_effect_list.onionOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p1_effect_list.onionOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p2_receiver_list.append('not onionOnCounter@' + str(dish_put_location))
                        p1_giver_list.append('not onionOnCounter@' + str(dish_put_location))
                    if p1_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p1_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p2_receiver_list.append('not dishOnCounter@' + str(dish_put_location))
                        p1_giver_list.append('not dishOnCounter@' + str(dish_put_location))
                    if p1_effect_list.soupOnCounter[dish_put_location[0]][dish_put_location[1]] == False and p1_effect_list.soupOnCounterChange[dish_put_location[0]][dish_put_location[1]] != 0:
                        p2_receiver_list.append('not soupOnCounter@' + str(dish_put_location))
                        p1_giver_list.append('not soupOnCounter@' + str(dish_put_location))
                    p2_effect_list.handEmpty = True
                    p2_effect_list.counterEmpty[dish_put_location[0]][dish_put_location[1]] = False
                    p2_effect_list.counterEmptyChange[dish_put_location[0]][dish_put_location[1]] += 1
                    p2_effect_list.dishOnCounter[dish_put_location[0]][dish_put_location[1]] = True
                    p2_effect_list.dishOnCounterChange[dish_put_location[0]][dish_put_location[1]] += 1
                # collect soup from pot
                elif holding_soup(p2_state_traj[i+1]):
                    # print("p2 pick soup from pot", i)
                    # check for preconditions
                    if p1_effect_list.potReady == True:
                        p1_effect_list.potReady == False
                        p2_receiver_list.append("potReady@" + str(dish_put_location))
                        p1_giver_list.append("potReady@" + str(dish_put_location))
                    p2_effect_list.handEmpty = False
                    p2_effect_list.potReady = False

            ''' Put Soup'''
            if holding_soup(p2_state_traj[i]) and not holding_soup(p2_state_traj[i+1]):
                soup_put_location = tuple(map(sum, zip(p2_state_traj[i]['position'],p2_state_traj[i]['orientation'])))
                # counter
                if not p2_events_traj[i]['delivery']:
                    # print("p2 has dropped soup off at counter", i)
                    if p1_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] == True and p1_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p1_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                        p1_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] = 0
                        p2_receiver_list.append('counterEmpty@' + str(soup_put_location))
                        p1_giver_list.append('counterEmpty@' + str(soup_put_location))
                    if p1_effect_list.onionOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p1_effect_list.onionOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p2_receiver_list.append('not onionOnCounter@' + str(soup_put_location))
                        p1_giver_list.append('not onionOnCounter@' + str(soup_put_location))
                    if p1_effect_list.dishOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p1_effect_list.dishOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p2_receiver_list.append('not dishOnCounter@' + str(soup_put_location))
                        p1_giver_list.append('not dishOnCounter@' + str(soup_put_location))
                    if p1_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] == False and p1_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] != 0:
                        p2_receiver_list.append('not soupOnCounter@' + str(soup_put_location))
                        p1_giver_list.append('not soupOnCounter@' + str(soup_put_location))
                    p2_effect_list.handEmpty = True
                    p2_effect_list.counterEmpty[soup_put_location[0]][soup_put_location[1]] = False
                    p2_effect_list.counterEmptyChange[soup_put_location[0]][soup_put_location[1]] += 1
                    p2_effect_list.soupOnCounter[soup_put_location[0]][soup_put_location[1]] = True
                    p2_effect_list.soupOnCounterChange[soup_put_location[0]][soup_put_location[1]] += 1

                # deliver
                else: 
                    print("soup delivered")
                    flag += 1
                    p2_effect_list.handEmpty = True
                    if flag >5:
                        print("game over")
                        return p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list
                
    # return
    return p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list

p1_receiver_list, p2_receiver_list, p1_giver_list, p2_giver_list = evaluate()
print("p1 receives", p1_receiver_list)
print("p2 gives", p2_giver_list)
print("p2 receives", p2_receiver_list)
print("p1 gives", p1_giver_list)
print("nan")
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