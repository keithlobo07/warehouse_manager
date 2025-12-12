#============================================================================
#inference.py - Inference Script
#Uses trained model to find paths in the grid
#Grid convention: 0=walkable, 1=wall, other=shelf/item
#============================================================================

import torch
import os
import json
import numpy as np

from dqn_model import DQNAgent, GridEnvironment
from setGrid import generate_warehouse, get_warehouse_grid


#==================== LOAD FUNCTION ====================

def load_agent(state_size, action_size, filepath):
    """
    Load a trained agent from a saved model file
    
    Args:
        state_size: Size of state vector (12 in our case)
        action_size: Number of possible actions (4 in our case)
        filepath: Path to the saved model file
    
    Returns:
        The loaded DQNAgent object, or None if loading failed
    """
    agent = DQNAgent(state_size, action_size)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return None
    
    try:
        agent.network.load_state_dict(torch.load(filepath, weights_only=True))
        agent.network.eval()
        print(f"Agent loaded from {filepath}")
        return agent
    except Exception as e:
        print(f"Error loading agent: {e}")
        return None


#==================== INFERENCE FUNCTION ====================

def find_path(agent, env, start, target_item, max_steps=100):
    """
    Use the trained agent to find a path from start to target
    
    Args:
        agent: The trained DQNAgent object
        env: The GridEnvironment object
        start: Starting position (row, col)
        target_item: The item number to find
        max_steps: Maximum steps to take (100 default)
    
    Returns:
        Tuple of (path, total_reward):
        - path: List of positions visited
        - total_reward: Sum of all rewards
    """
    state = env.reset()
    path = [tuple(env.agent_pos)]
    total_reward = 0
    
    for step in range(max_steps):
        with torch.no_grad():
            q_values = agent.network(state.to(agent.device))
            action = q_values.argmax(dim=1).item()
        
        next_state, reward, done = env.step(action)
        path.append(tuple(env.agent_pos))
        total_reward += reward
        state = next_state
        
        if done:
            break
    
    return path, total_reward


#==================== VISUALIZATION FUNCTION ====================

def visualize_path(grid, path, target_item):
    """Display grid with path marked as S (start), - (path), G (goal)"""
    import numpy as np
    
    # Create a copy of the grid
    grid_copy = [row[:] for row in grid]
    
    # Mark start position FIRST
    if path:
        start_pos = path[0]
        grid_copy[start_pos[0]][start_pos[1]] = "S"
    
    # Mark intermediate path positions
    for i in range(1, len(path) - 1):
        pos = path[i]
        grid_copy[pos[0]][pos[1]] = "-"
    
    # Mark goal position LAST (only if different from start)
    if len(path) > 1:
        goal_pos = path[-1]
        if not np.array_equal(goal_pos, path[0]):
            grid_copy[goal_pos[0]][goal_pos[1]] = "G"
        else:
            grid_copy[goal_pos[0]][goal_pos[1]] = "S/G"
    
    # Print the visualization
    print("\nVisualization (S = start, - = path, G = goal):")
    for row in grid_copy:
        print(' '.join(str(cell) for cell in row))


#==================== ACTION NAMES ====================

ACTION_NAMES = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}


#==================== MAIN ====================

if __name__ == "__main__":
    # Setup
    print("=" * 60)
    print("DQN PATHFINDING - INFERENCE")
    print("=" * 60)
    
    # Load grid from JSON if it exists
    grid_file = 'grid_data.json'
    if os.path.exists(grid_file):
        print(f"Loading grid from {grid_file}...")
        with open(grid_file, 'r') as f:
            grid_data = json.load(f)
        grid = grid_data['grid']
        start_pos = tuple(grid_data['start'])
        target_item = grid_data['target_item']
        print(f"Loaded custom grid from JSON")
    else:
        # Fallback: generate grid if JSON doesn't exist
        print("Setting up warehouse grid...")
        shelf_coords, aisle_coords = get_warehouse_grid()
        grid = generate_warehouse(63, 13, shelf_coords)
        start_pos = aisle_coords[0] if aisle_coords else (1, 1)
        unique_items = set(cell for row in grid for cell in row if cell not in [0, 1])
        target_item = min(unique_items) if unique_items else 2
        print(f"Available items: {sorted(unique_items)} | Selected: {target_item}")
    
    print(f"Grid size: 63x13")
    print(f"Start position: {start_pos}")
    print(f"Target item: {target_item}")
    print("=" * 60)
    
    # Check if trained model exists
    model_path = 'models/pathfinder_trained.pth'
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        print("Please run train.py first to train the model.")
        exit()
    
    # Load the trained model
    print(f"Loading trained model from {model_path}...")
    agent = load_agent(state_size=12, action_size=4, filepath=model_path)
    
    if agent is None:
        print("Failed to load model. Exiting.")
        exit()
    
    # Create environment for inference
    env = GridEnvironment(grid, start_pos, target_item)
    
    # Find a path using the trained agent
    print("\nRunning inference...")
    path, total_reward = find_path(agent, env, start_pos, target_item)
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    if len(path) > 1:
        print(f"Path found!")
        print(f"Path length: {len(path) - 1} steps")
        print(f"Total reward: {total_reward:.2f}")
        
        print(f"\nPath coordinates:")
        for i, pos in enumerate(path):
            if i < len(path) - 1:
                print(f"  Step {i}: {pos}")
            else:
                print(f"  Goal: {pos}")
        
        # Visualize the path
        visualize_path(grid, path, target_item)
    else:
        print("No path found (agent did not move).")
    
    print("=" * 60)