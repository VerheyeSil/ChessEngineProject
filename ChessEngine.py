'''
This class is responsible for storing all the information of the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It wil also keep a move log.
'''

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "wN", "--", "bN", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]            
        ]
        self.moveFunctions = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}

        self.whiteToMove = True
        self.moveLog = []

    '''
    Takes a move as a parameter and executes it (this will not work for castling, promotion and en-passant)
    '''
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # Log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # Switch turn
    
    '''
    Undos the last move that was made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0: # Make sure there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # Switch turn back

    '''
    All moves considering checks
    '''
    def getValidMoves(self):
        return self.getAllPossibleMoves() 
    
    '''
    All moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # Call the appropriate move function based on piece type
                    
        return moves
    
    '''
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    '''
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove: # White pawn moves
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0: # Captures to the left
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: # Captures to the right
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))

        else: # Black pawn moves
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0: # Captures to the left
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 < 7: # Captures to the right
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    '''
    Get all the rook moves for the rook located at row, col and add these moves to the list
    '''
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # Empty space to move to
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # Enemy piece to capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece
                        break
                else: # Off the board
                    break
 
    '''
    Get all the king moves for the king located at row, col and add these moves to the list
    '''
    def getKingMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, 1), (-1, -1), (1, 1), (-1, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 2):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # Empty space to move to
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # Enemy piece to capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece
                        break
                else: # Off the board
                    break

    '''
    Get all the Queen moves for the Queen located at row, col and add these moves to the list
    '''
    def getQueenMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, 1), (-1, -1), (1, 1), (-1, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # Empty space to move to
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # Enemy piece to capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece
                        break
                else: # Off the board
                    break

    '''
    Get all the Bishop moves for the Bishop located at row, col and add these moves to the list
    '''
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, 1), (-1, -1), (1, 1), (-1, -1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # Empty space to move to
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # Enemy piece to capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece
                        break
                else: # Off the board
                    break


    '''
    Get all the Knight moves for the Knight located at row, col and add these moves to the list
    '''
    def getKnightMoves(self, r, c, moves):
        directions = ((2, -1), (2, 1), (-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # Empty space to move to
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: # Enemy piece to capture
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: # Friendly piece
                        break
                else: # Off the board
                    break


class Move():
    # Maps keys to values
    # Key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = { v: k for k, v in filesToCols.items()}
    def __init__(self, startSq, endSq, board): 
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        # Add to make this like real chess notation, but works for now
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]




    