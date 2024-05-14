CHECKMATE = 999999999999999999
STALEMATE = 0

piece_value = {
    "K": 90000, "Q": 9000, "R": 5000, "B": 3300, "N": 3200, "p": 1000
}

pawnEvalWhite = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [5, 10, 10, -20, -20, 10, 10,  5],
    [5, -5, -10,  0,  0, -10, -5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [0, 0, 0, 0, 0, 0, 0, 0]
]
pawnEvalBlack = list(reversed(pawnEvalWhite))

knightEval = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

bishopEvalWhite = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]
bishopEvalBlack = list(reversed(bishopEvalWhite))

rookEvalWhite = [
    [0, 0, 0, 5, 5, 0, 0, 0],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]
rookEvalBlack = list(reversed(rookEvalWhite))

queenEval = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

kingEvalWhite = [
    [20, 30, 10, 0, 0, 10, 30, 20],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, -30, -30, -40, -40, -30, -30, -20],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30]
]
kingEvalBlack = list(reversed(kingEvalWhite))

kingEvalEndGameWhite = [
    [50, -30, -30, -30, -30, -30, -30, -50],
    [-30, -30,  0,  0,  0,  0, -30, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -20, -10,  0,  0, -10, -20, -30],
    [-50, -40, -30, -20, -20, -30, -40, -50]
]
kingEvalEndGameBlack = list(reversed(kingEvalEndGameWhite))

def evaluate_piece(piece, square, location, end_game) -> int:
    piece_type = piece
    mapping = []
    if piece_type == "p":
        mapping = pawnEvalWhite if square == "w" else pawnEvalBlack
    elif piece_type == "N":
        mapping = knightEval
    elif piece_type == "B":
        mapping = bishopEvalWhite if square == "w" else bishopEvalBlack
    elif piece_type == "R":
        mapping = rookEvalWhite if square == "w" else rookEvalBlack
    elif piece_type == "Q":
        mapping = queenEval
    elif piece_type == "K":
        if end_game:
            mapping = kingEvalEndGameWhite if square == "w" else kingEvalEndGameBlack
        else:
            mapping = kingEvalWhite if square == "w" else kingEvalBlack
    if 0 <= location[0] < 8 and 0 <= location[1] < 8:
        return mapping[location[0]][location[1]]

def evaluate_board(gs) -> float:
    total = 0
    end_game = check_end_game(gs.board)
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE # black win
        else:
            return CHECKMATE #white win
    elif gs.staleMate:
        return STALEMATE

    for row in range(8):
        for square in range(8):
            piece = gs.board[row][square]
            if piece is None or piece == "--":
                continue
            value = piece_value[piece[1]] + evaluate_piece(piece[1], piece[0], [row, square], end_game)
            total += value if piece[0] == "w" else -value
    return total

def check_end_game(board) -> bool:
    queens = 0
    minors = 0
    for row in board:
        for square in row:
            if square is not None:
                if square[1] == "Q":
                    queens += 1
                if square[1] == "B" or square[1] == "N":
                    minors += 1

    if queens == 0 or (queens == 2 and minors <= 1):
        return True

    return False

def check_mid_game(gs) -> bool:
    count = 0
    for row in gs.board:
        for square in row:
            if square != "--":
                count+=1
    if count > 20:
        return False
    return True
               
