from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database import Database

class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.db = Database()
        self.on_login_success = on_login_success
        self.init_ui()
        self.setMinimumSize(400, 250)
        self.resize(420, 320)

    def init_ui(self):
        self.setWindowTitle("Авторизация")
        layout = QVBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Войти")
        self.login_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        self.register_btn = QPushButton("Регистрация")
        self.register_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        self.setLayout(layout)
        self.login_btn.clicked.connect(self.try_login)
        self.register_btn.clicked.connect(self.try_register)
        # Глобальный стиль для окна
        self.setStyleSheet("""
            * {
                font-family: 'Bahnschrift Light SemiCondensed';
                font-size: 13pt;
            }
        """)

    def try_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        user = self.db.get_user_by_credentials(username, password)
        if user:
            self.close()
            self.on_login_success(user)
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def try_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        # Проверка на уникальность логина
        existing = self.db.get_single_value("SELECT COUNT(*) FROM users WHERE username=?", (username,))
        if existing and existing > 0:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином уже существует")
            return
        try:
            self.db.register_user(username, password, "worker")
            QMessageBox.information(self, "Успех", "Пользователь зарегистрирован с ролью 'worker'")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка регистрации: {e}")