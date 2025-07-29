from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from database import Database

class UsersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация (поле ввода + выпадающий список ролей)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Фильтр по содержимому")
        self.filter_input.textChanged.connect(self.apply_user_filter)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сначала админы", "Сначала менеджеры", "Сначала партнёры"])
        self.sort_combo.currentIndexChanged.connect(self.apply_user_filter)
        filter_layout.addWidget(self.sort_combo)
        filter_layout.addWidget(QLabel("Роль:"))
        self.role_filter_combo = QComboBox()
        self.role_filter_combo.addItems(["Все", "admin", "manager", "partner"])
        self.role_filter_combo.currentIndexChanged.connect(self.apply_user_filter)
        filter_layout.addWidget(self.role_filter_combo)
        layout.addLayout(filter_layout)
        # Список пользователей (карточки)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container.setLayout(self.cards_layout)
        self.cards_container.setStyleSheet("background-color: #BBDCFA;")  # Добавлено: фон контейнера пользователей
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        # Кнопка удаления, сброса фильтра и количество найденных справа
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Удалить пользователя")
        delete_btn.clicked.connect(self.delete_user)
        delete_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        self.clear_filter_button = QPushButton("Сбросить фильтр")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        self.clear_filter_button.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        btn_layout.addWidget(self.clear_filter_button)
        self.results_label = QLabel()
        btn_layout.addWidget(self.results_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.load_users()

    def clear_cards(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def apply_user_filter(self):
        filter_val = self.filter_input.text()
        role_val = self.role_filter_combo.currentText()
        self.load_users(filter_val=filter_val, role_filter=role_val)

    def load_users(self, filter_col=None, filter_val=None, sort_col=None, sort_desc=False, role_filter="Все"):
        self.clear_cards()
        query = """
        SELECT u.user_id, u.username, u.role, p.director_name, pt.name, u.partner_id
        FROM users u
        LEFT JOIN partners p ON u.partner_id = p.partner_id
        LEFT JOIN partner_types pt ON p.partner_type_id = pt.partner_type_id
        """
        col_map = {"ID": "u.user_id", "Логин": "u.username", "Роль": "u.role", "ФИО": "p.director_name"}
        params = []
        where_clauses = []
        if filter_val:
            where_clauses.append("(" + " OR ".join([f"{col} LIKE ?" for col in col_map.values()]) + ")")
            params.extend([f"%{filter_val}%"] * len(col_map))
        if role_filter and role_filter != "Все":
            where_clauses.append("u.role = ?")
            params.append(role_filter)
        where = ""
        if where_clauses:
            where = " WHERE " + " AND ".join(where_clauses)
        # Сортировка по выбору
        sort_index = self.sort_combo.currentIndex() if hasattr(self, 'sort_combo') else 0
        if sort_index == 0:
            order = " ORDER BY CASE u.role WHEN 'admin' THEN 0 WHEN 'manager' THEN 1 WHEN 'partner' THEN 2 ELSE 3 END, u.user_id DESC"
        elif sort_index == 1:
            order = " ORDER BY CASE u.role WHEN 'manager' THEN 0 WHEN 'admin' THEN 1 WHEN 'partner' THEN 2 ELSE 3 END, u.user_id DESC"
        else:
            order = " ORDER BY CASE u.role WHEN 'partner' THEN 0 WHEN 'admin' THEN 1 WHEN 'manager' THEN 2 ELSE 3 END, u.user_id DESC"
        full_query = query + where + order
        try:
            rows = self.db.execute_query(full_query, params) if params else self.db.execute_query(full_query)
            for row in rows:
                self.add_user_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.results_label.setText("")

    def add_user_card(self, row):
        (user_id, username, role, director_name, partner_type, partner_id) = row
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card_layout = QHBoxLayout()
        left = QVBoxLayout()
        # ФИО или роль
        if role == "admin":
            fio = "Админ"
            card.setProperty('role', 'admin')
            card.setStyleSheet("background-color: #ffe5e5;")
        elif role == "manager":
            fio = "Менеджер"
            card.setProperty('role', 'manager')
            card.setStyleSheet("background-color: #fffbe5;")
        else:
            fio = director_name or "Партнёр"
            card.setProperty('role', 'partner')
            card.setStyleSheet("background-color: #fff;")
        left.addWidget(QLabel(f"<b>{fio}</b>"))
        left.addWidget(QLabel(f"Логин: {username}"))
        if partner_type and partner_id:
            left.addWidget(QLabel(f"{partner_type} | {self.get_partner_name(partner_id)}"))
        card_layout.addLayout(left)
        # Справа выпадающий список ролей
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        role_combo = QComboBox()
        role_combo.addItems(["admin", "manager", "partner"])
        role_combo.setCurrentText(role)
        role_combo.currentIndexChanged.connect(lambda idx, uid=user_id, combo=role_combo: self.on_user_role_changed(uid, combo))
        role_combo.wheelEvent = lambda event: None
        right.addWidget(role_combo)
        card_layout.addLayout(right)
        card.setLayout(card_layout)
        card.setProperty('user_id', user_id)
        card.setProperty('selected', False)
        card.mousePressEvent = lambda event, c=card: self.select_user_card(c)
        self.cards_layout.addWidget(card)

    def set_card_role_color(self, card):
        role = card.property('role')
        if role == 'admin':
            card.setStyleSheet("background-color: #ffe5e5;")
        elif role == 'manager':
            card.setStyleSheet("background-color: #fffbe5;")
        else:
            card.setStyleSheet("background-color: #fff;")

    def select_user_card(self, card):
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                self.set_card_role_color(c)
        card.setProperty('selected', True)
        # Голубая заливка поверх цвета роли
        card.setStyleSheet(card.styleSheet() + "background-color: #BBDCFA;")

    def on_user_role_changed(self, user_id, combo):
        try:
            new_role = combo.currentText()
            query = "UPDATE users SET role=? WHERE user_id=?"
            self.db.execute_non_query(query, (new_role, user_id))
            QMessageBox.information(self, "Успех", "Роль изменена")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения роли: {e}")
        self.load_users()

    def get_selected_user_id(self):
        for i in range(self.cards_layout.count()):
            card = self.cards_layout.itemAt(i).widget()
            if card and card.property('selected'):
                return card.property('user_id')
        return None

    def delete_user(self):
        user_id = self.get_selected_user_id()
        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Выделите пользователя для удаления")
            return
        if QMessageBox.question(self, "Удалить", "Удалить пользователя?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                query = "DELETE FROM users WHERE user_id=?"
                self.db.execute_non_query(query, (user_id,))
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def get_partner_name(self, partner_id):
        try:
            row = self.db.execute_query("SELECT name FROM partners WHERE partner_id=?", (partner_id,))
            if row:
                return row[0][0]
        except Exception:
            pass
        return ""

    def clear_filter(self):
        self.filter_input.clear()
        self.role_filter_combo.setCurrentIndex(0)
        if hasattr(self, 'sort_combo'):
            self.sort_combo.setCurrentIndex(0)
        self.load_users()
