# Python Chess Engine (Command-Line)

A fully custom chess game built in Python with no external chess libraries. This project is being developed as a learning and portfolio piece to demonstrate software engineering fundamentals, object-oriented programming, algorithm design, and future AI implementation.

---

# Project Structure

The project is currently split into two main areas:

```
chess/
│   Core chess engine (final implementation)
│   - board logic
│   - piece movement rules
│   - game controller
│   - future AI integration
│
practice/
│   Experimental and learning code
│   - prototype chess engine
│   - feature testing
│   - timer experiments
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

---

# Practice / Development Work

The `practice/` folder contains:
- Early-stage full game prototype (~700 lines)
- Feature testing environment
- Timer experimentation (in progress)
- Refactoring and design exploration

This is used to test features before integrating them into the main engine.

---

# Planned Features

## Game Features
- Castling
- En passant
- Pawn promotion
- Save / load game state

## AI System
- Player vs AI mode
- Easy AI (random move selection)
- Medium AI (material-based evaluation)
- Hard AI (minimax search algorithm)
- Alpha-beta pruning optimization

## Additional Systems
- Chess clock / timer system
- Game history tracking


---

# Technologies Used

- Python
- Object-Oriented Programming (OOP)
- 2D array-based game state
- Algorithm design (move generation + validation)
- Git version control
- GitHub for remote repository management
- Visual Studio Code

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

Core movement logic and board representation are complete. The next phases include rule completion (check/checkmate) and AI integration.

---

# Author

Created by Tobit Vervat