# Chưa làm
# 1. (xong)
# đánh dấu nước đã đi
# 2. (xong)
# thay đổi cách đánh dấu nước đi hợp lệ
# 3. 
# đánh số và chữ cho ô
# 4. 
# giao diện chọn số người chơi

# Lỗi
# 1.(xong)
# undoMove tốt đi 2 nước k hiển thị lại hình ảnh

import pygame as p
import ChessEngine, SmartMoveFinder

WIDTH = HEIGHT = 512 # Kích thước cửa sổ
DIMENSION = 8 # Kích thước bảng cờ vua 8x8 ô
SQ_SIZE = HEIGHT // DIMENSION # Kích thước mỗi ô trên bàn cờ
MAX_FPS = 15 # Số lần lặp trên 1 giây để cập nhật trạng thái trò chơi
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
    p.init() # Tạo môi trường để sd chức năng của Pygame
    screen = p.display.set_mode((WIDTH, HEIGHT)) # Hiển thị cửa số có kích thước WxH
    clock = p.time.Clock()
    screen.fill(p.Color("white")) # Vẽ cửa sổ màu trắng
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    running = True
    # Nếu không có ô vuông nào chọn, xử lý lần nhấp chuột cuối cùng (tuple: (col, row))
    sqSelected = ()
    # Lưu lại các lần nhấp chuột
    playerClicks = []
    gameOver = False
    choosePP = False

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
                    # Nếu chọn cùng 1 ô
                    if sqSelected == (row, col):
                        # Bỏ chọn
                        sqSelected = ()
                        # Xóa danh sách
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    
                    if len(playerClicks) == 2:
                        # Tạo đối tượng move có lớp Move(điểm đầu, điểm cuối, bàn cờ)
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if not validMoves[i].pawnPromotion:
                                    gs.makeMove(validMoves[i])
                                else:
                                    choosePP = True
                                    while choosePP:
                                        drawPromotionOptions(screen, validMoves[i])
                                        p.display.flip()  # Cập nhật cửa sổ để hiển thị cửa sổ nhỏ mới
                                        for e in p.event.get():
                                            if e.type == p.MOUSEBUTTONDOWN:
                                                # Xác định quân cờ được chọn
                                                location = p.mouse.get_pos()
                                                c = location[0] // SQ_SIZE
                                                r = location[1] // SQ_SIZE
                                                pP = ['Q','R','B','N','Q','R','B','N']
                                                if validMoves[i].pieceMoved == 'wp' and \
                                                 0 <= r < 4 and c == validMoves[i].endCol:
                                                    gs.makeMove(validMoves[i], promotedPiece = 'w' + pP[r])
                                                elif validMoves[i].pieceMoved == 'bp' and \
                                                 4 <= r < 8 and c == validMoves[i].endCol:
                                                    gs.makeMove(validMoves[i], promotedPiece= 'b' + pP[r])
                                                choosePP = False
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
            AIMove = SmartMoveFinder.findBestMinimaxMove(gs, validMoves)
            if AIMove is None:  
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs, clock)
            validMoves= gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black win.', '#363636')
            else:
                drawText(screen, 'White win.', 'white')
        elif gs.staleMate:
            gameOver = True
            drawText(screen, 'Draw.', '#A9A9A9')
        clock.tick(MAX_FPS)
        p.display.flip()

# Chịu trách nhiệm về tất cả đồ họa trong trạng thái trò chơi hiện tại
def drawGameState(screen, gs, validMoves, sqSelected):
    # Vẽ hình vuông trên bảng
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected, gs.moveLog)
    # Vẽ các quân cờ lên trên các hình vuông
    drawPieces(screen, gs.board)

def highlightSquares(screen, gs, validMoves, sqSelected, moveLog):
    global colors
    s = p.Surface((SQ_SIZE, SQ_SIZE))

    # Đánh dấu quân cờ được chọn là màu xanh
    s.set_alpha(90)
    s.fill(p.Color('blue'))
    if sqSelected != ():
        r, c = sqSelected
        # sqSelected là 1 quân cờ có thể di chuyển
        if gs.board[r][c] is not None and gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): 
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    # Đặt vị trí cho hình tròn
                    center = (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2)
                    if move.pieceCaptured != '--':
                        radius = 29
                        p.draw.circle(screen, '#9C9C9C', center, radius)
                        color = colors[((move.endRow + move.endCol) % 2)]
                        radius = 25
                        p.draw.circle(screen, color, center, radius)
                        continue
                    radius = 10
                    # Vẽ hình tròn màu xám
                    p.draw.circle(screen, '#9C9C9C', center, radius)
    
    # Đánh dấu vị trí quân cờ vừa di chuyển là màu vàng
    s.set_alpha(130)
    s.fill(p.Color('yellow'))
    if len(moveLog) != 0:  # Kiểm tra nếu có quân cờ đã di chuyển
        s.fill(p.Color('yellow'))
        screen.blit(s, (moveLog[-1].endCol * SQ_SIZE, moveLog[-1].endRow * SQ_SIZE))
        # Vẽ màu vàng cho ô kết thúc
        screen.blit(s, (moveLog[-1].startCol * SQ_SIZE, moveLog[-1].startRow * SQ_SIZE))


# Vẽ hình vuông lên bảng, hình vuông góc trên bên trái luôn là màu trắng
def drawBoard(screen):
    global colors
    colors = [p.Color("#FFFFE0"), p.Color("#A2CD5A")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Vẽ quân cờ lên bảng
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE,r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
                
# Vẽ bảng chọn của tốt phong quân
def drawPromotionOptions(screen, location):
    locationOptionRow = location.endRow
    locationOptionCol = location.endCol
    
    if locationOptionRow == 7:
        locationOptionRow = locationOptionRow - 3
    
    # Tạo bề mặt có vị trí, kích thước
    optionPP = p.Rect(locationOptionCol * SQ_SIZE, locationOptionRow * SQ_SIZE, SQ_SIZE, 4 * SQ_SIZE)
    p.draw.rect(screen, p.Color('white'), optionPP)

    # Đặt kích thước cho viền đen
    border_width = 1
    p.draw.rect(screen, p.Color('black'), optionPP, border_width)
        
    promotionOptions = ['Q', 'R', 'B', 'N']
    for i, piece in enumerate(promotionOptions):
        screen.blit(IMAGES[location.pieceMoved[0] + piece], p.Rect(locationOptionCol * SQ_SIZE, locationOptionRow * SQ_SIZE  + (i * SQ_SIZE), SQ_SIZE, SQ_SIZE))

# Hoạt ảnh di chuyển
def animateMove(move, screen, gs, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    # Số lượng khung hình cần để hoàn thành bước đi.
    frameCount = (abs(dR) + abs(dC)) * 3
    for frame in range(frameCount + 1):
        # Tính toán vị trí hàng và cột của quân cờ tại từng khung hình trong quá trình di chuyển.
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, gs.board)
        
        # Vẽ màu lên ô cuối cùng khi di chuyển
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Nếu ô cuối cùng là quân thì vẽ quân
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE))

        # Nếu ô bắt đầu là quân thì vẽ quân
        if move.pieceMoved != '--':
            screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        
        # Cập nhật hình ảnh
        p.display.flip()
        # Số khung hình mỗi giây
        clock.tick(150)

def drawText(screen, text, color):
    # Tạo phông chữ (phông chữ, cỡ chữ, in đậm, in nghiêng)
    font = p.font.SysFont("Calibri", 32, True, False)
    # Đọc text và màu
    textObject = font.render(text, 0, p.Color('black'))
    # Tạo hình chữ nhật tính từ góc trên bên trái (0,0) có kích thước WxH và di chuyển ra giữa màn hình
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    # Vẽ text với màu đen trước đó vị trí lệch với vị trí ban đầu sang phải 2, xuống 2
    screen.blit(textObject, textLocation.move(2, 2))
    textObject = font.render(text, 0, p.Color(color))
    screen.blit(textObject, textLocation.move(3, 3)) 

if __name__ == "__main__":
    main()
