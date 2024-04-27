import pygame as p
import ChessEngine, SmartMoveFinder

WIDTH = HEIGHT = 512 # Kích thước cửa sổ
DIMENSION = 8 # Kích thước bảng cờ vua 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

playerOne = True # True = playerTurn = whiteTurn
playerTwo = True

# Khởi tạo từ điển của các ảnh
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

# Xử lý dữ liệu đầu vào của người dùng và cập nhật đồ họa
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    #
    moveMade = False
    #
    animate = False
    loadImages()
    running = True
    # Nếu không có ô vuông nào chọn, xử lý lần nhấp chuột cuối cùng (tuple: (col, row))
    sqSelected = ()
    # Lưu lại các lần nhấp chuột
    playerClicks = []
    gameOver = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False 
            # Xử lý chuột
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    # Lấy ra tạo độ (x,y) của chuột
                    location = p.mouse.get_pos() 
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        # Bỏ chọn
                        sqSelected = ()
                        # Xóa danh sách
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        # Thêm 2 lần nhấp chuột đầu tiên
                        playerClicks.append(sqSelected)
                    # Nhiều hơn 2 lần nhấp chuột
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessLocation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            # Xử lý phím
            elif e.type == p.KEYDOWN:
                # Hoàn tác nếu phím 'z' được nhấn
                if e.key == p.K_z:
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
                    animate = False
                    gameOver = False
                    
                # Cài lại bàn cờ khi ấn 'r'
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves) 
            if AIMove is None:  
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves= gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black win.')
            else:
                drawText(screen, 'White win.')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Stalemate.')

        clock.tick(MAX_FPS)
        p.display.flip()

# Chịu trách nhiệm về tất cả đồ họa trong trạng thái trò chơi hiện tại
def drawGameState(screen, gs, validMoves, sqSelected):
    # Vẽ hình vuông trên bảng
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    # Vẽ các quân cờ lên trên các hình vuông
    drawPieces(screen, gs.board)

# Đánh dấu ô vuông mà quân cờ được chọn để di chuyển
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        # sqSelected là 1 quân cờ có thể di chuyển
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): 
            # Đánh dấu ô vuông được chọn
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            # Đánh dấu ô vuông di chuyển được
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

# Vẽ hình vuông lên bảng, hình vuông góc trên bên trái luôn là màu trắng
def drawBoard(screen):
    global colors
    colors = [p.Color("#FFFFE0"), p.Color("#A2CD5A")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Vẽ quân cờ lên bảng sử dụng GameState.board
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE,r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Hành động di chuyển
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    frameCount = (abs(dR) + abs(dC)) * 2
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != '--':
            if move.enPassant:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        #
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], endSquare)
        #
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        #
        clock.tick(150)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation.move(2, 2))

if __name__ == "__main__":
    main()