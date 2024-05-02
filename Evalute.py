CHECKMATE = 100000
STALEMATE = 0

piece_value = {
    "K": 2000, "Q": 900, "R": 500, "B": 330, "N": 320, "p": 100
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

def evaluate_piece(piece, square, location) -> int:
    piece_type = piece
    mapping = []
    if piece_type == "p":
        mapping = pawnEvalWhite if square == "w" else pawnEvalBlack
    if piece_type == "K":
        mapping = knightEval
    if piece_type == "B":
        mapping = bishopEvalWhite if square == "w" else bishopEvalBlack
    if piece_type == "R":
        mapping = rookEvalWhite if square == "w" else rookEvalBlack
    if piece_type == "Q":
        mapping = queenEval
    if piece_type == "K":
        #if end_game:
        #    mapping = (
        #        kingEvalEndGameWhite
        #        if square == "w"
        #        else kingEvalEndGameBlack
        #    )
        #else:
        mapping = kingEvalWhite if square == "w" else kingEvalBlack

    return mapping[location[0]][location[1]]

def evaluate_board(gs) -> float:
    total = 0
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE # black win
        else:
            return CHECKMATE #white win
    elif gs.staleMate:
        return STALEMATE

    for row in len(gs.board):
        for square in len(row):
            piece = gs.board[row][square]
            if piece  == "--":
                continue
            value = piece_value[piece[1]] + evaluate_piece(piece[1], piece[0], [row, square])
            total += value if square[0] == "w" else -value
    return total
