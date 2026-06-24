APP_STYLE = """
QDialog, QMessageBox {
    background-color: #1E1E1E;
    color: white;
    font-family: Segoe UI, Arial;
}

QDialog QLabel,
QMessageBox QLabel {
    color: white;
    font-size: 15px;
}

QDialog QLineEdit,
QDialog QSpinBox,
QDialog QComboBox {
    background-color: #2E2E2E;
    color: white;
    border: 2px solid #5D4037;
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 15px;
}

QDialog QComboBox::drop-down {
    width: 32px;
    border-left: 1px solid #5D4037;
}

QDialog QComboBox::down-arrow {
    width: 12px;
    height: 12px;
}

QDialog QLineEdit:focus,
QDialog QSpinBox:focus,
QDialog QComboBox:focus {
    border: 2px solid #FBC02D;
}

QDialog QPushButton,
QMessageBox QPushButton {
    background-color: #5D4037;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 15px;
    font-weight: bold;
    min-height: 34px;
}

QDialog QPushButton:hover,
QMessageBox QPushButton:hover {
    background-color: #795548;
}

QDialog QPushButton:pressed,
QMessageBox QPushButton:pressed {
    background-color: #3E2723;
}

QComboBox QAbstractItemView {
    background-color: #2E2E2E;
    color: white;
    border: 2px solid #5D4037;
    selection-background-color: #FBC02D;
    selection-color: black;
}

QTabWidget::pane {
    border: 2px solid #5D4037;
    border-radius: 8px;
    padding: 6px;
}

QTabBar::tab {
    background-color: #2E2E2E;
    color: white;
    padding: 8px 16px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
}

QTabBar::tab:selected {
    background-color: #FBC02D;
    color: black;
    font-weight: bold;
}
"""