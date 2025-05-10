import json
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import pickle
# Action mapping dictionary
ACTION_MAPPING = {
    0: (0, -1),    # up
    1: (0, 1),   # down
    2: (1, 0),    # right
    3: (-1, 0),   # left
    4: (0, 0),    # stay
    5: "interact" # interact
}

def load_human_data(file_path: str = "human.json") -> Dict:
    """
    Load and parse the human gameplay data from JSON file.
    
    Args:
        file_path (str): Path to the human gameplay JSON file
        
    Returns:
        Dict: Parsed human gameplay data
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def convert_to_pkl(data: Dict) -> None:
    pkl_data = []
    
    for ep_idx in range(len(data['ep_states'])):
        episode_data = []
        for t in range(len(data['ep_states'][ep_idx])):
            state = data['ep_states'][ep_idx][t]
            
            # Convert state format
            converted_state = {
                'players': [
                    {
                        'position': tuple(state['players'][0]['position']),
                        'orientation': tuple(state['players'][0]['orientation']),
                        #'held_object': state['players'][0].get('held_object', None)
                    },
                    {
                        'position': tuple(state['players'][1]['position']),
                        'orientation': tuple(state['players'][1]['orientation']),
                        #'held_object': state['players'][1].get('held_object', None)
                    }
                ],
            }

            # Convert held objects
        
            held_object_0 = state['players'][0].get('held_object', None)
            if held_object_0 is not None:
                converted_state['players'][0]['held_object'] = {
                    'name': held_object_0['name'],
                    'position': tuple(held_object_0['position']),
                    'state': held_object_0.get('state', None)
                }
            else:
                converted_state['players'][0]['held_object'] = None


            held_object_1 = state['players'][1].get('held_object', None)
            if held_object_1 is not None:
                converted_state['players'][1]['held_object'] = {
                    'name': held_object_1['name'],
                    'position': tuple(held_object_1['position']),
                    'state': held_object_1.get('state', None)
                }
            else:
                converted_state['players'][1]['held_object'] = None
                
            
            if state['objects'] == {}:
                converted_state['objects'] = []
            else:
                objects = state['objects']
                converted_state['objects'] = []
                for obj in objects.values():
                    converted_state['objects'].append({
                        'name': obj['name'],
                        'position': tuple(obj['position']),
                        'state': obj.get('state', None)
                    })
            
            converted_state['order_list'] = state['order_list']
            converted_state['timestep'] = t
            # Convert action indices to direction tuples
            actions = data['ep_actions'][ep_idx][t]
            converted_actions = tuple(ACTION_MAPPING[action] for action in actions)
            
            #for now, Assuming that there is only one episode            
            pkl_data.append(converted_state)

            #agent idx
            pkl_data.append(0)

            #action
            pkl_data.append(converted_actions)

            #reward
            pkl_data.append(data['ep_rewards'][ep_idx][t])
        
        pkl_data.append(episode_data)
    
    return pkl_data

if __name__ == "__main__":
    data = load_human_data()
    pkl_data = convert_to_pkl(data)
    print(pkl_data[0:8])

    #save to pkl
    with open('human_trail.pkl', 'wb') as f:
        pickle.dump(pkl_data, f)