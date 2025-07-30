from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
from database import Database
from windows.styles import BTN_MAIN, BTN_DANGER, CARD_STYLE
from windows.ui_utils import make_button, CardWidget, generic_form_dialog

class MaterialsTab(QWidget):
    def __init__(self, parent=None, role='admin'):
        super().__init__(parent)
        self.db = Database()
        self.role = role  # admin, manager, worker
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация (по имени)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.material_filter_input = QLineEdit()
        self.material_filter_input.setPlaceholderText("Фильтр по названию")
        self.material_filter_input.textChanged.connect(self.apply_material_filter)
        filter_layout.addWidget(self.material_filter_input)
        # Сортировка
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "По умолчанию",
            "Сначала дефектность",
            "Сначала название"
        ])
        self.sort_combo.currentIndexChanged.connect(self.apply_material_filter)
        filter_layout.addWidget(self.sort_combo)
        layout.addLayout(filter_layout)
        # Список материалов (карточки)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container.setLayout(self.cards_layout)
        self.cards_container.setStyleSheet("background-color: #BBDCFA;")
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        # Кнопки создания/удаления и сброса фильтра, количество найденных справа
        btn_layout = QHBoxLayout()
        if self.role in ("admin", "manager"):
            create_btn = QPushButton("Создать материал")
            create_btn.clicked.connect(self.open_create_material_window)
            create_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            btn_layout.addWidget(create_btn)
        btn_layout.addStretch()
        self.clear_filter_button = QPushButton("Сбросить фильтр")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        self.clear_filter_button.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        btn_layout.addWidget(self.clear_filter_button)
        self.results_label = QLabel()
        btn_layout.addWidget(self.results_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.load_materials()

    def clear_cards(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def apply_material_filter(self):
        self.load_materials(
            filter_val=self.material_filter_input.text(),
            sort_index=self.sort_combo.currentIndex()
        )

    def load_materials(self, filter_val=None, sort_index=0):
        self.clear_cards()
        try:
            rows = self.db.get_materials()
            # Фильтрация
            if filter_val:
                rows = [r for r in rows if filter_val.lower() in r[1].lower()]
            # Сортировка
            if sort_index == 1:
                rows = sorted(rows, key=lambda x: x[2])  # по дефектности
            elif sort_index == 2:
                rows = sorted(rows, key=lambda x: x[1].lower())  # по названию
            for row in rows:
                self.add_material_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.results_label.setText("")

    def add_material_card(self, row):
        (material_id, name, defect_percent) = row
        left_widgets = [
            QLabel(f"<b>{name}</b>"),
            QLabel(f"Дефектность: {defect_percent}%")
        ]
        right_widgets = []
        if self.role in ("admin", "manager"):
            right_widgets.append(make_button("Редактировать", BTN_MAIN, lambda _, mid=material_id: self.open_edit_material_dialog(mid)))
            right_widgets.append(make_button("Удалить", BTN_DANGER, lambda _, mid=material_id: self.delete_material_by_id(mid)))
        card = CardWidget(left_widgets, right_widgets, CARD_STYLE)
        card.setProperty('material_id', material_id)
        card.setProperty('selected', False)
        if self.role in ("admin", "manager"):
            card.mousePressEvent = lambda event, c=card: self.select_material_card(c)
        self.cards_layout.addWidget(card)

    def select_material_card(self, card):
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                c.setStyleSheet(CARD_STYLE)
        card.setProperty('selected', True)
        card.setStyleSheet(CARD_STYLE + "background-color: #e3f2fd;")

    def get_selected_material_id(self):
        for i in range(self.cards_layout.count()):
            card = self.cards_layout.itemAt(i).widget()
            if card and card.property('selected'):
                return card.property('material_id')
        return None

    def open_edit_material_dialog(self, material_id):
        from windows.ui_utils import generic_form_dialog
        row = self.db.execute_query("SELECT name, defect_percent FROM materials WHERE material_id=?", (material_id,))[0]
        fields = [
            ("Название", "line", {"default": row[0]}),
            ("Дефектность (%)", "doublespin", {"default": float(row[1]), "min": 0, "max": 100, "decimals": 5})
        ]
        data = generic_form_dialog(self, "Редактировать материал", fields)
        if data:
            try:
                new_name = data['Название']
                new_defect = data['Дефектность (%)']
                self.db.execute_non_query("UPDATE materials SET name=?, defect_percent=? WHERE material_id=?", (new_name, new_defect, material_id))
                self.load_materials()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")

    def open_create_material_window(self):
        from windows.ui_utils import generic_form_dialog
        fields = [
            ("Название", "line", {"default": ""}),
            ("Дефектность (%)", "doublespin", {"default": 0, "min": 0, "max": 100, "decimals": 4})
        ]
        data = generic_form_dialog(self, "Создать материал", fields)
        if data:
            try:
                name = data['Название'].strip()
                defect = data['Дефектность (%)']
                if not name:
                    QMessageBox.warning(self, "Ошибка", "Введите название материала")
                    return
                self.db.execute_non_query("INSERT INTO materials (name, defect_percent) VALUES (?, ?)", (name, defect))
                self.load_materials()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка создания: {e}")

    def delete_material_by_id(self, material_id):
        # Логика удаления материала по id (аналогично delete_selected_material, но без выделения)
        # Проверяем, есть ли продукты с этим материалом
        products = self.db.execute_query("SELECT product_id, name FROM products WHERE material_id=?", (material_id,))
        if products:
            product_names = ', '.join([p[1] for p in products])
            msg = (f"Материал используется в следующих продуктах: {product_names}.\n"
                   "Удалить все связанные продукты вместе с материалом?\n"
                   "(Все связанные цеха продукции также будут удалены)")
            reply = QMessageBox.question(self, "Материал используется", msg, QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    for product_id, _ in products:
                        self.db.execute_non_query("DELETE FROM product_workshops WHERE product_id=?", (product_id,))
                        self.db.execute_non_query("DELETE FROM products WHERE product_id=?", (product_id,))
                    self.db.execute_non_query("DELETE FROM materials WHERE material_id=?", (material_id,))
                    self.load_materials()
                    if hasattr(self.parent(), 'products_tab'):
                        self.parent().products_tab.load_products()
                    QMessageBox.information(self, "Успех", "Материал и связанные продукты удалены")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")
            else:
                return
        else:
            if QMessageBox.question(self, "Удалить", "Удалить выбранный материал?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                try:
                    self.db.execute_non_query("DELETE FROM materials WHERE material_id=?", (material_id,))
                    self.load_materials()
                    if hasattr(self.parent(), 'products_tab'):
                        self.parent().products_tab.load_products()
                    QMessageBox.information(self, "Успех", "Материал удалён")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def clear_filter(self):
        self.material_filter_input.clear()
        self.load_materials()
