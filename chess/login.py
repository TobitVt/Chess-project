from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QStackedWidget,
    QWidget
)

from database import (
    create_player,
    get_player,
    hash_password,
    verify_login
)


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.player_info = None

        self.setWindowTitle("Chess Login")
        self.setFixedSize(420, 300)

        main_layout = QVBoxLayout()

        title = QLabel("Welcome to Chess")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
            }
        """)

        self.stack = QStackedWidget()

        self.choice_page = self.create_choice_page()
        self.login_page = self.create_login_page()
        self.signup_page = self.create_signup_page()

        self.stack.addWidget(self.choice_page)
        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.signup_page)

        main_layout.addWidget(title)
        main_layout.addWidget(self.stack)

        self.setLayout(main_layout)

    def create_choice_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        login_button = QPushButton("Log In")
        signup_button = QPushButton("Sign Up")
        guest_button = QPushButton("Continue as Guest")

        login_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_page))

        signup_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.signup_page))

        guest_button.clicked.connect(self.continue_as_guest)

        layout.addWidget(login_button)
        layout.addWidget(signup_button)
        layout.addWidget(guest_button)

        page.setLayout(layout)
        return page

    def create_login_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Log in to your account")

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Log In")
        back_button = QPushButton("Back")

        login_button.clicked.connect(self.handle_login)
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.choice_page))

        layout.addWidget(label)
        layout.addWidget(self.login_username)
        layout.addWidget(self.login_password)
        layout.addWidget(login_button)
        layout.addWidget(back_button)

        page.setLayout(layout)
        return page

    def create_signup_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Create a new account")

        self.signup_username = QLineEdit()
        self.signup_username.setPlaceholderText("Username")

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.Password)

        self.signup_confirm = QLineEdit()
        self.signup_confirm.setPlaceholderText("Confirm password")
        self.signup_confirm.setEchoMode(QLineEdit.Password)

        signup_button = QPushButton("Sign Up")
        back_button = QPushButton("Back")

        signup_button.clicked.connect(self.handle_signup)
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.choice_page))

        layout.addWidget(label)
        layout.addWidget(self.signup_username)
        layout.addWidget(self.signup_password)
        layout.addWidget(self.signup_confirm)
        layout.addWidget(signup_button)
        layout.addWidget(back_button)

        page.setLayout(layout)
        return page

    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()

        if username == "" or password == "":
            QMessageBox.warning(self, "Missing details", "Please enter both username and password.")
            return

        user_info = get_player(username)

        if user_info is None:
            switch_to_signup = QMessageBox.question(self, "User not found", "User not found in database.\n\nContinue to sign up instead?")

            if switch_to_signup == QMessageBox.Yes:
                self.signup_username.setText(username)
                self.signup_password.clear()
                self.signup_confirm.clear()
                self.stack.setCurrentWidget(self.signup_page)

            return

        player = verify_login(username, password)

        if player is None:
            QMessageBox.warning(self, "Incorrect password", "Password incorrect. Please try again.")

            self.login_password.clear()
            self.login_password.setFocus()
            return

        self.player_info = player

        QMessageBox.information(self, "Login successful", "Log in successful, welcome back.")

        self.accept()

    def handle_signup(self):
        username = self.signup_username.text().strip()
        password = self.signup_password.text()
        confirm_password = self.signup_confirm.text()

        if username == "" or password == "" or confirm_password == "":
            QMessageBox.warning(self, "Missing details", "Please fill in all fields.")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Passwords do not match", "Please make sure both passwords are the same.")
            return

        hashed_password = hash_password(password)

        new_id = create_player(username, hashed_password)

        if new_id is None:
            switch_to_login = QMessageBox.question(self, "Player already exists", "Player already exists.\n\nContinue to log in instead?")

            if switch_to_login == QMessageBox.Yes:
                self.login_username.setText(username)
                self.login_password.clear()
                self.stack.setCurrentWidget(self.login_page)

            return

        self.player_info = {
            "player_id": new_id,
            "username": username,
            "elo": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "is_guest": False
        }

        QMessageBox.information(self, "Sign up successful", "Sign up successful, welcome.")

        self.accept()

    def continue_as_guest(self):
        self.player_info = {
            "player_id": None,
            "username": "guest",
            "elo": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "is_guest": True
        }

        QMessageBox.information(self, "Guest mode", "Welcome to the chess app. Enjoy and good luck.")

        self.accept()