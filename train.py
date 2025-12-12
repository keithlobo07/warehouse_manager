#============================================================================
#Training Script - Train the DQN Agent on Grid Pathfinding
#============================================================================

#Import PyTorch for neural network operations
import torch

#Import os for file and directory operations
import os

#Import json for reading/writing JSON files
import json

#Import the DQN classes we defined in dqn_model.py
from dqn_model import DQNAgent, GridEnvironment

#==================== SAVE FUNCTIONS ====================

def save_agent(agent, filepath):
    """
    Save only the trained network weights (used for inference later)
    
    This saves a minimal file containing just the learned parameters.
    Much lighter than saving the entire model.
    
    Args:
        agent: The DQNAgent object to save
        filepath: Where to save the file (e.g., 'models/pathfinder_trained.pth')
    """
    #Create the directory path if it doesn't exist
    #os.path.dirname(filepath) extracts the directory from filepath
    #exist_ok=True means don't fail if directory already exists
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    #Save only the network weights (state_dict) to a PyTorch file
    #state_dict contains all learnable parameters (weights and biases)
    torch.save(agent.network.state_dict(), filepath)
    
    #Print confirmation message
    print(f"Agent saved to {filepath}")

def save_checkpoint(agent, episode, filepath):
    """
    Save complete training checkpoint (used to resume training later)
    
    This saves everything needed to continue training from where it stopped:
    - Model weights
    - Target network weights
    - Optimizer state
    - Current epsilon value
    
    Args:
        agent: The DQNAgent object to save
        episode: Current episode number (for resume info)
        filepath: Where to save the checkpoint file
    """
    #Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    #Create a dictionary containing all training state
    checkpoint = {
        #The episode number we're at (for resuming)
        'episode': episode,
        
        #The main network weights
        'model_state_dict': agent.network.state_dict(),
        
        #The target network weights
        'target_network_state_dict': agent.target_network.state_dict(),
        
        #The optimizer state (momentum, learning rate schedules, etc.)
        'optimizer_state_dict': agent.optimizer.state_dict(),
        
        #The current exploration rate (so we resume with same exploration level)
        'epsilon': agent.epsilon,
    }
    
    #Save the entire checkpoint dictionary to file
    torch.save(checkpoint, filepath)
    
    #Print confirmation
    print(f"Checkpoint saved to {filepath}")

#==================== TRAINING FUNCTION ====================

def train_agent(grid, start, target_item, episodes=500, batch_size=32):
    """
    Train the DQN agent for a specified number of episodes
    
    This is the main training loop where the agent learns to navigate the grid.
    
    Args:
        grid: 2D list representing the grid (1=walkable, 0=wall, numbers=items)
        start: Tuple (row, col) of agent starting position
        target_item: The number of the item to find
        episodes: How many episodes to train for (500 default)
        batch_size: How many experiences to train on per step (32 default)
        
    Returns:
        Tuple of (trained_agent, environment)
    """
    #Create the environment (the grid world)
    env = GridEnvironment(grid, start, target_item)
    
    #Size of the state vector (agent pos + goal pos + 8 surrounding cells = 12)
    state_size = 12
    
    #Number of possible actions (up, down, left, right = 4)
    action_size = 4
    
    #Create a new DQN agent with the specified state and action sizes
    agent = DQNAgent(state_size, action_size)
    
    #Print training information
    print(f"Starting training for {episodes} episodes...")
    print(f"Grid size: {env.grid_size}, Start: {start}, Target item: {target_item}")
    
    #Main training loop - iterate through episodes
    for episode in range(episodes):
        #Reset environment for new episode, get initial state
        state = env.reset()
        
        #Flag to track if episode is finished
        done = False
        
        #Track total reward for this episode (for monitoring)
        total_reward = 0
        
        #Track number of steps taken in this episode
        steps = 0
        
        #Inner loop - run until episode is done
        while not done:
            #Agent picks an action using epsilon-greedy strategy
            #With probability epsilon: random action (explore)
            #With probability 1-epsilon: best known action (exploit)
            action = agent.act(state)
            
            #Execute the action in the environment
            #get back: next state, reward for this step, done flag
            next_state, reward, done = env.step(action)
            
            #Store this experience in replay buffer for later learning
            agent.remember(state, action, reward, next_state, done)
            
            #Add this step's reward to episode total
            total_reward += reward
            
            #Update state for next iteration
            state = next_state
            
            #Increment step counter
            steps += 1
            
            #Train on a random batch from replay buffer
            #This improves the network based on past experiences
            agent.replay(batch_size)
        
        #After every 10 episodes, update the target network
        #Target network copy provides stable Q-value targets
        if (episode + 1) % 10 == 0:
            agent.update_target_network()
        
        #After each episode, decrease exploration rate (epsilon)
        #So agent gradually shifts from exploring to exploiting
        agent.decay_epsilon()
        
        #Every 50 episodes, print training progress
        if (episode + 1) % 50 == 0:
            #Print: episode number, reward for this episode, steps taken, current epsilon
            print(f"Episode {episode + 1}/{episodes} | Reward: {total_reward:7.2f} | Steps: {steps:3d} | Epsilon: {agent.epsilon:.4f}")
    
    #Print completion message
    print(f"Training complete!")
    
    #Return the trained agent and environment
    return agent, env

#==================== MAIN ====================

#This code only runs if script is executed directly (not imported)
if __name__ == "__main__":
    #Import json module (done here too in case needed)
    import json
    
    #===== Load grid configuration from file =====
    try:
        #Try to open grid_data.json
        with open('grid_data.json', 'r') as f:
            #Parse JSON file into Python dictionary
            data = json.load(f)
            
            #Extract the grid (2D list)
            grid = data['grid']
            
            #Extract start position and convert to tuple
            start = tuple(data['start'])
            
            #Extract target item number
            target_item = data['target_item']
    
    except FileNotFoundError:
        #If grid_data.json doesn't exist, create it with example data
        print("grid_data.json not found!")
        print("Creating example grid_data.json...")
        
        #Create example data structure
        example_data = {
            "grid": [
                [1, 1, 0, 1, 1],  #Row 0: walkable, walkable, wall, walkable, walkable
                [1, 0, 0, 0, 1],  #Row 1: walkable, wall, wall, wall, walkable
                [1, 1, 1, 1, 5],  #Row 2: walkable spaces and target item (5)
                [0, 0, 0, 0, 1],  #Row 3: walls and walkable
                [1, 1, 1, 1, 1]   #Row 4: all walkable
            ],
            "start": [0, 0],  #Agent starts at top-left
            "target_item": 5  #Looking for item numbered 5
        }
        
        #Write example data to file
        with open('grid_data.json', 'w') as f:
            #indent=2 makes the JSON file readable with nice formatting
            json.dump(example_data, f, indent=2)
        
        #Tell user to run again
        print("Created grid_data.json with example data")
        print("Please run again to train.")
        
        #Exit the program
        exit()
    
    #===== Print training configuration =====
    print("=" * 60)
    print("DQN PATHFINDING - TRAINING")
    print("=" * 60)
    
    #Print grid dimensions
    print(f"Grid shape: {len(grid)}x{len(grid[0])}")
    
    #Print starting position
    print(f"Start position: {start}")
    
    #Print target item to find
    print(f"Target item: {target_item}")
    
    print("=" * 60)
    
    #===== Train the agent =====
    agent, env = train_agent(grid, start, target_item, episodes=500)
    
    #===== Save the trained model =====
    
    #Create 'models' directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    #Save trained network weights
    save_agent(agent, 'models/pathfinder_trained.pth')
    
    #===== Print completion =====
    print("=" * 60)
    print("Training complete! Model saved to models/pathfinder_trained.pth")
    print("=" * 60)