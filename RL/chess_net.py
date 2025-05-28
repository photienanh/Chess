import torch
import torch.nn as nn

class ChessNet(nn.Module):
    """Modern chess neural network with CNN + Attention"""
    
    def __init__(self, input_planes=20, hidden_size=256):
        super(ChessNet, self).__init__()
        
        # Convolutional layers (similar to AlphaZero)
        self.conv_block1 = self._make_conv_block(input_planes, 256)
        self.conv_block2 = self._make_conv_block(256, 256)
        self.conv_block3 = self._make_conv_block(256, 256)
        self.conv_block4 = self._make_conv_block(256, 256)
        
        # Residual blocks
        self.res_blocks = nn.ModuleList([
            self._make_residual_block(256) for _ in range(6)
        ])
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(256, num_heads=8, batch_first=True)
        
        # Value head
        self.value_conv = nn.Conv2d(256, 1, kernel_size=1)
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(64, 256)
        self.value_fc2 = nn.Linear(256, 1)
        
        # Policy head (for move prediction)
        self.policy_conv = nn.Conv2d(256, 64, kernel_size=1)  # Changed from 73 to 64
        self.policy_bn = nn.BatchNorm2d(64)
        self.policy_fc = nn.Linear(64 * 8 * 8, 4096)  # Map to exact action size
        
    def _make_conv_block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU()
        )
    
    def _make_residual_block(self, channels):
        return nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(channels)
        )
    
    def forward(self, x):
        # Initial convolutions
        x = self.conv_block1(x)
        x = self.conv_block2(x)
        x = self.conv_block3(x)
        x = self.conv_block4(x)
        
        # Residual blocks with skip connections
        for res_block in self.res_blocks:
            residual = x
            x = res_block(x)
            x = torch.relu(x + residual)
        
        # Attention over spatial locations
        batch_size, channels, h, w = x.shape
        x_flat = x.view(batch_size, channels, h*w).transpose(1, 2)  # [B, 64, 256]
        attn_out, _ = self.attention(x_flat, x_flat, x_flat)
        x = attn_out.transpose(1, 2).view(batch_size, channels, h, w)
        
        # Value head
        value = self.value_conv(x)
        value = self.value_bn(value)
        value = torch.relu(value)
        value = value.view(batch_size, -1)
        value = torch.relu(self.value_fc1(value))
        value = torch.tanh(self.value_fc2(value))
        
        # Policy head
        policy = self.policy_conv(x)
        policy = self.policy_bn(policy)
        policy = policy.view(batch_size, -1)
        
        return value, policy

class MoveEncoder:
    """Direct move encoding like AlphaZero"""
    
    def __init__(self):
        self.action_size = 4096  # 64*64 possible moves + special moves
        
    def encode_move(self, move):
        """Encode move as single integer"""
        start_square = move.startRow * 8 + move.startCol
        end_square = move.endRow * 8 + move.endCol
        
        # Basic move encoding
        action = start_square * 64 + end_square
        
        # Add promotion encoding if needed
        if hasattr(move, 'pawnPromotion') and move.pawnPromotion:
            promotion_offset = 4096
            if move.promotedPiece == 'Q':
                action = promotion_offset + start_square * 64 + end_square
            elif move.promotedPiece == 'R':
                action = promotion_offset + 1024 + start_square * 64 + end_square
            # ... other promotions
            
        return action
    
    def decode_action(self, action, game_state):
        """Convert action back to move"""
        if action < 4096:  # Regular move
            start_square = action // 64
            end_square = action % 64
            start_row, start_col = start_square // 8, start_square % 8
            end_row, end_col = end_square // 8, end_square % 8
            
            # Find corresponding move in valid moves
            valid_moves = game_state.getValidMoves()
            for move in valid_moves:
                if (move.startRow == start_row and move.startCol == start_col and
                    move.endRow == end_row and move.endCol == end_col):
                    return move
        return None