import pickle
with open("traj_39_1.pkl", 'rb') as f:
    data = pickle.load(f)
#print(len(data))
print(data[0])
count_delivery = 0
delivery_timestep = []

k = len(data)
for n in range(0,k , 3):
    state_info = data[n]
    # Check if state has any dish objects
#     has_dish = False
#     if 'objects' in state_info:
#         for obj in state_info['objects']:
#             if obj['name'] == 'dish':
#                 has_dish = True
#                 break
    
    if True:
        print(f"\nState {n//3 + 1}:")
        print(f"State info: {state_info}")
        # if n+1 < len(data):
        #     print(f"Agent idx: {data[n+1]}")
        if n+1 < len(data):
            print("Player actions:")
            print(data[n+1])
        if n+2 < len(data):
            print(f"Events: {data[n+3]}")
            # if data[n+3][0]['delivery'] == 1 or data[n+3][1]['delivery'] == 1:
            #     print(f"State {n//4 + 1} has delivery event")
            #     print(f"Timestep: {state_info['timestep']}")
            #     delivery_timestep.append(state_info['timestep'])
            #     count_delivery += 1
                
        print("------------------------")

print("SECOND LAST STATE")
print(data[k-2])

print("LAST STATE")
print(data[k-1])
#     print("------------------------")

    # First check the events
#     if n+3 < len(data):
#         events = data[n+3]
#         has_soup_event = False
#         for event in events:
#             if (event.get('SOUP_PICKUP', 0) == 1 or 
#                 event.get('put_soup_on_X', 0) == 1 or 
#                 event.get('pickup_soup_from_X', 0) == 1 or 
#                 event.get('delivery', 0) == 1):
#                 has_soup_event = True
#                 break
        
#         if has_soup_event:
#             print(f"\nState {n//4 + 1}:")
#             print(f"State info: {state_info}")
#             if n+1 < len(data):
#                 print(f"Agent idx: {data[n+1]}")
#             if n+2 < len(data):
#                 print("Player actions:")
#                 for j, action in enumerate(data[n+2]):
#                     print(f"Player {j}: {action}")
#             print(f"Events: {events}")
#             print("------------------------")

# print("\n \n")
# print(f"Total number of states with delivery event: {count_delivery}")
# print(f"Delivery timesteps: {delivery_timestep}")
# p1_action_traj = []
# p2_action_traj = []
# p1_state_traj = []
# p2_state_traj = []
# p1_events_traj = []
# p2_events_traj = []
# agent_idx_traj = []
# for i in range(0, len(data)):
#         if i % 4 == 0 :
#                 p1_state_traj.append(data[i]["players"][0])
#                 p2_state_traj.append(data[i]["players"][1])
#                 if i + 1 < len(data):
#                         agent_idx_traj.append(data[i+1])
#                 if i + 2 < len(data):
#                         p1_action_traj.append(data[i+2][0])
#                         p2_action_traj.append(data[i+2][1])
#                 # if i + 3 < len(data):
#                 #         p1_events_traj.append(data[i+3][0])
#                 #         p2_events_traj.append(data[i+3][1])
# #print(agent_idx_traj)
# #print(f"Player 1 actions - {p1_action_traj}")
# print("\n \n \n")
# #print(f"Player 1 state - {p1_state_traj}")
print("\n \n \n")
#print(f"Player 1 events - {p1_events_traj}")

#print(p1_state_traj)


'''
trajectory properties - State 12:
State info: {'players': [{'position': (6, 1), 'orientation': (0, -1), 'held_object': {'name': 'onion', 'position': (6, 1)
, 'state': None}}, {'position': (1, 3), 'orientation': (0, 1), 'held_object': None}], 'objects': [{'name': 'dish',
 'position': (1, 4), 'state': None}], 'order_list': None, 'timestep': 11}

State_info contains players - array which has position, orientation and held objects of a player, objects - which objects 
are present in the environment. Order_list?

Agent idx: 0 - ?

Player actions: Can be move (specified by co-ordinates) and interact (interacting with a object)
Player 0: (-1, 0) //move
Player 1: (0, -1) //move 

Events: [{'put_onion_on_X': 0, 'put_dish_on_X': 0, 'put_soup_on_X': 0, 'pickup_onion_from_X': 0, 'pickup_onion_from_O': 0,
'pickup_dish_from_X': 0, 'pickup_dish_from_D': 0, 'pickup_soup_from_X': 0, 'USEFUL_DISH_PICKUP': 0, 'SOUP_PICKUP': 0,
'PLACEMENT_IN_POT': 0, 'delivery': 0, 'STAY': 0, 'MOVEMENT': 1, 'IDLE_MOVEMENT': 0, 'IDLE_INTERACT_X': 0,
'IDLE_INTERACT_EMPTY': 0}, {'put_onion_on_X': 0, 'put_dish_on_X': 0, 'put_soup_on_X': 0, 'pickup_onion_from_X': 0,
'pickup_onion_from_O': 0, 'pickup_dish_from_X': 0, 'pickup_dish_from_D': 0, 'pickup_soup_from_X': 0, 
'USEFUL_DISH_PICKUP': 0, 'SOUP_PICKUP': 0, 'PLACEMENT_IN_POT': 0, 'delivery': 0, 'STAY': 0, 'MOVEMENT': 1,
'IDLE_MOVEMENT': 0, 'IDLE_INTERACT_X': 0, 'IDLE_INTERACT_EMPTY': 0}]

when player moves - movement is 1
when player action interact - whatever action is taken is given by the event

'''