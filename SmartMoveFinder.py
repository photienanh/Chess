import random

pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0 # >0 => white win : <0 black win
DEPTH = 2
nextMove = None

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
        if gs.staleMate:
            MaxAIscore = STALEMATE
        elif gs.checkMate:           
            MaxAIscore = -CHECKMATE
        else:
            MaxAIscore = -CHECKMATE
            for PlayerMove in PlayerMoves:
                gs.makeMove(PlayerMove)
                gs.getValidMoves()
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
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

def findBestMinimaxMove(gs, validMoves):
    global nextMove
    findMiniMax(gs, validMoves, DEPTH, gs.whiteToMove)      
    return nextMove

def findMiniMax(gs, validMoves, depth, humanTurn):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if humanTurn:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMove = gs.getValidMoves()
            score = findMiniMax(gs, nextMove, depth - 1, humanTurn = False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore

    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMove = gs.getValidMoves() 
            score = findMiniMax(gs, nextMove, depth - 1, humanTurn = True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
        return minScore

#white điểm càng cao càng tốt, black điểm càng thấp càng tốt
def scoreBoard(gs):
    if gs.checkMate:
        if gs.WhiteToMove:
            return -CHECKMATE # black win
        else:
            return CHECKMATE #white win
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == "w":
                score += pieceScore[square[1]]
            elif square[0] == "b":
                score -= pieceScore[square[1]]
    return score