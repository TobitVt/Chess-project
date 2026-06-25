from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QSpinBox,
    QWidget,
    QFrame,
    QMessageBox
)

from PySide6.QtCore import Qt

from database import get_all_saved_games, load_saved_game


class MainMenuDialog(QDialog):
    def __init__(self, logged_in_player):
        super().__init__()

        self.logged_in_player = logged_in_player
        self.is_guest = logged_in_player["is_guest"]
        self.game_settings = None
        self.saved_games = []

        self.setWindowTitle("Chess - Main Menu")
        self.setFixedSize(720, 780)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(35, 35, 35, 35)
        main_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("menuCard")
        card.setFixedWidth(540)
        card.setStyleSheet("""
            QFrame#menuCard {
                background-color: #2E2E2E;
                border: 2px solid #5D4037;
                border-radius: 14px;
            }
        """)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(45, 35, 45, 35)
        card_layout.setSpacing(16)

        title = QLabel("New Game")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
            }
        """)

        profile_label = QLabel(f"Signed in as: {logged_in_player['username']}")
        profile_label.setAlignment(Qt.AlignCenter)
        profile_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #FBC02D;
            }
        """)

        mode_label = QLabel("Choose game mode:")
        mode_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
            }
        """)

        self.player_mode_radio = QRadioButton("Play against another player")
        self.bot_mode_radio = QRadioButton("Play against a bot")
        self.bot_mode_radio.setChecked(True)

        self.mode_group = QButtonGroup()
        self.mode_group.addButton(self.player_mode_radio)
        self.mode_group.addButton(self.bot_mode_radio)

        self.player_mode_radio.toggled.connect(self.update_visible_options)
        self.bot_mode_radio.toggled.connect(self.update_visible_options)

        # New/load section
        self.load_options_widget = QWidget()
        load_options_layout = QVBoxLayout()
        load_options_layout.setContentsMargins(0, 0, 0, 0)
        load_options_layout.setSpacing(10)

        self.new_game_radio = QRadioButton("Start new bot game")
        self.load_game_radio = QRadioButton("Load saved bot game")
        self.new_game_radio.setChecked(True)

        self.new_load_group = QButtonGroup()
        self.new_load_group.addButton(self.new_game_radio)
        self.new_load_group.addButton(self.load_game_radio)

        self.saved_games_combo = QComboBox()
        self.saved_games_combo.setFixedHeight(42)

        self.new_game_radio.toggled.connect(self.update_visible_options)
        self.load_game_radio.toggled.connect(self.update_visible_options)

        load_options_layout.addWidget(self.new_game_radio)
        load_options_layout.addWidget(self.load_game_radio)
        load_options_layout.addWidget(self.saved_games_combo)

        self.load_options_widget.setLayout(load_options_layout)

        # Bot options section
        self.bot_options_widget = QWidget()
        bot_options_layout = QVBoxLayout()
        bot_options_layout.setContentsMargins(0, 0, 0, 0)
        bot_options_layout.setSpacing(14)

        option_label_style = """
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: white;
            }
        """

        colour_row = QHBoxLayout()
        colour_row.setSpacing(18)

        colour_label = QLabel("Play as:")
        colour_label.setFixedWidth(130)
        colour_label.setStyleSheet(option_label_style)

        self.colour_combo = QComboBox()
        self.colour_combo.addItems(["White", "Black"])
        self.colour_combo.setFixedHeight(42)

        colour_row.addWidget(colour_label)
        colour_row.addWidget(self.colour_combo)

        difficulty_row = QHBoxLayout()
        difficulty_row.setSpacing(18)

        difficulty_label = QLabel("Bot difficulty:")
        difficulty_label.setFixedWidth(130)
        difficulty_label.setStyleSheet(option_label_style)

        self.difficulty_combo = QComboBox()
        self.difficulty_combo.addItems(["Easy", "Medium", "Hard"])
        self.difficulty_combo.setFixedHeight(42)

        difficulty_row.addWidget(difficulty_label)
        difficulty_row.addWidget(self.difficulty_combo)

        bot_options_layout.addLayout(colour_row)
        bot_options_layout.addLayout(difficulty_row)

        self.bot_options_widget.setLayout(bot_options_layout)

        # Time section
        self.time_label = QLabel("Time limit per player:")
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: white;
            }
        """)

        self.time_spinbox = QSpinBox()
        self.time_spinbox.setRange(1, 180)
        self.time_spinbox.setValue(10)
        self.time_spinbox.setSuffix(" minutes")
        self.time_spinbox.setFixedHeight(42)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)

        start_button = QPushButton("Start")
        cancel_button = QPushButton("Cancel")

        start_button.setFixedHeight(50)
        cancel_button.setFixedHeight(50)

        start_button.clicked.connect(self.start_game)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(start_button)
        button_layout.addWidget(cancel_button)

        # IMPORTANT: final widget order
        card_layout.addWidget(title)
        card_layout.addWidget(profile_label)

        card_layout.addSpacing(10)

        card_layout.addWidget(mode_label)
        card_layout.addWidget(self.player_mode_radio)
        card_layout.addWidget(self.bot_mode_radio)

        card_layout.addSpacing(10)

        card_layout.addWidget(self.load_options_widget)

        card_layout.addSpacing(5)

        card_layout.addWidget(self.bot_options_widget)

        card_layout.addSpacing(5)

        card_layout.addWidget(self.time_label)
        card_layout.addWidget(self.time_spinbox)

        card_layout.addSpacing(10)

        card_layout.addLayout(button_layout)

        card.setLayout(card_layout)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        self.load_saved_games_into_combo()
        self.update_visible_options()

    def load_saved_games_into_combo(self):
        self.saved_games_combo.clear()
        self.saved_games = []

        if self.is_guest:
            return

        player_id = self.logged_in_player["player_id"]
        self.saved_games = get_all_saved_games(player_id)

        if not self.saved_games:
            self.load_game_radio.setEnabled(False)
            self.saved_games_combo.setEnabled(False)
            self.saved_games_combo.addItem("No saved games found")
            return

        self.load_game_radio.setEnabled(True)
        self.saved_games_combo.setEnabled(True)

        for save in self.saved_games:
            save_id = save[0]

            loaded = load_saved_game(save_id)

            if loaded is None:
                self.saved_games_combo.addItem(f"Save {save_id}")
                continue

            saved_at = save[3] if len(save) > 3 else f"Save {save_id}"

            self.saved_games_combo.addItem(f"{saved_at} | turn: {loaded['current_turn']} | difficulty: {loaded['bot_difficulty']}")

    def update_visible_options(self):
        is_bot_mode = self.bot_mode_radio.isChecked()

        is_loading_game = (is_bot_mode and not self.is_guest and self.load_game_radio.isChecked() and self.load_game_radio.isEnabled())

        self.load_options_widget.setVisible(is_bot_mode and not self.is_guest)

        self.saved_games_combo.setVisible(is_loading_game)

        self.bot_options_widget.setVisible(is_bot_mode and not is_loading_game)

        self.time_label.setVisible(not is_loading_game)
        self.time_spinbox.setVisible(not is_loading_game)

    def start_game(self):
        minutes = self.time_spinbox.value()

        if self.player_mode_radio.isChecked():
            self.game_settings = {
                "mode": "player",
                "new_load": "new",
                "save_id": None,
                "human_colour": "white",
                "bot_colour": None,
                "bot_difficulty": None,
                "time_limit_seconds": minutes * 60
            }

            self.accept()
            return

        if (not self.is_guest and self.load_game_radio.isChecked() and self.load_game_radio.isEnabled()):
            selected_index = self.saved_games_combo.currentIndex()

            if selected_index < 0 or not self.saved_games:
                QMessageBox.warning(self, "No saved game", "No saved game was selected.")
                return

            save_id = self.saved_games[selected_index][0]

            self.game_settings = {
                "mode": "bot",
                "new_load": "load",
                "save_id": save_id,
                "human_colour": None,
                "bot_colour": None,
                "bot_difficulty": None,
                "time_limit_seconds": None
            }

            self.accept()
            return

        human_colour = self.colour_combo.currentText().lower()
        bot_colour = "black" if human_colour == "white" else "white"

        self.game_settings = {
            "mode": "bot",
            "new_load": "new",
            "save_id": None,
            "human_colour": human_colour,
            "bot_colour": bot_colour,
            "bot_difficulty": self.difficulty_combo.currentText().lower(),
            "time_limit_seconds": minutes * 60
        }

        self.accept()