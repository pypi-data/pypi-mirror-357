from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QDoubleSpinBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from database import Database
from windows.styles import BTN_MAIN, BTN_DANGER, CARD_STYLE
from windows.ui_utils import make_button, CardWidget
from windows.product_materials_dialog import ProductMaterialsDialog

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
            btn_layout.addWidget(create_btn)
            # Кнопку удаления товара убираем, она теперь только в карточке
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

    def select_product_card(self, card):
        # Снимаем выделение со всех карточек
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                c.setStyleSheet(CARD_STYLE)
        # Выделяем выбранную карточку
        card.setProperty('selected', True)
        card.setStyleSheet(CARD_STYLE + "background-color: #e3f2fd;")

    def add_product_card(self, row):
        # row: (product_id, name, type_name, article, min_price, coefficient)
        product_id, name, type_name, article, min_price, coefficient = row
        left_widgets = [
            QLabel(f"<b>{name}</b>"),
            QLabel(f"Тип: {type_name}"),
            QLabel(f"Артикул: {article}"),
            QLabel(f"Мин. цена: {min_price} руб."),
            QLabel(f"Коэффициент типа: {coefficient}")
        ]
        right_widgets = []
        if self.role in ("admin", "manager"):
            подробнее_btn = make_button("Подробнее", BTN_MAIN, lambda _, pid=product_id: self.open_edit_product_dialog(pid))
            материалы_btn = make_button("Материалы", BTN_MAIN, lambda _, pid=product_id: self.open_product_materials_dialog(pid, readonly=False))
            удалить_btn = make_button("Удалить", BTN_DANGER, lambda _, pid=product_id: self.delete_product_by_id(pid))
            подробнее_btn.setFixedWidth(120)
            материалы_btn.setFixedWidth(120)
            удалить_btn.setFixedWidth(120)
            подробнее_btn.setStyleSheet("font-size: 13pt; padding: 4px 12px; background-color: #0C4882; color: white;")
            материалы_btn.setStyleSheet("font-size: 13pt; padding: 4px 12px; background-color: #0C4882; color: white;")
            удалить_btn.setStyleSheet("font-size: 13pt; padding: 4px 12px; background-color: #d32f2f; color: white;")
            right_widgets = [подробнее_btn, материалы_btn, удалить_btn]
        elif self.role == "worker":
            подробнее_btn = make_button("Подробнее", BTN_MAIN, lambda _, pid=product_id: self.open_view_product_dialog(pid))
            материалы_btn = make_button("Материалы", BTN_MAIN, lambda _, pid=product_id: self.open_product_materials_dialog(pid, readonly=True))
            подробнее_btn.setFixedWidth(120)
            материалы_btn.setFixedWidth(120)
            подробнее_btn.setStyleSheet("font-size: 13pt; padding: 4px 12px; background-color: #0C4882; color: white;")
            материалы_btn.setStyleSheet("font-size: 13pt; padding: 4px 12px; background-color: #0C4882; color: white;")
            right_widgets = [подробнее_btn, материалы_btn]
        card = CardWidget(left_widgets, right_widgets, CARD_STYLE)
        card.setProperty('product_id', product_id)
        card.setProperty('selected', False)
        if self.role in ("admin", "manager"):
            card.mousePressEvent = lambda event, c=card: self.select_product_card(c)
        self.cards_layout.addWidget(card)

    def open_product_materials_dialog(self, product_id, readonly=False):
        dlg = ProductMaterialsDialog(product_id=product_id, parent=self, readonly=readonly, on_save=self.load_products if not readonly else None)
        dlg.exec_()

    def open_create_product_window(self):
        from windows.ui_utils import generic_form_dialog
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QMessageBox
        type_rows = self.db.get_product_types_with_id()
        fields = [
            ("Наименование", "line", {"default": ""}),
            ("Тип", "combo", {"items": [t[1] for t in type_rows]}),
            ("Артикул", "line", {"default": ""}),
            ("Мин. цена", "doublespin", {"default": 0, "min": 0, "max": 9999999, "decimals": 2})
        ]
        data = generic_form_dialog(self, "Создать товар", fields)
        if data:
            try:
                type_id = next((t[0] for t in type_rows if t[1]==data['Тип']), None)
                # --- Диалог выбора материалов ---
                dlg = ProductMaterialsDialog(product_id=None, parent=self, readonly=False)
                if dlg.exec_() == QDialog.Accepted:
                    # Проверяем, что выбран хотя бы один материал
                    any_material = False
                    for i in range(dlg.table.rowCount()):
                        qty = dlg.table.cellWidget(i, 1).value()
                        if qty > 0:
                            any_material = True
                    if not any_material:
                        QMessageBox.warning(self, "Ошибка", "Укажите хотя бы один материал!")
                        return
                    # Сохраняем продукт только если есть материалы
                    self.db.execute_non_query(
                        "INSERT INTO products (name, product_type_id, article, min_price) VALUES (?, ?, ?, ?)",
                        (data['Наименование'], type_id, data['Артикул'], data['Мин. цена'])
                    )
                    product_id = self.db.execute_query("SELECT TOP 1 product_id FROM products ORDER BY product_id DESC")[0][0]
                    for i, (mid, mname) in enumerate(dlg.material_rows):
                        qty = dlg.table.cellWidget(i, 1).value()
                        if qty > 0:
                            self.db.execute_non_query(
                                "INSERT INTO product_materials (product_id, material_id, required_qty) VALUES (?, ?, ?)",
                                (product_id, mid, qty)
                            )
                    self.load_products()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка создания: {e}")

    def open_edit_product_dialog(self, product_id):
        if self.role not in ("admin", "manager"):
            return  # worker не может редактировать
        from windows.ui_utils import generic_form_dialog
        from PyQt5.QtWidgets import QDialog, QMessageBox
        # Получить данные продукта
        row = self.db.execute_query("SELECT product_id, name, product_type_id, article, min_price FROM products WHERE product_id=?", (product_id,))
        if not row:
            QMessageBox.warning(self, "Ошибка", "Продукт не найден")
            return
        product = row[0]
        # Получить типы
        type_rows = self.db.get_product_types_with_id()
        # Получить коэффициент типа
        coefficient = self.db.execute_query("SELECT coefficient FROM product_types WHERE product_type_id=?", (product[2],))[0][0]
        fields = [
            ("Наименование", "line", {"default": product[1]}),
            ("Тип", "combo", {"items": [t[1] for t in type_rows], "default": next((t[1] for t in type_rows if t[0]==product[2]), "")} ),
            ("Артикул", "line", {"default": product[3]}),
            ("Мин. цена", "doublespin", {"default": float(product[4]) if product[4] is not None else 0, "min": 0, "max": 9999999, "decimals": 2}),
            ("Коэффициент типа", "label", {"default": str(coefficient)})
        ]
        data = generic_form_dialog(self, "Редактировать товар", fields)
        if data:
            try:
                type_id = next((t[0] for t in type_rows if t[1]==data['Тип']), None)
                self.db.execute_non_query(
                    "UPDATE products SET name=?, product_type_id=?, article=?, min_price=? WHERE product_id=?",
                    (data['Наименование'], type_id, data['Артикул'], data['Мин. цена'], product_id)
                )
                # --- Диалог редактирования материалов ---
                dlg = ProductMaterialsDialog(product_id=product_id, parent=self, readonly=False, on_save=self.load_products)
                dlg.exec_()
                self.load_products()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")

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

    # Удаление товара по product_id (вызывается из карточки)
    def delete_product_by_id(self, product_id):
        if QMessageBox.question(self, "Удалить", "Удалить выбранный товар?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                # Сначала удаляем связи с материалами
                self.db.execute_non_query("DELETE FROM product_materials WHERE product_id=?", (product_id,))
                # Затем сам продукт
                self.db.execute_non_query("DELETE FROM products WHERE product_id=?", (product_id,))
                self.load_products()
                QMessageBox.information(self, "Успех", "Товар удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    # Удаление выделенного товара (вызывается из старого интерфейса, если потребуется)
    def delete_selected_product(self):
        if self.role not in ("admin", "manager"):
            return
        product_id = self.get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self, "Ошибка", "Выделите товар для удаления")
            return
        self.delete_product_by_id(product_id)

    def clear_filter(self):
        self.product_filter_input.clear()
        self.product_type_filter_combo.setCurrentIndex(0)
        self.load_products()

    def open_view_product_dialog(self, product_id):
        # Окно только для просмотра (worker): только текст, кнопка "Закрыть"
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        row = self.db.execute_query("SELECT product_id, name, product_type_id, article, min_price FROM products WHERE product_id=?", (product_id,))
        if not row:
            QMessageBox.warning(self, "Ошибка", "Продукт не найден")
            return
        product = row[0]
        type_rows = self.db.get_product_types_with_id()
        type_name = next((t[1] for t in type_rows if t[0]==product[2]), "")
        coefficient = self.db.execute_query("SELECT coefficient FROM product_types WHERE product_type_id=?", (product[2],))[0][0]
        dlg = QDialog(self)
        dlg.setWindowTitle("Просмотр товара")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<b>Наименование:</b> {product[1]}"))
        layout.addWidget(QLabel(f"<b>Тип:</b> {type_name}"))
        layout.addWidget(QLabel(f"<b>Артикул:</b> {product[3]}"))
        layout.addWidget(QLabel(f"<b>Мин. цена:</b> {product[4]} руб."))
        layout.addWidget(QLabel(f"<b>Коэффициент типа:</b> {coefficient}"))
        btn_h = QHBoxLayout()
        btn_h.addStretch()
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("background-color: #B22222; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14pt; min-width: 120px;")
        close_btn.clicked.connect(dlg.reject)
        btn_h.addWidget(close_btn)
        layout.addLayout(btn_h)
        dlg.setLayout(layout)
        dlg.exec_()
