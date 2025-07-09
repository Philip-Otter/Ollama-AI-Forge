from __main__ import ForgePlugin
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import threading
import time
import random

class ChessForgeRelic(ForgePlugin):
    def __init__(self, app):
        super().__init__(app)
        self.name = "Chess Forge"
        self.description = "⚔️ Battle the AI in Chess or Checkers with divine strategy"
        self.config = {
            "difficulty": "Medium",
            "game_type": "Chess",
            "theme": "Classic",
            "animation_speed": 500,
            "show_hints": True,
            "auto_save": True
        }
        
        # Game state
        self.board = None
        self.current_player = "white"
        self.game_active = False
        self.selected_square = None
        self.ai_thinking = False
        self.move_history = []
        self.game_window = None
        self.board_buttons = {}
        
        # Chess pieces unicode
        self.chess_pieces = {
            'white': {'king': '♔', 'queen': '♕', 'rook': '♖', 'bishop': '♗', 'knight': '♘', 'pawn': '♙'},
            'black': {'king': '♚', 'queen': '♛', 'rook': '♜', 'bishop': '♝', 'knight': '♞', 'pawn': '♟'}
        }
        
        # Checkers pieces
        self.checker_pieces = {
            'white': {'man': '⚪', 'king': '👑'},
            'black': {'man': '⚫', 'king': '♛'}
        }

    def execute(self, **kwargs):
        try:
            self.game_window = self.create_themed_window("⚔️ Chess Forge Sanctum")
            self.game_window.geometry("1000x800")
            self.game_window.resizable(True, True)
            
            theme = self.get_theme()
            
            # Create main layout
            self._create_main_layout()
            self._create_settings_panel()
            self._create_game_board()
            self._create_control_panel()
            
            # Initialize game
            self._new_game()
            
            # Apply animations
            self._apply_forge_animations()
            
        except Exception as e:
            self.show_error("Chess Forge Failed", f"The sanctum could not be forged: {str(e)}")

    def _create_main_layout(self):
        """Create the main layout structure"""
        # Main container
        self.main_frame = ttk.Frame(self.game_window)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel for board
        self.board_frame = ttk.Frame(self.main_frame)
        self.board_frame.pack(side="left", fill="both", expand=True)
        
        # Right panel for controls
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side="right", fill="y", padx=(10, 0))

    def _create_settings_panel(self):
        """Create the settings panel with emojis"""
        settings_frame = ttk.LabelFrame(self.right_panel, text="⚙️ Divine Settings", padding=10)
        settings_frame.pack(fill="x", pady=(0, 10))
        
        # Game type selection
        ttk.Label(settings_frame, text="🎮 Game Type:").pack(anchor="w")
        self.game_type_var = tk.StringVar(value=self.config["game_type"])
        game_type_combo = ttk.Combobox(settings_frame, textvariable=self.game_type_var, 
                                      values=["Chess", "Checkers"], state="readonly")
        game_type_combo.pack(fill="x", pady=(0, 10))
        game_type_combo.bind('<<ComboboxSelected>>', self._on_game_type_change)
        
        # Difficulty selection
        ttk.Label(settings_frame, text="🔥 Difficulty:").pack(anchor="w")
        self.difficulty_var = tk.StringVar(value=self.config["difficulty"])
        difficulty_combo = ttk.Combobox(settings_frame, textvariable=self.difficulty_var,
                                       values=["Easy 😊", "Medium 😐", "Hard 😈", "Divine 👹"], state="readonly")
        difficulty_combo.pack(fill="x", pady=(0, 10))
        difficulty_combo.bind('<<ComboboxSelected>>', self._on_difficulty_change)
        
        # Theme selection
        ttk.Label(settings_frame, text="🎨 Theme:").pack(anchor="w")
        self.theme_var = tk.StringVar(value=self.config["theme"])
        theme_combo = ttk.Combobox(settings_frame, textvariable=self.theme_var,
                                  values=["Classic 🏛️", "Dark 🌑", "Fire 🔥", "Ice ❄️"], state="readonly")
        theme_combo.pack(fill="x", pady=(0, 10))
        theme_combo.bind('<<ComboboxSelected>>', self._on_theme_change)
        
        # Animation speed
        ttk.Label(settings_frame, text="⚡ Animation Speed:").pack(anchor="w")
        self.anim_speed_var = tk.IntVar(value=self.config["animation_speed"])
        anim_scale = ttk.Scale(settings_frame, from_=100, to=1000, variable=self.anim_speed_var,
                              orient="horizontal", command=self._on_anim_speed_change)
        anim_scale.pack(fill="x", pady=(0, 10))
        
        # Toggle options
        self.hints_var = tk.BooleanVar(value=self.config["show_hints"])
        hints_check = ttk.Checkbutton(settings_frame, text="💡 Show Hints", variable=self.hints_var)
        hints_check.pack(anchor="w", pady=(0, 5))
        
        self.autosave_var = tk.BooleanVar(value=self.config["auto_save"])
        autosave_check = ttk.Checkbutton(settings_frame, text="💾 Auto Save", variable=self.autosave_var)
        autosave_check.pack(anchor="w")

    def _create_game_board(self):
        """Create the game board"""
        # Board title
        self.board_title = ttk.Label(self.board_frame, text="⚔️ Chess Board", font=("Arial", 16, "bold"))
        self.board_title.pack(pady=(0, 10))
        
        # Board container
        self.board_container = ttk.Frame(self.board_frame)
        self.board_container.pack(expand=True)
        
        # Create 8x8 grid of buttons
        self.board_buttons = {}
        for row in range(8):
            for col in range(8):
                btn = tk.Button(self.board_container, width=6, height=3, font=("Arial", 16),
                               command=lambda r=row, c=col: self._on_square_click(r, c))
                btn.grid(row=row, column=col, padx=1, pady=1)
                self.board_buttons[(row, col)] = btn
        
        # Coordinate labels
        self._add_coordinate_labels()

    def _add_coordinate_labels(self):
        """Add coordinate labels around the board"""
        # File labels (a-h)
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        for i, file in enumerate(files):
            ttk.Label(self.board_container, text=file, font=("Arial", 10, "bold")).grid(row=8, column=i, pady=2)
        
        # Rank labels (1-8)
        for i in range(8):
            ttk.Label(self.board_container, text=str(8-i), font=("Arial", 10, "bold")).grid(row=i, column=8, padx=2)

    def _create_control_panel(self):
        """Create the control panel"""
        control_frame = ttk.LabelFrame(self.right_panel, text="🎮 Divine Controls", padding=10)
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Game controls
        ttk.Button(control_frame, text="🆕 New Game", command=self._new_game).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="🔄 Reset Board", command=self._reset_board).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="↩️ Undo Move", command=self._undo_move).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="💾 Save Game", command=self._save_game).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="📁 Load Game", command=self._load_game).pack(fill="x", pady=2)
        
        # Game info
        info_frame = ttk.LabelFrame(self.right_panel, text="📊 Game Info", padding=10)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.turn_label = ttk.Label(info_frame, text="Turn: White ⚪", font=("Arial", 12, "bold"))
        self.turn_label.pack(anchor="w")
        
        self.status_label = ttk.Label(info_frame, text="Status: Ready", font=("Arial", 10))
        self.status_label.pack(anchor="w")
        
        self.move_count_label = ttk.Label(info_frame, text="Moves: 0", font=("Arial", 10))
        self.move_count_label.pack(anchor="w")
        
        # AI thinking indicator
        self.ai_frame = ttk.Frame(info_frame)
        self.ai_frame.pack(fill="x", pady=(10, 0))
        
        self.ai_label = ttk.Label(self.ai_frame, text="🤖 AI Status:", font=("Arial", 10))
        self.ai_label.pack(anchor="w")
        
        self.ai_thinking_label = ttk.Label(self.ai_frame, text="Idle", font=("Arial", 10))
        self.ai_thinking_label.pack(anchor="w")

    def _new_game(self):
        """Start a new game"""
        self.game_active = True
        self.current_player = "white"
        self.selected_square = None
        self.move_history = []
        self.ai_thinking = False
        
        if self.config["game_type"] == "Chess":
            self._init_chess_board()
        else:
            self._init_checkers_board()
        
        self._update_board_display()
        self._update_game_info()
        self.show_toast("⚔️ New battle begins!")

    def _init_chess_board(self):
        """Initialize chess board"""
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

    def _init_checkers_board(self):
        """Initialize checkers board"""
        self.board = [
            ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
            ['b', '.', 'b', '.', 'b', '.', 'b', '.'],
            ['.', 'b', '.', 'b', '.', 'b', '.', 'b'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['w', '.', 'w', '.', 'w', '.', 'w', '.'],
            ['.', 'w', '.', 'w', '.', 'w', '.', 'w'],
            ['w', '.', 'w', '.', 'w', '.', 'w', '.']
        ]

    def _update_board_display(self):
        """Update the visual board display"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                btn = self.board_buttons[(row, col)]
                
                # Set piece text
                if piece == '.':
                    btn.config(text='')
                elif self.config["game_type"] == "Chess":
                    btn.config(text=self._get_chess_piece_symbol(piece))
                else:
                    btn.config(text=self._get_checker_piece_symbol(piece))
                
                # Set square color
                is_light = (row + col) % 2 == 0
                if self.selected_square == (row, col):
                    btn.config(bg="#FFD700")  # Gold for selected
                elif self._is_valid_move_highlight(row, col):
                    btn.config(bg="#90EE90")  # Light green for valid moves
                else:
                    btn.config(bg="#F0D0B0" if is_light else "#B08860")

    def _get_chess_piece_symbol(self, piece):
        """Get the unicode symbol for a chess piece"""
        if piece == '.':
            return ''
        
        color = 'white' if piece.isupper() else 'black'
        piece_type = piece.lower()
        
        type_map = {'k': 'king', 'q': 'queen', 'r': 'rook', 'b': 'bishop', 'n': 'knight', 'p': 'pawn'}
        return self.chess_pieces[color][type_map[piece_type]]

    def _get_checker_piece_symbol(self, piece):
        """Get the symbol for a checker piece"""
        if piece == '.':
            return ''
        elif piece == 'w':
            return self.checker_pieces['white']['man']
        elif piece == 'b':
            return self.checker_pieces['black']['man']
        elif piece == 'W':
            return self.checker_pieces['white']['king']
        elif piece == 'B':
            return self.checker_pieces['black']['king']
        return ''

    def _is_valid_move_highlight(self, row, col):
        """Check if square should be highlighted as valid move"""
        if not self.selected_square or not self.config["show_hints"]:
            return False
        
        return self._is_valid_move(self.selected_square[0], self.selected_square[1], row, col)

    def _on_square_click(self, row, col):
        """Handle square click"""
        if not self.game_active or self.ai_thinking:
            return
        
        if self.current_player == "black":  # AI's turn
            return
        
        if self.selected_square is None:
            # Select piece
            piece = self.board[row][col]
            if piece != '.' and self._is_player_piece(piece, self.current_player):
                self.selected_square = (row, col)
                self._update_board_display()
                self._animate_selection(row, col)
        else:
            # Try to move
            from_row, from_col = self.selected_square
            if (row, col) == self.selected_square:
                # Deselect
                self.selected_square = None
                self._update_board_display()
            elif self._is_valid_move(from_row, from_col, row, col):
                # Valid move
                self._make_move(from_row, from_col, row, col)
                self.selected_square = None
                self._update_board_display()
                self._end_turn()
            else:
                # Invalid move
                self.selected_square = None
                self._update_board_display()
                self.show_toast("❌ Invalid move!")

    def _is_player_piece(self, piece, player):
        """Check if piece belongs to player"""
        if piece == '.':
            return False
        
        if self.config["game_type"] == "Chess":
            return (player == "white" and piece.isupper()) or (player == "black" and piece.islower())
        else:
            return (player == "white" and piece.lower() == 'w') or (player == "black" and piece.lower() == 'b')

    def _is_valid_move(self, from_row, from_col, to_row, to_col):
        """Check if move is valid"""
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        if piece == '.':
            return False
        
        # Can't capture own piece
        if target != '.' and self._is_player_piece(target, self.current_player):
            return False
        
        if self.config["game_type"] == "Chess":
            return self._is_valid_chess_move(piece, from_row, from_col, to_row, to_col)
        else:
            return self._is_valid_checker_move(piece, from_row, from_col, to_row, to_col)

    def _is_valid_chess_move(self, piece, from_row, from_col, to_row, to_col):
        """Check if chess move is valid"""
        piece_type = piece.lower()
        row_diff = to_row - from_row
        col_diff = to_col - from_col
        
        # Basic piece movement rules
        if piece_type == 'p':  # Pawn
            direction = 1 if piece.islower() else -1
            if col_diff == 0:  # Forward move
                if row_diff == direction and self.board[to_row][to_col] == '.':
                    return True
                if row_diff == 2 * direction and (from_row == 1 or from_row == 6) and self.board[to_row][to_col] == '.':
                    return True
            elif abs(col_diff) == 1 and row_diff == direction:  # Capture
                return self.board[to_row][to_col] != '.'
        
        elif piece_type == 'r':  # Rook
            if row_diff == 0 or col_diff == 0:
                return self._is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece_type == 'n':  # Knight
            return (abs(row_diff) == 2 and abs(col_diff) == 1) or (abs(row_diff) == 1 and abs(col_diff) == 2)
        
        elif piece_type == 'b':  # Bishop
            if abs(row_diff) == abs(col_diff):
                return self._is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece_type == 'q':  # Queen
            if row_diff == 0 or col_diff == 0 or abs(row_diff) == abs(col_diff):
                return self._is_path_clear(from_row, from_col, to_row, to_col)
        
        elif piece_type == 'k':  # King
            return abs(row_diff) <= 1 and abs(col_diff) <= 1
        
        return False

    def _is_valid_checker_move(self, piece, from_row, from_col, to_row, to_col):
        """Check if checker move is valid"""
        row_diff = to_row - from_row
        col_diff = to_col - from_col
        
        # Must move diagonally
        if abs(row_diff) != abs(col_diff):
            return False
        
        # Regular piece movement
        if piece.lower() == piece:  # Not a king
            direction = 1 if piece == 'w' else -1
            if abs(row_diff) == 1:  # Simple move
                return row_diff == direction and self.board[to_row][to_col] == '.'
            elif abs(row_diff) == 2:  # Jump
                mid_row = from_row + row_diff // 2
                mid_col = from_col + col_diff // 2
                mid_piece = self.board[mid_row][mid_col]
                return (mid_piece != '.' and 
                        not self._is_player_piece(mid_piece, self.current_player) and
                        self.board[to_row][to_col] == '.')
        
        return False

    def _is_path_clear(self, from_row, from_col, to_row, to_col):
        """Check if path is clear for sliding pieces"""
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while current_row != to_row or current_col != to_col:
            if self.board[current_row][current_col] != '.':
                return False
            current_row += row_step
            current_col += col_step
        
        return True

    def _make_move(self, from_row, from_col, to_row, to_col):
        """Make a move on the board"""
        piece = self.board[from_row][from_col]
        captured = self.board[to_row][to_col]
        
        # Store move for history
        move = {
            'from': (from_row, from_col),
            'to': (to_row, to_col),
            'piece': piece,
            'captured': captured
        }
        
        # Handle special checker captures
        if self.config["game_type"] == "Checkers" and abs(to_row - from_row) == 2:
            mid_row = from_row + (to_row - from_row) // 2
            mid_col = from_col + (to_col - from_col) // 2
            move['jumped'] = (mid_row, mid_col)
            move['jumped_piece'] = self.board[mid_row][mid_col]
            self.board[mid_row][mid_col] = '.'
        
        # Make the move
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = '.'
        
        # Handle promotions
        if self.config["game_type"] == "Checkers":
            if piece == 'w' and to_row == 0:
                self.board[to_row][to_col] = 'W'
            elif piece == 'b' and to_row == 7:
                self.board[to_row][to_col] = 'B'
        
        self.move_history.append(move)
        self._animate_move(from_row, from_col, to_row, to_col)

    def _end_turn(self):
        """End current player's turn"""
        self.current_player = "black" if self.current_player == "white" else "white"
        self._update_game_info()
        
        if self.current_player == "black":
            # AI's turn
            self._ai_move()

    def _ai_move(self):
        """Handle AI move"""
        if not self.game_active:
            return
        
        self.ai_thinking = True
        self.ai_thinking_label.config(text="🤔 Thinking...")
        
        # Run AI in separate thread
        threading.Thread(target=self._ai_think, daemon=True).start()

    def _ai_think(self):
        """AI thinking process"""
        try:
            # Simulate thinking time based on difficulty
            difficulty_map = {"Easy": 0.5, "Medium": 1.5, "Hard": 3.0, "Divine": 5.0}
            base_time = difficulty_map.get(self.config["difficulty"].split()[0], 1.5)
            time.sleep(base_time + random.uniform(0, 1))
            
            # Get board state
            board_state = self._get_board_state_string()
            
            # Ask AI for move
            move = self._get_ai_move(board_state)
            
            # Schedule move execution on main thread
            self.game_window.after(0, lambda: self._execute_ai_move(move))
            
        except Exception as e:
            self.game_window.after(0, lambda: self._ai_error(str(e)))

    def _get_board_state_string(self):
        """Get board state as string for AI"""
        state = f"Game: {self.config['game_type']}\n"
        state += f"Turn: {self.current_player}\n"
        state += f"Difficulty: {self.config['difficulty']}\n\n"
        
        state += "Board (rows 0-7, cols a-h):\n"
        for i, row in enumerate(self.board):
            state += f"{i}: {' '.join(row)}\n"
        
        state += "\nPiece Legend:\n"
        if self.config["game_type"] == "Chess":
            state += "Uppercase = White, Lowercase = Black\n"
            state += "K/k=King, Q/q=Queen, R/r=Rook, B/b=Bishop, N/n=Knight, P/p=Pawn, .=Empty\n"
        else:
            state += "w=White man, b=Black man, W=White king, B=Black king, .=Empty\n"
        
        state += "\nPlease respond with your move in format: 'from_row,from_col to_row,to_col'"
        state += "\nExample: '1,0 to 3,0' or '6,4 to 4,4'"
        
        return state

    def _get_ai_move(self, board_state):
        """Get AI move using the app's AI"""
        try:
            # Use the forge's AI to get a move
            prompt = f"You are playing {self.config['game_type']} as black pieces. Analyze this board state and make the best move:\n\n{board_state}"
            
            # Add the message to conversation and get response
            response = self._query_ai(prompt)
            
            # Parse the response for a move
            move = self._parse_ai_response(response)
            return move
            
        except Exception as e:
            # Fallback to random move
            return self._get_random_move()

    def _query_ai(self, prompt):
        """Query the AI through the forge"""
        try:
            # Add message to conversation
            self.add_message(content=prompt, sender_id="ChessForge", role="user")
            
            # Pause conversation to get response
            self.pause_conversation()
            
            # Get the latest response
            history = self.get_history()
            if history:
                return history[-1].get('content', '')
            
            return ""
            
        except Exception as e:
            return ""
        finally:
            self.resume_conversation()

    def _parse_ai_response(self, response):
        """Parse AI response for move"""
        try:
            # Look for move pattern in response
            import re
            pattern = r'(\d+),(\d+)\s+to\s+(\d+),(\d+)'
            match = re.search(pattern, response)
            
            if match:
                from_row, from_col, to_row, to_col = map(int, match.groups())
                return (from_row, from_col, to_row, to_col)
            
            # Fallback to random move
            return self._get_random_move()
            
        except Exception:
            return self._get_random_move()

    def _get_random_move(self):
        """Get a random valid move"""
        valid_moves = []
        
        for from_row in range(8):
            for from_col in range(8):
                piece = self.board[from_row][from_col]
                if piece != '.' and self._is_player_piece(piece, self.current_player):
                    for to_row in range(8):
                        for to_col in range(8):
                            if self._is_valid_move(from_row, from_col, to_row, to_col):
                                valid_moves.append((from_row, from_col, to_row, to_col))
        
        if valid_moves:
            return random.choice(valid_moves)
        
        return None

    def _execute_ai_move(self, move):
        """Execute AI move"""
        self.ai_thinking = False
        self.ai_thinking_label.config(text="✅ Move made")
        
        if move is None:
            self.show_toast("🤖 AI surrenders!")
            self._end_game("Player wins!")
            return
        
        from_row, from_col, to_row, to_col = move
        
        # Validate move
        if not self._is_valid_move(from_row, from_col, to_row, to_col):
            # Try to get another move
            new_move = self._get_random_move()
            if new_move:
                self._execute_ai_move(new_move)
            else:
                self._end_game("Stalemate!")
            return
        
        # Make the move
        self._make_move(from_row, from_col, to_row, to_col)
        self._update_board_display()
        self._end_turn()

    def _ai_error(self, error):
        """Handle AI error"""
        self.ai_thinking = False
        self.ai_thinking_label.config(text="❌ Error")
        self.show_toast(f"AI Error: {error}")
        
        # Try random move
        move = self._get_random_move()
        if move:
            self._execute_ai_move(move)
        else:
            self._end_game("Game ended due to AI error")

    def _animate_selection(self, row, col):
        """Animate piece selection"""
        try:
            btn = self.board_buttons[(row, col)]
            self.app.animation_engine.coral_pulse(btn, "background", "#FFD700", "#FFA500", 
                                                 duration=self.config["animation_speed"])
        except Exception:
            pass

    def _animate_move(self, from_row, from_col, to_row, to_col):
        """Animate piece movement"""
        try:
            from_btn = self.board_buttons[(from_row, from_col)]
            to_btn = self.board_buttons[(to_row, to_col)]
            
            # Pulse the destination
            self.app.animation_engine.coral_pulse(to_btn, "background", "#90EE90", "#32CD32",
                                                 duration=self.config["animation_speed"])
            
            # Flash the source
            self.app.animation_engine.flesh_pulse(from_btn, "background")
            
        except Exception:
            pass

    def _update_game_info(self):
        """Update game information display"""
        player_emoji = "⚪" if self.current_player == "white" else "⚫"
        self.turn_label.config(text=f"Turn: {self.current_player.title()} {player_emoji}")
        self.move_count_label.config(text=f"Moves: {len(self.move_history)}")
        
        if self.game_active:
            self.status_label.config(text="Status: Active ⚔️")
        else:
            self.status_label.config(text="Status: Game Over 🏁")

    def _undo_move(self):
        """Undo the last move"""
        if not self.move_history or self.ai_thinking:
            return
        
        # Undo last move
        move = self.move_history.pop()
        
        # Restore piece positions
        self.board[move['from'][0]][move['from'][1]] = move['piece']
        self.board[move['to'][0]][move['to'][1]] = move['captured']
        
        # Restore jumped piece in checkers
        if 'jumped' in move:
            self.board[move['jumped'][0]][move['jumped'][1]] = move['jumped_piece']
        
        # Switch player
        self.current_player = "black" if self.current_player == "white" else "white"
        
        # Update display
        self._update_board_display()
        self._update_game_info()
        self.show_toast("↩️ Move undone")

    def _reset_board(self):
        """Reset the board to starting position"""
        self.move_history = []
        self.current_player = "white"
        self.selected_square = None
        self.ai_thinking = False
        
        if self.config["game_type"] == "Chess":
            self._init_chess_board()
        else:
            self._init_checkers_board()
        
        self._update_board_display()
        self._update_game_info()
        self.show_toast("🔄 Board reset")

    def _save_game(self):
        """Save current game state"""
        try:
            game_data = {
                'game_type': self.config['game_type'],
                'board': self.board,
                'current_player': self.current_player,
                'move_history': self.move_history,
                'config': self.config
            }
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Game"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(game_data, f, indent=2)
                self.show_toast("💾 Game saved!")
                
        except Exception as e:
            self.show_error("Save Failed", f"Could not save game: {str(e)}")

    def _load_game(self):
        """Load a saved game"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Game"
            )
            
            if filename:
                with open(filename, 'r') as f:
                    game_data = json.load(f)
                
                # Restore game state
                self.config.update(game_data.get('config', {}))
                self.board = game_data['board']
                self.current_player = game_data['current_player']
                self.move_history = game_data['move_history']
                self.game_active = True
                
                # Update UI
                self._update_board_display()
                self._update_game_info()
                self._update_settings_ui()
                self.show_toast("📁 Game loaded!")
                
        except Exception as e:
            self.show_error("Load Failed", f"Could not load game: {str(e)}")

    def _update_settings_ui(self):
        """Update settings UI to reflect loaded config"""
        self.game_type_var.set(self.config["game_type"])
        self.difficulty_var.set(self.config["difficulty"])
        self.theme_var.set(self.config["theme"])
        self.anim_speed_var.set(self.config["animation_speed"])
        self.hints_var.set(self.config["show_hints"])
        self.autosave_var.set(self.config["auto_save"])

    def _end_game(self, result):
        """End the game with result"""
        self.game_active = False
        self.ai_thinking = False
        self._update_game_info()
        
        messagebox.showinfo("Game Over", f"🏁 {result}")
        
        # Auto-save if enabled
        if self.config["auto_save"]:
            try:
                self._save_game()
            except Exception:
                pass

    def _apply_forge_animations(self):
        """Apply forge-style animations to UI"""
        try:
            theme = self.get_theme()
            
            # Animate the title
            self.app.animation_engine.coral_pulse(self.board_title, "foreground", 
                                                 theme.get("fg", "#f5f5f5"), 
                                                 theme.get("bot_a_color", "#ff4d4d"))
            
            # Animate control buttons periodically
            self.game_window.after(2000, self._periodic_animations)
            
        except Exception:
            pass

    def _periodic_animations(self):
        """Apply periodic animations"""
        try:
            if self.game_window and self.game_window.winfo_exists():
                theme = self.get_theme()
                
                # Animate AI thinking indicator if active
                if self.ai_thinking:
                    self.app.animation_engine.flesh_pulse(self.ai_thinking_label, "foreground")
                
                # Continue periodic animations
                self.game_window.after(3000, self._periodic_animations)
                
        except Exception:
            pass

    # Event handlers for settings
    def _on_game_type_change(self, event=None):
        """Handle game type change"""
        self.config["game_type"] = self.game_type_var.get()
        self.board_title.config(text=f"⚔️ {self.config['game_type']} Board")
        self._new_game()

    def _on_difficulty_change(self, event=None):
        """Handle difficulty change"""
        self.config["difficulty"] = self.difficulty_var.get().split()[0]
        self.show_toast(f"🔥 Difficulty: {self.config['difficulty']}")

    def _on_theme_change(self, event=None):
        """Handle theme change"""
        self.config["theme"] = self.theme_var.get().split()[0]
        self._apply_theme()

    def _on_anim_speed_change(self, value):
        """Handle animation speed change"""
        self.config["animation_speed"] = int(float(value))

    def _apply_theme(self):
        """Apply selected theme"""
        theme_colors = {
            "Classic": {"light": "#F0D0B0", "dark": "#B08860", "select": "#FFD700"},
            "Dark": {"light": "#404040", "dark": "#202020", "select": "#FF6B6B"},
            "Fire": {"light": "#FF6B35", "dark": "#8B0000", "select": "#FFD700"},
            "Ice": {"light": "#B0E0E6", "dark": "#4682B4", "select": "#00CED1"}
        }
        
        colors = theme_colors.get(self.config["theme"], theme_colors["Classic"])
        
        # Update board colors
        for row in range(8):
            for col in range(8):
                btn = self.board_buttons[(row, col)]
                if self.selected_square != (row, col) and not self._is_valid_move_highlight(row, col):
                    is_light = (row + col) % 2 == 0
                    btn.config(bg=colors["light"] if is_light else colors["dark"])

def load_plugin(app):
    """Load the Chess Forge plugin"""
    try:
        return ChessForgeRelic(app)
    except Exception as e:
        print(f"Heresy in Chess Forge load_plugin: {str(e)}")
        return None