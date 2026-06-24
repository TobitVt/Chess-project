from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QSpinBox,
    QWidget,
    QFrame
)

from PySide6.QtCore import Qt


class MainMenuDialog(QDialog):
    def __init__(self, logged_in_player):
        super().__init__()

        self.logged_in_player = logged_in_player
        self.game_settings = None

        self.setWindowTitle("Chess - Main Menu")
        self.setFixedSize(640, 680)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        card = QFrame()
        card.setObjectName("menuCard")
        card.setStyleSheet("""
            QFrame#menuCard {
                background-color: #2E2E2E;
                border: 2px solid #5D4037;
                border-radius: 14px;
                padding: 18px;
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(18)

        title = QLabel("New Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: white;
                padding-bottom: 10px;
            }
        """)

        username = self.logged_in_player["username"]

        profile_label = QLabel(f"Signed in as: {username}")
        profile_label.setAlignment(Qt.AlignCenter)
        profile_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #FBC02D;
                padding-bottom: 12px;
            }
        """)

        # Game mode selection
        mode_label = QLabel("Choose game mode:")
        mode_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")

        self.player_mode_radio = QRadioButton("Play against another player")
        self.bot_mode_radio = QRadioButton("Play against a bot")

        self.bot_mode_radio.setChecked(True)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.player_mode_radio)
        self.mode_group.addButton(self.bot_mode_radio)

        self.player_mode_radio.toggled.connect(self.update_visible_options)
        self.bot_mode_radio.toggled.connect(self.update_visible_options)

        # Bot settings
        self.bot_options_widget = QWidget()
        self.bot_options_widget.setFixedHeight(155)

        bot_options_layout = QVBoxLayout()
        bot_options_layout.setContentsMargins(0, 18, 0, 24)
        bot_options_layout.setSpacing(18)

        option_label_style = """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: white;
            }
        """

        # Row 1: colour
        colour_row = QHBoxLayout()
        colour_row.setSpacing(18)

        colour_label = QLabel("Play as:")
        colour_label.setFixedWidth(120)
        colour_label.setAlignment(Qt.AlignVCenter)
        colour_label.setStyleSheet(option_label_style)

        self.colour_combo = QComboBox()
        self.colour_combo.addItems(["White", "Black"])
        self.colour_combo.setFixedHeight(44)
        self.colour_combo.setMinimumWidth(260)

        colour_row.addWidget(colour_label)
        colour_row.addWidget(self.colour_combo)

        # Row 2: difficulty
        difficulty_row = QHBoxLayout()
        difficulty_row.setSpacing(18)

        difficulty_label = QLabel("Bot difficulty:")
        difficulty_label.setFixedWidth(120)
        difficulty_label.setAlignment(Qt.AlignVCenter)
        difficulty_label.setStyleSheet(option_label_style)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_combo.setFixedHeight(44)
        self.difficulty_combo.setMinimumWidth(260)

        difficulty_row.addWidget(difficulty_label)
        difficulty_row.addWidget(self.difficulty_combo)

        bot_options_layout.addLayout(colour_row)
        bot_options_layout.addLayout(difficulty_row)

        self.bot_options_widget.setLayout(bot_options_layout)

        # Time limit, always visible
        time_label = QLabel("Time limit per player:")
        time_label.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")

        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(1, 180)
        self.time_spinbox.setValue(10)
        self.time_spinbox.setSuffix(" minutes")

        self.time_spinbox.setMinimumHeight(42)
        self.time_spinbox.setMinimumWidth(300)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(14)

        start_button = QPushButton("Start")
        cancel_button = QPushButton("Cancel")

        start_button.setMinimumHeight(42)
        cancel_button.setMinimumHeight(42)

        start_button.clicked.connect(self.start_game)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(start_button)
        button_layout.addWidget(cancel_button)

        card_layout.addWidget(title)
        card_layout.addWidget(profile_label)

        card_layout.addWidget(mode_label)
        card_layout.addWidget(self.player_mode_radio)
        card_layout.addWidget(self.bot_mode_radio)

        card_layout.addWidget(self.bot_options_widget)

        card_layout.addWidget(time_label)
        card_layout.addWidget(self.time_spinbox)

        card_layout.addLayout(button_layout)

        card.setLayout(card_layout)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        self.update_visible_options()

    def update_visible_options(self):
        self.bot_options_widget.setVisible(self.bot_mode_radio.isChecked())

    def start_game(self):
        minutes = self.time_spinbox.value()

        if self.player_mode_radio.isChecked():
            self.game_settings = {
                "mode": "player",
                "human_colour": "white",
                "bot_colour": None,
                "bot_difficulty": None,
                "time_limit_seconds": minutes * 60
            }

        else:
            human_colour = self.colour_combo.currentText().lower()

            bot_colour = (
                "black" if human_colour == "white" else "white"
            )

            self.game_settings = {
                "mode": "bot",
                "human_colour": human_colour,
                "bot_colour": bot_colour,
                "bot_difficulty": self.difficulty_combo.currentText().lower(),
                "time_limit_seconds": minutes * 60
            }

        self.accept()