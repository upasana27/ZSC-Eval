import pickle
from rl_to_pddl import (
    print_occupancy, build_terrain_grid, get_initial_agent_positions,
    initialize_grid, record_grid_snapshot, update_grid_for_interact_and_record,
    update_grid_for_move_and_record, construct_grid_from_state, process_actions
)

with open("output_data.pkl", 'rb') as f:
        data = pickle.load(f)

snapshots = data['snapshots']
action_logs = data['action_logs']

# Convert action logs to array with sequential indices
action_logs_array = []
for i in range(len(action_logs)):
    action_logs_array.append(action_logs[i])

def is_executable(from_pos, to_pos, curr_action_log, curr_grid_log):
    """
    Check if the trajectory from to_pos to the end is executable starting from the grid state at from_pos.
    Args:
        from_pos: Starting index in the trajectory (grid state to start from)
        to_pos: Position to start executing actions from
        curr_action_log: Current action log array
        curr_grid_log: Current grid log array
    Returns:
        bool: True if the segment is executable, False otherwise
    """
    # Get the initial grid state at from_pos
    initial_grid = curr_grid_log[from_pos]
    
    # Process all actions from to_pos till the end
    for i in range(to_pos, len(curr_action_log)):
        # Get the action log for this timestep
        action_log = curr_action_log[i]
        
        # Process the action and update the grid
        if action_log['action'] == 'interact':
            # Handle interact action
            agent_idx = action_log['agent']
            pos = action_log['from_pos']
            next_state = curr_grid_log[i+1] if i+1 < len(curr_grid_log) else None
            update_grid_for_interact_and_record(
                agent_idx=agent_idx,
                pos=pos,
                timestep=i,
                grid=initial_grid,
                next_state=next_state
            )
        else:
            # Handle movement action
            agent_idx = action_log['agent']
            from_pos = action_log['from_pos']
            to_pos = action_log['to_pos']
            update_grid_for_move_and_record(
                agent_idx=agent_idx,
                from_pos=from_pos,
                to_pos=to_pos,
                timestep=i,
                grid=initial_grid,
                action=action_log['action']
            )
    
    # Compare the final grid state with the expected final grid state
    final_grid = curr_grid_log[-1]  # Get the last grid state
    
    # Compare each cell in the grid
    for y in range(len(initial_grid)):
        for x in range(len(initial_grid[0])):
            if initial_grid[y][x] != final_grid[y][x]:
                return False
    
    return True
      