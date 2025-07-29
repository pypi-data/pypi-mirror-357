from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QFormLayout
)
from database import Database
import random
import string

class CreateProductWindow(QDialog):
    def __init__(self, parent=None, on_product_created=None):
        super().__init__(parent)
        self.db = Database()
        self.on_product_created = on_product_created
        self.setWindowTitle("Создать товар")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        form = QFormLayout()

        # Тип продукции
        self.type_combo = QComboBox()
        self.type_combo.setEditable(True)
        self.type_combo.addItem("")
        try:
            rows = self.db.execute_query("SELECT name FROM product_types")
            for row in rows:
                self.type_combo.addItem(row[0])
        except Exception:
            self.type_combo.addItem("Ошибка загрузки типов")
        form.addRow(QLabel("Тип продукции:"), self.type_combo)

        # Наименование
        self.name_input = QLineEdit()
        form.addRow(QLabel("Наименование:"), self.name_input)

        # Артикул (автоматически генерируется)
        self.article_input = QLineEdit()
        self.article_input.setReadOnly(True)
        self.article_input.setText(self.generate_unique_article())
        gen_btn = QPushButton("Сгенерировать")
        gen_btn.clicked.connect(self.set_new_article)
        article_hbox = QHBoxLayout()
        article_hbox.addWidget(self.article_input)
        article_hbox.addWidget(gen_btn)
        form.addRow(QLabel("Артикул:"), article_hbox)

        # Мин. цена
        self.price_input = QLineEdit()
        form.addRow(QLabel("Мин. цена:"), self.price_input)

        # Коэффициент
        self.coef_input = QLineEdit()
        form.addRow(QLabel("Коэффициент:"), self.coef_input)

        # Кнопки
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Создать")
        create_btn.clicked.connect(self.create_product)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)

        vbox = QVBoxLayout()
        vbox.addLayout(form)
        vbox.addLayout(btn_layout)
        self.setLayout(vbox)

    def set_new_article(self):
        self.article_input.setText(self.generate_unique_article())

    def generate_unique_article(self):
        # Генерируем случайный артикул и проверяем уникальность
        for _ in range(100):
            article = 'A' + ''.join(random.choices(string.digits, k=6))
            exists = self.db.execute_query("SELECT 1 FROM products WHERE article=?", (article,))
            if not exists:
                return article
        return "UNIQUE_ERR"

    def create_product(self):
        type_name = self.type_combo.currentText().strip()
        name = self.name_input.text().strip()
        article = self.article_input.text().strip()
        min_price = self.price_input.text().strip()
        coef = self.coef_input.text().strip()
        if not type_name or not name or not article or not min_price or not coef:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        try:
            min_price_val = float(min_price)
            coef_val = float(coef)
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Мин. цена и коэффициент должны быть числами")
            return
        # Проверяем, есть ли такой тип
        type_row = self.db.execute_query("SELECT product_type_id FROM product_types WHERE name=?", (type_name,))
        if type_row:
            product_type_id = type_row[0][0]
        else:
            # Создаём новый тип
            self.db.execute_non_query(
                "INSERT INTO product_types (name, coefficient) VALUES (?, ?)",
                (type_name, coef_val)
            )
            type_row = self.db.execute_query("SELECT product_type_id FROM product_types WHERE name=?", (type_name,))
            product_type_id = type_row[0][0]
        # Создаём продукт
        try:
            self.db.execute_non_query(
                "INSERT INTO products (product_type_id, name, article, min_price) VALUES (?, ?, ?, ?)",
                (product_type_id, name, article, min_price_val)
            )
            QMessageBox.information(self, "Успех", "Товар создан")
            if self.on_product_created:
                self.on_product_created()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка создания товара: {e}")
