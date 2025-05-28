import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random

from chess_net import ChessNet, MoveEncoder
from state_encoder import ChessStateEncoder
from reward_system import ChessReward

class ChessPPOAgent:
    """PPO Agent for Chess - more stable than DQN"""
    
    def __init__(self, lr=3e-4, device=None):
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device
            
        # Initialize components
        self.network = ChessNet().to(self.device)
        self.optimizer = optim.Adam(self.network.parameters(), lr=lr)
        self.state_encoder = ChessStateEncoder()
        self.move_encoder = MoveEncoder()
        self.reward_system = ChessReward()
        
        # PPO parameters
        self.gamma = 0.99
        self.eps_clip = 0.2
        self.k_epochs = 4
        self.entropy_coef = 0.01
        self.value_coef = 0.5
        
        # Experience buffer
        self.buffer = PPOBuffer()
        
    def select_action(self, game_state, valid_moves, training=True):
        """Select action using policy network"""
        state = self.state_encoder.encode_state(game_state)
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            value, policy_logits = self.network(state_tensor)
        
        # Mask invalid moves
        valid_actions = []
        for move in valid_moves:
            try:
                action = self.move_encoder.encode_move(move)
                valid_actions.append(action)
            except:
                continue
        
        if not valid_actions:
            # Fallback to random move
            return random.choice(valid_moves), 0, 0.0
        
        # Create action mask
        action_mask = torch.full((self.move_encoder.action_size,), float('-inf'), device=self.device)
        action_mask[valid_actions] = 0
        
        masked_logits = policy_logits.squeeze() + action_mask
        
        if training:
            # Sample from policy
            action_probs = torch.softmax(masked_logits, dim=0)
            action_dist = torch.distributions.Categorical(action_probs)
            action = action_dist.sample().item()
            log_prob = action_dist.log_prob(torch.tensor(action, device=self.device)).item()
        else:
            # Greedy selection
            action = torch.argmax(masked_logits).item()
            log_prob = 0.0
        
        # Convert back to move
        selected_move = self.move_encoder.decode_action(action, game_state)
        if selected_move is None:
            selected_move = random.choice(valid_moves)
            
        return selected_move, action, log_prob
    
    def store_transition(self, state, action, reward, next_state, done, log_prob):
        """Store transition in buffer - FIXED"""
        # State is already encoded from environment, don't encode again
        if isinstance(state, np.ndarray):
            encoded_state = state  # Already encoded
        else:
            encoded_state = self.state_encoder.encode_state(state)
            
        if next_state is not None:
            if isinstance(next_state, np.ndarray):
                encoded_next_state = next_state  # Already encoded
            else:
                encoded_next_state = self.state_encoder.encode_state(next_state)
        else:
            encoded_next_state = None
        
        self.buffer.store(encoded_state, action, reward, encoded_next_state, done, log_prob)
    
    def update(self):
        """Update network using PPO"""
        if len(self.buffer) < 32:  # Minimum batch size
            return
        
        # Get batch data
        states, actions, rewards, next_states, dones, old_log_probs = self.buffer.get_batch()
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        old_log_probs = torch.FloatTensor(old_log_probs).to(self.device)
        
        # Calculate returns and advantages
        returns = self._calculate_returns(rewards)
        
        # PPO update
        for _ in range(self.k_epochs):
            # Forward pass
            values, policy_logits = self.network(states)
            
            # Calculate new log probabilities
            action_probs = torch.softmax(policy_logits, dim=1)
            action_dist = torch.distributions.Categorical(action_probs)
            new_log_probs = action_dist.log_prob(actions)
            
            # Calculate ratio
            ratio = torch.exp(new_log_probs - old_log_probs)
            
            # Calculate advantages
            advantages = returns - values.squeeze()
            
            # PPO loss
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            policy_loss = -torch.min(surr1, surr2).mean()
            
            # Value loss
            value_loss = nn.MSELoss()(values.squeeze(), returns)
            
            # Entropy loss (for exploration)
            entropy_loss = -action_dist.entropy().mean()
            
            # Total loss
            total_loss = (policy_loss + 
                         self.value_coef * value_loss + 
                         self.entropy_coef * entropy_loss)
            
            # Backward pass
            self.optimizer.zero_grad()
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.network.parameters(), 0.5)
            self.optimizer.step()
        
        # Clear buffer after update
        self.buffer.clear()
    
    def _calculate_returns(self, rewards):
        """Calculate discounted returns"""
        returns = []
        R = 0
        for r in reversed(rewards):
            R = r + self.gamma * R
            returns.insert(0, R)
        return torch.FloatTensor(returns).to(self.device)
    
    def save_model(self, filepath):
        """Save model"""
        torch.save({
            'network_state_dict': self.network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
        }, filepath)
    
    def load_model(self, filepath):
        """Load model"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.network.load_state_dict(checkpoint['network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

# PPOBuffer class remains the same
class PPOBuffer:
    """Experience buffer for PPO"""
    
    def __init__(self, max_size=10000):
        self.max_size = max_size
        self.clear()
    
    def store(self, state, action, reward, next_state, done, log_prob):
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.next_states.append(next_state)
        self.dones.append(done)
        self.log_probs.append(log_prob)
        
        # Remove oldest if buffer is full
        if len(self.states) > self.max_size:
            self.states.pop(0)
            self.actions.pop(0)
            self.rewards.pop(0)
            self.next_states.pop(0)
            self.dones.pop(0)
            self.log_probs.pop(0)
    
    def get_batch(self):
        return (np.array(self.states), 
                np.array(self.actions),
                np.array(self.rewards),
                np.array(self.next_states),
                np.array(self.dones),
                np.array(self.log_probs))
    
    def clear(self):
        self.states = []
        self.actions = []
        self.rewards = []
        self.next_states = []
        self.dones = []
        self.log_probs = []
    
    def __len__(self):
        return len(self.states)