import pickle
from rl_to_pddl import (
    print_occupancy, build_terrain_grid, get_initial_agent_positions,
    initialize_grid,  update_grid_for_interact_and_record,
    update_grid_for_move_and_record, construct_grid_from_state, process_actions
)

with open("output_data.pkl", 'rb') as f:
        data = pickle.load(f)

def extract_cells_with_object(grid_state):
    """
    Extracts cells from the grid state that contain the 'object' field.

    Args:
    - grid_state (dict): A dictionary where keys are cell positions (tuples), and
                         values are dictionaries representing the cell's properties.

    Returns:
    - dict: A filtered dictionary with only the cells that contain the 'object' field.
    """
    return {position: properties for position, properties in grid_state.items() if 'object' in properties}

def filter_effect_list_by_state(effect_list, state_snapshot):
    """
    Filters the effect list by:
    1. Removing entries where the object is not present or its state doesn't match in the state snapshot.
    2. Keeping only the most recent entry for duplicate objects based on their state.

    Args:
    - effect_list: A list containing effect entries for a single agent at a timestep.
                   Each effect entry is a tuple of (effect_object, timestamp).
    - state_snapshot: A 2D list representing the state of the grid at a timestep.

    Returns:
    - A filtered effect list with valid and deduplicated entries.
    """
    
    
    filtered_effect_list = []  # Store valid entries
    object_states_timestamps = {}  # Track the most recent entry for each object by its state

    for effect_entry in effect_list:
        # Unpack the effect entry
        try:
            effect_object, timestamp = effect_entry
        except ValueError:
            print(f"Unexpected effect_entry structure: {effect_entry}")
            continue  # Skip invalid entries

        is_valid = True  # Flag to determine if we should keep this entry
        # print("this is the object",effect_object)
        for position, object_properties in effect_object.items():
            # print(position)
            x, y = position  # Extract cell coordinates

            try:
                # Retrieve the actual state from the snapshot
                actual_state = state_snapshot[y][x]
                actual_object = actual_state.get('object', None)
                object_name = object_properties['name'] # comment this out when soup fixed
                if actual_object == None:
                    is_valid = False
                    break
                if object_properties['id'] != actual_object['id']:
                    is_valid = False
                    break
                # print("its valid")

            except IndexError:
                # If the position is out of bounds in the state snapshot
                is_valid = False
                break

            # Check if this object's state already exists in the filtered list
            object_state_id = object_properties['id']
            # print(object_state_id)
            # print(object_states_timestamps)
            if object_state_id in object_states_timestamps:
                # Compare timestamps: keep the most recent entry
                if timestamp <= object_states_timestamps[object_state_id]:
                    is_valid = False
                    break

        # Only keep the effect entry if it is valid
        if is_valid:
            # print("it should be valid")
            for position, object_properties in effect_object.items():
                object_states_timestamps[object_state_id] = timestamp  # Update the most recent timestamp
            filtered_effect_list.append(effect_entry)

    return filtered_effect_list

def check_precondition_in_effect_list(action, effect_list_other_agent):
    """
    Check if the preconditions of an action, including the state of the object, 
    are present in the effect list of the other agent.

    Args:
    - action: A dictionary containing the action details.
    - effect_list_other_agent: The effect list for the other agent at the same timestep.

    Returns:
    - True if the precondition (including the state) is present in the effect list, False otherwise.
    """
    preconditions = extract_cells_with_object(action.get('preconditions', {}))
    pre_position = None
    for pre_position, pre_data in preconditions.items():
        pre_object = pre_data['object']
    for effect_entry in effect_list_other_agent:
        effect_object, _ = effect_entry  # Extract the effect details and timestamp
        # print(effect_entry)
        for position, effect_data in effect_object.items():
            if pre_position == position and pre_object is not None:
                # print(pre_position, pre_data)
                if pre_object['name'] == effect_data['name']:
                        # print(effect_data)
                        return True,effect_data
    return False, None  # Precondition with state not found

def check_if_int_goal(int_obj_id, goal_object):
    for object in goal_object['state'][0]:
        if object['id'] == int_obj_id:
            return True
    return False
def check_if_giver_loop(int_obj_id, giver_agent_id, snapshot_logs_array):
    # at each timestep, check the cell where the giver agent is at and if they are holding that object again
    giver_agent = 'Agent_0' if giver_agent_id == 0 else 'Agent_1'
    for t, curr_state in enumerate(snapshot_logs_array):
        # print(curr_state[0][0])
        flattened_state = [element for row in curr_state for element in row]
        for cell in flattened_state:
            # print("this is cell", cell)
            if cell[giver_agent]['is_present'] == True and cell[giver_agent]['held_objects'] is not None:
                giver_holding_obj = cell[giver_agent]['held_objects']
                # print(giver_holding_obj)
                if giver_holding_obj['id'] == int_obj_id:
                    print("giver got object back", int_obj_id)
                    return False
    return True

def check_if_receiver_loop(int_obj_id, rec_agent_id, snapshot_logs_array):
    # at each timestep, check the cell where the giver agent is at and if they are holding that object again
    rec_agent = 'Agent_0' if rec_agent_id == 0 else 'Agent_1'
    for t, curr_state in enumerate(snapshot_logs_array):
        # print(curr_state[0][0])
        flattened_state = [element for row in curr_state for element in row]
        for cell in flattened_state:
            # print("this is cell", cell)
            if cell[rec_agent]['is_present'] == True and cell[rec_agent]['held_objects'] is not None:
                rec_holding_obj = cell[rec_agent]['held_objects']
                # print(giver_holding_obj)
                if rec_holding_obj['id'] == int_obj_id:
                    print("receiver had object already", int_obj_id)
                    return False
    return True

snapshots = data['snapshots']
action_logs = data['action_logs']
# print("check",snapshots[10][4][1])
# Convert action logs to array with sequential indices
action_logs_array = []
snapshot_logs_array = []
for i in range(len(snapshots)):
    snapshot_logs_array.append(snapshots[i])
effect_list = [[],[]]
for t,joint_action in enumerate(action_logs):
    for agent_id,action in enumerate(joint_action):
        if action['action'] == 'interact' and action['action_type'] == 'deliver_soup':
                x,y = action['from_pos']
                # print(snapshot_logs_array[t-1][y][x])
                if agent_id == 0:
                    goal_object = snapshot_logs_array[t-1][y][x]['Agent_0']['held_objects']
                else:
                    goal_object = snapshot_logs_array[t-1][y][x]['Agent_0']['held_objects']
        
        


for t,joint_action in enumerate(action_logs):
    if t<171:
        print(t)
        for agent_id, action in enumerate(joint_action):
            # action is of form dictionary with keys
            # dict_keys(['agent', 'action', 'from_pos', 'to_pos', 'timestep', 'move_successful', 'preconditions', 'effects'])
            for cell, effect_dict_item in action['effects'].items():
                # for all the cells that the action affects, only consider the objects field in the dictionary
                effect_dict_item = {cell : effect_dict_item}
                for key,values in effect_dict_item.items():
                    if 'object' in values and values['object'] is not None:
                        effect_dict_item_cell = {key : values['object']}
                        effect_list[agent_id].append([effect_dict_item_cell, t])
            # now we have effect list for each agent as list of dictionaries, call function to validate if the past
            # effects are present in the state snapshot at the current time step or not
            # print("prior effect list for ", agent_id, effect_list[agent_id])
            
            effect_list[agent_id] = filter_effect_list_by_state(effect_list[agent_id], snapshots[t])
            print("curr effect list for", agent_id, len(effect_list[agent_id]))
            # check if precondition of this action is present in the effect list of the other agent
            other_agent_id = 0 if agent_id == 1 else 1
            # print("lets check for", agent_id)
            # print(effect_list[other_agent_id])
            is_int, int_obj= check_precondition_in_effect_list(action, effect_list[other_agent_id])
            if is_int:
                print("precondition matched at", t)
                int_obj_id = int_obj['id']
                if check_if_int_goal(int_obj_id, goal_object):
                    print("object was in goal state")
                print("receiver object id", agent_id)
                print("giver object id", other_agent_id)
                if check_if_giver_loop(int_obj_id, other_agent_id, snapshot_logs_array[t:len(snapshot_logs_array)]):
                    print('object did not get back to giver')
                if check_if_receiver_loop(int_obj_id, agent_id, snapshot_logs_array[0:t]):
                    print('object was not at receiver')
            
                
      
