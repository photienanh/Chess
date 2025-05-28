import pygame as p
import os
import sys
import ChessEngine, SmartMoveFinder, Evalute

# Initialize RL_AVAILABLE first
RL_AVAILABLE = False
rl_env = None
rl_agent = None

# Update imports cho Modern RL System
try:
    # Add RL path
    rl_path = os.path.join(os.path.dirname(__file__), 'RL')
    if rl_path not in sys.path:
        sys.path.append(rl_path)
    
    from ppo_agent import ChessPPOAgent
    from chess_env import ChessEnvironment
    RL_AVAILABLE = True
except ImportError as e:
    RL_AVAILABLE = False
except Exception as e:
    RL_AVAILABLE = False

WIDTH = HEIGHT = 512  # Kích thước cửa sổ
DIMENSION = 8  # Kích thước bảng cờ vua 8x8 ô
SQ_SIZE = HEIGHT // DIMENSION  # Kích thước mỗi ô trên bàn cờ
MAX_FPS = 15  # Số lần lặp trên 1 giây để cập nhật trạng thái trò chơi
IMAGES = {}

playerOne = False  # True = playerTurn = whiteTurn
playerTwo = False
running = False
onePlayer = False
choosePlayer = True
choose_opponent = False  # Thêm biến mới
use_rl = False  # Thêm biến để xác định dùng RL hay Minimax
ai_battle = False  # Thêm biến cho AI Battle

def resource_path(relative_path):
       try:
           base_path = sys._MEIPASS
       except Exception:
           base_path = os.path.abspath(".")
       return os.path.join(base_path, relative_path)

# Khởi tạo từ điển của các ảnh
def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(resource_path("images/" + piece + ".png")), (50, 50))

# Xử lý dữ liệu đầu vào của người dùng và cập nhật đồ họa
def main():
    global playerOne, playerTwo, running, onePlayer, choosePlayer, choose_opponent, use_rl, ai_battle
    global RL_AVAILABLE, rl_env, rl_agent  # Make these global
    
    p.init()  # Tạo môi trường để sd chức năng của Pygame
    screen = p.display.set_mode((WIDTH, HEIGHT))  # Hiển thị cửa số có kích thước WxH
    clock = p.time.Clock()
    screen.fill(p.Color("white"))  # Vẽ cửa sổ màu trắng
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    loadImages()
    
    # Khởi tạo Modern RL System
    if RL_AVAILABLE:
        try:
            # Initialize modern RL environment and agent
            rl_env = ChessEnvironment()
            rl_agent = ChessPPOAgent()
            
            # Try to load trained model
            model_paths = [
                "RL/RL_model.pth"
            ]
            
            for model_path in model_paths:
                try:
                    if os.path.exists(model_path):
                        rl_agent.load_model(resource_path(model_path))
                        model_loaded = True
                        break
                except Exception as e:
                    continue
            
        except Exception as e:
            rl_agent = None
            rl_env = None
            RL_AVAILABLE = False
    
    # Nếu không có ô vuông nào chọn, xử lý lần nhấp chuột cuối cùng (tuple: (col, row))
    sqSelected = ()
    # Lưu lại các lần nhấp chuột
    playerClicks = []
    gameOver = False
    choosePP = False
    mousePressed = False
    buttonPressed = None

    buttons = [
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 - 100, 200, 50),  # AI Battle
            'text': 'AI Battle',
            'textColor': '#006400',
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',
            'buttonColorDown': '#006400',
            'borderColor': 'black',
            'action': {'playerOne': False, 'playerTwo': False, 'running': True, 'onePlayer': False,
                       'choosePlayer': False, 'ai_battle': True, 'choose_opponent': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 - 25, 200, 50),
            'text': 'Single Player',
            'textColor': '#006400',
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',
            'buttonColorDown': '#006400',
            'borderColor': 'black',
            'action': {'playerOne': False, 'playerTwo': False, 'running': False, 'onePlayer': False, 
                       'choosePlayer': False, 'choose_opponent': True, 'ai_battle': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 + 50, 200, 50),
            'text': 'Two Players',
            'textColor': '#006400',
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',
            'buttonColorDown': '#006400',
            'borderColor': 'black',
            'action': {'playerOne': True, 'playerTwo': True, 'running': True, 'onePlayer': False, 
                       'choosePlayer': False, 'choose_opponent': False, 'ai_battle': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 - 50, 200, 50),  # Play vs Minimax
            'text': 'Play vs Minimax',
            'textColor': '#006400',
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',
            'buttonColorDown': '#006400',
            'borderColor': 'black',
            'action': {'playerOne': False, 'playerTwo': False, 'running': False, 'onePlayer': True, 
                       'choosePlayer': False, 'choose_opponent': False, 'use_rl': False}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 + 25, 200, 50),  # Play vs RL
            'text': 'Play vs RL',
            'textColor': '#006400',
            'textColorDown': '#B3EE3A',
            'buttonColor': '#B3EE3A',
            'buttonColorDown': '#006400',
            'borderColor': 'black',
            'action': {'playerOne': False, 'playerTwo': False, 'running': False, 'onePlayer': True, 
                       'choosePlayer': False, 'choose_opponent': False, 'use_rl': True}
        },
        {
            'rect': p.Rect(WIDTH / 2 - 200 / 2, HEIGHT / 2 - 75, 200, 50),
            'text': 'White',
            'textColor': 'white',
            'textColorDown': 'black',
            'buttonColor': 'black',
            'buttonColorDown': 'white',
            'borderColor': 'white',
            'action': {'playerOne': True, 'playerTwo': False, 'running': True, 'onePlayer': False, 
                       'choosePlayer': False, 'choose_opponent': False}
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
                       'choosePlayer': False, 'choose_opponent': False}
        }
    ]

    while True:  # Vòng lặp chính
        while choosePlayer or onePlayer or choose_opponent:
            # Vẽ bàn cờ
            drawBoard(screen)
            drawAlphabetNumber(screen)
            drawPieces(screen, gs.board)

            # Xác định các nút cần hiển thị
            ranges = []
            if choosePlayer:
                ranges = range(3)  # AI Battle, Single Player, Two Players
            elif choose_opponent:
                ranges = range(3, 5)  # Play vs Minimax, Play vs RL
            elif onePlayer:
                ranges = range(5, 7)  # White, Black
            else:
                ranges = range(3)

            # Vẽ các nút (và disable RL options nếu không available)
            for i in ranges:
                if i < len(buttons):
                    button = buttons[i]
                    
                    # Disable RL-related buttons if RL not available
                    if not RL_AVAILABLE and ('RL' in button['text'] or 'AI Battle' in button['text']):
                        # Draw disabled button
                        disabled_button = button.copy()
                        disabled_button['buttonColor'] = '#808080'
                        disabled_button['textColor'] = '#404040'
                        disabled_button['text'] = button['text'] + ' (N/A)'
                        drawButton(screen, disabled_button['rect'], disabled_button['text'], 
                                 disabled_button['textColor'], disabled_button['buttonColor'], 
                                 disabled_button['borderColor'])
                    else:
                        drawButton(screen, button['rect'], button['text'], button['textColor'], 
                                 button['buttonColor'], button['borderColor'])
            
            # Vẽ nút được nhấn
            if buttonPressed is not None:
                drawButtonDown(screen, buttonPressed['rect'], buttonPressed['text'], 
                             buttonPressed['textColorDown'], buttonPressed['buttonColorDown'], 
                             buttonPressed['borderColor'])
            
            # Cập nhật giao diện
            p.display.flip()

            # Xử lý sự kiện
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.quit()
                    return
                elif e.type == p.MOUSEBUTTONDOWN:
                    for i in ranges:
                        if i < len(buttons):
                            button = buttons[i]
                            if button['rect'].collidepoint(e.pos):
                                # Skip disabled buttons
                                if not RL_AVAILABLE and ('RL' in button['text'] or 'AI Battle' in button['text']):
                                    continue
                                buttonPressed = button
                                mousePressed = True
                elif e.type == p.MOUSEBUTTONUP:
                    for i in ranges:
                        if i < len(buttons):
                            button = buttons[i]
                            if mousePressed and button['rect'].collidepoint(e.pos):
                                # Skip disabled buttons
                                if not RL_AVAILABLE and ('RL' in button['text'] or 'AI Battle' in button['text']):
                                    continue
                                    
                                # Xử lý logic chuyển trạng thái
                                if 'AI Battle' in button['text']:
                                    if not RL_AVAILABLE or rl_agent is None:
                                        continue
                                    # Reset và bắt đầu AI Battle
                                    gs = ChessEngine.GameState()
                                    validMoves = gs.getValidMoves()
                                    sqSelected = ()
                                    playerClicks = []
                                    moveMade = False
                                    animate = False
                                    gameOver = False
                                    ai_battle = True
                                    choosePlayer = False
                                    choose_opponent = False
                                    onePlayer = False
                                    playerOne = False
                                    playerTwo = False
                                    running = True
                                elif button['text'] == 'Two Players':
                                    # Reset và bắt đầu Two Players
                                    gs = ChessEngine.GameState()
                                    validMoves = gs.getValidMoves()
                                    sqSelected = ()
                                    playerClicks = []
                                    moveMade = False
                                    animate = False
                                    gameOver = False
                                    for key, value in button['action'].items():
                                        globals()[key] = value
                                elif button['text'] == 'Single Player':
                                    # Chuyển sang choose_opponent
                                    choose_opponent = True
                                    choosePlayer = False
                                elif 'Play vs' in button['text']:
                                    # Đặt use_rl và chuyển sang chọn màu
                                    if 'RL' in button['text']:
                                        if not RL_AVAILABLE or rl_agent is None:
                                            continue
                                        use_rl = True
                                    else:
                                        use_rl = False
                                    choose_opponent = False
                                    onePlayer = True
                                elif button['text'] in ['White', 'Black']:
                                    # Reset và bắt đầu game
                                    gs = ChessEngine.GameState()
                                    validMoves = gs.getValidMoves()
                                    sqSelected = ()
                                    playerClicks = []
                                    moveMade = False
                                    animate = False
                                    gameOver = False
                                    for key, value in button['action'].items():
                                        globals()[key] = value
                    buttonPressed = None
                    mousePressed = False

        # Game loop
        running = True
        while running:
            humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
            
            for e in p.event.get():
                if e.type == p.QUIT:
                    p.quit()
                    return
                elif e.type == p.KEYDOWN:
                    # Thoát về menu chính
                    if e.key == p.K_ESCAPE:
                        running = False
                        choosePlayer = True
                        onePlayer = False
                        choose_opponent = False
                        ai_battle = False
                        use_rl = False
                        playerOne = False
                        playerTwo = False
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False
                        break
                    # Hoàn tác nước đi
                    if e.key == p.K_z:
                        gs.undoMove()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = True
                        animate = False
                        gameOver = False
                    # Reset game
                    if e.key == p.K_r:
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False
                # Xử lý chuột
                elif e.type == p.MOUSEBUTTONDOWN:
                    if not gameOver and humanTurn:
                        location = p.mouse.get_pos()
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        if sqSelected == (row, col):
                            sqSelected = ()
                            playerClicks = []
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)

                        if len(playerClicks) == 2:
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    if not validMoves[i].pawnPromotion:
                                        gs.makeMove(validMoves[i])
                                    else:
                                        # Xử lý pawn promotion
                                        choosePP = True
                                        while choosePP:
                                            drawPromotionOptions(screen, validMoves[i])
                                            for e in p.event.get():
                                                if e.type == p.MOUSEBUTTONDOWN:
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

            # AI move logic - UPDATED for Modern RL
            if not gameOver and not humanTurn and running:
                if ai_battle:  # AI Battle: Minimax vs Modern RL
                    if gs.whiteToMove:  # Minimax (White)
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
                    else:  # Modern RL (Black)
                        try:
                            # Use modern RL agent
                            move, action, log_prob = rl_agent.select_action(gs, validMoves, training=False)
                            
                            if move and move in validMoves:
                                # Handle pawn promotion
                                if move.pawnPromotion:
                                    move.promotedPiece = move.pieceMoved[0] + 'Q'
                                gs.makeMove(move)
                                moveMade = True
                                animate = True
                            else:
                                # Fallback to random move
                                AIMove = SmartMoveFinder.findRandomMove(validMoves)
                                if AIMove:
                                    gs.makeMove(AIMove)
                                    moveMade = True
                                    animate = True
                                else:
                                    gameOver = True
                        except Exception as e:
                            # Fallback to random move
                            AIMove = SmartMoveFinder.findRandomMove(validMoves)
                            if AIMove:
                                gs.makeMove(AIMove)
                                moveMade = True
                                animate = True
                            else:
                                gameOver = True
                                
                elif use_rl:  # Single Player vs Modern RL
                    try:
                        # Use modern RL agent
                        move, action, log_prob = rl_agent.select_action(gs, validMoves, training=False)
                        
                        if move and move in validMoves:
                            # Handle pawn promotion
                            if move.pawnPromotion:
                                move.promotedPiece = move.pieceMoved[0] + 'Q'
                            gs.makeMove(move)
                            moveMade = True
                            animate = True
                        else:
                            # Fallback to random move
                            AIMove = SmartMoveFinder.findRandomMove(validMoves)
                            if AIMove:
                                gs.makeMove(AIMove)
                                moveMade = True
                                animate = True
                            else:
                                gameOver = True
                    except Exception as e:
                        # Fallback to random move
                        AIMove = SmartMoveFinder.findRandomMove(validMoves)
                        if AIMove:
                            gs.makeMove(AIMove)
                            moveMade = True
                            animate = True
                        else:
                            gameOver = True
                else:  # Single Player vs Minimax
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
                    if ai_battle:
                        drawText(screen, 'Modern RL (Black) Wins!', '#363636')
                    else:
                        drawText(screen, 'Black win.', '#363636')
                else:
                    if ai_battle:
                        drawText(screen, 'Minimax (White) Wins!', 'white')
                    else:
                        drawText(screen, 'White win.', 'white')
            elif gs.staleMate:
                gameOver = True
                if ai_battle:
                    drawText(screen, 'Draw - Minimax vs RL', '#A9A9A9')
                else:
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
