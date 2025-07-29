from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QMessageBox, QSpinBox
from PyQt5.QtCore import Qt
from database import Database

class PartnerProductsTab(QWidget):
    def __init__(self, user, orders_tab=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.orders_tab = orders_tab
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация и сортировка
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр:"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Фильтр по содержимому")
        self.filter_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(QLabel("Тип:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("Все типы")
        try:
            rows = self.db.execute_query("SELECT name FROM product_types")
            for row in rows:
                self.type_combo.addItem(row[0])
        except Exception:
            self.type_combo.addItem("Ошибка загрузки типов")
        self.type_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.type_combo)
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "По умолчанию",
            "По цене (убыв.)",
            "По цене (возр.)"
        ])
        self.sort_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.sort_combo)
        layout.addLayout(filter_layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.products_container = QWidget()
        self.products_layout = QVBoxLayout()
        self.products_layout.setAlignment(Qt.AlignTop)
        self.products_container.setLayout(self.products_layout)
        self.products_container.setStyleSheet("background-color: #BBDCFA;")  # Фон контейнера карточек
        self.scroll_area.setWidget(self.products_container)
        layout.addWidget(self.scroll_area)
        # Сброс фильтра и найдено
        count_layout = QHBoxLayout()
        count_layout.addStretch()
        self.clear_filter_button = QPushButton("Сбросить фильтр")
        self.clear_filter_button.clicked.connect(self.clear_filter)
        self.clear_filter_button.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        count_layout.addWidget(self.clear_filter_button)
        self.results_label = QLabel()
        count_layout.addWidget(self.results_label)
        layout.addLayout(count_layout)
        self.setLayout(layout)
        self.load_products()

    def apply_filter(self):
        self.load_products()

    def clear_filter(self):
        self.filter_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        self.load_products()

    def clear_products(self):
        while self.products_layout.count():
            child = self.products_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_products(self):
        self.clear_products()
        query = '''
        SELECT p.product_id, p.name, pt.name, p.article, p.min_price
        FROM products p
        LEFT JOIN product_types pt ON p.product_type_id = pt.product_type_id
        '''
        params = []
        where_clauses = []
        filter_val = self.filter_input.text()
        if filter_val:
            where_clauses.append("(p.name LIKE ? OR p.article LIKE ?)")
            params.extend([f"%{filter_val}%", f"%{filter_val}%"])
        type_val = self.type_combo.currentText() if hasattr(self, 'type_combo') else "Все типы"
        if type_val and type_val != "Все типы" and type_val != "Ошибка загрузки типов":
            where_clauses.append("pt.name = ?")
            params.append(type_val)
        where = ""
        if where_clauses:
            where = " WHERE " + " AND ".join(where_clauses)
        sort_index = self.sort_combo.currentIndex() if hasattr(self, 'sort_combo') else 0
        if sort_index == 1:
            order = " ORDER BY p.min_price DESC"
        elif sort_index == 2:
            order = " ORDER BY p.min_price ASC"
        else:
            order = " ORDER BY p.product_id DESC"
        full_query = query + where + order
        try:
            rows = self.db.execute_query(full_query, params)
            for row in rows:
                self.add_product_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки продукции: {e}")
            self.results_label.setText("")

    def add_product_card(self, row):
        (product_id, product_name, type_name, article, min_price) = row
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: #fff;")  # Белый фон карточки
        card_layout = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel(f"<b>{product_name}</b>"))
        left.addWidget(QLabel(f"Тип: {type_name}"))
        left.addWidget(QLabel(f"Артикул: {article}"))
        left.addWidget(QLabel(f"Мин. цена: {min_price}"))
        card_layout.addLayout(left)
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        qty_label = QLabel("Количество:")
        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setMaximum(1000000)
        right.addWidget(qty_label)
        right.addWidget(qty_spin)
        btn = QPushButton("Оформить заявку")
        btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        btn.clicked.connect(lambda _, pid=product_id, spin=qty_spin: self.create_application(pid, spin.value()))
        right.addWidget(btn)
        card_layout.addLayout(right)
        card.setLayout(card_layout)
        self.products_layout.addWidget(card)

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
            if self.orders_tab:
                self.orders_tab.load_orders()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка создания заявки: {e}")
