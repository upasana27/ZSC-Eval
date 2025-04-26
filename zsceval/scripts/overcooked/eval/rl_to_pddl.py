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
            #print(cell)
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
            elif cell['object'] is not None:
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
        
        # Update held object fields - copy the entire held object state
        held_obj = grid[fy][fx][agent_key]['held_objects']
        if held_obj is not None:
            held_obj = held_obj.copy()  # Create a copy to avoid reference issues
            held_obj['position'] = to_pos  # Update position to new location
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
            agent_key: grid[fy][fx][agent_key],
            'object': grid[fy][fx]['object'],
            'is_empty': grid[fy][fx]['is_empty']
        },
        to_pos: {
            'terrain': grid[ty][tx]['terrain'],
            agent_key: grid[ty][tx][agent_key],
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

def update_grid_for_interact_and_record(agent_idx, pos, timestep, grid, snapshots=None, next_state=None):
    """
    Update the grid for an agent's interact action and record the snapshot if snapshots dict is provided.
    Args:
        agent_idx: Index of the agent (0 or 1)
        pos: Current position of the agent (x, y)
        timestep: Current timestep
        grid: Current grid state
        snapshots: Dictionary to store snapshots
        next_state: State information from the next timestep to determine action type
    Returns a dictionary containing the action log, preconditions, and effects.
    """
    if snapshots is None:
        snapshots = {}
    
    # Record snapshot before interact
    record_grid_snapshot(grid, timestep, snapshots)
    
    # Get agent key
    agent_key = f'Agent_{agent_idx}'
    x, y = pos
    
    # Get the cell in front of the agent based on orientation
    orientation = grid[y][x][agent_key]['orientation']
    if orientation == (0, 1):  # Up
        target_cell = grid[y+1][x]
        target_pos = (x, y+1)
    elif orientation == (0, -1):  # Down
        target_cell = grid[y-1][x]
        target_pos = (x, y-1)
    elif orientation == (1, 0):  # Right
        target_cell = grid[y][x+1]
        target_pos = (x+1, y)
    else:  # Left
        target_cell = grid[y][x-1]
        target_pos = (x-1, y)
    
    # Update cooking state for all pots in the grid
    for row in grid:
        for cell in row:
            if cell['terrain'] == 'pot' and cell['object'] is not None:
                soup = cell['object']
                if soup['name'] == 'soup' and soup['state'][1] == 3:  # If pot has 3 onions
                    cooking_time = soup['state'][2]
                    if cooking_time < 20:  # Only cook if not fully cooked
                        soup['state'] = ('onion', 3, cooking_time + 1)
    
    # Determine the type of interact action based on current and next state
    action_type = None
    current_held = grid[y][x][agent_key]['held_objects']
    preconditions = {}
    effects = {}

    #print("Agent position: ", pos)
    #print("Agent key: ", agent_key)
    #print("Orientation: ", orientation)
    #print("target_Cell position: ", target_pos)
    #print("target_cell: ", target_cell)
    #print("Target cell terrain: ", target_cell['terrain'])
    if next_state is not None:
        next_player = next_state['players'][agent_idx]
        next_held = next_player['held_object']
        
        # Check for pickup actions
        if current_held is None and next_held is not None:
            if target_cell['terrain'] == 'onion_dispenser':
                action_type = 'pickup_onion_from_dispenser'
            elif target_cell['terrain'] == 'dish_dispenser':
                action_type = 'pickup_dish_from_dispenser'
            elif target_cell['object']['name'] == 'onion':
                action_type = 'pickup_onion_from_counter'
            elif target_cell['object']['name'] == 'dish':
                action_type = 'pickup_dish_from_counter'
            elif target_cell['object']['name'] == 'soup':
                action_type = 'pickup_soup_from_counter'
        
        # Check for put actions
        elif current_held is not None and next_held is None:
            if target_cell['terrain'] == 'counter' and target_cell['object'] is None:
                if current_held['name'] == 'onion':
                    action_type = 'put_onion_on_counter'
                elif current_held['name'] == 'dish':
                    action_type = 'put_dish_on_counter'
                elif current_held['name'] == 'soup':
                    action_type = 'put_soup_on_counter'
            elif target_cell['terrain'] == 'pot':
                if current_held['name'] == 'onion':
                    if target_cell['object'] is None:
                        action_type = 'put_onion_in_pot_0_onion'
                    elif target_cell['object']['name'] == 'soup' and target_cell['object']['state'][1] == 1:
                        action_type = 'put_onion_in_pot_1_onion'
                    elif target_cell['object']['name'] == 'soup' and target_cell['object']['state'][1] == 2:
                        action_type = 'put_onion_in_pot_2_onion'
            elif target_cell['terrain'] == 'delivery' and current_held['name'] == 'soup':
                action_type = 'deliver_soup'
        
        elif current_held is not None and next_held is not None:
            if current_held['name'] == 'dish' and next_held['name'] == 'soup':
                action_type = 'pickup_soup_from_pot'


        if action_type== "pickup_onion_from_dispenser":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': True,
                        'held_objects': None
                    }
                },
                target_pos: {
                    'terrain': "onion_dispenser",
                }
            }
        elif action_type == "pickup_dish_from_dispenser":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': True,
                        'held_objects': None
                    }
                },
                target_pos: {
                    'terrain': "dish_dispenser",
                }
            }
        elif action_type == "pickup_onion_from_counter":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': True,
                        'held_objects': None
                    }   
                },
                target_pos: {
                    'terrain': 'counter',
                    'object': {
                        'name': 'onion',
                        'position': target_pos,
                        'state': None
                    }
                }
            }
        elif action_type == "pickup_dish_from_counter":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': True,
                        'held_objects': None
                    }   
                },
                target_pos: {
                    'terrain': 'counter',
                    'object': {
                        'name': 'dish',
                        'position': target_pos,
                        'state': None
                    }
                }
            }
        elif action_type == "put_onion_on_counter":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'onion',
                            'position': pos,
                            'state': None
                        }
                    }
                },
                target_pos: {
                    'terrain': 'counter',
                    'object': None
                }
            }
        elif action_type == "put_dish_on_counter":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'dish',
                            'position': pos,
                            'state': None
                        }
                    }
                },
                target_pos: {
                    'terrain': 'counter',
                    'object': None
                }
            }
        elif action_type == "put_onion_in_pot_0_onion":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'onion',
                            'position': pos,
                            'state': None
                        }
                    }
                },
                target_pos: {
                    'terrain': 'pot',
                    'object': None  # Pot must be empty
                }
            }
            
        elif action_type == "put_onion_in_pot_1_onion":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'onion',
                            'position': pos,
                            'state': None
                        }
                    }
                },
                target_pos: {
                    'terrain': 'pot',
                    'object': {
                        'name': 'soup',
                        'position': target_pos,
                        'state': ['onion', 1, 0]  # Pot must have 1 onion
                    }
                }
            }
            
        elif action_type == "put_onion_in_pot_2_onion":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'onion',
                            'position': pos,
                            'state': None
                        }
                    }
                },
                target_pos: {
                    'terrain': 'pot',
                    'object': {
                        'name': 'soup',
                        'position': target_pos,
                        'state': ['onion', 2, 0]  # Pot must have 2 onions
                    }
                }
            }
            
        elif action_type == "pickup_soup_from_pot":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'dish',
                            'position': pos,
                            'state': None
                        }
                    }
                },
                target_pos: {
                    'terrain': 'pot',
                    'object': {
                        'name': 'soup',
                        'position': target_pos,
                        'state': ('onion', 3, 20)  # Pot must have fully cooked soup
                    }
                }
            }
        
        elif action_type == "put_soup_on_counter":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'soup',
                            'position': pos,
                            'state': ('onion', 3, 20)
                        }
                    }
                },
                target_pos: {
                    'terrain': 'counter',
                    'object': None  # Counter must be empty
                }
            }
            
        elif action_type == "pickup_soup_from_counter":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': True,
                        'held_objects': None
                    }
                },
                target_pos: {
                    'terrain': 'counter',
                    'object': {
                        'name': 'soup',
                        'position': target_pos,
                        'state': ('onion', 3, 20)
                    }
                }
            }
        
        elif action_type == "deliver_soup":
            preconditions = {
                pos: {
                    agent_key: {
                        'hand_empty': False,
                        'held_objects': {
                            'name': 'soup',
                            'position': pos,
                            'state': ('onion', 3, 20)
                        }
                    }
                },
                target_pos: {
                    'terrain': 'delivery'  # Target must be delivery station
                }
            }
        
        # Check if action is possible based on type
        can_interact = False
        if action_type == 'pickup_onion_from_dispenser':
            can_interact = (
                current_held is None and
                target_cell['terrain'] == 'onion_dispenser'
            )
        elif action_type == 'pickup_dish_from_dispenser':
            can_interact = (
                current_held is None and
                target_cell['terrain'] == 'dish_dispenser'
            )
        elif action_type == 'pickup_soup_from_pot':
            can_interact = (
                current_held is not None and
                current_held['name'] == 'dish' and
                target_cell['terrain'] == 'pot' and
                target_cell['object'] is not None and
                target_cell['object']['name'] == 'soup' and
                target_cell['object']['state'] == ('onion', 3, 20)
            )
        elif action_type == 'pickup_onion_from_counter':
            can_interact = (
                current_held is None and
                target_cell['object']['name'] == 'onion'
            )
        elif action_type == 'pickup_dish_from_counter':
            can_interact = (
                current_held is None and
                target_cell['object']['name'] == 'dish'
            )
        elif action_type == 'put_onion_on_counter':
            can_interact = (
                current_held is not None and
                current_held['name'] == 'onion' and
                target_cell['terrain'] == 'counter' and
                target_cell['object'] is None
            )
        elif action_type == 'put_dish_on_counter':
            can_interact = (
                current_held is not None and
                current_held['name'] == 'dish' and
                target_cell['terrain'] == 'counter' and
                target_cell['object'] is None
            )
        elif action_type == 'put_soup_on_counter':
            can_interact = (
                current_held is not None and
                current_held['name'] == 'soup' and
                current_held['state'] == ('onion', 3, 20) and
                target_cell['terrain'] == 'counter' and
                target_cell['object'] is None
            )
        elif action_type == 'pickup_soup_from_counter':
            can_interact = (
                current_held is None and
                target_cell['terrain'] == 'counter' and
                target_cell['object'] is not None and
                target_cell['object']['name'] == 'soup' and
                target_cell['object']['state'] == ('onion', 3, 20)
            )
        elif action_type == 'deliver_soup':
            can_interact = (
                current_held is not None and
                current_held['name'] == 'soup' and
                current_held['state'] == ('onion', 3, 20) and
                target_cell['terrain'] == 'delivery'
            )
        elif action_type in ['put_onion_in_pot_0_onion', 'put_onion_in_pot_1_onion', 'put_onion_in_pot_2_onion']:
            # Get current soup state
            current_soup = target_cell['object']
            onion_count = 0
            if current_soup is not None and current_soup['name'] == 'soup':
                onion_count = current_soup['state'][1]
            
            can_interact = (
                current_held is not None and
                current_held['name'] == 'onion' and
                target_cell['terrain'] == 'pot' and
                onion_count < 3  # Can't put more than 3 onions in pot
            )
        
        if can_interact:
            # Update grid based on action type
            if action_type in ['pickup_onion_from_dispenser', 'pickup_dish_from_dispenser']:
                # Update agent's held object with complete state
                held_obj = {
                    'name': 'onion' if action_type == 'pickup_onion_from_dispenser' else 'dish',
                    'position': pos,
                    'state': None  # Default state for picked up items
                }
                grid[y][x][agent_key]['held_objects'] = held_obj
                grid[y][x][agent_key]['hand_empty'] = False

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': False,
                            'held_objects': held_obj
                        }  
                    }
                }
                
            elif action_type in ['pickup_onion_from_counter', 'pickup_dish_from_counter']:
                # Update agent's held object with complete state
                held_obj = {
                    'name': 'onion' if action_type == 'pickup_onion_from_counter' else 'dish',
                    'position': pos,
                    'state': None  # Default state for picked up items
                }
                grid[y][x][agent_key]['held_objects'] = held_obj
                grid[y][x][agent_key]['hand_empty'] = False
                
                # Remove object from target cell if it's not a dispenser
                if target_cell['object'] is not None:
                    target_cell['object'] = None
                    target_cell['is_empty'] = True

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': False,
                            'held_objects': held_obj
                        }
                    },
                    target_pos: {
                        'object': None,
                        'is_empty': True
                    }
                }
                
            elif action_type in ['put_onion_on_counter', 'put_dish_on_counter']:
                # Clear agent's held object
                grid[y][x][agent_key]['held_objects'] = None
                grid[y][x][agent_key]['hand_empty'] = True
                
                # Place object on counter
                target_cell['object'] = current_held
                target_cell['is_empty'] = False

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': True,
                            'held_objects': None
                        }
                    },
                    target_pos: {
                        'object': current_held,
                        'is_empty': False
                    }
                }
                
            elif action_type in ['put_onion_in_pot_0_onion', 'put_onion_in_pot_1_onion', 'put_onion_in_pot_2_onion']:
                # Get current soup state
                current_soup = target_cell['object']
                onion_count = 0
                if current_soup is not None and current_soup['name'] == 'soup':
                    onion_count = current_soup['state'][1]
                
                # can_interact = (
                #     current_held is not None and
                #     current_held['name'] == 'onion' and
                #     target_cell['terrain'] == 'pot' and
                #     onion_count < 3  # Can't put more than 3 onions in pot
                # )

                # if can_interact:
                    # Clear agent's held object
                grid[y][x][agent_key]['held_objects'] = None
                grid[y][x][agent_key]['hand_empty'] = True
                
                # Get current soup state
                current_soup = target_cell['object']
                onion_count = 0
                if current_soup is not None and current_soup['name'] == 'soup':
                    onion_count = current_soup['state'][1]
                
                # Update pot state
                new_onion_count = onion_count + 1
                target_cell['object'] = {
                    'name': 'soup',
                    'position': target_pos,
                    'state': ('onion', new_onion_count, 0)  # Cooking starts only when onions = 3
                }
                target_cell['is_empty'] = False

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': True,
                            'held_objects': None
                        }
                    },
                    target_pos: {
                        'object': target_cell['object'],
                        'is_empty': False
                    }
                }
            
            elif action_type == 'pickup_soup_from_pot':
                # can_interact = (
                #     current_held is not None and
                #     current_held['name'] == 'dish' and
                #     target_cell['terrain'] == 'pot' and
                #     target_cell['object'] is not None and
                #     target_cell['object']['name'] == 'soup' and
                #     target_cell['object']['state'] == ('onion', 3, 20)
                # )

                # if can_interact:
                    # Update agent's held object to soup
                held_obj = {
                    'name': 'soup',
                    'position': pos,
                    'state': ('onion', 3, 20)
                }
                grid[y][x][agent_key]['held_objects'] = held_obj
                grid[y][x][agent_key]['hand_empty'] = False
                
                # Clear the pot
                target_cell['object'] = None
                target_cell['is_empty'] = True

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': False,
                            'held_objects': held_obj
                        }
                    },
                    target_pos: {
                        'object': None,
                        'is_empty': True
                    }
                }
            
            elif action_type == 'put_soup_on_counter':
                # can_interact = (
                #     current_held is not None and
                #     current_held['name'] == 'soup' and
                #     current_held['state'] == ('onion', 3, 20) and
                #     target_cell['terrain'] == 'counter' and
                #     target_cell['object'] is None
                # )

                # if can_interact:
                    # Clear agent's held object
                grid[y][x][agent_key]['held_objects'] = None
                grid[y][x][agent_key]['hand_empty'] = True
                
                # Place soup on counter
                target_cell['object'] = {
                    'name': 'soup',
                    'position': target_pos,
                    'state': ('onion', 3, 20)
                }
                target_cell['is_empty'] = False

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': True,
                            'held_objects': None
                        }
                    },
                    target_pos: {
                        'object': target_cell['object'],
                        'is_empty': False
                    }
                }
            
            elif action_type == 'pickup_soup_from_counter':
                # can_interact = (
                #     current_held is None and
                #     target_cell['terrain'] == 'counter' and
                #     target_cell['object'] is not None and
                #     target_cell['object']['name'] == 'soup' and
                #     target_cell['object']['state'] == ('onion', 3, 20)
                # )

                # if can_interact:
                    # Update agent's held object to soup
                held_obj = {
                    'name': 'soup',
                    'position': pos,
                    'state': ('onion', 3, 20)
                }
                grid[y][x][agent_key]['held_objects'] = held_obj
                grid[y][x][agent_key]['hand_empty'] = False
                
                # Clear the counter
                target_cell['object'] = None
                target_cell['is_empty'] = True

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': False,
                            'held_objects': held_obj
                        }
                    },
                    target_pos: {
                        'object': None,
                        'is_empty': True
                    }
                }
            
            elif action_type == 'deliver_soup':
                # can_interact = (
                #     current_held is not None and
                #     current_held['name'] == 'soup' and
                #     current_held['state'] == ('onion', 3, 20) and
                #     target_cell['terrain'] == 'delivery'
                # )

                # if can_interact:
                    # Clear agent's held object
                grid[y][x][agent_key]['held_objects'] = None
                grid[y][x][agent_key]['hand_empty'] = True

                effects = {
                    pos: {
                        agent_key: {
                            'hand_empty': True,
                            'held_objects': None
                        }
                    }
                }
            
            # Update effects
            # effects = {
            #     pos: {
            #         'terrain': grid[y][x]['terrain'],
            #         'Agent_0': grid[y][x]['Agent_0'],
            #         'Agent_1': grid[y][x]['Agent_1'],
            #         'object': grid[y][x]['object'],
            #         'is_empty': grid[y][x]['is_empty']
            #     },
            #     target_pos: {
            #         'terrain': target_cell['terrain'],
            #         'object': target_cell['object'],
            #         'is_empty': target_cell['is_empty']
            #     }
            # }
    else:
        effects = {}
    
    # Record snapshot after interact
    record_grid_snapshot(grid, timestep, snapshots)
    
    # Create detailed action log
    action_log = {
        'agent': agent_idx,
        'action': 'interact',
        'action_type': action_type,
        'from_pos': pos,
        'to_pos': pos,
        'success': can_interact,
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
        
        # Handle held objects with complete state
        if player['held_object'] is not None:
            held_obj = {
                'name': player['held_object']['name'],
                'position': (x, y),
                'state': player['held_object']['state']
            }
            grid[y][x][f'Agent_{player_idx}']['held_objects'] = held_obj
            grid[y][x][f'Agent_{player_idx}']['hand_empty'] = False
    
    # Place objects
    for obj in state_info['objects']:
        x, y = obj['position']
        grid[y][x]['object'] = obj
        grid[y][x]['is_empty'] = False
    
    return grid

def process_actions(step, grid, next_state=None):
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
    if next_state is not None:
     next_state_info = next_state['State_info']
    
    if step['Player_actions'] is not None:
        for player_idx, action in enumerate(step['Player_actions']):
            # Get current position
            current_pos = state_info['players'][player_idx]['position']
            
            if action == 'interact':
                # Handle interact action using new function
                action_log = update_grid_for_interact_and_record(
                    agent_idx=player_idx,
                    pos=current_pos,
                    timestep=state_info['timestep'],
                    grid=grid,
                    next_state=next_state_info  # Pass next state info if available
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

def parse_trajectory_step(step, terrain_grid, next_state=None):
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
    grid, action_logs = process_actions(step, grid, next_state)
    
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
    
    for i in range(len(trajectory)):                
        step = trajectory[i]
        next_state = trajectory[i+1] if i+1 < len(trajectory) else None
        timestep = step['State_info']['timestep']
        grid, step_action_logs = parse_trajectory_step(step, terrain_grid, next_state)
        #print("Grid: ", grid[4][4])
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
    #print("Terrain grid: ", terrain_grid[4][4])
    agent_positions = get_initial_agent_positions(layout_list)
    grid = initialize_grid(terrain_grid, agent_positions)
    #print("Grid: ", grid[4][4])
    # Parse the pickle trajectory
    trajectory = parse_pickle_file("traj_0_1.pkl")
    trajectory = trajectory[:173]
    
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
                try:
                    if log['action'] == 'interact':
                        print(f"Agent {log['agent']} attempted to interact at position {log['from_pos']}")
                    else:
                        print(f"Agent {log['agent']} attempted to move {log['action']} from {log['from_pos']} to {log['to_pos']}")
                    print("Preconditions:", log['preconditions'])
                    print("Effects:", log['effects'])
                    print(f"Move successful: {log['move_successful']}")
                except:
                    print(log)
        else:
            print("\nNo actions in this timestep")
        
        print("\n" + "-"*50)



if __name__ == "__main__":
    main()
