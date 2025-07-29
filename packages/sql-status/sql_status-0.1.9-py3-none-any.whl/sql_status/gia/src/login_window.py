from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox, QComboBox, QHBoxLayout
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
        self.partner_checkbox = QCheckBox("Регистрация как партнёр")
        self.partner_checkbox.stateChanged.connect(self.toggle_partner_fields)
        self.login_btn = QPushButton("Войти")
        self.register_btn = QPushButton("Регистрация")
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.partner_checkbox)
        # Partner fields (hidden by default)
        self.partner_fields = QWidget()
        pf_layout = QVBoxLayout()
        self.partner_type_combo = QComboBox()
        self.partner_type_combo.setPlaceholderText("Тип партнёра")
        self.load_partner_types()
        pf_layout.addWidget(QLabel("Тип партнёра"))
        pf_layout.addWidget(self.partner_type_combo)
        self.partner_name_input = QLineEdit()
        self.partner_name_input.setPlaceholderText("Наименование организации")
        pf_layout.addWidget(self.partner_name_input)
        self.director_input = QLineEdit()
        self.director_input.setPlaceholderText("ФИО директора")
        pf_layout.addWidget(self.director_input)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        pf_layout.addWidget(self.email_input)
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")
        pf_layout.addWidget(self.phone_input)
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Юридический адрес")
        pf_layout.addWidget(self.address_input)
        self.inn_input = QLineEdit()
        self.inn_input.setPlaceholderText("ИНН")
        pf_layout.addWidget(self.inn_input)
        self.partner_fields.setLayout(pf_layout)
        self.partner_fields.setVisible(False)
        layout.addWidget(self.partner_fields)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        self.setLayout(layout)
        self.login_btn.clicked.connect(self.try_login)
        self.register_btn.clicked.connect(self.try_register)

    def load_partner_types(self):
        self.partner_type_combo.clear()
        try:
            rows = self.db.execute_query("SELECT partner_type_id, name FROM partner_types")
            for row in rows:
                self.partner_type_combo.addItem(row[1], row[0])
        except Exception:
            self.partner_type_combo.addItem("Не удалось загрузить", -1)

    def toggle_partner_fields(self, state):
        self.partner_fields.setVisible(bool(state))
        self.adjustSize()

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
        if self.partner_checkbox.isChecked():
            # Partner registration
            partner_type_id = self.partner_type_combo.currentData()
            partner_name = self.partner_name_input.text()
            director = self.director_input.text()
            email = self.email_input.text()
            phone = self.phone_input.text()
            address = self.address_input.text()
            inn = self.inn_input.text()
            rating_val = 0  # Всегда 0 при регистрации
            if not partner_name or not partner_type_id or partner_type_id == -1:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля для партнёра")
                return
            try:
                # 1. Insert into partners
                query = """
                INSERT INTO partners (partner_type_id, name, director_name, email, phone, legal_address, inn, rating)
                OUTPUT INSERTED.partner_id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (partner_type_id, partner_name, director, email, phone, address, inn, rating_val)
                row = self.db.execute_insert_returning(query, params)
                partner_id = row[0] if row else None
                if not partner_id:
                    raise Exception("Не удалось создать организацию")
                # 2. Register user with partner_id and role 'partner'
                self.db.register_user(username, password, "partner", partner_id)
                QMessageBox.information(self, "Успех", "Партнёр и пользователь зарегистрированы")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка регистрации партнёра: {e}")
        else:
            # Internal user registration (manager by default)
            try:
                self.db.register_user(username, password, "manager")
                QMessageBox.information(self, "Успех", "Пользователь зарегистрирован")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка регистрации: {e}")