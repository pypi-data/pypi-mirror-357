from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QDoubleSpinBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from database import Database
from windows.styles import BTN_MAIN, BTN_DANGER, CARD_STYLE
from windows.ui_utils import make_button, CardWidget, generic_form_dialog

class MaterialProductsDialog(QDialog):
    def __init__(self, products, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Где используется материал")
        self.resize(400, 300)
        layout = QVBoxLayout()
        table = QTableWidget(len(products), 2)
        table.setHorizontalHeaderLabels(["Название продукции", "Артикул"])
        for row_idx, (name, article) in enumerate(products):
            table.setItem(row_idx, 0, QTableWidgetItem(str(name)))
            table.setItem(row_idx, 1, QTableWidgetItem(str(article)))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(table)
        self.setLayout(layout)

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
            # Получаем все нужные поля для карточки, defect_percent из material_types
            rows = self.db.execute_query('''
                SELECT m.material_id, m.name, mt.name, m.unit_price, m.stock_qty, m.min_qty, m.package_qty, ut.name, mt.defect_percent
                FROM materials m
                LEFT JOIN material_types mt ON m.material_type_id = mt.material_type_id
                LEFT JOIN unit_types ut ON m.unit_type_id = ut.unit_type_id
            ''')
            # Фильтрация
            if filter_val:
                rows = [r for r in rows if filter_val.lower() in r[1].lower()]
            # Сортировка
            if sort_index == 1:
                rows = sorted(rows, key=lambda x: x[8])  # по дефектности
            elif sort_index == 2:
                rows = sorted(rows, key=lambda x: x[1].lower())  # по названию
            for row in rows:
                self.add_material_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.results_label.setText("")

    def add_material_card(self, row):
        (material_id, name, material_type, unit_price, stock_qty, min_qty, package_qty, unit_type, defect_percent) = row
        left_widgets = [
            QLabel(f"<b>{name}</b>"),
            QLabel(f"Тип: {material_type}"),
            QLabel(f"Остаток: {stock_qty} {unit_type}")
        ]
        right_widgets = []
        # "Где используется" доступно всем ролям
        right_widgets.append(make_button("Где используется", BTN_MAIN, lambda _, mid=material_id: self.show_material_products(mid)))
        if self.role in ("admin", "manager"):
            right_widgets.insert(0, make_button("Подробнее", BTN_MAIN, lambda _, mid=material_id: self.open_edit_material_dialog(mid)))
            right_widgets.append(make_button("Удалить", BTN_DANGER, lambda _, mid=material_id: self.delete_material_by_id(mid)))
        card = CardWidget(left_widgets, right_widgets, CARD_STYLE)
        card.setProperty('material_id', material_id)
        card.setProperty('selected', False)
        if self.role in ("admin", "manager"):
            card.mousePressEvent = lambda event, c=card: self.select_material_card(c)
        self.cards_layout.addWidget(card)

    def show_material_products(self, material_id):
        # Получить список продукции, где используется материал
        try:
            query = '''
                SELECT p.name, p.article
                FROM product_materials pm
                JOIN products p ON p.product_id = pm.product_id
                WHERE pm.material_id = ?
            '''
            products = self.db.execute_query(query, (material_id,))
            if not products:
                QMessageBox.information(self, "Где используется", "Материал не используется ни в одной продукции.")
                return
            dlg = MaterialProductsDialog(products, self)
            dlg.exec_()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка поиска продукции: {e}")

    def delete_material_by_id(self, material_id):
        # Проверяем, используется ли материал в продукции
        used = self.db.execute_query("SELECT COUNT(*) FROM product_materials WHERE material_id=?", (material_id,))[0][0]
        if used:
            QMessageBox.warning(self, "Удаление запрещено", "Материал используется в продукции и не может быть удалён.")
            return
        if QMessageBox.question(self, "Удалить", "Удалить выбранный материал?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.execute_non_query("DELETE FROM materials WHERE material_id=?", (material_id,))
                self.load_materials()
                QMessageBox.information(self, "Успех", "Материал удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def clear_filter(self):
        self.material_filter_input.clear()
        self.load_materials()

    def open_edit_material_dialog(self, material_id):
        if self.role not in ("admin", "manager"):
            return  # worker не может редактировать
        from windows.ui_utils import generic_form_dialog
        row = self.db.execute_query('''
            SELECT m.name, mt.name, m.unit_price, m.stock_qty, m.min_qty, m.package_qty, ut.name, mt.defect_percent, m.material_type_id, m.unit_type_id
            FROM materials m
            LEFT JOIN material_types mt ON m.material_type_id = mt.material_type_id
            LEFT JOIN unit_types ut ON m.unit_type_id = ut.unit_type_id
            WHERE m.material_id=?
        ''', (material_id,))[0]
        # Получаем списки типов и единиц
        material_types = self.db.execute_query("SELECT material_type_id, name, defect_percent FROM material_types")
        unit_types = self.db.execute_query("SELECT unit_type_id, name FROM unit_types")
        fields = [
            ("Название", "line", {"default": row[0]}),
            ("Тип", "combo", {"default": row[1], "items": [t[1] for t in material_types]}),
            ("Ед. изм.", "combo", {"default": row[6], "items": [u[1] for u in unit_types]}),
            ("Цена", "doublespin", {"default": float(row[2]), "min": 0, "max": 1e6, "decimals": 2}),
            ("Остаток", "doublespin", {"default": float(row[3]), "min": 0, "max": 1e6, "decimals": 2}),
            ("Мин. остаток", "doublespin", {"default": float(row[4]), "min": 0, "max": 1e6, "decimals": 2}),
            ("Упаковка", "doublespin", {"default": float(row[5]), "min": 0, "max": 1e6, "decimals": 2}),
            ("Дефектность (%)", "doublespin", {"default": float(row[7]), "min": 0, "max": 100, "decimals": 4})
        ]
        data = generic_form_dialog(self, "Редактировать материал", fields)
        if data:
            try:
                name = data['Название'].strip()
                material_type_id = next(t[0] for t in material_types if t[1] == data['Тип'])
                unit_type_id = next(u[0] for u in unit_types if u[1] == data['Ед. изм.'])
                unit_price = data['Цена']
                stock_qty = data['Остаток']
                min_qty = data['Мин. остаток']
                package_qty = data['Упаковка']
                defect_percent = data['Дефектность (%)']
                if not name:
                    QMessageBox.warning(self, "Ошибка", "Введите название материала")
                    return
                # Обновляем материал
                self.db.execute_non_query('''
                    UPDATE materials SET name=?, material_type_id=?, unit_price=?, stock_qty=?, min_qty=?, package_qty=?, unit_type_id=? WHERE material_id=?
                ''', (name, material_type_id, unit_price, stock_qty, min_qty, package_qty, unit_type_id, material_id))
                # Обновляем дефектность типа материала
                self.db.execute_non_query('''
                    UPDATE material_types SET defect_percent=? WHERE material_type_id=?
                ''', (defect_percent, material_type_id))
                self.load_materials()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")

    def open_create_material_window(self):
        if self.role not in ("admin", "manager"):
            return  # worker не может создавать
        from windows.ui_utils import generic_form_dialog
        material_types = self.db.execute_query("SELECT material_type_id, name FROM material_types")
        unit_types = self.db.execute_query("SELECT unit_type_id, name FROM unit_types")
        fields = [
            ("Название", "line", {"default": ""}),
            ("Тип", "combo", {"default": material_types[0][1] if material_types else "", "items": [t[1] for t in material_types]}),
            ("Ед. изм.", "combo", {"default": unit_types[0][1] if unit_types else "", "items": [u[1] for u in unit_types]}),
            ("Цена", "doublespin", {"default": 0, "min": 0, "max": 1e6, "decimals": 2}),
            ("Остаток", "doublespin", {"default": 0, "min": 0, "max": 1e6, "decimals": 2}),
            ("Мин. остаток", "doublespin", {"default": 0, "min": 0, "max": 1e6, "decimals": 2}),
            ("Упаковка", "doublespin", {"default": 0, "min": 0, "max": 1e6, "decimals": 2})
        ]
        data = generic_form_dialog(self, "Создать материал", fields)
        if data:
            try:
                name = data['Название'].strip()
                material_type_id = next(t[0] for t in material_types if t[1] == data['Тип'])
                unit_type_id = next(u[0] for u in unit_types if u[1] == data['Ед. изм.'])
                unit_price = data['Цена']
                stock_qty = data['Остаток']
                min_qty = data['Мин. остаток']
                package_qty = data['Упаковка']
                if not name:
                    QMessageBox.warning(self, "Ошибка", "Введите название материала")
                    return
                self.db.execute_non_query('''
                    INSERT INTO materials (name, material_type_id, unit_price, stock_qty, min_qty, package_qty, unit_type_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (name, material_type_id, unit_price, stock_qty, min_qty, package_qty, unit_type_id))
                self.load_materials()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка создания: {e}")

    def select_material_card(self, card):
        # Снимаем выделение со всех карточек
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                c.setStyleSheet(CARD_STYLE)
        # Выделяем выбранную карточку
        card.setProperty('selected', True)
        card.setStyleSheet(CARD_STYLE + "background-color: #e3f2fd;")
