import json
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

def load_human_data(file_path: str = "prob.json") -> Dict:
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


if __name__ == "__main__":
    data = load_human_data()
    print(data.keys())
    print(data['ep_rewards'][0])

    for i in range(len(data['ep_states'][0])):
        print(f"Timestep: {i}")
        players = data['ep_states'][0][i]['players']
        info= []
        # for player in players:
        #     info.append({"position": player['position'], "orientation": player['orientation']})
        print(f"Timestep: {i} - {info}")
        print("\n")

        print(f"Actions:")
        print(data['ep_actions'][0][i])
        print("\n")

        print(f"Rewards: ")
        print(data['ep_rewards'][0][i])
        print("\n")   


    #for i in range(len(data['ep_rewards'][0])):
        