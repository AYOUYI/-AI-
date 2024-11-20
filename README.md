# Gomoku AI

A Gomoku (Five in a Row) game with AI opponent using Minimax algorithm.

## Features

- Play against AI with Minimax algorithm
- Choose to play as Black or White
- Simple and intuitive graphical interface
- Restart game and switch colors anytime

## Installation

### Option 1: Run from Source Code (requires Python)

1. Install required packages:
```bash
pip install numpy pygame
```

2. Run the game:
```bash
python gui.py
```

### Option 2: Standalone Windows Executable

1. Download `Gomoku.exe` from the `dist` folder
2. Double-click to run (no Python installation required)

## How to Play

1. Start the game and choose your color:
   - Click "Play Black" to play first
   - Click "Play White" to play second

2. During your turn:
   - Click on any intersection to place your piece
   - Wait for AI to make its move

3. Game Controls:
   - Click anywhere after game ends to start a new game
   - Choose your color again for the new game

## Technical Details

- Built with Python and Pygame
- AI uses Minimax algorithm with Alpha-Beta pruning
- Search depth of 4 moves for balanced performance
