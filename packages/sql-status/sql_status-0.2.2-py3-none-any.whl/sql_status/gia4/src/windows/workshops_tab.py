from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox, QMessageBox, QDialog, QFormLayout, QScrollArea, QFrame, QComboBox
)
from PyQt5.QtCore import Qt
from database import Database
from windows.styles import BTN_CREATE, BTN_MAIN, BTN_DANGER, CARD_STYLE
from windows.ui_utils import make_button

class WorkshopsTab(QWidget):
    def __init__(self, parent=None, role='admin'):
        super().__init__(parent)
        self.db = Database()
        self.role = role
        self.init_ui()
        self.load_workshops()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация и сортировка
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Фильтр:'))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText('Название')
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        # Фильтр по типу
        filter_layout.addWidget(QLabel('Тип:'))
        self.type_combo = QComboBox()
        self.type_combo.addItem('Все')
        self.type_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.type_combo)
        filter_layout.addWidget(QLabel('Сортировка:'))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            'По умолчанию',
            'По названию',
            'По количеству сотрудников (убыв.)',
            'По количеству сотрудников (возр.)'
        ])
        self.sort_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.sort_combo)
        layout.addLayout(filter_layout)
        # Список цехов (карточки)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container.setLayout(self.cards_layout)
        self.cards_container.setStyleSheet("background-color: #BBDCFA;")
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        # Кнопки внизу: добавить цех слева, сбросить фильтр и количество результатов справа
        btn_layout = QHBoxLayout()
        if self.role != 'worker':
            self.add_btn = make_button('Добавить цех', BTN_CREATE, self.open_add_workshop_dialog)
            btn_layout.addWidget(self.add_btn)
        btn_layout.addStretch()
        self.clear_filter_button = make_button('Сбросить фильтр', BTN_MAIN, self.clear_filter)
        btn_layout.addWidget(self.clear_filter_button)
        self.results_label = QLabel()
        btn_layout.addWidget(self.results_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def toggle_sort_direction(self):
        self.sort_staff_desc = not self.sort_staff_desc
        self.sort_dir_btn.setText('↓' if self.sort_staff_desc else '↑')
        self.apply_filter()

    def apply_filter(self):
        self.load_workshops()

    def clear_cards(self):
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def update_type_filter(self):
        workshops = self.db.get_workshops()
        types = {t for _, _, t, _ in workshops if t}
        current = self.type_combo.currentText() if hasattr(self, 'type_combo') else 'Все'
        self.type_combo.blockSignals(True)
        self.type_combo.clear()
        self.type_combo.addItem('Все')
        for t in sorted(types):
            self.type_combo.addItem(t)
        idx = self.type_combo.findText(current)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.type_combo.blockSignals(False)

    def load_workshops(self):
        self.clear_cards()
        workshops = self.db.get_workshops()
        self.update_type_filter()
        filter_val = self.filter_input.text().lower() if hasattr(self, 'filter_input') else ''
        type_val = self.type_combo.currentText() if hasattr(self, 'type_combo') else 'Все'
        filtered = [row for row in workshops if (not filter_val or filter_val in row[1].lower()) and (type_val == 'Все' or (row[2] or '') == type_val)]
        sort_index = self.sort_combo.currentIndex() if hasattr(self, 'sort_combo') else 0
        if sort_index == 1:
            filtered.sort(key=lambda x: x[1].lower())
        elif sort_index == 2:
            filtered.sort(key=lambda x: x[3], reverse=True)
        elif sort_index == 3:
            filtered.sort(key=lambda x: x[3])
        for row in filtered:
            self.add_workshop_card(row)
        if hasattr(self, 'results_label'):
            self.results_label.setText(f"Найдено: {len(filtered)}")

    def add_workshop_card(self, row):
        workshop_id, name, type_, staff_count = row
        left_widgets = [QLabel(f"<b>{name}</b>"), QLabel(f"Тип: {type_}"), QLabel(f"Сотрудников: {staff_count}")]
        right_widgets = []
        if self.role != 'worker':
            right_widgets = [
                make_button("Редактировать", BTN_MAIN, lambda _, wid=workshop_id, n=name, t=type_, s=staff_count: self.open_edit_workshop_dialog(wid, n, t, s)),
                make_button("Удалить", BTN_DANGER, lambda _, wid=workshop_id: self.delete_workshop(wid))
            ]
        from windows.ui_utils import CardWidget
        card = CardWidget(left_widgets, right_widgets if right_widgets else None, CARD_STYLE)
        self.cards_layout.addWidget(card)

    def open_add_workshop_dialog(self):
        if self.role == 'worker':
            return
        from windows.ui_utils import generic_form_dialog
        # Список типов цехов (можно расширить при необходимости)
        workshop_types = ["Сборочный", "Механический", "Покрасочный", "Сварочный", "Тестовый"]
        fields = [
            ("Название", "line", {"default": ""}),
            ("Тип", "combo", {"items": workshop_types}),
            ("Кол-во сотрудников", "spin", {"default": 1, "min": 1, "max": 1000})
        ]
        data = generic_form_dialog(self, "Добавить цех", fields)
        if data:
            try:
                self.db.add_workshop(data['Название'], data['Тип'], data['Кол-во сотрудников'])
                self.load_workshops()
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка добавления: {e}')

    def open_edit_workshop_dialog(self, workshop_id, name, type_, staff_count):
        if self.role == 'worker':
            return
        from windows.ui_utils import generic_form_dialog
        fields = [
            ("Название", "line", {"default": name}),
            ("Тип", "line", {"default": type_}),
            ("Кол-во сотрудников", "spin", {"default": staff_count, "min": 1, "max": 9999})
        ]
        data = generic_form_dialog(self, "Редактировать цех", fields)
        if data:
            try:
                self.db.execute_non_query("UPDATE workshops SET name=?, type=?, staff_count=? WHERE workshop_id=?",
                                         (data['Название'], data['Тип'], data['Кол-во сотрудников'], workshop_id))
                self.load_workshops()
            except Exception as e:
                QMessageBox.warning(self, 'Ошибка', f'Ошибка редактирования: {e}')

    def clear_filter(self):
        self.filter_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        self.apply_filter()

    def delete_workshop(self, workshop_id):
        if self.role == 'worker':
            return
        product_workshops = self.db.execute_query("SELECT product_id FROM product_workshops WHERE workshop_id=?", (workshop_id,))
        if product_workshops:
            product_ids = list(set(pw[0] for pw in product_workshops))
            products = self.db.execute_query(
                f"SELECT product_id, name FROM products WHERE product_id IN ({','.join(['?']*len(product_ids))})",
                tuple(product_ids)
            ) if product_ids else []
            product_names = ', '.join(p[1] for p in products) if products else ''
            if products:
                msg = (f"Цех используется в следующих продуктах: {product_names}.\nУдалить все связанные продукты и связи вместе с цехом?\n(Все связанные product_workshops и продукты будут удалены)")
                if QMessageBox.question(self, "Цех используется", msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    try:
                        for product_id, _ in products:
                            self.db.execute_non_query("DELETE FROM product_workshops WHERE product_id=?", (product_id,))
                            self.db.execute_non_query("DELETE FROM products WHERE product_id=?", (product_id,))
                        self.db.execute_non_query("DELETE FROM workshops WHERE workshop_id=?", (workshop_id,))
                        self.load_workshops()
                        QMessageBox.information(self, "Успех", "Цех, связанные продукты и связи удалены")
                    except Exception as e:
                        QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")
            else:
                if QMessageBox.question(self, 'Удалить', 'Удалить выбранный цех и все связи?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    try:
                        self.db.execute_non_query("DELETE FROM product_workshops WHERE workshop_id=?", (workshop_id,))
                        self.db.execute_non_query("DELETE FROM workshops WHERE workshop_id=?", (workshop_id,))
                        self.load_workshops()
                        QMessageBox.information(self, 'Успех', 'Цех и связи удалены')
                    except Exception as e:
                        QMessageBox.warning(self, 'Ошибка', f'Ошибка удаления: {e}')
        else:
            if QMessageBox.question(self, 'Удалить', 'Удалить выбранный цех?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                try:
                    self.db.execute_non_query("DELETE FROM workshops WHERE workshop_id=?", (workshop_id,))
                    self.load_workshops()
                    QMessageBox.information(self, 'Успех', 'Цех удалён')
                except Exception as e:
                    QMessageBox.warning(self, 'Ошибка', f'Ошибка удаления: {e}')
