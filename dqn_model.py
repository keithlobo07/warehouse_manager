#============================================================================
#DQN Model Definition File
#This file contains all the classes needed for the DQN pathfinding system
#============================================================================

#Import PyTorch - machine learning framework
import torch

#Import neural network layers and components
import torch.nn as nn

#Import optimization algorithms for training
import torch.optim as optim

#Import numerical computing library
import numpy as np

#Import deque for efficient memory storage
from collections import deque

#Import random number generation
import random

#==================== NEURAL NETWORK ====================

class DQNNetwork(nn.Module):
    """
    Deep Q-Network for pathfinding
    This is the brain of the AI. It takes a state as input and outputs
    Q-values (quality scores) for each possible action.
    
    Architecture:
    - Input layer: 12 values (agent position, goal position, surroundings)
    - Hidden layer 1: 128 neurons with ReLU activation
    - Hidden layer 2: 128 neurons with ReLU activation
    - Output layer: 4 Q-values (one for each action: up, down, left, right)
    """
    
    def __init__(self, input_size, hidden_size=128, num_actions=4):
        """
        Initialize the neural network layers
        
        Args:
            input_size: Number of input features (12 in our case)
            hidden_size: Number of neurons in hidden layers (128)
            num_actions: Number of possible actions (4: up, down, left, right)
        """
        #Call parent class constructor (required for nn.Module)
        super(DQNNetwork, self).__init__()
        
        #First layer: input_size (12) -> hidden_size (128)
        #This layer learns patterns from the input state
        self.fc1 = nn.Linear(input_size, hidden_size)
        
        #Second layer: hidden_size (128) -> hidden_size (128)
        #This layer creates more complex representations
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        
        #Output layer: hidden_size (128) -> num_actions (4)
        #This produces the Q-value for each action
        self.fc3 = nn.Linear(hidden_size, num_actions)
    
    def forward(self, state):
        """
        Forward pass through the network
        Takes a state and outputs Q-values for all actions
        
        Args:
            state: Input state tensor with shape [batch_size, 12]
        
        Returns:
            Q-values tensor with shape [batch_size, 4]
        """
        #Apply first linear layer and ReLU activation
        #ReLU (Rectified Linear Unit) = max(0, x)
        #This adds non-linearity, allowing the network to learn complex patterns
        x = torch.relu(self.fc1(state))
        
        #Apply second linear layer and ReLU activation
        #Further process the features
        x = torch.relu(self.fc2(x))
        
        #Apply output layer (no activation here)
        #We want raw Q-values, not bounded 0-1
        return self.fc3(x)

#==================== ENVIRONMENT ====================

class GridEnvironment:
    """
    2D Grid navigation environment
    
    This class represents the world that the agent navigates.
    It handles:
    - Grid representation (walls, walkable spaces, items)
    - Agent position tracking
    - Reward calculation
    - Step execution
    - State representation
    """
    
    def __init__(self, grid, start, target_item):
        """
        Initialize the environment
        
        Args:
            grid: 2D list where 0=walkable, 1=wall, other=item
            start: Tuple (row, col) for agent start position
            target_item: The number of the item to find
        """
        #Convert grid to numpy array for efficient operations
        self.grid = np.array(grid)
        
        #Store the starting position (won't change during initialization)
        self.start = start
        
        #Current position of the agent (changes as agent moves)
        #np.array makes it a numpy array for vector operations
        self.agent_pos = np.array(start)
        
        #The item number we're trying to find
        self.target_item = target_item
        
        #Only call _find_target() if target_item is in the grid
        try:
            self.goal_pos = self._find_target()
        except ValueError:
            self.goal_pos = np.array(start)  #Fallback to start position
        
        #Store grid dimensions (rows, cols)
        self.grid_size = self.grid.shape
        
        #Define the four possible actions as coordinate changes
        #0=up: (-1, 0) means row decreases (move up)
        #1=down: (1, 0) means row increases (move down)
        #2=left: (0, -1) means col decreases (move left)
        #3=right: (0, 1) means col increases (move right)
        self.actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        #Counter for steps taken in current episode
        self.step_count = 0
        
        #Maximum steps allowed in an episode
        #Set to grid area * 2 to give agent enough time to explore
        self.max_steps = 300
    
    def set_episode_target(self, new_start, new_target_pos):
        """
        Safely update environment for a new episode with a specific target.
        
        Args:
            new_start: Tuple (row, col) for new starting position
            new_target_pos: Tuple (row, col) for new target position
        """
        self.start = new_start
        self.agent_pos = np.array(new_start)
        self.goal_pos = np.array(new_target_pos)
        self.step_count = 0
    
    def _find_target(self):
        """
        Search the entire grid for the target item
        
        Returns:
            numpy array with the [row, col] position of the target
        
        Raises:
            ValueError if target not found in grid
        """
        #Loop through each row
        for i in range(self.grid.shape[0]):
            #Loop through each column
            for j in range(self.grid.shape[1]):
                #Check if this cell contains the target item
                if self.grid[i][j] == self.target_item:
                    #Return the position as numpy array
                    return np.array([i, j])
        
        #If we get here, target wasn't found - raise error
        raise ValueError(f"Target item {self.target_item} not found in grid")
    
    def reset(self):
        """
        Reset the environment for a new episode
        
        Returns:
            Initial state after reset
        """
        #Move agent back to starting position
        self.agent_pos = np.array(self.start)
        
        #Reset step counter
        self.step_count = 0
        
        #Get and return the initial state
        return self._get_state()
    
    def _get_state(self):
        """
        Create the current state representation
        State = [agent_row, agent_col, goal_row, goal_col, 8 surrounding cells]
        Total: 12 values
        
        Returns:
            PyTorch tensor with shape [1, 12] representing current state
        """
        #Combine multiple features into one state vector
        state = np.concatenate([
            #Agent's current position (2 values)
            self.agent_pos.astype(float),
            
            #Goal's position (2 values)
            self.goal_pos.astype(float),
            
            #Information about 8 surrounding cells (8 values)
            self._get_surrounding()
        ])
        
        #Convert numpy array to PyTorch tensor
        #dtype=torch.float32 specifies 32-bit floating point precision
        #unsqueeze(0) adds batch dimension: [12] -> [1, 12]
        return torch.tensor(state, dtype=torch.float32).unsqueeze(0)
    
    def _get_surrounding(self):
        """
        Get information about the 8 cells surrounding the agent
        
        Grid layout:
        [-1,-1] [-1,0] [-1,1]
        [0,-1] [Agent] [0,1]
        [1,-1] [1,0] [1,1]
        
        Returns:
            numpy array of 8 values (0=walkable, 1=obstacle)
        """
        #List to store surrounding cell information
        surrounding = []
        
        #Check all 8 adjacent cells (up, down, left, right, and diagonals)
        for dx, dy in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]:
            #Calculate the position of this adjacent cell
            new_pos = self.agent_pos + np.array([dx, dy])
            
            #Check if this adjacent cell is within bounds
            if self._is_valid(new_pos):
                #Check if the cell is walkable (grid value != 0)
                #0.0 = walkable, 1.0 = obstacle
                surrounding.append(0.0 if self.grid[new_pos[0], new_pos[1]] != 0 else 1.0)
            else:
                #Out of bounds = treat as obstacle
                surrounding.append(1.0)
        
        #Convert list to numpy array
        return np.array(surrounding)
    
    def _is_valid(self, pos):
        """
        Check if a position is within the grid bounds
        
        Args:
            pos: Position [row, col] to check
        
        Returns:
            True if position is valid, False otherwise
        """
        #Check if row is in bounds AND column is in bounds
        return 0 <= pos[0] < self.grid_size[0] and 0 <= pos[1] < self.grid_size[1]
    
    def step(self, action):
        """
        Execute one action in the environment
        
        This is where the agent interacts with the world and learns.
        Returns reward based on the action outcome.
        
        Args:
            action: Integer 0-3 (up, down, left, right)
        
        Returns:
            Tuple of (next_state, reward, done)
            - next_state: The state after taking action
            - reward: Scalar reward for this action
            - done: Boolean indicating if episode is over
        """
        #Increment step counter (for episode timeout)
        self.step_count += 1
        
        #Calculate where the agent would be after this action
        new_pos = self.agent_pos + np.array(self.actions[action])
        
        #===== Check if move is out of bounds =====
        if not self._is_valid(new_pos):
            #Out of bounds is bad - give large negative reward
            reward = -100
            
            #Episode continues (agent can try another action)
            done = False
            
            #Return current state (agent didn't move), reward, and done flag
            return self._get_state(), reward, done
        
        #===== Check if moving into a wall =====
        if self.grid[new_pos[0], new_pos[1]] == 1:
            #Hitting a wall is bad - give large negative reward
            reward = -80
            
            #Episode continues
            done = False
            
            return self._get_state(), reward, done
        
        #===== Valid move - update agent position =====
        self.agent_pos = new_pos
        
        #===== Check if reached the goal =====
        if np.array_equal(self.agent_pos, self.goal_pos):
            #Success! Give huge positive reward
            reward = 250
            
            #Episode is done (goal reached)
            done = True
            
            return self._get_state(), reward, done
        
        #===== Calculate reward for moving in open space =====
        #Base penalty: -3 per step (encourages finding shortest path)
        #Distance bonus: Negative of distance to goal (encourages moving closer)
        distance_reward = -np.linalg.norm(self.agent_pos - self.goal_pos) * 0.1
        reward = -3 + distance_reward
        
        #===== Check if episode timed out =====
        #If agent has taken too many steps, end episode (learning failed)
        done = self.step_count >= self.max_steps
        
        #Return new state, calculated reward, and done flag
        return self._get_state(), reward, done

#==================== DQN AGENT ====================

class DQNAgent:
    """
    Deep Q-Learning Agent
    
    This class implements the DQN algorithm. It:
    - Stores experiences (state, action, reward, next_state, done)
    - Trains the network using experience replay
    - Uses epsilon-greedy exploration
    - Maintains both main and target networks for stability
    """
    
    def __init__(self, state_size, action_size, learning_rate=0.001):
        """
        Initialize the DQN agent
        
        Args:
            state_size: Size of state vector (12 in our case)
            action_size: Number of possible actions (4 in our case)
            learning_rate: Learning rate for optimizer (0.001)
        """
        #Size of input state
        self.state_size = state_size
        
        #Number of possible actions
        self.action_size = action_size
        
        #Experience replay buffer - stores up to 10,000 experiences
        #When full, oldest experiences are forgotten
        self.memory = deque(maxlen=10000)
        
        #Gamma (γ) - discount factor
        #0.95 means future rewards are worth 95% as much as immediate rewards
        #This helps agent focus on both immediate and long-term rewards
        self.gamma = 0.95
        
        #Epsilon (ε) - exploration rate
        #Starts at 1.0 (100% exploration - take random actions)
        #Decreases over time to use learned knowledge
        self.epsilon = 1.0
        
        #Epsilon minimum - never explore less than this
        #Ensures some exploration even late in training
        self.epsilon_min = 0.025
        
        #Epsilon decay - how fast to reduce exploration
        #After each episode: epsilon *= 0.99
        #So epsilon slowly decreases over time
        self.epsilon_decay = 0.992
        
        #Create the main network - this one gets trained
        self.network = DQNNetwork(state_size, num_actions=action_size)
        
        #Create the target network - this one is updated periodically
        #Having two networks stabilizes training
        #Main network predicts, target network provides stable targets
        self.target_network = DQNNetwork(state_size, num_actions=action_size)
        
        #Copy weights from main to target at initialization
        self.target_network.load_state_dict(self.network.state_dict())
        
        #Create Adam optimizer for the main network
        #Adam adapts learning rate automatically for each parameter
        self.optimizer = optim.Adam(self.network.parameters(), lr=learning_rate)
        
        #Check if GPU is available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        #Move both networks to GPU (if available) or CPU
        #This speeds up training on GPU
        self.network.to(self.device)
        self.target_network.to(self.device)
    
    def remember(self, state, action, reward, next_state, done):
        """
        Store an experience in the replay buffer
        
        This is called after each step in the environment.
        Experiences are later sampled randomly for training.
        
        Args:
            state: Current state before action
            action: Action taken
            reward: Reward received
            next_state: State after action
            done: Whether episode ended
        """
        #Append the experience tuple to the memory buffer
        #The deque automatically forgets old experiences when full
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        """
        Choose an action using epsilon-greedy strategy
        
        Exploration vs Exploitation:
        - With probability epsilon: pick random action (explore)
        - With probability 1-epsilon: pick best known action (exploit)
        
        Args:
            state: Current state
        
        Returns:
            Action integer 0-3
        """
        #Generate random number between 0 and 1
        if np.random.random() < self.epsilon:
            #Exploration: pick random action
            return random.randrange(self.action_size)
        
        #Exploitation: use network to pick best action
        #torch.no_grad disables gradient computation (we're not training here)
        with torch.no_grad():
            #Move state to GPU/CPU where network is
            state_tensor = state.to(self.device)
            
            #Get Q-values for all actions from network
            #Output shape: [1, 4] (1 state, 4 actions)
            q_values = self.network(state_tensor)
            
            #Find the action with highest Q-value
            #argmax(dim=1) finds max along action dimension
            #.item() converts tensor to Python number
            return q_values.argmax(dim=1).item()
    
    def replay(self, batch_size):
        """
        Train the network on a batch of experiences from memory
        
        This implements the core DQN learning algorithm:
        1. Sample random batch from replay buffer
        2. Calculate current Q-values (network predictions)
        3. Calculate target Q-values using Bellman equation
        4. Compute loss between them
        5. Update network weights via backpropagation
        
        Args:
            batch_size: Number of experiences to sample (32)
        """
        #Check if we have enough experiences to form a batch
        if len(self.memory) < batch_size:
            #Not enough data yet, can't train
            return
        
        #Randomly sample a batch from replay buffer
        #This breaks temporal correlation between experiences
        batch = random.sample(self.memory, batch_size)
        
        #Extract each component from the batch
        #Instead of list of tuples, create separate tensors for each component
        
        #Concatenate all states into one tensor [batch_size, 12]
        states = torch.cat([exp[0] for exp in batch]).to(self.device)
        
        #Create tensor of actions taken [batch_size]
        #dtype=torch.long because actions are integers
        actions = torch.tensor([exp[1] for exp in batch], dtype=torch.long).to(self.device)
        
        #Create tensor of rewards received [batch_size]
        #dtype=torch.float32 for numerical computation
        rewards = torch.tensor([exp[2] for exp in batch], dtype=torch.float32).to(self.device)
        
        #Concatenate all next states [batch_size, 12]
        next_states = torch.cat([exp[3] for exp in batch]).to(self.device)
        
        #Create tensor of done flags [batch_size]
        #1.0 if episode ended, 0.0 if episode continues
        dones = torch.tensor([exp[4] for exp in batch], dtype=torch.float32).to(self.device)
        
        #===== Calculate Q-values for actions taken =====
        #Main Network
        #Get Q-values for all actions from current states
        #q_values shape: [batch_size, 4]
        q_values = self.network(states)
        
        #Use .gather to select Q-value for the action actually taken
        #This extracts only the Q-value for action[i] from q_values[i]
        #Result shape: [batch_size]
        q_values = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        #===== Calculate Target Q-values =====
        #Target Network
        #Get Q-values for all actions from next states using target network
        #target_network output shape: [batch_size, 4]
        next_q_values = self.target_network(next_states)
        
        #Take the maximum Q-value for each next state
        #This is the best action the agent could take
        #max(dim=1)[0] gets the values, [1] would get indices
        #Result shape: [batch_size]
        next_q_values = next_q_values.max(dim=1)[0]
        
        #===== Apply Bellman Equation =====
        #Q(s,a) = r + γ * max(Q(s',a')) * (1 - done)
        #If episode ended (done=1), target is just the reward
        #If episode continues (done=0), include future value
        target_q_values = rewards + self.gamma * next_q_values * (1 - dones)
        
        #===== Calculate Loss =====
        #Mean Squared Error between predicted and target Q-values
        #This measures how wrong our predictions are
        loss = nn.MSELoss()(q_values, target_q_values)
        
        #===== Backpropagation & Weight Update =====
        #Clear old gradients from previous training step
        #Without this, gradients would accumulate
        self.optimizer.zero_grad()
        
        #Backpropagation: compute gradients of loss with respect to weights
        #Tells us how much each weight contributed to the error
        loss.backward()
        
        #Adam optimizer step: update weights in direction of negative gradient
        #This reduces loss, making predictions more accurate
        self.optimizer.step()
    
    def update_target_network(self):
        """
        Copy weights from main network to target network
        
        This stabilizes training by providing stable Q-value targets.
        Done periodically (every 10 episodes) to prevent moving targets.
        """
        #Load: copy all weights from main network into target network
        self.target_network.load_state_dict(self.network.state_dict())
    
    def decay_epsilon(self):
        """
        Decrease exploration rate over time
        
        Called after each episode.
        Gradually shifts from exploration to exploitation.
        """
        #Check if epsilon is above minimum
        if self.epsilon > self.epsilon_min:
            #Multiply epsilon by decay factor (0.999)
            #This gradually decreases epsilon from 1.0 toward epsilon_min
            self.epsilon *= self.epsilon_decay