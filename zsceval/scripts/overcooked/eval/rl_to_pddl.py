def build_terrain_grid(layout_list):
    terrain_grid = []
    for row in layout_list:
        terrain_row = []
        for cell in row:
            if cell == 'X':
                terrain_row.append('counter')
            elif cell == 'P':
                terrain_row.append('pot')
            elif cell == 'D':
                terrain_row.append('dish_dispenser')
            elif cell == 'O':
                terrain_row.append('onion_dispenser')
            elif cell == 'S':
                terrain_row.append('delivery')
            elif cell in [1, 2]:
                terrain_row.append('floor')  # agents start on floor
            elif cell is None:
                terrain_row.append('floor')
            else:
                raise ValueError(f"Unknown layout cell: {cell}")
        terrain_grid.append(terrain_row)
    return terrain_grid


def get_initial_agent_positions(layout_list):
    positions = {}
    for y, row in enumerate(layout_list):
        for x, cell in enumerate(row):
            if cell == 1 or cell == 2:
                positions[int(cell)-1] = (x, y)
    return [positions[i] for i in sorted(positions)]



def print_occupancy(grid):
    """
    Print a detailed view of the grid state showing terrain, agents, and objects.
    Symbols:
    - Agents: A0, A1 (with held objects in parentheses)
    - Objects: o=onion, d=dish, s=soup
    - Terrain: X=counter, P=pot, D=dish dispenser, O=onion dispenser, S=serving, .=floor
    """
    height = len(grid)
    width = len(grid[0])
    
    # Print column numbers for reference
    print('  ' + ' '.join([str(i) for i in range(width)]))
    
    for y in range(height):
        row_str = [str(y)]  # Add row number
        for x in range(width):
            cell = grid[y][x]
            # First check for agents
            if cell['Agent_0']['is_present']:
                if cell['Agent_0']['held_objects']:
                    row_str.append(f"A0({cell['Agent_0']['held_objects']['name'][:1]})")
                else:
                    row_str.append("A0")
            elif cell['Agent_1']['is_present']:
                if cell['Agent_1']['held_objects']:
                    row_str.append(f"A1({cell['Agent_1']['held_objects']['name'][:1]})")
                else:
                    row_str.append("A1")
            # Then check for objects
            elif cell['object']:
                obj_name = cell['object']['name']
                if obj_name == 'onion':
                    row_str.append('o')
                elif obj_name == 'dish':
                    row_str.append('d')
                elif obj_name == 'soup':
                    row_str.append('s')
                else:
                    row_str.append(obj_name[0])
            # Finally show terrain
            else:
                terrain = cell['terrain']
                if terrain == 'counter':
                    row_str.append('X')
                elif terrain == 'pot':
                    row_str.append('P')
                elif terrain == 'dish_dispenser':
                    row_str.append('D')
                elif terrain == 'onion_dispenser':
                    row_str.append('O')
                elif terrain == 'delivery':
                    row_str.append('S')
                elif terrain == 'floor':
                    row_str.append('.')
                else:
                    row_str.append(terrain[0].upper())
        print(' '.join(row_str))


def initialize_grid(terrain_grid, agent_positions):
    width = len(terrain_grid[0])  # Number of columns
    height = len(terrain_grid)    # Number of rows
    grid = []
    
    for y in range(height):
        row = []
        for x in range(width):
            cell = {
                'terrain': terrain_grid[y][x],
                'Agent_0': {
                    'is_present': False,
                    'hand_empty': True,
                    'held_objects': None,
                    'orientation': (0,-1)  # Default orientation
                },
                'Agent_1': {
                    'is_present': False,
                    'hand_empty': True,
                    'held_objects': None,
                    'orientation': (0,-1)  # Default orientation
                },
                'object': None,
                'is_empty': True
            }
            row.append(cell)
        grid.append(row)
    
    # Place agents in their initial positions
    for agent_idx, (x, y) in enumerate(agent_positions):
        grid[y][x][f'Agent_{agent_idx}']['is_present'] = True
        grid[y][x]['is_empty'] = False
    
    return grid

def record_grid_snapshot(grid, timestep, snapshots):
    """
    Record the current state of the grid at the given timestep.
    Args:
        grid: Current grid state
        timestep: Current timestep
        snapshots: Dictionary to store snapshots, keyed by timestep
    """
    # Create a deep copy of the grid to avoid reference issues
    snapshot = []
    for row in grid:
        snapshot_row = []
        for cell in row:
            snapshot_row.append(cell.copy())
        snapshot.append(snapshot_row)
    
    snapshots[timestep] = snapshot

def update_grid_for_move_and_record(agent_idx, from_pos, to_pos, timestep, grid, snapshots=None, action=None):
    """
    Update the grid for an agent's move and record the snapshot if snapshots dict is provided.
    Args:
        agent_idx: Index of the agent (0 or 1)
        from_pos: Current position of the agent (x, y)
        to_pos: Target position for the move (x, y)
        timestep: Current timestep
        grid: Current grid state
        snapshots: Dictionary to store snapshots
        action: The action being attempted (dx, dy) for movement or 'interact'
    Returns a dictionary containing the move log, preconditions, and effects.
    """
    if snapshots is None:
        snapshots = {}
    
    # Record snapshot before move
    record_grid_snapshot(grid, timestep, snapshots)
    
    # Get agent key
    agent_key = f'Agent_{agent_idx}'

    if agent_idx == 0:
        other_agent = 1
    else:
        other_agent = 0
    fx, fy = from_pos
    tx, ty = to_pos
    
    # Define preconditions as cell states before the move
    preconditions = {
        to_pos: {
            'terrain': 'floor',
            f'Agent_{other_agent}': {'is_present': False},
            'object': None,
        }
    }
    
    # Check if preconditions are met
    to_cell = grid[ty][tx]
    can_move = (
        to_cell['terrain'] == 'floor' and
        not to_cell[f'Agent_{other_agent}']['is_present'] and
        to_cell['object'] is None
    )
    
    # Only update orientation if there's actual movement (not 0,0)
    if action != 'interact' and action != (0, 0):
        grid[fy][fx][agent_key]['orientation'] = action
    
    # Only update positions if preconditions are met
    if can_move:
        # Update agent position and is_empty status
        grid[fy][fx][agent_key]['is_present'] = False
        grid[ty][tx][agent_key]['is_present'] = True
        if action != (0, 0):  # Only update orientation if there's actual movement
            grid[ty][tx][agent_key]['orientation'] = action
        
        # Update held object fields
        held_obj = grid[fy][fx][agent_key]['held_objects']
        grid[ty][tx][agent_key]['held_objects'] = held_obj
        grid[fy][fx][agent_key]['held_objects'] = None
        
        # Update hand_empty status
        grid[ty][tx][agent_key]['hand_empty'] = held_obj is None
        grid[fy][fx][agent_key]['hand_empty'] = True
        
        # Update is_empty status for both cells
        grid[fy][fx]['is_empty'] = not (grid[fy][fx]['Agent_0']['is_present'] or grid[fy][fx]['Agent_1']['is_present'] or grid[fy][fx]['object'])
        grid[ty][tx]['is_empty'] = not (grid[ty][tx]['Agent_0']['is_present'] or grid[ty][tx]['Agent_1']['is_present'] or grid[ty][tx]['object'])
    else:
        # If preconditions not met, agent stays in current position
        to_pos = from_pos
        tx, ty = to_pos
    
    # Record snapshot after move
    record_grid_snapshot(grid, timestep, snapshots)
    
    # Define effects as cell states after the move
    effects = {
        from_pos: {
            'terrain': grid[fy][fx]['terrain'],
            'Agent_0': grid[fy][fx]['Agent_0'],
            'Agent_1': grid[fy][fx]['Agent_1'],
            'object': grid[fy][fx]['object'],
            'is_empty': grid[fy][fx]['is_empty']
        },
        to_pos: {
            'terrain': grid[ty][tx]['terrain'],
            'Agent_0': grid[ty][tx]['Agent_0'],
            'Agent_1': grid[ty][tx]['Agent_1'],
            'object': grid[ty][tx]['object'],
            'is_empty': grid[ty][tx]['is_empty']
        }
    }
    
    # Create detailed action log
    action_log = {
        'agent': agent_idx,
        'action': action,  # Raw action (dx, dy) or 'interact'
        'from_pos': from_pos,
        'to_pos': to_pos,
        'timestep': timestep,
        'move_successful': can_move,
        'preconditions': preconditions,
        'effects': effects
    }
    
    return action_log

def construct_grid_from_state(state_info, terrain_grid):
    """
    Construct grid from state information.
    Args:
        state_info: Dictionary containing state information
        terrain_grid: The base terrain grid
    Returns:
        grid: Grid with agents and objects placed
    """
    # Initialize grid with terrain
    height = len(terrain_grid)
    width = len(terrain_grid[0])
    grid = []
    
    for y in range(height):
        row = []
        for x in range(width):
            cell = {
                'terrain': terrain_grid[y][x],
                'Agent_0': {
                    'is_present': False,
                    'hand_empty': True,
                    'held_objects': None,
                    'orientation': (0, -1)
                },
                'Agent_1': {
                    'is_present': False,
                    'hand_empty': True,
                    'held_objects': None,
                    'orientation': (0, -1)
                },
                'object': None,
                'is_empty': True
            }
            row.append(cell)
        grid.append(row)
    
    # Place agents
    for player_idx, player in enumerate(state_info['players']):
        x, y = player['position']
        grid[y][x][f'Agent_{player_idx}']['is_present'] = True
        grid[y][x][f'Agent_{player_idx}']['orientation'] = player['orientation']
        grid[y][x]['is_empty'] = False
        
        # Handle held objects
        if player['held_object'] is not None:
            grid[y][x][f'Agent_{player_idx}']['held_objects'] = player['held_object']
            grid[y][x][f'Agent_{player_idx}']['hand_empty'] = False
            
    
    # Place objects
    for obj in state_info['objects']:
        x, y = obj['position']
        grid[y][x]['object'] = obj
        grid[y][x]['is_empty'] = False
    
    return grid

def process_actions(step, grid):
    """
    Process actions and update grid accordingly.
    Args:
        step: Dictionary containing state info, agent idx, actions, and events
        grid: Current grid state
    Returns:
        grid: Updated grid after actions
        action_logs: List of action logs containing preconditions and effects
    """
    state_info = step['State_info']
    action_logs = []
    
    if step['Player_actions'] is not None:
        for player_idx, action in enumerate(step['Player_actions']):
            # Get current position
            current_pos = state_info['players'][player_idx]['position']
            
            if action == 'interact':
                # Handle interact action
                action_log = update_grid_for_move_and_record(
                    agent_idx=player_idx,
                    from_pos=current_pos,
                    to_pos=current_pos,  # Stay in same position for interact
                    timestep=state_info['timestep'],
                    grid=grid,
                    action=action
                )
                action_logs.append(action_log)
            else:
                # Handle movement action - action is just (dx, dy)
                dx, dy = action
                next_pos = (current_pos[0] + dx, current_pos[1] + dy)
                
                # Update grid and get preconditions/effects
                action_log = update_grid_for_move_and_record(
                    agent_idx=player_idx,
                    from_pos=current_pos,
                    to_pos=next_pos,
                    timestep=state_info['timestep'],
                    grid=grid,
                    action=action
                )
                action_logs.append(action_log)
    
    return grid, action_logs

def parse_trajectory_step(step, terrain_grid):
    """
    Parse a single trajectory step into a grid snapshot.
    Args:
        step: Dictionary containing state info, agent idx, actions, and events
        terrain_grid: The base terrain grid
    Returns:
        grid: Grid snapshot for this step
        action_logs: List of action logs containing preconditions and effects
    """
    # First construct the grid from state
    grid = construct_grid_from_state(step['State_info'], terrain_grid)
    
    # Then process actions and update grid
    grid, action_logs = process_actions(step, grid)
    
    return grid, action_logs

def parse_trajectory(trajectory, terrain_grid):
    """
    Parse a complete trajectory and take grid snapshots at each step.
    Args:
        trajectory: List of state dictionaries
        terrain_grid: The base terrain grid
    Returns:
        snapshots: Dictionary of grid snapshots keyed by timestep
        action_logs: Dictionary of action logs keyed by timestep
    """
    snapshots = {}
    action_logs = {}
    
    for step in trajectory:
        timestep = step['State_info']['timestep']
        grid, step_action_logs = parse_trajectory_step(step, terrain_grid)
        snapshots[timestep] = grid
        action_logs[timestep] = step_action_logs
    
    return snapshots, action_logs

def parse_pickle_file(pickle_file):
    """
    Parse a pickle trajectory file and store each step in an array.
    Args:
        pickle_file: Path to the pickle file
    Returns:
        trajectory: Array of trajectory steps, each containing state info, agent idx, actions, and events
    """
    import pickle
    
    with open(pickle_file, 'rb') as f:
        data = pickle.load(f)
    
    trajectory = []
    # Each step consists of 4 elements: state info, agent idx, actions, events
    for n in range(0, len(data), 4):
        step = {
            'State_info': data[n] if n < len(data) else None,
            'Agent_idx': data[n+1] if n+1 < len(data) else None,
            'Player_actions': data[n+2] if n+2 < len(data) else None,
            'Events': data[n+3] if n+3 < len(data) else None
        }
        trajectory.append(step)
    
    return trajectory

def main():
    layout_list = [ 
        ['X','X','X','P','P','X','X','X'],
        ['X',None,None,2,None,None,None,'X'],
        ['D',None,'X','X','X','X',None,'S'],
        ['X',None,None,1,None,None,None,'X'],
        ['X','X','X','O','O','X','X','X']
    ]

    terrain_grid = build_terrain_grid(layout_list)
    agent_positions = get_initial_agent_positions(layout_list)
    grid = initialize_grid(terrain_grid, agent_positions)
    
    # Parse the pickle trajectory
    trajectory = parse_pickle_file("traj_0_1.pkl")
    trajectory = trajectory[:10]
    
    # Parse trajectory and get snapshots and action logs
    snapshots, action_logs = parse_trajectory(trajectory, terrain_grid)
    
    # Print grid and action logs for each timestep
    for timestep in sorted(snapshots.keys()):
        print(f"\nTimestep {timestep}:")
        print("\nGrid State:")
        print_occupancy(snapshots[timestep])
        
        if timestep in action_logs and action_logs[timestep]:
            print("\nAction Logs:")
            for log in action_logs[timestep]:
                if log['action'] == 'interact':
                    print(f"Agent {log['agent']} attempted to interact at position {log['from_pos']}")
                else:
                    print(f"Agent {log['agent']} attempted to move {log['action']} from {log['from_pos']} to {log['to_pos']}")
                print("Preconditions:", log['preconditions'])
                print("Effects:", log['effects'])
                print(f"Move successful: {log['move_successful']}")
        else:
            print("\nNo actions in this timestep")
        
        print("\n" + "-"*50)



if __name__ == "__main__":
    main()
