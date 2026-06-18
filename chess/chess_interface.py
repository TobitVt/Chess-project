import sys

from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget
)

from PySide6.QtGui import QPalette, QColor

from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon

# stores path to piece images in global variable
ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets" / "pieces"

# create list of pieces in order
pieces = ["r", "n", "b", "q", "k", "b", "n", "r"]

# dictionary for mapping piece images to pieces on board
piece_images = {
    "K": "white_king.svg",
    "Q": "white_queen.svg",
    "R": "white_rook.svg",
    "B": "white_bishop.svg",
    "N": "white_knight.svg",
    "P": "white_pawn.svg",

    "k": "black_king.svg",
    "q": "black_queen.svg",
    "r": "black_rook.svg",
    "b": "black_bishop.svg",
    "n": "black_knight.svg",
    "p": "black_pawn.svg"
}


class ChessBoard(QMainWindow):
    def __init__(self):
        super().__init__()
        # create main window

        self.setWindowTitle("Chess board")
        self.resize(900, 900)

        main_container = QWidget()
        grid_layout = QGridLayout()

        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(20, 20, 20, 20)

        self.buttons = []

        for row in range(8):
            button_row = []

            for col in range(8):
                # create buttons
                block = QPushButton()
                block.setMinimumSize(100, 110)
                palette = block.palette()

                # gives alternating blocks different colours for checkered look
                if (col+row) % 2 == 0:
                    palette.setColor(QPalette.ColorRole.Button, QColor("#D7CCC8"))
                else:
                    palette.setColor(QPalette.ColorRole.Button, QColor("#5D4037"))

                # assign names/images to pieces on board

                # black pieces
                if row == 0:
                    piece = pieces[col]

                # black pawns
                elif row == 1:
                    piece = "p"

                # white pawns
                elif row == 6:
                    piece = "P"
                
                # white pieces
                elif row == 7:
                    piece = pieces[col].upper()

                # empty blocks
                else:
                    piece = "-"

                # assign icons to chess pieces on board
                if piece != "-":
                    image_path = ASSETS_PATH / piece_images[piece]
                    block.setIcon(QIcon(str(image_path)))
                    block.setIconSize(QSize(75, 75))

                # set colours of blocks
                block.setPalette(palette)

                # add widgets to grid and buttons to list
                grid_layout.addWidget(block, row, col)
                button_row.append(block)

            self.buttons.append(button_row)

        main_container.setLayout(grid_layout)
        self.setCentralWidget(main_container)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ChessBoard()
    window.show()

    sys.exit(app.exec())