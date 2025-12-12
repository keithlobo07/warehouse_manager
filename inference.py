#============================================================================
#Inference Script - Use Trained Model to Find Paths
#This file loads a saved model and uses it to find paths in the grid
#============================================================================

#Import PyTorch for loading the model
import torch

#Import os for file operations
import os

#Import json for reading grid data
import json

#Import the DQN classes from dqn_model.py
from dqn_model import DQNAgent, GridEnvironment

#==================== LOAD FUNCTION ====================

def load_agent(state_size, action_size, filepath):
    """
    Load a trained agent from a saved model file
    
    This creates a new agent and loads the trained weights into it.
    Used when you want to run inference (use the model) without training.
    
    Args:
        state_size: Size of state vector (12 in our case)
        action_size: Number of possible actions (4 in our case)
        filepath: Path to the saved model file (e.g., 'models/pathfinder_trained.pth')
        
    Returns:
        The loaded DQNAgent object, or None if loading failed
    """
    #Create a new agent with the specified dimensions
    agent = DQNAgent(state_size, action_size)
    
    #Check if the model file exists
    if not os.path.exists(filepath):
        #File doesn't exist - print error
        print(f"File not found: {filepath}")
        #Return None to indicate failure
        return None
    
    #Load the saved weights into the agent's network
    #weights_only=True is a security setting (only load weights, not arbitrary code)
    agent.network.load_state_dict(torch.load(filepath, weights_only=True))
    
    #Set network to evaluation mode (disables dropout, batch norm, etc.)
    #This is important for consistent inference results
    agent.network.eval()
    
    #Print success message
    print(f"Agent loaded from {filepath}")
    
    #Return the loaded agent
    return agent

#==================== INFERENCE FUNCTION ====================

def find_path(agent, env, start, target_item, max_steps=100):
    """
    Use the trained agent to find a path from start to target
    
    This runs the agent through the environment without training,
    using the learned policy to navigate.
    
    Args:
        agent: The trained DQNAgent object
        env: The GridEnvironment object
        start: Starting position (row, col)
        target_item: The item number to find
        max_steps: Maximum steps to take (100 default)
        
    Returns:
        Tuple of (path, total_reward)
        - path: List of positions visited
        - total_reward: Sum of all rewards
    """
    #Reset environment to start position and get initial state
    state = env.reset()
    
    #Initialize path list with starting position
    #Convert numpy array to tuple for list
    path = [tuple(env.agent_pos)]
    
    #Initialize reward accumulator
    total_reward = 0
    
    #Run the agent for up to max_steps
    for step in range(max_steps):
        #Use torch.no_grad() to disable gradient computation
        #We're not training, just inferring, so don't need gradients
        with torch.no_grad():
            #Pass state to network and get Q-values for all actions
            q_values = agent.network(state.to(agent.device))
            
            #Pick action with highest Q-value (greedy, no exploration)
            #argmax returns index of maximum value
            #.item() converts tensor to Python number
            action = q_values.argmax(dim=1).item()
        
        #Execute action in environment
        #Get next state, reward, and done flag
        next_state, reward, done = env.step(action)
        
        #Add the new position to the path
        path.append(tuple(env.agent_pos))
        
        #Add reward to total
        total_reward += reward
        
        #Update state for next iteration
        state = next_state
        
        #Check if we reached the goal
        if done:
            #Episode is complete, exit loop
            break
    
    #Return the path taken and total reward earned
    return path, total_reward

#==================== VISUALIZATION FUNCTION ====================

def visualize_path(grid, path, target_item):
    """
    Display the grid with the path marked on it
    
    Shows each step of the path as numbers 1-9 on the grid
    (can only show first 9 steps due to single-digit limitation)
    
    Args:
        grid: The original 2D grid
        path: List of positions visited (order matters!)
        target_item: The target item number
    """
    #Import numpy (needed for this function)
    import numpy as np
    
    #Create a copy of the grid so we don't modify the original
    grid_copy = [row[:] for row in grid]
    
    #Mark each position in the path with its step number (1-9)
    for i, pos in enumerate(path[:-1]):  #Exclude final position (already the target)
        #Only mark first 9 steps (can't use double-digit numbers in single grid cells)
        if i < 9:
            #Place step number at this position
            grid_copy[pos[0]][pos[1]] = i + 1
    
    #Mark the final position with the target item number
    final_pos = path[-1]
    grid_copy[final_pos[0]][final_pos[1]] = target_item
    
    #Print the visualization
    print("\nPath visualization (numbers = step order):")
    #Print each row
    for row in grid_copy:
        print(row)

#==================== ACTION NAMES ====================

#Dictionary to map action numbers to names (for readability)
ACTION_NAMES = {
    0: "UP",      #Action 0 = move up
    1: "DOWN",    #Action 1 = move down
    2: "LEFT",    #Action 2 = move left
    3: "RIGHT"    #Action 3 = move right
}

#==================== MAIN ====================

#This code only runs if the script is executed directly (not imported)
if __name__ == "__main__":
    #===== Load grid data from file =====
    try:
        #Try to open and read grid_data.json
        with open('grid_data.json', 'r') as f:
            #Parse JSON file
            data = json.load(f)
            
            #Extract grid
            grid = data['grid']
            
            #Extract starting position and convert to tuple
            start = tuple(data['start'])
            
            #Extract target item number
            target_item = data['target_item']
    
    except FileNotFoundError:
        #If file doesn't exist, tell user and exit
        print("grid_data.json not found!")
        print("Please create grid_data.json or run train.py first.")
        #Exit the program
        exit()
    
    #===== Check if trained model exists =====
    model_path = 'models/pathfinder_trained.pth'
    
    if not os.path.exists(model_path):
        #Model file doesn't exist
        print(f"Model not found at {model_path}")
        print("Please run train.py first to train the model.")
        #Exit the program
        exit()
    
    #===== Print inference header =====
    print("=" * 60)
    print("DQN PATHFINDING - INFERENCE")
    print("=" * 60)
    
    #Print grid information
    print(f"Grid shape: {len(grid)}x{len(grid[0])}")
    print(f"Start position: {start}")
    print(f"Target item: {target_item}")
    
    print("=" * 60)
    
    #===== Load the trained model =====
    agent = load_agent(state_size=12, action_size=4, filepath=model_path)
    
    #Check if loading was successful
    if agent is None:
        #Loading failed, exit
        exit()
    
    #===== Create environment for inference =====
    env = GridEnvironment(grid, start, target_item)
    
    #===== Find a path using the trained agent =====
    print("\nFinding path with trained agent...")
    
    #Call find_path to get the path and total reward
    path, total_reward = find_path(agent, env, start, target_item)
    
    #===== Display results =====
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    #Check if a path was found (path has more than 1 position)
    print(f"Path found: {len(path) > 1}")
    
    #Print number of steps (path length minus 1, because path includes start)
    print(f"Path length: {len(path) - 1} steps")
    
    #Print total reward (higher is better)
    print(f"Total reward: {total_reward:.2f}")
    
    #===== Print the path coordinates =====
    print(f"\nPath coordinates:")
    
    #Loop through each position in the path
    for i, pos in enumerate(path):
        #For all but the last position, print as step
        if i < len(path) - 1:
            print(f"  Step {i}: {pos}")
        else:
            #For the last position, print as goal
            print(f"  Goal:   {pos} ✓")
    
    #===== Visualize the path on the grid =====
    visualize_path(grid, path, target_item)
    
    #Print footer
    print("=" * 60)