# Tên: Nguyễn Xuân Hiệp
# Mã sv: 22022591

import pygame as p
import ChessEngine, SmartMoveFinder, Evalute

WIDTH = HEIGHT = 512  # Kích thước cửa sổ
DIMENSION = 8  # Kích thước bảng cờ vua 8x8 ô
SQ_SIZE = HEIGHT // DIMENSION  # Kích thước mỗi ô trên bàn cờ
MAX_FPS = 15  # Số lần lặp trên 1 giây để cập nhật trạng thái trò chơi
IMAGES = {}

playerOne = False  # True = playerTurn = whiteTurn
playerTwo = False
running = False
onePlayer = False
choosePlayer = True


# Khởi tạo từ điển của các ảnh
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (50, 50))


# Xử lý dữ liệu đầu vào của người dùng và cập nhật đồ họa
def main():
    global playerOne, playerTwo, running, onePlayer, choosePlayer
    p.init()  # Tạo môi trường để sd chức năng của Pygame
    screen = p.display.set_mode((WIDTH, HEIGHT))  # Hiển thị cửa số có kích thước WxH
    clock = p.time.Clock()
    screen.fill(p.Color("white"))  # Vẽ cửa sổ màu trắng
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    # Nếu không có ô vuông nào chọn, xử lý lần nhấp chuột cuối cùng (tuple: (col, row))
    sqSelected = ()
    # Lưu lại các lần nhấp chuột
    playerClicks = []
    gameOver = False
    choosePP = False
    mousePressed = False
    buttonPressed = None

    buttons = [
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 - 100, 200, 50),  # Vẽ hình chữ nhật
            'text': 'AI Play',  # Văn bản
            'textColor': '#006400',  # Màu văn bản
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',  # Màu hình chữ nhật
            'buttonColorDown': '#006400',
            'borderColor': 'black',  # Màu viền ô
            'action': {'playerOne': False, 'playerTwo': False, 'running': True, 'onePlayer': False,
                       'choosePlayer': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 - 25, 200, 50),
            'text': 'One Player',
            'textColor': '#006400',
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',
            'buttonColorDown': '#006400',
            'borderColor': 'black',
            'action': {'playerOne': True, 'playerTwo': False, 'running': True, 'onePlayer': True, 'choosePlayer': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 + 50, 200, 50),
            'text': 'Two Player',
            'textColor': '#006400',
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',
            'buttonColorDown': '#006400',
            'borderColor': 'black',
            'action': {'playerOne': True, 'playerTwo': True, 'running': True, 'onePlayer': False, 'choosePlayer': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 - 75, 200, 50),
            'text': 'White',
            'textColor': 'white',
            'textColorDown': 'black',
            'buttonColor': 'black',
            'buttonColorDown': 'white',
            'borderColor': 'white',
            'action': {'playerOne': True, 'playerTwo': False, 'running': True, 'onePlayer': False, 'choosePlayer': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 + 25, 200, 50),
            'text': 'Black',
            'textColor': 'black',
            'textColorDown': 'white',
            'buttonColor': 'white',
            'buttonColorDown': 'black',
            'borderColor': 'black',
            'action': {'playerOne': False, 'playerTwo': True, 'running': True, 'onePlayer': False,
                       'choosePlayer': False}
        }
    ]

    while choosePlayer or onePlayer:
        # Vẽ bàn cờ
        drawBoard(screen)
        drawAlphabetNumber(screen)
        drawPieces(screen, gs.board)

        # Tạo mảng rỗng
        ranges = []
        if onePlayer: # Nếu onePlayer = True thì mảng có 2 phần tử [4,5]
            ranges = range(3, 5)
        else:
            ranges = range(3)

        # Vẽ các nút với các chỉ số trong mảng
        for i in ranges:
            button = buttons[i]
            drawButton(screen, button['rect'], button['text'], button['textColor'], button['buttonColor'], button['borderColor'])
        
        # Thay đổi nút khi nút được nhất (buttonPressed) không rỗng
        if buttonPressed is not None:
            drawButtonDown(screen, buttonPressed['rect'], buttonPressed['text'], buttonPressed['textColorDown'], buttonPressed['buttonColorDown'], buttonPressed['borderColor'])
        
        # Cập nhật giao diện
        p.display.flip()

        # Xử lý chuột
        for e in p.event.get():
            if e.type == p.QUIT:
                choosePlayer = False
                onePlayer = False
            elif e.type == p.MOUSEBUTTONDOWN:
                for i in ranges:
                    button = buttons[i]
                    # Nếu vị trí chuột bấm xuống nằm trong nút
                    if button['rect'].collidepoint(e.pos):
                        buttonPressed = button
                        mousePressed = True
            elif e.type == p.MOUSEBUTTONUP:
                for i in ranges:
                    button = buttons[i]
                    # Nếu vị trí nhấc chuột nằm trong nút
                    if mousePressed and button['rect'].collidepoint(e.pos):
                        for key, value in button['action'].items():
                            if key in globals():
                                # Cập nhật biến toàn cục trong button['action']
                                globals()[key] = value
                buttonPressed = None
                mousePressed = False

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
                                        for e in p.event.get():
                                            if e.type == p.MOUSEBUTTONDOWN:
                                                # Xác định quân cờ được chọn
                                                location = p.mouse.get_pos()
                                                c = location[0] // SQ_SIZE
                                                r = location[1] // SQ_SIZE
                                                pP = ['Q', 'R', 'B', 'N', 'Q', 'R', 'B', 'N']
                                                if validMoves[i].pieceMoved == 'wp' and \
                                                        0 <= r < 4 and c == validMoves[i].endCol:
                                                    validMoves[i].promotedPiece = 'w' + pP[r]
                                                    gs.makeMove(validMoves[i])
                                                elif validMoves[i].pieceMoved == 'bp' and \
                                                        4 <= r < 8 and c == validMoves[i].endCol:
                                                    validMoves[i].promotedPiece = 'b' + pP[r]
                                                    gs.makeMove(validMoves[i])
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
            if Evalute.check_mid_game(gs):
                SmartMoveFinder.DEPTH = 4
            else:
                SmartMoveFinder.DEPTH = 3
            AIMove = SmartMoveFinder.findBestMinimaxMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs, clock)
            validMoves = gs.getValidMoves()
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


def drawButtonDown(screen, rect, text, textColorDown, buttonColorDown, borderColor):
    # Vẽ hình chữ nhật
    p.draw.rect(screen, buttonColorDown, rect)
    # Vẽ viền
    border_width = 1
    p.draw.rect(screen, borderColor, rect, border_width)
    # Chỉnh phông chữ
    font = p.font.SysFont('Calibri', 30, True, False)
    # Đọc text
    textSurface = font.render(text, True, textColorDown)
    # Vẽ text ở giữa hình chữ nhật
    textRect = textSurface.get_rect(center=rect.center)
    screen.blit(textSurface, textRect)


def drawButton(screen, rect, text, textColor, buttonColor, borderColor):
    p.draw.rect(screen, buttonColor, rect)
    border_width = 1
    p.draw.rect(screen, borderColor, rect, border_width)
    font = p.font.SysFont('Calibri', 30, True, False)
    textSurface = font.render(text, True, textColor)
    textRect = textSurface.get_rect(center=rect.center)
    screen.blit(textSurface, textRect)


# Chịu trách nhiệm về tất cả đồ họa trong trạng thái trò chơi hiện tại
def drawGameState(screen, gs, validMoves, sqSelected):
    # Vẽ hình vuông trên bảng
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected, gs.moveLog)
    # Đánh số và chữ
    drawAlphabetNumber(screen)
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
                    if move.pieceCaptured != '--' or move.enPassant:
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


def drawAlphabetNumber(screen):
    font = p.font.SysFont("Calibri", 13, True, False)
    for i, char in enumerate(range(ord('a'), ord('h') + 1)):
        # In chữ
        alphabet = font.render(chr(char), True, p.Color('#556B2F'))
        alphabetLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(SQ_SIZE / 10, i * SQ_SIZE + SQ_SIZE / 10)
        screen.blit(alphabet, alphabetLocation)

        # In số
        number = font.render(str(i + 1), True, p.Color('#556B2F'))
        numberLocation = p.Rect(0, SQ_SIZE * 7, WIDTH, HEIGHT).move((i + 1) * SQ_SIZE - 10, SQ_SIZE - 15)
        screen.blit(number, numberLocation)


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
            if piece != "--" and piece is not None:
                image = IMAGES[piece]
                screen.blit(image, p.Rect(c * SQ_SIZE + SQ_SIZE / 2 - image.get_width() / 2,
                                          r * SQ_SIZE + SQ_SIZE / 2 - image.get_height() / 2, SQ_SIZE, SQ_SIZE))


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
        image = IMAGES[location.pieceMoved[0] + piece]
        screen.blit(image, p.Rect(locationOptionCol * SQ_SIZE + SQ_SIZE / 2 - image.get_width() / 2,
                                  locationOptionRow * SQ_SIZE + SQ_SIZE / 2 - image.get_height() / 2 + (i * SQ_SIZE),
                                  SQ_SIZE, SQ_SIZE))
    p.display.flip()


# Hoạt ảnh di chuyển
def animateMove(move, screen, gs, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    # Số lượng khung hình cần để hoàn thành bước đi.
    frameCount = (abs(dR) + abs(dC)) * 4
    for frame in range(frameCount + 1):
        # Tính toán vị trí hàng và cột của quân cờ tại từng khung hình trong quá trình di chuyển.
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)

        # Vẽ lại bàn cờ
        drawBoard(screen)
        drawPieces(screen, gs.board)

        # Vẽ màu lên ô cuối cùng khi di chuyển
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Nếu ô cuối cùng là quân thì vẽ quân
        if move.pieceCaptured != '--':
            imageC = IMAGES[move.pieceCaptured]
            if move.enPassant:
                screen.blit(imageC, p.Rect(move.endCol * SQ_SIZE + SQ_SIZE / 2 - imageC.get_width() / 2,
                                           move.startRow * SQ_SIZE + SQ_SIZE / 2 - imageC.get_height() / 2, SQ_SIZE,
                                           SQ_SIZE))
            else:
                screen.blit(imageC, p.Rect(move.endCol * SQ_SIZE + SQ_SIZE / 2 - imageC.get_width() / 2,
                                           move.endRow * SQ_SIZE + SQ_SIZE / 2 - imageC.get_height() / 2, SQ_SIZE,
                                           SQ_SIZE))

        # Nếu ô bắt đầu là quân thì vẽ quân
        if move.pieceMoved != '--':
            imageM = IMAGES[move.pieceMoved]
            screen.blit(imageM, p.Rect(c * SQ_SIZE + SQ_SIZE / 2 - imageM.get_width() / 2,
                                       r * SQ_SIZE + SQ_SIZE / 2 - imageM.get_height() / 2, SQ_SIZE, SQ_SIZE))

        drawAlphabetNumber(screen)

        # Cập nhật hình ảnh
        p.display.flip()
        # Số khung hình mỗi giây
        clock.tick(100)


def drawText(screen, text, color):
    # Tạo phông chữ (phông chữ, cỡ chữ, in đậm, in nghiêng)
    font = p.font.SysFont("Calibri", 32, True, False)
    # Đọc text và màu
    textObject = font.render(text, 0, p.Color('black'))
    # Tạo hình chữ nhật tính từ góc trên bên trái (0,0) có kích thước WxH và di chuyển ra giữa màn hình
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    # Vẽ text với màu đen trước đó vị trí lệch với vị trí ban đầu sang phải 2, xuống 2
    screen.blit(textObject, textLocation.move(2, 2))
    textObject = font.render(text, 0, p.Color(color))
    screen.blit(textObject, textLocation.move(3, 3))


if __name__ == "__main__":
    main()
