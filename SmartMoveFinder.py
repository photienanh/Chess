import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0 # >0 => white win : <0 black win


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove(gs, validMoves):
    turn = 1 if gs.whiteToMove else -1
    MiniMaxScore = CHECKMATE
    bestAIMove = None
    random.shuffle(validMoves)
    for AIMove in validMoves:
        gs.makeMove(AIMove)
        PlayerMoves = gs.getValidMoves()
        if gs.stalemate:
            MaxAIscore = STALEMATE
        elif gs.checkmate:           
            MaxAIscore = -CHECKMATE
        else:
            MaxAIscore = -CHECKMATE
            for PlayerMove in PlayerMoves:
                gs.makeMove(PlayerMove)
                gs.getValidMoves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn * scoreMaterial(gs.board)
                if score > MaxAIscore:
                    MaxAIscore = score
                gs.undoMove()
        if MiniMaxScore > MaxAIscore:
            MiniMaxScore = MaxAIscore
            bestAIMove = AIMove
        gs.undoMove()
    return bestAIMove

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score