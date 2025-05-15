# Chess
This is a Chess game project built with Python and Pygame. The project supports both player-vs-player and player-vs-AI modes, with a graphical user interface.
## Features
- Graphical interface using Pygame.
- Supports single-player (vs AI) and two-player modes.
- AI uses Minimax algorithm with board evaluation.
- Full chess rules: castling, pawn promotion, en passant, checkmate, stalemate.
- Undo moves and reset the board.
- Highlights valid moves, last move, and special states (checkmate, stalemate).
## Directory Structure
```
Chess/
├── images/                # Folder containing chess piece images
│   └── [wp.png, wR.png, ...]
├── ChessMain.py           # Main file: GUI and game loop
├── ChessEngine.py         # Handles logic, state, and chess rules
├── Evalute.py             # Board evaluation for AI
└── SmartMoveFinder.py     # AI algorithm to find the best move
```
## Main Files Explained

- **ChessMain.py**: Manages the GUI, main loop, and user events.
- **ChessEngine.py**: Stores board state, checks rules, generates valid moves.
- **Evalute.py**: Evaluates the board for the AI based on piece value and position.
- **SmartMoveFinder.py**: Minimax (with alpha-beta pruning) algorithm for AI move selection.
- **images/**: Contains chess piece images (png).

## Installation
### 1. Clone the repository
```bash
git clone https://github.com/photienanh/Chess
```
Alternatively, download the ZIP file from GitHub and extract it.
### 2. Install Dependencies
Ensure Python (version >=3.7) is installed. If not, you can download and install it from the [official Python website](https://www.python.org/downloads/). Then, install the required library:
```bash
pip install pygame
```
## Usage
After installing the requirements and downloading the project, open a terminal or command prompt, navigate to the project directory, and start the game with:
   ```bash
   python ChessMain.py
   ```
This will launch the chess game window. You can then:
- Choose the game mode (AI, one player, two players).
- Click to select and move pieces.
- Undo a move by pressing `z`.
- Reset the board by pressing `r`.
- When a pawn is promoted, select the piece you want to promote to.
## Contribution
Contributions are welcome! To contribute:
- Fork the repository.
- Create a new branch for your feature or bug fix.
- Submit a pull request with a clear description of your changes.