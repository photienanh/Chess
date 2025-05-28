import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ChessEngine  
from state_encoder import ChessStateEncoder
from reward_system import ChessReward

class ChessEnvironment:
    """Modern Chess Environment for PPO training"""
    
    def __init__(self):
        self.game_state = ChessEngine.GameState()
        self.state_encoder = ChessStateEncoder()
        self.reward_system = ChessReward()
        self.done = False
        
    def reset(self):
        """Reset environment to starting position"""
        self.game_state = ChessEngine.GameState()
        self.done = False
        return self.get_state()
    
    def get_state(self):
        """Get current state encoding"""
        return self.state_encoder.encode_state(self.game_state)
    
    def get_valid_moves(self):
        """Get valid moves"""
        return self.game_state.getValidMoves()
    
    def step(self, move):
        """Execute move and return (next_state, reward, done, info)"""
        # Store previous state for reward calculation
        prev_state = self.game_state
        
        # Make move
        self.game_state.makeMove(move)
        
        # Check if game is done
        self.done = self.game_state.checkMate or self.game_state.staleMate
        
        # Calculate reward
        game_outcome = self._get_game_outcome()
        reward = self.reward_system.calculate_reward(prev_state, move, game_outcome)
        
        # Get next state
        next_state = self.get_state()
        
        # Info dictionary
        info = {
            'game_outcome': game_outcome,
            'move_count': len(self.game_state.moveLog),
            'in_check': self.game_state.inCheck if hasattr(self.game_state, 'inCheck') else False
        }
        
        return next_state, reward, self.done, info
    
    def _get_game_outcome(self):
        """Determine game outcome"""
        if self.game_state.checkMate:
            # Determine winner based on whose turn it is
            if self.game_state.whiteToMove:
                return "loss"  # White is checkmated, so current player (white) loses
            else:
                return "win"   # Black is checkmated, so current player wins
        elif self.game_state.staleMate:
            return "draw"
        else:
            return "ongoing"
    
    def is_game_over(self):
        """Check if game is over"""
        return self.done
    
    def get_result(self):
        """Get final game result"""
        return self._get_game_outcome()