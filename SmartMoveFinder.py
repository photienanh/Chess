import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0 # >0 => white win : <0 black win

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove(gs, validMoves):
    turn = 1 if gs.whiteToMove else -1
    maxScore = -CHECKMATE
    bestMove = None
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        apponentsMoves = gs.getValidMoves()
        for apponentsMove in apponentsMoves:
            gs.makeMove(apponentsMove)
            if gs.checkmate:
                score = CHECKMATE
            elif gs.stalemate:
                score = 0
            else:
                score = turn * scoreMaterial(gs.board)
            if score > maxScore:
                maxScore = score
                bestMove = playerMove
        gs.undoMove
    return bestMove

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score