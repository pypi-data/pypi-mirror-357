from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt
from database import Database
from windows.styles import BTN_DANGER, BTN_MAIN, CARD_STYLE
from windows.ui_utils import make_button, CardWidget

class UsersTab(QWidget):
    def __init__(self, parent=None, role='admin'):
        super().__init__(parent)
        self.db = Database()
        self.role = role  # admin, manager, worker
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация (поле ввода + выпадающий список ролей)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Фильтр по логину")
        self.filter_input.textChanged.connect(self.apply_user_filter)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("Роль:"))
        self.role_filter_combo = QComboBox()
        self.role_filter_combo.addItems(["Все", "admin", "manager", "worker"])
        self.role_filter_combo.currentIndexChanged.connect(self.apply_user_filter)
        filter_layout.addWidget(self.role_filter_combo)
        # Сортировка по роли
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.role_sort_combo = QComboBox()
        self.role_sort_combo.addItems([
            "Сначала админ",
            "Сначала менеджер",
            "Сначала сотрудник"
        ])
        self.role_sort_combo.currentIndexChanged.connect(self.apply_user_filter)
        filter_layout.addWidget(self.role_sort_combo)
        layout.addLayout(filter_layout)
        # Список пользователей (карточки)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container.setLayout(self.cards_layout)
        self.cards_container.setStyleSheet("background-color: #BBDCFA;")
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        # Кнопки создания, сброса фильтра и количество найденных справа
        btn_layout = QHBoxLayout()
        if self.role in ("admin", "manager"):
            create_btn = make_button("Создать пользователя", BTN_MAIN, lambda _: self.open_create_user_dialog())
            btn_layout.addWidget(create_btn)
        btn_layout.addStretch()
        self.clear_filter_button = make_button("Сбросить фильтр", BTN_MAIN, lambda _: self.clear_filter())
        btn_layout.addWidget(self.clear_filter_button)
        self.results_label = QLabel()
        btn_layout.addWidget(self.results_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.load_users()

    def clear_cards(self):
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def apply_user_filter(self):
        self.load_users(
            filter_val=self.filter_input.text(),
            role_filter=self.role_filter_combo.currentText()
        )

    def load_users(self, filter_val=None, role_filter="Все"):
        self.clear_cards()
        users = self.db.get_users()
        filtered = [row for row in users if (role_filter == "Все" or row[2] == role_filter) and (not filter_val or filter_val.lower() in row[1].lower())]
        sort_index = self.role_sort_combo.currentIndex() if hasattr(self, 'role_sort_combo') else 0
        if sort_index == 0:
            role_order = {'admin': 0, 'manager': 1, 'worker': 2}
        elif sort_index == 1:
            role_order = {'manager': 0, 'admin': 1, 'worker': 2}
        else:
            role_order = {'worker': 0, 'manager': 1, 'admin': 2}
        filtered.sort(key=lambda x: (role_order.get(x[2], 99), x[1].lower()))
        for row in filtered:
            self.add_user_card(row)
        self.results_label.setText(f"Найдено: {len(filtered)}")

    def add_user_card(self, row):
        user_id, username, role = row
        role_rus = {'admin': 'Админ', 'manager': 'Менеджер', 'worker': 'Сотрудник'}.get(role, role)
        left_widgets = [QLabel(f"<b>{username}</b>"), QLabel(f"Роль: {role_rus}")]
        right_widgets = []
        if self.role in ("admin", "manager"):
            role_combo = QComboBox(); role_combo.addItems(["admin", "manager", "worker"]); role_combo.setCurrentText(role)
            role_combo.currentIndexChanged.connect(lambda idx, uid=user_id, combo=role_combo: self.on_user_role_changed(uid, combo))
            role_combo.wheelEvent = lambda event: None
            right_widgets.append(role_combo)
            right_widgets.append(make_button("Удалить", BTN_DANGER, lambda _, uid=user_id: self.delete_user(uid)))
        card = CardWidget(left_widgets, right_widgets, CARD_STYLE)
        self.cards_layout.addWidget(card)

    def on_user_role_changed(self, user_id, combo):
        try:
            self.db.update_user_role(user_id, combo.currentText())
            QMessageBox.information(self, "Успех", "Роль изменена")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения роли: {e}")
        self.load_users()

    def get_selected_user_id(self):
        return next((card.property('user_id') for i in range(self.cards_layout.count())
                     if (card := self.cards_layout.itemAt(i).widget()) and card.property('selected')), None)

    def delete_user(self, user_id):
        if not user_id:
            QMessageBox.warning(self, "Ошибка", "Выделите пользователя для удаления")
            return
        if QMessageBox.question(self, "Удалить", "Удалить пользователя?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.delete_user(user_id)
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def open_create_user_dialog(self):
        from windows.ui_utils import generic_form_dialog
        fields = [
            ("Логин", "line", {"default": ""}),
            ("Пароль", "line", {"default": "", "password": True}),
            ("Роль", "combo", {"items": ["admin", "manager", "worker"]})
        ]
        data = generic_form_dialog(self, "Создать пользователя", fields)
        if data:
            try:
                self.db.register_user(data['Логин'], data['Пароль'], data['Роль'])
                self.load_users()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка создания: {e}")

    def clear_filter(self):
        self.filter_input.clear()
        self.role_filter_combo.setCurrentIndex(0)
        self.load_users()
