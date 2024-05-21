# Phó Viết Tiến Anh
# 22022568
class GameState():
    def __init__(self):
        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N":self.getKnightMoves,
                            "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteToMove = True #Lượt đi của trắng
        self.moveLog = [] #Lịch sử nước đi
        self.whiteKingLocation = (7,4) #Vị trí vua trắng
        self.blackKingLocation = (0,4) #Vị trí vua đen
        self.noCapturedMoves = 0 #Lịch sử ăn quân và di tốt
        self.historyBoard = [([r[:] for r in self.board])]
        self.countPiece = {'p':16, 'R':4, 'B':4, 'N':4, 'Q':2, 'K':2}
        self.inCheck = False #Bị chiếu
        self.pins = [] #Danh sách ghim
        self.checks = [] #Danh sách chiếu
        self.checkMate = False #Chiếu hết
        self.staleMate = False #Hòa cơ
        self.enPassantPossible = () #Bắt quân qua đường
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True,True,True,True) #Nhập thành
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]
    # Thực hiện một nước đi trên bàn cờ.
    # Cập nhật bàn cờ với vị trí mới của quân cờ.
    # Thêm nước đi vào lịch sử nước đi.
    # Cập nhật các biến khác như lượt của người chơi, vị trí của vua, quyền nhập thành, v.v.
    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move)
        self.historyBoard.append([r[:] for r in self.board])
        if move.pieceCaptured != '--':
            self.countPiece[move.pieceCaptured[1]] -= 1
        # Đảo chiều người chơi.
        self.whiteToMove = not self.whiteToMove
        
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        
        # Có thể bắt tốt qua đường
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enPassantPossible = ()
        
        # Bắt tốt qua đường
        if move.enPassant:
            self.board[move.startRow][move.endCol] = '--'
            self.countPiece['p'] -= 1
        
        # Tốt phong hàm
        if move.pawnPromotion:
            self.board[move.endRow][move.endCol] = move.promotedPiece
            if move.promotedPiece is not None:
                self.board[move.endRow][move.endCol] = move.promotedPiece
                self.countPiece[move.promotedPiece[1]] += 1
                self.countPiece['p'] -= 1
        
        # Xử lý nhập thành
        if move.castle:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = '--'
            elif move.startCol - move.endCol == 2:
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'
        
        # Cập nhật bắt quân qua đường
        self.enPassantPossibleLog.append(self.enPassantPossible)

        # Cập nhật trạng thái nhập thành
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        
        # Nếu nước đi không ăn quân và không di tốt
        if move.pieceCaptured == '--' and move.pieceMoved[1] != 'p':
            self.noCapturedMoves += 1
        else:
            self.noCapturedMoves = 0
                    
    # Hoàn tác nước đi trước đó.
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop() #Lấy nước đi cuối cùng
            self.noCapturedMoves -= 1
            if move.pieceCaptured != '--':
                self.countPiece[move.pieceCaptured[1]] += 1
            self.historyBoard.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved #Trả quân về vị trí ban đầu
            self.board[move.endRow][move.endCol] = move.pieceCaptured #Trả lại quân bị ăn
            self.whiteToMove = not self.whiteToMove #Đảo chiều người chơi

            # Trả lại vị trí của vua
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            # Trả lại vị trí quân tốt bị bắt quân qua đường
            if move.enPassant:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = 'bp' if self.whiteToMove else 'wp'
                self.countPiece['p'] += 1
            if len(self.enPassantPossibleLog) != 0:
                self.enPassantPossibleLog.pop() 
                self.enPassantPossible = self.enPassantPossibleLog[-1]

            if move.pawnPromotion and move.promotedPiece is not None:
                self.countPiece[move.promotedPiece[1]] -= 1
                self.countPiece['p'] += 1
            # Trả lại trạng thái nhập thành
            self.castleRightsLog.pop() 
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            
            if move.castle:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'
            self.checkMate = False
            self.staleMate = False

    # Trả về danh sách các nước đi hợp lệ cho người chơi hiện tại.
    # Kiểm tra xem người chơi có đang bị chiếu không và xem có nước đi nào để thoát khỏi chiếu không.
    # Kiểm tra xem trò chơi có đang ở trong tình trạng chiếu mạng (checkmate) hay hòa (stalemate) không.
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        
        # Xác định vị trí quân vua của người chơi hiện tại
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.inCheck: #Nếu bị chiếu
            if len(self.checks) == 1: #Nếu chỉ có 1 quân chiếu(không phải quân mã)
                moves = self.getAllPossibleMoves() #Xác định tất cả nước có thể đi
                check = self.checks[0]
                # Xác định vị trí quân cờ đang chiếu
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = [] #Tạo danh sách các ô có thể di chuyển để bảo vệ vua

                if pieceChecking[1] == 'N': #Nếu quân chiếu là mã
                    validSquares = [(checkRow, checkCol)]
                else: #Xác định hướng quân chiếu
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                
                # Loại bỏ các nước đi không bảo vệ được vua
                for i in range(len(moves) - 1, -1, -1): #Duyệt từ cuối danh sách lên đầu
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            if moves[i].enPassant:
                                continue
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
        
        if len(moves) == 0:
            if self.inCheck:
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            if self.noCapturedMoves == 50:
                self.staleMate = True
            elif (len(self.historyBoard) >= 9) and self.historyBoard[-1] == self.historyBoard[-5] == self.historyBoard[-9]:
                self.staleMate = True
            else:
                self.staleMate = self.missPiece()
        return moves
    
    def missPiece(self):
        if self.countPiece == {'p':0, 'R':0, 'B':0, 'N':0, 'Q':0, 'K':2}:
            return True
        elif self.countPiece == {'p':0, 'R':0, 'B':1, 'N':0, 'Q':0, 'K':2}:
            return True
        elif self.countPiece == {'p':0, 'R':0, 'B':0, 'N':1, 'Q':0, 'K':2}:
            return True
        else:
            return False

    # Kiểm tra 1 ô trên bàn cờ có bị tấn công hay không.
    def squareUnderAttack(self, r, c, allyColor):
        enemyColor = 'w' if allyColor == 'b' else 'b'
        directions = ((-1,0), (0,-1), (1,0), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)) #8 hướng di chuyển
        for j in range(len(directions)): #Duyệt qua các hướng di chuyển
            d = directions[j]
            for i in range(1, 8): #Tăng dần khoảng cách các hướng
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #Duyệt trong phạm vi bàn cờ
                    endPiece = self.board[endRow][endCol]
                    if endPiece is None:
                        continue
                    if endPiece[0] == allyColor: #Nếu là quân đồng minh
                        break
                    elif endPiece[0] == enemyColor: #Nếu là quân địch
                        type = endPiece[1] 
                        
                        #Xác định loại quân và hướng di chuyển
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <=7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                    (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            return True
                        else:
                            break
                else:
                    break
                
        knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)) #Hướng di chuyển của quân mã
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    return True
        return False
    
    # Lấy tất cả các nước đi có thể của người chơi hiện tại.
    def getAllPossibleMoves(self):
        moves = [] #Khởi tạo danh sách các nước đi hợp lệ

        # Duyệt toàn bộ bàn cờ
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] is not None:
                    turn = self.board[r][c][0] #Xác định màu quân
                    if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove): 
                        piece = self.board[r][c][1]
                        self.moveFunctions[piece](r, c, moves)
        return moves
    
    # Kiểm tra vua có bị ghim hoặc bị chiếu
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False
        
        # Xác định vị trí của vua
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        # Duyệt qua 8 hướng cho vua
        directions = ((-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0]*i
                endCol = startCol + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece is None:
                        continue
                    if endPiece[0] == allyColor and endPiece[1] != 'K': #Nếu có quân đồng minh khác vua
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor: #Nếu gặp quân địch
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                            (4 <= j <= 7 and type == 'B') or \
                            (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                            (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): #Nếu chưa có quân đồng minh chặn
                                inCheck = True # => Vua bị chiếu
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)) #Hướng đi quân mã
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece is not None and endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
                    break
        return inCheck, pins, checks
    
    # Cập nhật quyền nhập thành
    def updateCastleRights(self, move):
        # Nếu vua di chuyển, cập nhật lại quyền nhập thành
        if move.pieceMoved == 'wK': 
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        # Nếu xe di chuyển, cập nhật lại quyền nhập thành
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: #Xe bên hậu
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #Xe bên vua
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    # Nước đi của tốt
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = 'b'
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = 'w'
            kingRow, kingCol = self.blackKingLocation

        if 0 <= r + moveAmount < 8 and self.board[r + moveAmount][c] == '--':
            if not piecePinned or pinDirection == (moveAmount, 0): #nếu không bị chặn
                moves.append(Move((r, c), (r + moveAmount, c), self.board)) #Tiến 1 bước
                if r == startRow and self.board[r + 2 * moveAmount][c] == '--': #Tiến 2 bước
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        
        if c - 1 >= 0: #Giới hạn bên trái bàn cờ
            if not piecePinned or pinDirection == (moveAmount, -1): #Nếu không bị chặn hoặc hướng chặn chéo 1 ô liền kề
                if 0 <= r + moveAmount < 8: #Giới hạn trên dưới bàn cờ
                    if self.board[r + moveAmount][c - 1] is not None and self.board[r + moveAmount][c - 1][0] == enemyColor: #Quân địch ở chéo 1 ô
                        moves.append(Move((r, c), (r + moveAmount, c - 1), self.board)) #Ăn quân
                    if (r + moveAmount, c - 1) == self.enPassantPossible: #Nếu là nước đi bắt quân qua đường
                        attackingPiece = blockkingPiece = False
                        if kingRow == r: #Vua trùng hàng với tốt
                            if kingCol < c: #Vua ở bên trái tốt
                                insideRange = range(kingCol + 1, c - 1) #Từ ô liền sau vua đến liền trước tốt
                                outsideRange = range(c + 1, 8) #Từ ô liền sau tốt đến hết bàn cờ
                            else: #Vua ở bên phải tốt
                                insideRange = range(kingCol - 1, c, -1)
                                outsideRange = range(c - 2, -1, -1)
                            for i in insideRange:
                                if self.board[r][i] != '--':
                                    blockkingPiece = True
                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                    attackingPiece = True
                                elif square != '--':
                                    blockkingPiece = True
                        if not attackingPiece or blockkingPiece: #Nếu vua không bị xe hoặc hậu tấn công hoặc đã có quân chặn
                            moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))

        if c + 1 <= 7: #Tương tự ở trên
            if not piecePinned or pinDirection == (moveAmount,1):
                if 0 <= r + moveAmount < 8:
                    if self.board[r + moveAmount][c + 1][0] == enemyColor:
                        moves.append(Move((r, c), (r + moveAmount, c + 1), self.board))
                    if (r + moveAmount, c + 1) == self.enPassantPossible:
                        attackingPiece = blockkingPiece = False
                        if kingRow == r:
                            if kingCol < c:
                                insideRange = range(kingCol + 1, c)
                                outsideRange = range(c + 2, 8)
                            else:
                                insideRange = range(kingCol - 1, c + 1, -1)
                                outsideRange = range(c - 1, -1, -1)
                            for i in insideRange:
                                if self.board[r][i] != '--':
                                    blockkingPiece = True
                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == enemyColor and (square[1] == 'R' or square[1] == 'Q'):
                                    attackingPiece = True
                                elif square != '--':
                                    blockkingPiece = True
                        if not attackingPiece or blockkingPiece:
                            moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, enPassant=True))

    # Nước đi của xe
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': #Nếu đây là quân hậu 
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0),(0, -1),(1, 0),(0, 1)) #4 hướng lên xuống trái phải
        enemyColor = "b" if self.whiteToMove else "w"
        
        # Duyệt các hướng đi
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol <8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]): #Nếu không bị ghim hoặc di chuyển trong hướng ghim
                        endPiece = self.board[endRow][endCol]
                        if endPiece is not None:
                            if endPiece == "--": #Nếu ô trống
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                            elif endPiece[0] == enemyColor: #Nếu gặp quân địch
                                moves.append(Move((r, c), (endRow, endCol), self.board))
                                break
                            else: #Nếu gặp quân ta
                                break
                else:
                    break

    # Nước đi của mã
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) #Hướng đi của mã
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece is not None and endPiece[0] != allyColor:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
    
    # Nước đi của tượng
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,-1),(-1,1),(1,-1),(1,1)) #4 hướng chéo
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]): #Nếu không bị ghim hoặc di chuyển trong hướng ghim
                        endPiece = self.board[endRow][endCol]
                        if endPiece is None:
                            continue
                        if endPiece == "--":
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r,c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break
    
    # Nước đi của hậu(Kết hợp xe và tượng)
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    # Nước đi của vua
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece is not None and endPiece[0] != allyColor:
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    
                    inCheck, pins, check = self.checkForPinsAndChecks()
                    
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        self.getCastleMoves(r, c, moves, allyColor)
    
    # Quyền nhập thành
    def getCastleMoves(self, r, c, moves, allyColor):
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves, allyColor)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves, allyColor)
    
    # Nhập thành phía vua
    def getKingsideCastleMoves(self, r, c, moves, allyColor):
        if c+3 < len(self.board[r]) and self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--' and \
         not self.squareUnderAttack(r, c, allyColor) and \
         not self.squareUnderAttack(r, c + 1, allyColor) and not self.squareUnderAttack(r, c + 2, allyColor) and \
         self.board[r][c + 3] == allyColor + 'R':
            moves.append(Move((r, c), (r, c + 2), self.board, castle = True))
    
    # Nhập thành phía hậu
    def getQueensideCastleMoves(self, r, c, moves, allyColor):
        if c-4 < len(self.board[r]) and self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--' and \
         not self.squareUnderAttack(r, c, allyColor) and \
         not self.squareUnderAttack(r, c - 1,allyColor) and not self.squareUnderAttack(r, c - 2, allyColor) and \
         self.board[r][c - 4] == allyColor + 'R':
            moves.append(Move((r, c), (r, c - 2), self.board, castle = True))

class Move():    
    def __init__(self, startSq, endSq, board, enPassant = False, castle = False, promotedPiece = None):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        if self.pieceMoved is not None:
            self.pawnPromotion = self.pieceMoved[1] == 'p' and (self.endRow == 0 or self.endRow == 7) 
        self.enPassant = enPassant
        self.castle = castle
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        
        if self.enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved[0] == 'w' else 'wp'

        # Lựa chọn cho AI
        if self.pawnPromotion:
            self.promotedPiece = self.pieceMoved[0] + 'Q' or 'R' or 'N' or 'B'

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
