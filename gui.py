import pygame
import sys
from board import Board
from minimax import GomokuAI
import time
import os

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (205, 133, 63)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)

class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.is_hovered = False

    def draw(self, screen, font):
        color = self.color if not self.is_hovered else GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class GomokuGUI:
    def __init__(self):
        pygame.init()
        
        # Window settings
        self.cell_size = 40
        self.margin = 40
        self.board_size = 15
        self.window_size = self.cell_size * (self.board_size - 1) + self.margin * 2
        self.info_height = 60
        self.screen = pygame.display.set_mode((self.window_size, self.window_size + self.info_height))
        pygame.display.set_caption("Gomoku")
        
        # Game state
        self.board = Board()
        self.ai = GomokuAI(max_depth=4)
        self.game_over = False
        self.winner = 0
        self.message = ""
        self.player_color = 1
        self.selecting_color = True
        
        # Font settings
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Buttons
        button_width = 120
        button_height = 40
        button_margin = 20
        center_x = self.window_size // 2
        center_y = self.window_size // 2
        
        self.black_button = Button(
            center_x - button_width - button_margin,
            center_y - button_height // 2,
            button_width,
            button_height,
            "Play Black",
            WHITE
        )
        
        self.white_button = Button(
            center_x + button_margin,
            center_y - button_height // 2,
            button_width,
            button_height,
            "Play White",
            WHITE
        )

    def draw_board(self):
        """Draw the game board"""
        self.screen.fill(BROWN)
        
        # Draw grid lines
        for i in range(self.board_size):
            pygame.draw.line(self.screen, BLACK,
                           (self.margin, self.margin + i * self.cell_size),
                           (self.window_size - self.margin, self.margin + i * self.cell_size))
            pygame.draw.line(self.screen, BLACK,
                           (self.margin + i * self.cell_size, self.margin),
                           (self.margin + i * self.cell_size, self.window_size - self.margin))
        
        # Draw pieces
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board.board[i][j] != 0:
                    color = BLACK if self.board.board[i][j] == 1 else WHITE
                    pos = (self.margin + j * self.cell_size,
                          self.margin + i * self.cell_size)
                    pygame.draw.circle(self.screen, color, pos, self.cell_size // 2 - 2)
                    if self.board.board[i][j] == -1:
                        pygame.draw.circle(self.screen, BLACK, pos, self.cell_size // 2 - 2, 1)
        
        # Draw info area
        info_rect = pygame.Rect(0, self.window_size, self.window_size, self.info_height)
        pygame.draw.rect(self.screen, WHITE, info_rect)
        
        if self.selecting_color:
            self.draw_color_selection()
        else:
            if self.game_over:
                text = self.font.render(self.message, True, RED)
                restart_text = self.small_font.render("Click to restart", True, BLUE)
                
                text_rect = text.get_rect(center=(self.window_size // 2, self.window_size + 20))
                restart_rect = restart_text.get_rect(center=(self.window_size // 2, self.window_size + 45))
                
                self.screen.blit(text, text_rect)
                self.screen.blit(restart_text, restart_rect)
            else:
                if self.message:
                    text = self.font.render(self.message, True, BLACK)
                    text_rect = text.get_rect(center=(self.window_size // 2, self.window_size + 20))
                    self.screen.blit(text, text_rect)
                
                turn_text = self.small_font.render(
                    f"{'Your' if self.board.current_player == self.player_color else 'AI'} turn",
                    True, BLACK
                )
                turn_rect = turn_text.get_rect(center=(self.window_size // 2, self.window_size + 45))
                self.screen.blit(turn_text, turn_rect)
        
        pygame.display.flip()

    def draw_color_selection(self):
        """Draw color selection screen"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.window_size, self.window_size))
        overlay.fill(WHITE)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title
        text = self.font.render("Choose your color", True, BLACK)
        text_rect = text.get_rect(center=(self.window_size // 2, self.window_size // 2 - 60))
        self.screen.blit(text, text_rect)
        
        # Draw buttons
        self.black_button.draw(self.screen, self.font)
        self.white_button.draw(self.screen, self.font)

    def get_board_pos(self, mouse_pos):
        """Convert mouse position to board position"""
        x, y = mouse_pos
        i = round((y - self.margin) / self.cell_size)
        j = round((x - self.margin) / self.cell_size)
        
        if 0 <= i < self.board_size and 0 <= j < self.board_size:
            return i, j
        return None

    def run(self):
        """Run the game loop"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if self.selecting_color:
                    self.black_button.handle_event(event)
                    self.white_button.handle_event(event)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.black_button.is_hovered:
                            self.player_color = 1
                            self.selecting_color = False
                        elif self.white_button.is_hovered:
                            self.player_color = -1
                            self.selecting_color = False
                            self.ai_move()
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.game_over:
                            self.selecting_color = True
                            self.reset_game()
                        elif self.board.current_player == self.player_color:
                            mouse_pos = pygame.mouse.get_pos()
                            board_pos = self.get_board_pos(mouse_pos)
                            
                            if board_pos and self.board.is_valid_move(board_pos):
                                self.board.make_move(board_pos)
                                self.check_game_state()
                                
                                if not self.game_over:
                                    self.ai_move()
            
            self.draw_board()
            pygame.time.wait(50)

    def ai_move(self):
        """AI makes a move"""
        self.message = "AI thinking..."
        self.draw_board()
        
        start_time = time.time()
        ai_move = self.ai.get_move(self.board)
        end_time = time.time()
        
        if ai_move:
            self.board.make_move(ai_move)
            self.message = f"AI move time: {end_time - start_time:.1f}s"
            self.check_game_state()

    def check_game_state(self):
        """Check game state"""
        winner = self.board.check_win()
        if winner != 0:
            self.game_over = True
            self.winner = winner
            win_text = "Black" if winner == 1 else "White"
            self.message = f"{win_text} wins!"
        elif len(self.board.get_valid_moves()) == 0:
            self.game_over = True
            self.message = "Draw!"

    def reset_game(self):
        """Reset the game"""
        self.board = Board()
        self.game_over = False
        self.winner = 0
        self.message = ""
        if self.player_color == -1 and not self.selecting_color:
            self.ai_move()

if __name__ == "__main__":
    game = GomokuGUI()
    game.run()
