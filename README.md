# Python Chess Engine (Command-Line)

A fully custom chess game built in Python with no external chess libraries. This project is being developed as a learning and portfolio piece to demonstrate software engineering fundamentals, object-oriented programming, algorithm design, and AI implementation.

---

# Project Structure

The project is currently split into two main areas:

```
chess/
│   Core chess engine (final implementation)
│   - board logic
│   - piece movement rules
│   - game controller
│   - Chess bot integration
practice/
│   Experimental and learning code
│   - prototype chess engine
│   - feature testing
```

---

# Current Features

## Chess Engine Core

- 8x8 board representation using a 2D list
- Coordinate-based input system (e.g. e2 → e4)
- Turn-based system (White / Black)
- Piece ownership validation
- Legal move generation system
- Move highlighting on board using `#`
- Move listing in chess notation (e.g. A3, E5)
- Capture detection logic
- Fully implemented movement rules for:
  - Pawn
  - Rook
  - Knight
  - Queen
  - King
  - bishop

- Check detection
- Checkmate detection
- Stalemate detection
- Move undo system
- Castling
- En passant
- Pawn promotion

- Player vs AI mode
- Easy AI (less sophisticated greedy algorithm)
- Medium AI (material based evaluation with greedy algorithm)
- Hard AI (minimax search algorithm)
- Alpha-beta pruning optimization
- Save / load game state for bot games

---

# Practice / Development Work

The `practice/` folder contains:
- Early-stage full game prototype
- Feature testing environment
- Refactoring and design exploration

This is used to test features before integrating them into the main engine.

---

# Planned Features

## Additional Systems
- Game history tracking
- Chess clock / timer system


---

# Technologies Used

- Python
- Object-Oriented Programming (OOP)
- 2D array-based game state
- Algorithm design (move generation + validation)
- Git version control
- GitHub for remote repository management
- Visual Studio Code
- SQLite 3
- PySide6

---

# How to Run

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
```

Navigate into the project:

```bash
cd YOUR_REPO
```

Run the game:

```bash
python chess/main.py
```

---

# Development Philosophy

This project is being built incrementally, focusing on:

- Correct chess rules implementation first
- Clean separation of logic (board, pieces, game controller)
- Gradual refactoring from prototype → production structure
- Future expansion into AI-driven gameplay

---

# Current Status

The project is in active development.

---

# Author

Created by Tobit Vervat