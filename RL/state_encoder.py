import numpy as np

class ChessStateEncoder:
    """Advanced chess state encoding for modern RL"""
    
    def __init__(self):
        # 12 piece types (6 white + 6 black) + additional planes
        self.piece_planes = 12
        self.additional_planes = 8  # castling, en passant, etc.
        self.total_planes = self.piece_planes + self.additional_planes
        
    def encode_state(self, game_state):
        """
        Encode chess position as tensor [20, 8, 8]
        Similar to AlphaZero representation
        """
        state = np.zeros((self.total_planes, 8, 8), dtype=np.float32)
        
        # Piece planes (12 planes)
        piece_map = {
            'wp': 0, 'wR': 1, 'wN': 2, 'wB': 3, 'wQ': 4, 'wK': 5,
            'bp': 6, 'bR': 7, 'bN': 8, 'bB': 9, 'bQ': 10, 'bK': 11
        }
        
        for r in range(8):
            for c in range(8):
                piece = game_state.board[r][c]
                if piece != '--':
                    plane = piece_map[piece]
                    state[plane, r, c] = 1.0
        
        # Additional planes
        plane_idx = 12
        
        # Current player to move
        if game_state.whiteToMove:
            state[plane_idx, :, :] = 1.0
        plane_idx += 1
        
        # Castling rights (4 planes)
        if hasattr(game_state, 'currentCastlingRight'):
            castling = game_state.currentCastlingRight
            if castling.wks:  # White king side
                state[plane_idx, :, :] = 1.0
            plane_idx += 1
            if castling.wqs:  # White queen side
                state[plane_idx, :, :] = 1.0
            plane_idx += 1
            if castling.bks:  # Black king side
                state[plane_idx, :, :] = 1.0
            plane_idx += 1
            if castling.bqs:  # Black queen side
                state[plane_idx, :, :] = 1.0
            plane_idx += 1
        else:
            plane_idx += 4
            
        # En passant target square
        if hasattr(game_state, 'enpassantPossible') and game_state.enpassantPossible:
            # Mark en passant square
            ep_row, ep_col = game_state.enpassantPossible
            state[plane_idx, ep_row, ep_col] = 1.0
        plane_idx += 1
        
        # Move count / game phase
        move_count = len(game_state.moveLog) if hasattr(game_state, 'moveLog') else 0
        state[plane_idx, :, :] = min(move_count / 100.0, 1.0)  # Normalized
        plane_idx += 1
        
        # King in check
        in_check = self._is_in_check(game_state)
        if in_check:
            state[plane_idx, :, :] = 1.0
            
        return state
    
    def _is_in_check(self, game_state):
        """Safe check detection"""
        if hasattr(game_state, 'inCheck'):
            if callable(game_state.inCheck):
                return game_state.inCheck()
            else:
                return game_state.inCheck
        return False