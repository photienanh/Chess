class ChessReward:
    def __init__(self):
        self.piece_values = {'p': 1, 'R': 5, 'N': 3, 'B': 3, 'Q': 9, 'K': 0}
        self.center_squares = [(3,3), (3,4), (4,3), (4,4)]
    
    def calculate_reward(self, game_state, move, game_outcome):
        """Balanced reward with both bonuses and penalties"""
        reward = 0.0
        
        # Game outcome (main rewards)
        if game_outcome == "win":
            reward = 2.0  # Moderate increase from 1.0
        elif game_outcome == "loss":
            reward = -2.0
        elif game_outcome == "draw":
            reward = 0.1  # Small positive for draw
        else:
            # Step rewards for ongoing game
            reward = 0.005  # Slight increase from 0.001
            
            # Material rewards/penalties
            if hasattr(move, 'pieceCaptured') and move.pieceCaptured != '--':
                captured_value = self.piece_values.get(move.pieceCaptured[1], 0)
                reward += captured_value * 0.2  # Double from 0.1
            
            # Positional bonuses (small)
            if (move.endRow, move.endCol) in self.center_squares:
                reward += 0.05  # Small center control bonus
            
            # Check bonus (small)
            if hasattr(game_state, 'inCheck') and game_state.inCheck:
                reward += 0.1
            
            # PENALTIES to balance bonuses:
            
            # Penalty for losing material (if we lost a piece this turn)
            if hasattr(move, 'pieceMoved') and move.pieceMoved != '--':
                # Check if we're moving into danger (simplified)
                if (move.endRow, move.endCol) in [(0,0), (0,7), (7,0), (7,7)]:  # Corner squares
                    reward -= 0.02  # Small penalty for corner moves
            
            # Penalty for very passive moves (moving backwards)
            if move.pieceMoved[0] == 'w' and move.endRow > move.startRow:  # White moving backward
                reward -= 0.01
            elif move.pieceMoved[0] == 'b' and move.endRow < move.startRow:  # Black moving backward
                reward -= 0.01
            
            # Penalty for repetitive moves (moving same piece back and forth)
            if hasattr(game_state, 'moveLog') and len(game_state.moveLog) >= 2:
                last_move = game_state.moveLog[-1]
                if (last_move.endRow == move.startRow and 
                    last_move.endCol == move.startCol and
                    last_move.startRow == move.endRow and 
                    last_move.startCol == move.endCol):
                    reward -= 0.1  # Penalty for moving back immediately
            
            # Penalty for very long games (discourage draws)
            if hasattr(game_state, 'moveLog'):
                move_count = len(game_state.moveLog)
                if move_count > 80:
                    reward -= 0.002  # Small penalty for long games
                if move_count > 120:
                    reward -= 0.005  # Bigger penalty for very long games
            
            # Penalty for moving king early (unless castling)
            if move.pieceMoved[1] == 'K' and not getattr(move, 'isCastleMove', False):
                if hasattr(game_state, 'moveLog') and len(game_state.moveLog) < 20:  # Early game
                    reward -= 0.05  # Discourage early king moves
        
        return reward