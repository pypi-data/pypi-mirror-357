from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QDoubleSpinBox, QSpinBox
)
from PyQt5.QtCore import Qt
from database import Database

class ProductCard(QFrame):
    def __init__(self, product, role, on_edit=None, on_order=None):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #fff;")
        layout = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel(f"<b>{product['name']}</b>"))
        left.addWidget(QLabel(f"Тип: {product['type_name']}"))
        left.addWidget(QLabel(f"Артикул: {product['article']}"))
        layout.addLayout(left)
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right.addWidget(QLabel(f"Коэффициент: {product.get('coefficient', '')}"))
        right.addWidget(QLabel(f"Мин. цена: {product['min_price']} руб."))
        if role in ("manager", "admin") and on_edit:
            edit_btn = QPushButton("Редактировать")
            edit_btn.clicked.connect(lambda: on_edit(product['product_id']))
            edit_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            right.addWidget(edit_btn)
        elif role == "partner" and on_order:
            qty_label = QLabel("Количество:")
            qty_spin = QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(1000000)
            right.addWidget(qty_label)
            right.addWidget(qty_spin)
            btn = QPushButton("Оформить заявку")
            btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            btn.clicked.connect(lambda: on_order(product['product_id'], qty_spin.value()))
            right.addWidget(btn)
        layout.addLayout(right)
        self.setLayout(layout)

class ProductsTab(QWidget):
    def __init__(self, user=None, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.user = user
        self.role = user['role'] if user and 'role' in user else None
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
        if self.role in ("manager", "admin"):
            create_btn = QPushButton("Создать товар")
            create_btn.clicked.connect(self.open_create_product_window)
            create_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            delete_btn = QPushButton("Удалить товар")
            delete_btn.clicked.connect(self.delete_selected_product)
            delete_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            btn_layout.addWidget(create_btn)
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
        self.load_products()

    def clear_cards(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def apply_product_filter(self):
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
        product = {
            'product_id': row[0],
            'name': row[1],
            'type_name': row[2],
            'article': row[3],
            'min_price': row[4],
            'coefficient': row[5] if len(row) > 5 else None
        }
        card = ProductCard(
            product,
            self.role,
            on_edit=self.open_edit_product_dialog if self.role in ("manager", "admin") else None,
            on_order=self.create_application if self.role == "partner" else None
        )
        card.setProperty('product_id', product['product_id'])
        card.setProperty('selected', False)
        card.mousePressEvent = lambda event, c=card: self.select_product_card(c)
        self.cards_layout.addWidget(card)

    def select_product_card(self, card):
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                c.setStyleSheet("background-color: #fff;")  # Всегда возвращаем белый фон
        card.setProperty('selected', True)
        card.setStyleSheet("background-color: #e3f2fd;")

    def get_selected_product_id(self):
        for i in range(self.cards_layout.count()):
            card = self.cards_layout.itemAt(i).widget()
            if card and card.property('selected'):
                return card.property('product_id')
        return None

    def open_edit_product_dialog(self, product_id):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle("Редактировать товар")
        form = QFormLayout(dlg)
        # Загрузка данных
        row = self.db.get_product_by_id(product_id)
        name, type_name, article, min_price, coefficient, product_type_id = row
        name_input = QLineEdit(name)
        type_combo = QComboBox()
        type_rows = self.db.get_product_types_with_id()
        type_id_map = {}
        for tid, tname in type_rows:
            type_combo.addItem(tname, tid)
            type_id_map[tname] = tid
        type_combo.setCurrentText(type_name)
        article_input = QLineEdit(article)
        min_price_input = QDoubleSpinBox()
        min_price_input.setMinimum(0)
        min_price_input.setMaximum(9999999)
        min_price_input.setDecimals(2)
        min_price_input.setValue(float(min_price) if min_price is not None else 0)
        min_price_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        coef_input = QDoubleSpinBox()
        coef_input.setMinimum(0)
        coef_input.setMaximum(9999999)
        coef_input.setDecimals(2)
        coef_input.setValue(float(coefficient) if coefficient is not None else 0)
        coef_input.setButtonSymbols(QDoubleSpinBox.NoButtons)
        form.addRow("Наименование", name_input)
        form.addRow("Тип", type_combo)
        form.addRow("Артикул", article_input)
        form.addRow("Мин. цена", min_price_input)
        form.addRow("Коэффициент", coef_input)
        save_btn = QPushButton("Сохранить")
        save_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        form.addRow(save_btn)
        def save():
            try:
                new_name = name_input.text()
                new_type_id = type_combo.currentData()
                new_article = article_input.text()
                new_min_price = min_price_input.value()
                new_coef = coef_input.value()
                self.db.update_product(product_id, new_name, new_type_id, new_article, new_min_price)
                self.db.update_product_type_coefficient(new_type_id, new_coef)
                dlg.accept()
                self.load_products()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка сохранения: {e}")
        save_btn.clicked.connect(save)
        dlg.exec_()

    def change_coefficient(self, product_id, value):
        try:
            # Меняем коэффициент типа продукта
            type_id = self.db.execute_query("SELECT product_type_id FROM products WHERE product_id=?", (product_id,))[0][0]
            self.db.execute_non_query("UPDATE product_types SET coefficient=? WHERE product_type_id=?", (value, type_id))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения коэффициента: {e}")

    def change_min_price(self, product_id, value):
        try:
            self.db.execute_non_query("UPDATE products SET min_price=? WHERE product_id=?", (value, product_id))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения мин. цены: {e}")

    def open_create_product_window(self):
        from windows.create_product_window import CreateProductWindow
        dlg = CreateProductWindow(self, on_product_created=self.load_products)
        dlg.exec_()

    def delete_selected_product(self):
        product_id = self.get_selected_product_id()
        if not product_id:
            QMessageBox.warning(self, "Ошибка", "Выделите товар для удаления")
            return
        if QMessageBox.question(self, "Удалить", "Удалить выбранный товар?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.execute_non_query("DELETE FROM products WHERE product_id=?", (product_id,))
                self.load_products()
                QMessageBox.information(self, "Успех", "Товар удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def create_application(self, product_id, quantity):
        if quantity <= 0:
            QMessageBox.warning(self, "Ошибка", "Количество должно быть положительным")
            return
        try:
            self.db.execute_non_query(
                "INSERT INTO applications (partner_id, product_id, quantity, status) VALUES (?, ?, ?, 'новая')",
                (self.user['partner_id'], product_id, quantity)
            )
            QMessageBox.information(self, "Успех", "Заявка создана!")
            # Обновить окно заявок, если оно есть
            parent = self.parent()
            # Если ProductsTab открыт как вкладка, ищем orders_tab среди соседних вкладок
            if hasattr(self, "orders_tab") and self.orders_tab:
                self.orders_tab.load_orders()
            elif parent:
                # Поиск orders_tab среди братьев по QTabWidget
                try:
                    tab_widget = parent.parent() if hasattr(parent, "parent") else None
                    if tab_widget and hasattr(tab_widget, "count"):
                        for i in range(tab_widget.count()):
                            widget = tab_widget.widget(i)
                            if hasattr(widget, "load_orders"):
                                widget.load_orders()
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка создания заявки: {e}")

    def clear_filter(self):
        self.product_filter_input.clear()
        self.product_type_filter_combo.setCurrentIndex(0)
        self.load_products()
