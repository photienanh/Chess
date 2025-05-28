import torch
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import os
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ppo_agent import ChessPPOAgent
from chess_env import ChessEnvironment
import SmartMoveFinder
import Evalute

def train_ppo_vs_minimax(episodes=1000, use_gpu=True, save_interval=100):
    """Advanced PPO Training vs Minimax with Curriculum Learning"""
    
    # Setup device
    device = torch.device('cuda' if use_gpu and torch.cuda.is_available() else 'cpu')
    print(f"🚀 Training on device: {device}")
    
    # Initialize environment and agent
    env = ChessEnvironment()
    agent = ChessPPOAgent(device=device)
    
    # Load existing model if available
    model_loaded = False
    model_paths = [
        "ppo_chess_final.pth"
    ]
    
    for model_path in model_paths:
        try:
            if os.path.exists(model_path):
                agent.load_model(model_path)
                model_loaded = True
                print(f"✅ Loaded existing model: {model_path}")
                break
        except Exception as e:
            print(f"Failed to load {model_path}: {e}")
            continue
    
    if not model_loaded:
        print("⚠️ No existing model found. Starting training from scratch.")
    else:
        print("🎯 Continuing training from loaded model...")
    
    # Training tracking
    episode_rewards = []
    win_count = 0
    loss_count = 0
    draw_count = 0
    
    # Curriculum parameters với mốc mới: 0, 500, 800, 950
    curriculum_phases = [
        {"episodes": 500, "depth": 1, "description": "Easy Minimax (Depth 1)"},      # 0-499
        {"episodes": 300, "depth": 2, "description": "Medium Minimax (Depth 2)"},    # 500-799
        {"episodes": 150, "depth": 3, "description": "Hard Minimax (Depth 3)"},     # 800-949
        {"episodes": 50, "depth": 4, "description": "Expert Minimax (Depth 4)"}     # 950-999
    ]
    
    current_phase = 0
    phase_start_episode = 0
    
    for episode in tqdm(range(episodes), desc="Advanced Training"):
        # Update curriculum phase
        if episode >= phase_start_episode + curriculum_phases[current_phase]["episodes"]:
            if current_phase < len(curriculum_phases) - 1:
                # Save model BEFORE changing phase (với depth của phase vừa complete)
                try:
                    completed_depth = curriculum_phases[current_phase]["depth"]
                    model_name = f'ppo_chess_advanced_episode_{episode}_depth_{completed_depth}.pth'
                    agent.save_model(model_name)
                    print(f"💾 Model saved after completing depth {completed_depth}: {model_name}")
                except Exception as e:
                    print(f"Save error at transition: {e}")
                
                # Then update to next phase
                current_phase += 1
                phase_start_episode = episode
                print(f"\n🎓 Phase {current_phase + 1}: {curriculum_phases[current_phase]['description']}")
        
        # Reset environment
        state = env.reset()
        total_reward = 0
        moves_count = 0
        max_moves = 200
        
        # Choose random starting player for agent
        agent_plays_white = episode % 2 == 0
        
        while not env.is_game_over() and moves_count < max_moves:
            valid_moves = env.get_valid_moves()
            
            if not valid_moves:
                break
            
            # Determine whose turn
            if (env.game_state.whiteToMove and agent_plays_white) or \
               (not env.game_state.whiteToMove and not agent_plays_white):
                # Agent's turn
                try:
                    move, action, log_prob = agent.select_action(env.game_state, valid_moves, training=True)
                    next_state, reward, done, info = env.step(move)
                    
                    # Store transition
                    agent.store_transition(state, action, reward, next_state, done, log_prob)
                    
                    state = next_state
                    total_reward += reward
                    
                except Exception as e:
                    print(f"Agent error: {e}")
                    # Fallback to random move
                    random_move = random.choice(valid_moves)
                    next_state, _, done, info = env.step(random_move)
                    state = next_state
                
            else:
                # Minimax opponent with curriculum depth
                minimax_depth = curriculum_phases[current_phase]["depth"]
                
                try:
                    # Set minimax depth
                    SmartMoveFinder.DEPTH = minimax_depth
                    
                    # Use evaluation-based depth adjustment
                    if Evalute.check_mid_game(env.game_state):
                        SmartMoveFinder.DEPTH = min(minimax_depth + 1, 5)  # Slightly deeper in mid-game
                    
                    # Get minimax move
                    minimax_move = SmartMoveFinder.findBestMinimaxMove(env.game_state, valid_moves)
                    
                    if minimax_move is None:
                        minimax_move = SmartMoveFinder.findRandomMove(valid_moves)
                    
                    if minimax_move:
                        next_state, _, done, info = env.step(minimax_move)
                        state = next_state
                    else:
                        break
                        
                except Exception as e:
                    print(f"Minimax error: {e}")
                    # Fallback to random move
                    random_move = random.choice(valid_moves)
                    next_state, _, done, info = env.step(random_move)
                    state = next_state
            
            moves_count += 1
        
        # Update agent every 10 episodes
        if episode % 10 == 0 and episode > 0:
            try:
                agent.update()
            except Exception as e:
                print(f"Update error: {e}")
        
        # Record episode results
        episode_rewards.append(total_reward)
        game_result = env.get_result()
        
        # Adjust reward based on agent's perspective
        if agent_plays_white:
            if game_result == "win":
                win_count += 1
            elif game_result == "loss":
                loss_count += 1
            else:
                draw_count += 1
        else:
            if game_result == "loss":  # Agent was black, so white won = agent lost
                win_count += 1
            elif game_result == "win":  # Agent was black, so black won = agent won
                loss_count += 1
            else:
                draw_count += 1
        
        # Print progress
        if episode % 100 == 0 and episode > 0:
            recent_rewards = episode_rewards[-100:] if len(episode_rewards) >= 100 else episode_rewards
            avg_reward = np.mean(recent_rewards)
            win_rate = win_count / (episode + 1) * 100
            
            current_desc = curriculum_phases[current_phase]['description']
            phase_progress = (episode - phase_start_episode) / curriculum_phases[current_phase]['episodes'] * 100
            
            print(f"\n📊 Episode {episode}")
            print(f"🎓 Current Phase: {current_desc} ({phase_progress:.1f}% complete)")
            print(f"📈 Avg Reward (last 100): {avg_reward:.3f}")
            print(f"🏆 Win Rate: {win_rate:.1f}% (W:{win_count}, L:{loss_count}, D:{draw_count})")
            print(f"♟️ Moves this game: {moves_count}")
            print(f"🎯 Minimax Depth: {curriculum_phases[current_phase]['depth']}")
    
    # Final statistics
    total_games = win_count + loss_count + draw_count
    print(f"\n🎉 === Advanced Training Complete ===")
    print(f"📊 Total Games: {total_games}")
    if total_games > 0:
        print(f"🏆 Wins: {win_count} ({win_count/total_games*100:.1f}%)")
        print(f"💀 Losses: {loss_count} ({loss_count/total_games*100:.1f}%)")
        print(f"🤝 Draws: {draw_count} ({draw_count/total_games*100:.1f}%)")
    
    # Plot advanced results
    plot_advanced_results(episode_rewards, curriculum_phases, win_count, loss_count, draw_count)
    
    # Save final model
    try:
        agent.save_model('RL_model.pth')
        print("💾 Final advanced model saved!")
    except Exception as e:
        print(f"Final save error: {e}")
    
    return agent

def plot_advanced_results(episode_rewards, curriculum_phases, wins, losses, draws):
    """Plot comprehensive training results"""
    
    plt.figure(figsize=(16, 10))
    
    # Episode rewards
    plt.subplot(2, 3, 1)
    plt.plot(episode_rewards, alpha=0.7)
    
    # Add phase boundaries at episodes 500, 800, 950
    phase_boundaries = [500, 800, 950]
    for boundary in phase_boundaries:
        plt.axvline(x=boundary, color='red', linestyle='--', alpha=0.5)
    
    plt.title('Episode Rewards with Curriculum Phases')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.grid(True, alpha=0.3)
    
    # Rolling win rate
    plt.subplot(2, 3, 2)
    window = 100
    rolling_win_rates = []
    for i in range(len(episode_rewards)):
        start_idx = max(0, i - window + 1)
        recent_wins = sum(1 for r in episode_rewards[start_idx:i+1] if r > 0.5)
        win_rate = recent_wins / min(window, i + 1) * 100
        rolling_win_rates.append(win_rate)
    
    plt.plot(rolling_win_rates)
    for boundary in phase_boundaries:
        plt.axvline(x=boundary, color='red', linestyle='--', alpha=0.5)
    plt.title(f'Rolling Win Rate ({window} episodes)')
    plt.xlabel('Episode')
    plt.ylabel('Win Rate (%)')
    plt.grid(True, alpha=0.3)
    
    # Win/Loss/Draw distribution
    plt.subplot(2, 3, 3)
    labels = ['Wins', 'Losses', 'Draws']
    sizes = [wins, losses, draws]
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title('Game Outcomes Distribution')
    
    # Reward distribution by phase
    plt.subplot(2, 3, 4)
    phase_rewards = []
    episode_ranges = [(0, 500), (500, 800), (800, 950), (950, 1000)]
    
    for start, end in episode_ranges:
        phase_reward = episode_rewards[start:min(end, len(episode_rewards))]
        if phase_reward:
            phase_rewards.append(phase_reward)
    
    plt.boxplot(phase_rewards, labels=[f"Depth {i+1}" for i in range(len(phase_rewards))])
    plt.title('Reward Distribution by Curriculum Phase')
    plt.ylabel('Reward')
    
    # Performance improvement over time
    plt.subplot(2, 3, 5)
    smoothed_rewards = []
    smooth_window = 50
    for i in range(len(episode_rewards)):
        start_idx = max(0, i - smooth_window + 1)
        smoothed_rewards.append(np.mean(episode_rewards[start_idx:i+1]))
    
    plt.plot(smoothed_rewards, color='blue', linewidth=2)
    for boundary in phase_boundaries:
        plt.axvline(x=boundary, color='red', linestyle='--', alpha=0.5)
    plt.title(f'Smoothed Performance ({smooth_window}-episode average)')
    plt.xlabel('Episode')
    plt.ylabel('Average Reward')
    plt.grid(True, alpha=0.3)
    
    # Training phases info
    plt.subplot(2, 3, 6)
    plt.axis('off')
    info_text = "🎓 Curriculum Training Phases:\n\n"
    info_text += "Episodes 0-499: Depth 1 (Easy)\n"
    info_text += "Episodes 500-799: Depth 2 (Medium)\n"
    info_text += "Episodes 800-949: Depth 3 (Hard)\n"
    info_text += "Episodes 950-999: Depth 4 (Expert)\n\n"
    
    info_text += f"📊 Final Statistics:\n"
    total_games = wins + losses + draws
    if total_games > 0:
        info_text += f"  Win Rate: {wins/total_games*100:.1f}%\n"
        info_text += f"  Total Games: {total_games}\n"
        info_text += f"  Average Reward: {np.mean(episode_rewards):.3f}"
    
    plt.text(0.1, 0.9, info_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace')
    
    plt.tight_layout()
    plt.savefig('ppo_advanced_training_results.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("🎓 Starting Curriculum Training vs Minimax...")
    trained_agent = train_ppo_vs_minimax(episodes=1000, use_gpu=True)
    print("🎉 Advanced training completed!")