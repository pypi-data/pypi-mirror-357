from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QDoubleSpinBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from database import Database
from windows.styles import BTN_MAIN, BTN_DANGER, CARD_STYLE
from windows.ui_utils import make_button, CardWidget

class ProductsTab(QWidget):
    def __init__(self, parent=None, role='admin'):
        super().__init__(parent)
        self.db = Database()
        self.role = role  # admin, manager, worker
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация (поле ввода + выпадающий список типов)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.product_filter_input = QLineEdit()
        self.product_filter_input.setPlaceholderText("Фильтр по содержимому")
        self.product_filter_input.textChanged.connect(self.apply_product_filter)
        filter_layout.addWidget(self.product_filter_input)
        filter_layout.addWidget(QLabel("Тип:"))
        self.product_type_filter_combo = QComboBox()
        self.product_type_filter_combo.addItem("Все типы")
        try:
            rows = self.db.get_product_types()
            for row in rows:
                self.product_type_filter_combo.addItem(row[0])
        except Exception:
            self.product_type_filter_combo.addItem("Ошибка загрузки типов")
        self.product_type_filter_combo.currentIndexChanged.connect(self.apply_product_filter)
        filter_layout.addWidget(self.product_type_filter_combo)
        # Добавляем сортировку
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "По умолчанию",
            "Сначала мин. цена",
            "Сначала макс. цена"
        ])
        self.sort_combo.currentIndexChanged.connect(self.apply_product_filter)
        filter_layout.addWidget(self.sort_combo)
        layout.addLayout(filter_layout)
        # Список товаров (карточки)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container.setLayout(self.cards_layout)
        self.cards_container.setStyleSheet("background-color: #BBDCFA;")  # Фон контейнера карточек
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        # Кнопки создания/удаления и сброса фильтра, количество найденных справа
        btn_layout = QHBoxLayout()
        if self.role in ("admin", "manager"):
            create_btn = make_button("Создать товар", BTN_MAIN, lambda _: self.open_create_product_window())
            delete_btn = make_button("Удалить товар", BTN_MAIN, lambda _: self.delete_selected_product())
            btn_layout.addWidget(create_btn)
            btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        self.clear_filter_button = make_button("Сбросить фильтр", BTN_MAIN, lambda _: self.clear_filter())
        btn_layout.addWidget(self.clear_filter_button)
        self.results_label = QLabel()
        btn_layout.addWidget(self.results_label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.load_products()

    def clear_cards(self):
        # Очищает все карточки из layout
        for i in reversed(range(self.cards_layout.count())):
            widget = self.cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def apply_product_filter(self):
        # Универсальный вызов фильтрации и сортировки
        self.load_products(
            filter_val=self.product_filter_input.text(),
            type_filter=self.product_type_filter_combo.currentText(),
            sort_index=self.sort_combo.currentIndex()
        )

    def load_products(self, filter_col=None, filter_val=None, sort_col=None, sort_desc=False, type_filter="Все типы", sort_index=0):
        self.clear_cards()
        try:
            rows = self.db.get_products(
                filter_val=filter_val,
                type_filter=type_filter,
                sort_index=sort_index
            )
            for row in rows:
                self.add_product_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки данных: {e}")
            self.results_label.setText("")

    def add_product_card(self, row):
        # row: (product_id, name, type_name, article, min_price, coefficient)
        product_id, name, type_name, article, min_price, coefficient = row
        material_row = self.db.execute_query("SELECT material FROM products WHERE product_id=?", (product_id,))
        material_name = material_row[0][0] if material_row and material_row[0][0] else "-"
        left_widgets = [
            QLabel(f"<b>{name}</b>"),
            QLabel(f"Тип: {type_name}"),
            QLabel(f"Материал: {material_name}"),
            QLabel(f"Артикул: {article}"),
            QLabel(f"Время изготовления: {self.db.calculate_total_production_time(product_id) or 0} ч")
        ]
        right_widgets = [
            QLabel(f"Коэффициент: {coefficient}"),
            QLabel(f"Мин. цена: {min_price} руб."),
        ]
        # Только для admin/manager — кнопки редактирования и удаления
        if self.role in ("admin", "manager"):
            right_widgets.append(make_button("Редактировать", BTN_MAIN, lambda _, pid=product_id: self.open_edit_product_dialog(pid)))
        # Кнопка "Цеха продукции" всегда доступна
        right_widgets.append(make_button("Цеха продукции", BTN_MAIN, lambda _, pid=product_id: self.open_product_workshops_dialog(pid)))
        card = CardWidget(left_widgets, right_widgets, CARD_STYLE)
        card.setProperty('product_id', product_id)
        card.setProperty('selected', False)
        if self.role in ("admin", "manager"):
            card.mousePressEvent = lambda event, c=card: self.select_product_card(c)
        self.cards_layout.addWidget(card)

    def open_product_workshops_dialog(self, product_id):
        from windows.product_workshops_dialog import ProductWorkshopsDialog
        dlg = ProductWorkshopsDialog(product_id, self, role=self.role)
        dlg.exec_()
        self.load_products()

    def get_selected_product_id(self):
        # Возвращает product_id выделенной карточки или None
        return next((card.property('product_id') for i in range(self.cards_layout.count())
                     if (card := self.cards_layout.itemAt(i).widget()) and card.property('selected')), None)

    def select_product_card(self, card):
        # Универсальный обработчик выделения карточки
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                c.setStyleSheet(CARD_STYLE)
        card.setProperty('selected', True)
        card.setStyleSheet(CARD_STYLE + "background-color: #e3f2fd;")

    def open_edit_product_dialog(self, product_id):
        from windows.ui_utils import generic_form_dialog
        # Получить данные продукта
        row = self.db.execute_query("SELECT product_id, name, product_type_id, article, material_id, min_price, (SELECT coefficient FROM product_types WHERE product_type_id=products.product_type_id) FROM products WHERE product_id=?", (product_id,))
        if not row:
            QMessageBox.warning(self, "Ошибка", "Продукт не найден")
            return
        product = row[0]
        # Получить типы и материалы
        type_rows = self.db.get_product_types_with_id()
        material_rows = self.db.execute_query("SELECT material_id, name FROM materials")
        fields = [
            ("Наименование", "line", {"default": product[1]}),
            ("Тип", "combo", {"items": [t[1] for t in type_rows], "default": next((t[1] for t in type_rows if t[0]==product[2]), "")} ),
            ("Материал", "combo", {"items": [m[1] for m in material_rows], "default": next((m[1] for m in material_rows if m[0]==product[4]), "")} ),
            ("Артикул", "line", {"default": product[3]}),
            ("Мин. цена", "doublespin", {"default": float(product[5]) if product[5] is not None else 0, "min": 0, "max": 9999999, "decimals": 2}),
            ("Коэффициент", "doublespin", {"default": float(product[6]) if product[6] is not None else 0, "min": 0, "max": 9999999, "decimals": 2})
        ]
        data = generic_form_dialog(self, "Редактировать товар", fields)
        if data:
            try:
                # Получить id типа и материала по имени
                type_id = next((t[0] for t in type_rows if t[1]==data['Тип']), None)
                material_id = next((m[0] for m in material_rows if m[1]==data['Материал']), None)
                self.db.execute_non_query(
                    "UPDATE products SET name=?, product_type_id=?, product_type=?, material_id=?, material=?, article=?, min_price=? WHERE product_id=?",
                    (data['Наименование'], type_id, data['Тип'], material_id, data['Материал'], data['Артикул'], data['Мин. цена'], product_id)
                )
                self.db.update_product_type_coefficient(type_id, data['Коэффициент'])
                self.load_products()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")

    def open_create_product_window(self):
        from windows.ui_utils import generic_form_dialog
        type_rows = self.db.get_product_types_with_id()
        material_rows = self.db.execute_query("SELECT material_id, name FROM materials")
        fields = [
            ("Наименование", "line", {"default": ""}),
            ("Тип", "combo", {"items": [t[1] for t in type_rows]}),
            ("Материал", "combo", {"items": [m[1] for m in material_rows]}),
            ("Артикул", "line", {"default": ""}),
            ("Мин. цена", "doublespin", {"default": 0, "min": 0, "max": 9999999, "decimals": 2}),
            ("Коэффициент", "doublespin", {"default": 0, "min": 0, "max": 9999999, "decimals": 2})
        ]
        data = generic_form_dialog(self, "Создать товар", fields)
        if data:
            try:
                type_id = next((t[0] for t in type_rows if t[1]==data['Тип']), None)
                material_id = next((m[0] for m in material_rows if m[1]==data['Материал']), None)
                self.db.execute_non_query(
                    "INSERT INTO products (name, product_type_id, product_type, material_id, material, article, min_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (data['Наименование'], type_id, data['Тип'], material_id, data['Материал'], data['Артикул'], data['Мин. цена'])
                )
                self.db.update_product_type_coefficient(type_id, data['Коэффициент'])
                row = self.db.execute_query("SELECT product_id FROM products WHERE article=?", (data['Артикул'],))
                if row:
                    from windows.product_workshops_dialog import ProductWorkshopsDialog
                    product_id = row[0][0]
                    dlg2 = ProductWorkshopsDialog(product_id, self)
                    if dlg2.exec_() == dlg2.Accepted:
                        self.load_products()
                else:
                    self.load_products()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка создания: {e}")

    def change_coefficient(self, product_id, value):
        try:
            type_id = self.db.execute_query("SELECT product_type_id FROM products WHERE product_id=?", (product_id,))[0][0]
            self.db.execute_non_query("UPDATE product_types SET coefficient=? WHERE product_type_id=?", (value, type_id))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения коэффициента: {e}")

    def change_min_price(self, product_id, value):
        try:
            self.db.execute_non_query("UPDATE products SET min_price=? WHERE product_id=?", (value, product_id))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения мин. цены: {e}")

    def delete_selected_product(self):
        if self.role not in ("admin", "manager"):
            return
        product_id = self.get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self, "Ошибка", "Выделите товар для удаления")
            return
        if QMessageBox.question(self, "Удалить", "Удалить выбранный товар?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.execute_non_query("DELETE FROM product_workshops WHERE product_id=?", (product_id,))
                self.db.execute_non_query("DELETE FROM products WHERE product_id=?", (product_id,))
                self.load_products()
                QMessageBox.information(self, "Успех", "Товар удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def clear_filter(self):
        self.product_filter_input.clear()
        self.product_type_filter_combo.setCurrentIndex(0)
        self.load_products()
