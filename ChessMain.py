import pygame as p
import ChessEngine, SmartMoveFinder

WIDTH = HEIGHT = 512 # Kích thước cửa sổ
DIMENSION = 8 # Kích thước bảng cờ vua 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

gameOver = False

playerOne = True # True = playerTurn = whiteTurn
playerTwo = False 

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
    moveMade = False
    loadImages()
    running = True
    # Nếu không có ô vuông nào chọn, xử lý lần nhấp chuột cuối cùng (tuple: (col, row))
    sqSelected = ()
    # Lưu lại các lần nhấp chuột
    playerClicks = []

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)


        for e in p.event.get():
            if e.type == p.QUIT:
                running = False 
            # Xử lý chuột
            elif e.type == p.MOUSEBUTTONDOWN:
                # Lấy ra tạo đọ (x,y) của chuột
                if not gameOver and humanTurn:
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
                        if move in validMoves:
                            gs.makeMove(move)
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                        else:
                            playerClicks = [sqSelected]
            # Xử lý phím
            elif e.type == p.KEYDOWN:
                # Hoàn tác nếu phím 'z' được nhấn
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False

        if not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves) 
            if AIMove is None:  
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            validMoves= gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

# Chịu trách nhiệm về tất cả đồ họa trong trạng thái trò chơi hiện tại
def drawGameState(screen, gs):
    # Vẽ hình vuông trên bảng
    drawBoard(screen)
    # Vẽ các quân cờ lên trên các hình vuông
    drawPieces(screen, gs.board)

# Vẽ hình vuông lên bảng, hình vuông góc trên bên trái luôn là màu trắng
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
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

                
main()
