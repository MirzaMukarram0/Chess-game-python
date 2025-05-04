import os
import time
import copy

class Piece:
    def __init__(self, clr, pos):
        self.clr = clr  # 'white' or 'black'
        self.pos = pos  # tuple (row, col)
        self.moved = False
    def sym(self): # Return piece symbol
        return ' '
    def moves(self, brd): # Get valid moves considering check
        return []
    def valid(self, brd, end): # Check if move is valid
        moves = self.moves(brd)
        return end in moves
    def raw_moves(self, brd): # Get moves without check validation
        return []

class P(Piece):
    def sym(self): # Return pawn symbol
        return '♙' if self.clr == 'white' else '♟'
    def raw_moves(self, brd): # Calculate pawn moves without check
        moves = []
        r, c = self.pos
        dir = -1 if self.clr == 'white' else 1
        # Forward move
        if 0 <= r + dir < 8 and brd.brd[r + dir][c] is None:
            moves.append((r + dir, c))
            # Double move from start
            if not self.moved and 0 <= r + 2*dir < 8 and brd.brd[r + 2*dir][c] is None:
                moves.append((r + 2*dir, c))
        # Captures
        for offset in [-1, 1]:
            if 0 <= r + dir < 8 and 0 <= c + offset < 8:
                p = brd.brd[r + dir][c + offset]
                if p is not None and p.clr != self.clr:
                    moves.append((r + dir, c + offset))
        # En passant
        if brd.passant:
            en_r, en_c = brd.passant
            if r == (3 if self.clr == 'white' else 4) and abs(c - en_c) == 1:
                moves.append((r + dir, en_c))
        return moves
    
    def moves(self, brd): # Filter moves to avoid check
        moves = self.raw_moves(brd)
        valid = []
        for m in moves:
            if not brd.in_check(self.clr, self.pos, m):
                valid.append(m)
        return valid

class R(Piece):
    def sym(self): # Return rook symbol
        return '♖' if self.clr == 'white' else '♜'
    
    def raw_moves(self, brd): # Calculate rook moves
        moves = []
        r, c = self.pos
        dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for dr, dc in dirs:
            for i in range(1, 8):
                nr, nc = r + i * dr, c + i * dc
                if not (0 <= nr < 8 and 0 <= nc < 8): break
                if brd.brd[nr][nc] is None: moves.append((nr, nc))
                elif brd.brd[nr][nc].clr != self.clr:
                    moves.append((nr, nc))
                    break
                else: break
        return moves
    
    def moves(self, brd): # Filter rook moves
        moves = self.raw_moves(brd)
        valid = []
        for m in moves:
            if not brd.in_check(self.clr, self.pos, m):
                valid.append(m)
        return valid

class N(Piece):
    def sym(self): # Return knight symbol
        return '♘' if self.clr == 'white' else '♞'
    
    def raw_moves(self, brd): # Calculate knight moves
        moves = []
        r, c = self.pos
        jumps = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in jumps:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < 8 and 0 <= nc < 8): continue
            if brd.brd[nr][nc] is None or brd.brd[nr][nc].clr != self.clr:
                moves.append((nr, nc))
        return moves
    
    def moves(self, brd): # Filter knight moves
        moves = self.raw_moves(brd)
        valid = []
        for m in moves:
            if not brd.in_check(self.clr, self.pos, m):
                valid.append(m)
        return valid

class B(Piece):
    def sym(self): # Return bishop symbol
        return '♗' if self.clr == 'white' else '♝'
    
    def raw_moves(self, brd): # Calculate bishop moves
        moves = []
        r, c = self.pos
        dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in dirs:
            for i in range(1, 8):
                nr, nc = r + i * dr, c + i * dc
                if not (0 <= nr < 8 and 0 <= nc < 8): break
                if brd.brd[nr][nc] is None: moves.append((nr, nc))
                elif brd.brd[nr][nc].clr != self.clr:
                    moves.append((nr, nc))
                    break
                else: break
        return moves
    
    def moves(self, brd): # Filter bishop moves
        moves = self.raw_moves(brd)
        valid = []
        for m in moves:
            if not brd.in_check(self.clr, self.pos, m): valid.append(m)
        return valid

class Q(Piece):
    def sym(self): # Return queen symbol
        return '♕' if self.clr == 'white' else '♛'
    
    def raw_moves(self, brd): # Calculate queen moves
        moves = []
        r, c = self.pos
        dirs = [(-1, 0), (0, 1), (1, 0), (0, -1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in dirs:
            for i in range(1, 8):
                nr, nc = r + i * dr, c + i * dc
                if not (0 <= nr < 8 and 0 <= nc < 8): break
                if brd.brd[nr][nc] is None: moves.append((nr, nc))
                elif brd.brd[nr][nc].clr != self.clr:
                    moves.append((nr, nc))
                    break
                else: break
        return moves
    
    def moves(self, brd): # Filter queen moves
        moves = self.raw_moves(brd)
        valid = []
        for m in moves:
            if not brd.in_check(self.clr, self.pos, m): valid.append(m)
        return valid

class K(Piece):
    def sym(self): # Return king symbol
        return '♔' if self.clr == 'white' else '♚'
    
    def raw_moves(self, brd): # Calculate king moves including castling
        moves = []
        r, c = self.pos # Regular moves
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0: continue
                nr, nc = r + dr, c + dc
                if not (0 <= nr < 8 and 0 <= nc < 8): continue
                if brd.brd[nr][nc] is None or brd.brd[nr][nc].clr != self.clr:
                    moves.append((nr, nc))
        # Castling
        if not self.moved: # Kingside
            rk = brd.at((r, 7))
            if (rk is not None and isinstance(rk, R) 
                and rk.clr == self.clr and not rk.moved):
                if all(brd.brd[r][c] is None for c in range(c + 1, 7)): moves.append((r, c + 2))
            # Queenside
            rq = brd.at((r, 0))
            if (rq is not None and isinstance(rq, R) 
                and rq.clr == self.clr and not rq.moved):
                if all(brd.brd[r][c] is None for c in range(1, c)): moves.append((r, c - 2))
        return moves
    
    def moves(self, brd): # Filter king moves, including castling checks
        moves = self.raw_moves(brd)
        valid = []
        for m in moves:
            if abs(m[1] - self.pos[1]) == 2:  # Castling
                r, c = self.pos
                ec = m[1]
                dir = 1 if ec > c else -1
                if (brd.attacked(self.clr, (r, c)) or 
                    brd.attacked(self.clr, (r, c + dir)) or 
                    brd.attacked(self.clr, (r, c + 2 * dir))):
                    continue
            if not brd.in_check(self.clr, self.pos, m): valid.append(m)
        return valid

class Board:
    def __init__(self): # Initialize 8x8 board
        self.brd = [[None for _ in range(8)] for _ in range(8)]
        self.passant = None  # En passant target
        self.turn = 'white'
        self.setup()
    
    def setup(self): # Place pawns
        for c in range(8):
            self.brd[1][c] = P('black', (1, c))
            self.brd[6][c] = P('white', (6, c))
        # Place other pieces
        for c, t in enumerate([R, N, B, Q, K, B, N, R]):
            self.brd[0][c] = t('black', (0, c))
            self.brd[7][c] = t('white', (7, c))
    
    def at(self, pos): # Get piece at position
        r, c = pos
        if 0 <= r < 8 and 0 <= c < 8:
            return self.brd[r][c]
        return None
    
    def clone(self): # Deep copy board
        return copy.deepcopy(self)
    
    def move(self, start, end, promo=None, sim=False): # Execute move
        sr, sc = start
        er, ec = end
        p = self.brd[sr][sc]
        if p is None or p.clr != self.turn or not p.valid(self, end):
            return False
        # Handle castling
        if isinstance(p, K) and abs(ec - sc) == 2:
            if ec > sc:  # Kingside
                r = self.brd[sr][7]
                self.brd[sr][5] = r
                self.brd[sr][7] = None
                r.pos = (sr, 5)
                r.moved = True
            else:  # Queenside
                r = self.brd[sr][0]
                self.brd[sr][3] = r
                self.brd[sr][0] = None
                r.pos = (sr, 3)
                r.moved = True
        
        # Handle en passant capture
        if isinstance(p, P) and end == self.passant:
            cr = sr
            cc = ec
            self.brd[cr][cc] = None
        
        self.passant = None
        if isinstance(p, P) and abs(er - sr) == 2:
            self.passant = (sr + (1 if p.clr == 'black' else -1), sc)
        # Move piece
        self.brd[sr][sc] = None
        self.brd[er][ec] = p
        p.pos = end
        p.moved = True
        # Handle promotion
        if isinstance(p, P) and (er == 0 or er == 7):
            if sim or promo is not None: c = promo if promo is not None else 'Q'
            else: c = self.promote()
            if c == 'Q': self.brd[er][ec] = Q(p.clr, end)
            elif c == 'R': self.brd[er][ec] = R(p.clr, end)
            elif c == 'B': self.brd[er][ec] = B(p.clr, end)
            elif c == 'N': self.brd[er][ec] = N(p.clr, end)
            self.brd[er][ec].moved = True
        
        self.turn = 'black' if self.turn == 'white' else 'white'
        return True
    
    def promote(self): # Get promotion choice
        valid = ['Q', 'R', 'B', 'N']
        while True:
            c = input("Promote to (Q)ueen, (R)ook, (B)ishop, (N)ight? ").strip().upper()
            if c in valid: return c
            print("Invalid choice. Use Q, R, B, or N.")
    
    def attacked(self, clr, sq): # Check if square is attacked
        r, c = sq
        opp = 'black' if clr == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                p = self.brd[r][c]
                if p and p.clr == opp:
                    moves = p.raw_moves(self)
                    if sq in moves:
                        return True
        return False
    
    def check(self, clr): # Find if king is in check
        king = None
        for r in range(8):
            for c in range(8):
                p = self.brd[r][c]
                if p and isinstance(p, K) and p.clr == clr:
                    king = (r, c)
                    break
            if king: break
        return self.attacked(clr, king)
    
    def in_check(self, clr, start, end): # Simulate move to check for check
        temp = self.clone().brd
        temp_obj = self.clone()
        temp_obj.brd = temp
        temp_obj.passant = self.passant
        sr, sc = start
        er, ec = end
        p = temp[sr][sc]
        
        if isinstance(p, P) and (er, ec) == self.passant:
            temp[sr][ec] = None
        temp[sr][sc] = None
        temp[er][ec] = p
        king = None
        if isinstance(p, K):
            king = end
        else:
            for r in range(8):
                for c in range(8):
                    tp = temp[r][c]
                    if tp and isinstance(tp, K) and tp.clr == clr:
                        king = (r, c)
                        break
                if king: break

        opp = 'black' if clr == 'white' else 'white'
        for r in range(8):
            for c in range(8):
                tp = temp[r][c]
                if tp and tp.clr == opp:
                    if isinstance(tp, P):
                        dir = -1 if tp.clr == 'white' else 1
                        if king in [(r + dir, c - 1), (r + dir, c + 1)]:
                            if 0 <= king[0] < 8 and 0 <= king[1] < 8:
                                return True
                    else:
                        moves = tp.raw_moves(temp_obj)
                        if king in moves:
                            return True
        return False
    
    def checkmate(self, clr): # Check for checkmate
        if not self.check(clr):
            return False
        for r in range(8):
            for c in range(8):
                p = self.brd[r][c]
                if p and p.clr == clr:
                    moves = p.moves(self)
                    if moves: return False
        return True
    
    def stalemate(self, clr): # Check for stalemate
        if self.check(clr):
            return False
        for r in range(8):
            for c in range(8):
                p = self.brd[r][c]
                if p and p.clr == clr:
                    moves = p.moves(self)
                    if moves: return False
        return True
    
    def show(self): # Display board with enhanced visuals
        os.system('cls' if os.name == 'nt' else 'clear')
        # ANSI color codes for checkered pattern
        LIGHT_SQUARE = '\033[48;5;187m'  # Light beige
        DARK_SQUARE = '\033[48;5;94m'   # Dark brown
        RESET = '\033[0m'
        
        # Title
        print("\n ♔♚ AI-Powered Chess ♚♔")
        print(" ───────────────────────")
        
        # Top border and column labels
        print("   ┌───┬───┬───┬───┬───┬───┬───┬───┐")
        print("   │ a │ b │ c │ d │ e │ f │ g │ h │")
        print(" ├─┼───┼───┼───┼───┼───┼───┼───┼───┤")
        
        # Board rows
        for r in range(8):
            print(f" {8-r} │", end="")
            for c in range(8):
                # Determine square color (checkered pattern)
                square_color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
                p = self.brd[r][c]
                symbol = p.sym() if p else ' '
                # Center symbol with spaces
                print(f"{square_color} {symbol} {RESET}│", end="")
            print(f" {8-r}")
            if r < 7:
                print(" ├─┼───┼───┼───┼───┼───┼───┼───┼───┤")
        
        # Bottom border and column labels
        print(" └─┴───┴───┴───┴───┴───┴───┴───┴───┘")
        print("   │ a │ b │ c │ d │ e │ f │ g │ h │")
        print(" ───────────────────────")
        
        # Status bar
        status = f" Turn: {self.turn.capitalize()} {'♔' if self.turn == 'white' else '♚'}"
        if self.check(self.turn):
            status += " (In Check)"
        print(status)
        print()

vals = { P: 1, N: 3, B: 3, R: 5, Q: 9, K: 1000 }
def score(brd): # Evaluate board position
    s = 0
    for r in brd.brd:
        for p in r:
            if p:
                for t, v in vals.items():
                    if isinstance(p, t):
                        s += v if p.clr == 'white' else -v
                        break
    return s

def all_moves(brd, clr): # Get all possible moves for color
    moves = []
    for r in range(8):
        for c in range(8):
            p = brd.brd[r][c]
            if p and p.clr == clr:
                for m in p.moves(brd):
                    moves.append(((r, c), m))
    return moves

def minimax(brd, depth, alpha, beta, max_player): # Minimax with alpha-beta pruning
    if depth == 0 or brd.checkmate('white') or brd.checkmate('black') or brd.stalemate(brd.turn):
        if brd.checkmate('black'):
            return 10000, None
        if brd.checkmate('white'):
            return -10000, None
        return score(brd), None
    
    if max_player:
        max_eval = float('-inf')
        best = None
        for m in all_moves(brd, 'white'):
            new = brd.clone()
            new.move(m[0], m[1], 'Q', True)
            eval, _ = minimax(new, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best = m
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best
    else:
        min_eval = float('inf')
        best = None
        for m in all_moves(brd, 'black'):
            new = brd.clone()
            new.move(m[0], m[1], 'Q', True)
            eval, _ = minimax(new, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best = m
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best

def comp_move(brd, depth=3): # Get computer's move
    _, m = minimax(brd, depth, float('-inf'), float('inf'), False)
    return m

def intro(): # Print game instructions
    print("AI Powered Chess Game!!!!")
    print(" Human (White♔) VS AI (Black♚)")
    print("Input moves acording to format i.e 'a2a4' / input 'quit' to exit.")
    input("\nPress ENTER to start...")

def parse(pos): # Parse position string to tuple
    if len(pos) != 2:
        return None
    c = ord(pos[0].lower()) - ord('a')
    try:
        r = 8 - int(pos[1])
    except ValueError:
        return None
    if 0 <= r < 8 and 0 <= c < 8:
        return (r, c)
    return None

def main(): # Main game loop
    intro()
    brd = Board()
    while True:
        brd.show()
        if brd.checkmate(brd.turn):
            win = 'White' if brd.turn == 'black' else 'Black'
            print(f"Checkmate! {win} color wins!")
            break
        if brd.stalemate(brd.turn):
            print("Stalemate! The game results in a Draw.")
            break
        if brd.check(brd.turn):
            print(f"{brd.turn.capitalize()} is under check!")
        if brd.turn == 'white':
            m = input(f"{brd.turn.capitalize()}'s move (e.g., e2e4) or 'quit': ").strip().lower()
            if m == 'quit':
                print("Hope you enjoyed the game!")
                break
            if len(m) != 4:
                print("Not according to format i.e. 'a2a4'.")
                time.sleep(1.5)
                continue
            start = parse(m[:2])
            end = parse(m[2:])
            if start is None or end is None:
                print("Not a valid position (a1-h8).")
                time.sleep(1.5)
                continue
            p = brd.at(start)
            if p is None:
                print("No piece at start.")
                time.sleep(1.5)
                continue
            if not brd.move(start, end):
                print("Input a valid move.")
                time.sleep(1.5)
        else:
            print("Loading ...")
            m = comp_move(brd, 3)
            if m is None:
                print("No further moves found. Game over.")
                break
            start, end = m
            brd.move(start, end, 'Q', True)
            def pos_str(pos):
                r, c = pos
                return f"{chr(c+97)}{8-r}"
            print(f"AI move: {pos_str(start)}{pos_str(end)}")
            time.sleep(1.5)

if __name__ == "__main__":
    main()