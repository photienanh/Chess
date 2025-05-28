# Chess
This is a Chess game project built with Python and Pygame. The project supports both player-vs-player and player-vs-AI modes, with a graphical user interface.
## Features
- **Graphical interface** using Pygame with intuitive controls.
- **Multiple game modes:**
  - Single-player vs Traditional AI (Minimax algorithm).
  - Single-player vs Reinforcement Learning AI.
  - Two-player local multiplayer.
- **Advanced AI systems:**
  - Traditional AI uses Minimax algorithm with alpha-beta pruning.
  - RL AI trained using Deep Q-Learning for adaptive gameplay.
- **Complete chess implementation:**
  - Full chess rules: castling, pawn promotion, en passant.
  - Game state detection: checkmate, stalemate, draw conditions.
  - Move validation and legal move generation.
- **Interactive features:**
  - Highlights valid moves when piece is selected.
  - Visual indicators for last move played.
  - Special state highlighting (check, checkmate, stalemate).
- **Game controls:**
  - Undo moves functionality (press `z`).
  - Reset board to starting position (press `r`).
  - Return main menu while playing (press `Esc`).
  - Pawn promotion with piece selection dialog
## Directory Structure
```
Chess/
├── images/                    # Chess piece images (PNG files)
│   ├── wp.png, wR.png, wN.png, wB.png, wQ.png, wK.png  # White pieces
│   └── bp.png, bR.png, bN.png, bB.png, bQ.png, bK.png  # Black pieces
├── RL/                        # Reinforcement Learning AI system
│   ├── ppo_agent.py           # PPO (Proximal Policy Optimization) agent
│   ├── chess_env.py           # Chess environment for RL training
│   ├── state_encoder.py       # Game state encoding for neural networks
│   ├── chess_net.py           # Neural network architectures
│   ├── reward_system.py       # Reward calculation for RL training
│   ├── train_advanced.py      # Advanced training script with curriculum learning
│   ├── ppo_chess_final.pth    # Trained RL model (basic)
│   └── RL_model.pth           # Advanced trained RL model
├── ChessMain.py               # Main game file: GUI, game loop, and controls
├── ChessEngine.py             # Chess game logic, rules, and move validation
├── SmartMoveFinder.py         # Traditional AI using Minimax with alpha-beta pruning
└── Evalute.py                 # Board position evaluation for traditional AI
```
## Main Files Explained

- **ChessMain.py**: Manages the GUI, main loop, and user events.
- **ChessEngine.py**: Stores board state, checks rules, generates valid moves.
- **Evalute.py**: Evaluates the board for the AI based on piece value and position.
- **SmartMoveFinder.py**: Minimax (with alpha-beta pruning) algorithm for AI move selection.
- **images/**: Contains chess piece images (png).

## Installation
### Option 1: Run the standalone `Chess.exe` (Recommended for Windows users)
**Note: This option doesn't have RL mode.**
1. Go to the [Releases](https://github.com/photienanh/Chess/releases) page.
2. Download the latest version of `Chess.exe`.
3. Double-click the file to play – No Python or Pygame installation required!
### Option 2: Run from source code (requires Python)
#### 1. Clone the repository
```bash
git clone https://github.com/photienanh/Chess
```
Alternatively, download the ZIP file from GitHub and extract it.
#### 2. Install Dependencies
Ensure Python (version >=3.7) is installed. If not, you can download and install it from the [official Python website](https://www.python.org/downloads/). Then, install the required library:
```bash
pip install pygame
```
## Usage

- **If you chose Option 1 (Chess.exe):**  
  Just double-click `Chess.exe` to launch the game.

- **If you chose Option 2 (Run from source code):**
   After installing the requirements and downloading the project, open a terminal or command prompt, navigate to the project directory, and start the game with:
      ```bash
      python ChessMain.py
      ```
   This will launch the chess game window. You can then:
   - Choose the game mode (AI, one player, two players).
   - Click to select and move pieces.
   - Undo a move by pressing `z`.
   - Reset the board by pressing `r`.
   - Return main menu by pressing `Esc`.
   - When a pawn is promoted, select the piece you want to promote to.
## Contribution
Contributions are welcome! To contribute:
- Fork the repository.
- Create a new branch for your feature or bug fix.
- Submit a pull request with a clear description of your changes.