#============================================================================
# train.py - Complete Training Pipeline (A* + DQN)
# Generates training data and trains DQN agent in one script
# Grid convention: 0=walkable, 1=wall, other=shelf/item
#============================================================================

import torch
import os
import json
import random
import numpy as np
import heapq
import time
from typing import List, Tuple, Optional
from dqn_model import DQNAgent, GridEnvironment
from setGrid import generate_warehouse, get_warehouse_grid

#==================== A* PATHFINDING ====================

def heuristic(pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
    """Manhattan distance heuristic"""
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


def get_neighbors(grid: List[List[int]], pos: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Get valid neighboring positions (up, down, left, right)"""
    row, col = pos
    height = len(grid)
    width = len(grid[0])
    neighbors = []
    
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < height and 0 <= new_col < width:
            if grid[new_row][new_col] != 1:  # Not a wall
                neighbors.append((new_row, new_col))
    
    return neighbors


def a_star_search(
    grid: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int]
) -> Tuple[Optional[List[Tuple[int, int]]], int, int]:
    """Find shortest path using A* algorithm"""
    open_set = [(0, 0, start)]
    counter = 0
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    closed_set = set()
    expansions = 0
    
    while open_set:
        _, _, current = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
        
        closed_set.add(current)
        expansions += 1
        
        if current == goal:
            path = []
            node = current
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            return path, len(path) - 1, expansions
        
        for neighbor in get_neighbors(grid, current):
            if neighbor in closed_set:
                continue
            
            tentative_g = g_score[current] + 1
            if neighbor in g_score and tentative_g >= g_score[neighbor]:
                continue
            
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            new_f = tentative_g + heuristic(neighbor, goal)
            f_score[neighbor] = new_f
            
            counter += 1
            heapq.heappush(open_set, (new_f, counter, neighbor))
    
    return None, -1, expansions


#==================== TRAINING DATA GENERATION ====================

def generate_training_samples(grid, aisles, shelves, num_samples=1000):
    """
    Generate training samples on-the-fly using A* search.
    
    Returns:
        List of dicts with 'start', 'goal', 'path_length', 'path_exists'
    """
    samples = []
    
    print(f"Generating {num_samples} A* training samples...")
    
    for i in range(num_samples):
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i + 1}/{num_samples}")
        
        start = random.choice(aisles)
        goal = random.choice(shelves)
        
        path, cost, expansions = a_star_search(grid, start, goal)
        
        if use_a_star_sample:
            a_star_sample = random.choice(a_star_samples)
    if a_star_sample['path_exists']:
        episode_start = a_star_sample['start']
        episode_goal_pos = a_star_sample['goal']
        
        # Use the proper method instead of direct assignment
        env.set_episode_target(episode_start, episode_goal_pos)

    # Reset environment
state = env.reset()

print(f"Generated {num_samples} training samples!")

#==================== SAVE FUNCTIONS ====================

def save_agent(agent, filepath):
    """Save trained network weights"""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    torch.save(agent.network.state_dict(), filepath)
    print(f"Agent saved to {filepath}")


def save_checkpoint(agent, episode, filepath):
    """Save complete training checkpoint"""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    checkpoint = {
        'episode': episode,
        'model_state_dict': agent.network.state_dict(),
        'target_network_state_dict': agent.target_network.state_dict(),
        'optimizer_state_dict': agent.optimizer.state_dict(),
        'epsilon': agent.epsilon,
    }
    
    torch.save(checkpoint, filepath)
    print(f"Checkpoint saved to {filepath}")


#==================== TRAINING WITH A* GUIDANCE ====================

def train_agent(grid, start, target_item, a_star_samples=None, 
                       episodes=1000, batch_size=32):
    """
    Train DQN agent with optional A* data guidance.
    
    Args:
        grid: 2D grid (0=walkable, 1=wall, other=shelf)
        start: Starting position
        target_item: Target item number
        a_star_samples: Pre-generated A* samples (or None to skip)
        episodes: Number of training episodes
        batch_size: Replay buffer batch size
    """
    
    # Create environment
    env = GridEnvironment(grid, start, target_item)
    
    # Create agent
    state_size = 12
    action_size = 4
    agent = DQNAgent(state_size, action_size)
    
    # Training statistics
    episode_rewards = []
    episode_steps = []
    
    use_a_star = a_star_samples is not None and len(a_star_samples) > 0
    
    print(f"Starting training for {episodes} episodes...")
    print(f"A* guidance: {'Enabled' if use_a_star else 'Disabled'}")
    print("=" * 60)
    
    # Main training loop
    for episode in range(episodes):
        # Decide whether to use A* sample
        use_a_star_sample = (use_a_star and 
                             a_star_samples and 
                             random.random() < 0.3)  # 30% chance
        
        if use_a_star_sample:
            a_star_sample = random.choice(a_star_samples)
            if a_star_sample['path_exists']:
                episode_start = a_star_sample['start']
                episode_goal_pos = a_star_sample['goal']
                
                # Temporarily update environment
                env.start = episode_start
                env.agent_pos = np.array(episode_start)
                env.goal_pos = np.array(episode_goal_pos)
        
        # Reset environment
        state = env.reset()
        done = False
        total_reward = 0
        steps = 0
        
        # Inner loop - run until episode is done
        while not done:
            action = agent.act(state)
            next_state, reward, done = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            
            total_reward += reward
            state = next_state
            steps += 1
            
            agent.replay(batch_size)
        
        # Store statistics
        episode_rewards.append(total_reward)
        episode_steps.append(steps)
        
        # Update target network
        if (episode + 1) % 10 == 0:
            agent.update_target_network()
        
        # Decay epsilon
        agent.decay_epsilon()
        
        # Print progress
        if (episode + 1) % 50 == 0:
            avg_reward = np.mean(episode_rewards[-50:])
            avg_steps = np.mean(episode_steps[-50:])
            print(f"Episode {episode + 1}/{episodes} | Avg Reward: {avg_reward:7.2f} | "
                  f"Avg Steps: {avg_steps:6.1f} | Epsilon: {agent.epsilon:.4f}")
    
    print("=" * 60)
    print("Training complete!")
    
    stats = {
        'episode_rewards': episode_rewards,
        'episode_steps': episode_steps,
        'final_epsilon': agent.epsilon,
        'total_episodes': episodes
    }
    
    return agent, env, stats


#==================== MAIN ====================

if __name__ == "__main__":
    # Configuration
    EPISODES = 1000
    BATCH_SIZE = 32
    GENERATE_DATA = True  # Set to False to skip A* data generation
    NUM_A_STAR_SAMPLES = 1000
    
    print("=" * 60)
    print("DQN PATHFINDING")
    print("=" * 60)
    
    # Setup warehouse grid
    print("Setting up warehouse grid...")
    shelf_coords, aisle_coords = get_warehouse_grid()
    grid = generate_warehouse(63, 13, shelf_coords)
    
    start_pos = aisle_coords[0] if aisle_coords else (1, 1)
    target_item = 5
    
    print(f"Grid size: 63x13")
    print(f"Shelves: {len(shelf_coords)}")
    print(f"Aisles: {len(aisle_coords)}")
    print(f"Start position: {start_pos}")
    print(f"Target item: {target_item}")
    print("=" * 60)
    
    # Generate A* training data
    a_star_samples = None
    if GENERATE_DATA:
        print("\n--- A* DATA GENERATION PHASE ---")
        a_star_samples = generate_training_samples(grid, aisle_coords, shelf_coords, NUM_A_STAR_SAMPLES)
        print(f"Loaded {len(a_star_samples)} A* samples for guidance\n")
    
    # Train DQN agent
    print("--- DQN TRAINING PHASE ---")
    agent, env, stats = train_agent(
        grid,
        start_pos,
        target_item,
        a_star_samples=a_star_samples,
        episodes=EPISODES,
        batch_size=BATCH_SIZE
    )
    
    # Save models
    os.makedirs('models', exist_ok=True)
    save_agent(agent, 'models/pathfinder_trained.pth')
    save_checkpoint(agent, EPISODES, 'models/pathfinder_checkpoint.pth')
    
    # Save training statistics
    with open('models/training_stats.json', 'w') as f:
        json.dump({
            'episodes': EPISODES,
            'final_epsilon': stats['final_epsilon'],
            'avg_final_reward': float(np.mean(stats['episode_rewards'][-50:])),
            'avg_final_steps': float(np.mean(stats['episode_steps'][-50:])),
            'a_star_samples_used': NUM_A_STAR_SAMPLES if GENERATE_DATA else 0
        }, f, indent=2)
    
    print("=" * 60)
    print("All training complete! Models saved to models/")
    print("=" * 60)