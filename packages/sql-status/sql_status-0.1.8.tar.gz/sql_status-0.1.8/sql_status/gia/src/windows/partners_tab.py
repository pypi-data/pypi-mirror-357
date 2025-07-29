from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QSpinBox, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt
from database import Database

class PartnersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация (поле ввода + выпадающий список типов + фильтр и сортировка по рейтингу)
        filter_layout = QHBoxLayout()
        self.partner_filter_input = QLineEdit()
        self.partner_filter_input.setPlaceholderText("Фильтр по содержимому")
        self.partner_filter_input.textChanged.connect(self.apply_partner_filter)
        filter_layout.addWidget(QLabel("Фильтр:"))
        filter_layout.addWidget(self.partner_filter_input)
        filter_layout.addWidget(QLabel("Тип:"))
        self.partner_type_filter_combo = QComboBox()
        self.partner_type_filter_combo.addItem("Все типы")
        try:
            rows = self.db.get_partner_types()
            for row in rows:
                self.partner_type_filter_combo.addItem(row[0])
        except Exception:
            self.partner_type_filter_combo.addItem("Ошибка загрузки типов")
        self.partner_type_filter_combo.currentIndexChanged.connect(self.apply_partner_filter)
        filter_layout.addWidget(self.partner_type_filter_combo)
        filter_layout.addWidget(QLabel("Рейтинг:"))
        self.rating_filter_combo = QComboBox()
        self.rating_filter_combo.addItems(["Все", "0-5", "5-8", "8-10"])
        self.rating_filter_combo.currentIndexChanged.connect(self.apply_partner_filter)
        filter_layout.addWidget(self.rating_filter_combo)
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По ID (убыв.)", "По рейтингу (убыв.)", "По рейтингу (возр.)"])
        self.sort_combo.currentIndexChanged.connect(self.apply_partner_filter)
        filter_layout.addWidget(self.sort_combo)
        layout.addLayout(filter_layout)
        # Список партнёров (карточки)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container.setLayout(self.cards_layout)
        self.cards_container.setStyleSheet("background-color: #BBDCFA;")  # Фон контейнера карточек
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        # Кнопка удаления и сброса фильтра, количество найденных справа
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Удалить партнёра")
        delete_btn.clicked.connect(self.delete_selected_partner)
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
        self.load_partners()

    def clear_cards(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def apply_partner_filter(self):
        self.load_partners(
            filter_val=self.partner_filter_input.text(),
            type_filter=self.partner_type_filter_combo.currentText(),
            rating_filter=self.rating_filter_combo.currentText(),
            sort_index=self.sort_combo.currentIndex()
        )

    def load_partners(self, filter_col=None, filter_val=None, sort_col=None, sort_desc=False, type_filter="Все типы", rating_filter="Все", sort_index=0):
        self.clear_cards()
        try:
            rows = self.db.get_partners(
                filter_val=filter_val,
                type_filter=type_filter,
                rating_filter=rating_filter,
                sort_index=sort_index
            )
            for row in rows:
                self.add_partner_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.results_label.setText("")

    def add_partner_card(self, row):
        (partner_id, type_name, name, director, email, phone, address, inn, rating) = row
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: #fff;")
        card_layout = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel(f"<b>{type_name} | {name}</b>"))
        left.addWidget(QLabel(f"Директор: {director}"))
        left.addWidget(QLabel(f"Email: {email}"))
        left.addWidget(QLabel(f"Телефон: {phone}"))
        left.addWidget(QLabel(f"ИНН: {inn}"))
        left.addWidget(QLabel(f"Адрес: {address}"))
        card_layout.addLayout(left)
        # Справа: рейтинг и кнопка редактирования
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        rating_label = QLabel("Рейтинг:")
        rating_spin = QSpinBox()
        rating_spin.setMinimum(0)
        rating_spin.setMaximum(10)
        rating_spin.setValue(rating if rating is not None else 0)
        rating_spin.valueChanged.connect(lambda val, pid=partner_id: self.change_rating(pid, val))
        right.addWidget(rating_label)
        right.addWidget(rating_spin)
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(lambda _, pid=partner_id: self.open_edit_partner_dialog(pid))
        edit_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        right.addWidget(edit_btn)
        card_layout.addLayout(right)
        card.setLayout(card_layout)
        card.setProperty('partner_id', partner_id)
        card.setProperty('selected', False)
        card.mousePressEvent = lambda event, c=card: self.select_partner_card(c)
        self.cards_layout.addWidget(card)

    def select_partner_card(self, card):
        # Снять выделение со всех
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                c.setStyleSheet("background-color: #fff;")  # Всегда возвращаем белый фон
        # Выделить выбранную
        card.setProperty('selected', True)
        card.setStyleSheet("background-color: #e3f2fd;")

    def get_selected_partner_id(self):
        for i in range(self.cards_layout.count()):
            card = self.cards_layout.itemAt(i).widget()
            if card and card.property('selected'):
                return card.property('partner_id')
        return None

    def change_rating(self, partner_id, value):
        try:
            self.db.update_partner_rating(partner_id, value)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения рейтинга: {e}")

    def open_edit_partner_dialog(self, partner_id):
        dlg = QDialog(self)
        dlg.setWindowTitle("Редактировать партнёра")
        dlg.setMinimumWidth(500)
        form = QFormLayout(dlg)
        # Загрузка данных
        row = self.db.get_partner_by_id(partner_id)[0]
        type_name, name, director, email, phone, address, inn = row
        type_input = QLineEdit(type_name)
        name_input = QLineEdit(name)
        director_input = QLineEdit(director)
        email_input = QLineEdit(email)
        phone_input = QLineEdit(phone)
        address_input = QLineEdit(address)
        inn_input = QLineEdit(inn)
        form.addRow("Тип", type_input)
        form.addRow("Наименование", name_input)
        form.addRow("Директор", director_input)
        form.addRow("Email", email_input)
        form.addRow("Телефон", phone_input)
        form.addRow("Адрес", address_input)
        form.addRow("ИНН", inn_input)
        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        form.addRow(save_btn)
        def save():
            try:
                new_type = type_input.text().strip()
                type_id = self.db.get_partner_type_id(new_type)
                if not type_id:
                    type_id = self.db.add_partner_type(new_type)
                self.db.update_partner(
                    partner_id,
                    type_id,
                    name_input.text(),
                    director_input.text(),
                    email_input.text(),
                    phone_input.text(),
                    address_input.text(),
                    inn_input.text()
                )
                dlg.accept()
                self.load_partners()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")
        save_btn.clicked.connect(save)
        dlg.exec_()

    def delete_selected_partner(self):
        partner_id = self.get_selected_partner_id()
        if not partner_id:
            QMessageBox.warning(self, "Ошибка", "Выделите партнёра для удаления")
            return
        if QMessageBox.question(self, "Удалить", "Удалить выбранного партнёра?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.delete_partner(partner_id)
                self.load_partners()
                QMessageBox.information(self, "Успех", "Партнёр удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def clear_filter(self):
        self.partner_filter_input.clear()
        self.partner_type_filter_combo.setCurrentIndex(0)
        self.rating_filter_combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        self.load_partners()
