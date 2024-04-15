import pygame as p
from Chess import ChessEngine

WIDTH = HEIGHT = 512 # Kích thước cửa sổ
DIMENSION = 8 # Kích thước bảng cờ vua 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

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
    loadImages()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running - False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

# Chịu trách nhiệm về tất cả đồ họa trong trạng thái trò chơi hiện tại
def drawGameState(screen, gs):
    # Vẽ hình vuông trên bảng
    drawBoard(screen)
    # Vẽ các mảnh lên trên các hình vuông
    drawPieces(screen, gs.board)

# Vẽ hình vuông lên trển bảng, hình vuông góc trên bên trái luôn là màu trắng
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r * c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    pass

if __name__ == "  main  ":
    main()

main()