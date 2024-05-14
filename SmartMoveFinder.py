import random
from ChessEngine import Move
import Evalute

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = Evalute.CHECKMATE
STALEMATE = Evalute.STALEMATE # >0 => white win : <0 black win
DEPTH = 4
global nextMove


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMinimaxMove(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMiniMaxScore(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, True if gs.whiteToMove else False)      
    return nextMove

def findMiniMaxScore(gs, validMoves, depth, alpha, beta, turnMutiplayer):
    global nextMove
    if depth == 0:
        return Evalute.evaluate_board(gs)
    if turnMutiplayer:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextValidMoves = gs.getValidMoves()
            score = findMiniMaxScore(gs, nextValidMoves, depth-1, alpha, beta, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            alpha = max(alpha, score)
            gs.undoMove()
            if beta <= alpha:
                break
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextValidMoves = gs.getValidMoves()
            score = findMiniMaxScore(gs, nextValidMoves, depth-1, alpha, beta, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
            beta = min(beta, score)
            if beta <= alpha:
                break
            
        return minScore