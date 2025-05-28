import torch
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ppo_agent import ChessPPOAgent
from chess_env import ChessEnvironment
import SmartMoveFinder
import random

def train_ppo_chess(episodes=1000, use_gpu=True, save_interval=100):
    """Train Chess PPO Agent"""
    
    # Setup device
    device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
    print(f"Training on device: {device}")
    
    # Initialize environment and agent
    env = ChessEnvironment()
    agent = ChessPPOAgent(device=device)
    
    # Training tracking
    episode_rewards = []
    win_count = 0
    loss_count = 0
    draw_count = 0
    
    print(f"Starting PPO Chess Training for {episodes} episodes...")
    
    for episode in tqdm(range(episodes), desc="Training"):
        # Reset environment
        state = env.reset()
        total_reward = 0
        moves_count = 0
        max_moves = 200
        
        # Choose random starting player
        agent_plays_white = episode % 2 == 0
        
        while not env.is_game_over() and moves_count < max_moves:
            valid_moves = env.get_valid_moves()
            
            if not valid_moves:
                break
            
            # Determine whose turn
            if (env.game_state.whiteToMove and agent_plays_white) or \
               (not env.game_state.whiteToMove and not agent_plays_white):
                # Agent's turn
                move, action, log_prob = agent.select_action(env.game_state, valid_moves, training=True)
                next_state, reward, done, info = env.step(move)
                
                # Store transition
                agent.store_transition(state, action, reward, next_state, done, log_prob)
                
                state = next_state
                total_reward += reward
                
            else:
                # Random opponent for now (can be replaced with Minimax)
                random_move = random.choice(valid_moves)
                next_state, _, done, info = env.step(random_move)
                state = next_state
            
            moves_count += 1
        
        # Update agent
        if episode % 10 == 0:  # Update every 10 episodes
            agent.update()
        
        # Record episode results
        episode_rewards.append(total_reward)
        game_result = env.get_result()
        
        if game_result == "win":
            win_count += 1
        elif game_result == "loss":
            loss_count += 1
        else:
            draw_count += 1
        
        # Print progress
        if episode % 50 == 0:
            avg_reward = np.mean(episode_rewards[-50:]) if episode_rewards else 0
            win_rate = win_count / (episode + 1) * 100
            print(f"\nEpisode {episode}")
            print(f"Avg Reward (last 50): {avg_reward:.3f}")
            print(f"Win Rate: {win_rate:.1f}% (W:{win_count}, L:{loss_count}, D:{draw_count})")
            print(f"Moves this game: {moves_count}")
    
    # Final statistics
    total_games = win_count + loss_count + draw_count
    print(f"\n=== Training Complete ===")
    print(f"Total Games: {total_games}")
    print(f"Wins: {win_count} ({win_count/total_games*100:.1f}%)")
    print(f"Losses: {loss_count} ({loss_count/total_games*100:.1f}%)")
    print(f"Draws: {draw_count} ({draw_count/total_games*100:.1f}%)")
    
    # Plot results
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(episode_rewards)
    plt.title('Episode Rewards')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    
    plt.subplot(1, 2, 2)
    # Calculate rolling win rate
    window = 50
    rolling_win_rates = []
    for i in range(len(episode_rewards)):
        start_idx = max(0, i - window + 1)
        # Simple win detection based on positive rewards
        recent_wins = sum(1 for r in episode_rewards[start_idx:i+1] if r > 0.5)
        win_rate = recent_wins / min(window, i + 1) * 100
        rolling_win_rates.append(win_rate)
    
    plt.plot(rolling_win_rates)
    plt.title(f'Rolling Win Rate ({window} episodes)')
    plt.xlabel('Episode')
    plt.ylabel('Win Rate (%)')
    
    plt.tight_layout()
    plt.savefig('ppo_training_results.png')
    plt.show()
    
    # Save final model
    agent.save_model('ppo_chess_final.pth')
    
    return agent

if __name__ == "__main__":
    print("Starting PPO Chess Training...")
    trained_agent = train_ppo_chess(episodes=1000, use_gpu=True)
    print("Training completed!")