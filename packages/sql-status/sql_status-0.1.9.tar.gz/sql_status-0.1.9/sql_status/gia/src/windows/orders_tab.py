from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QScrollArea, QFrame, QDialog, QTextEdit
)
from PyQt5.QtCore import Qt
from database import Database

class OrdersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Фильтрация (поле ввода + выпадающий список статусов)
        filter_layout = QHBoxLayout()
        self.orders_filter_input = QLineEdit()
        self.orders_filter_input.setPlaceholderText("Фильтр по содержимому")
        self.orders_filter_input.textChanged.connect(self.apply_orders_filter)
        filter_layout.addWidget(QLabel("Фильтр:"))
        filter_layout.addWidget(self.orders_filter_input)
        self.orders_status_filter_combo = QComboBox()
        self.orders_status_filter_combo.addItems(["Все", "новая", "выполнено", "отклонено"])
        self.orders_status_filter_combo.currentIndexChanged.connect(self.apply_orders_filter)
        filter_layout.addWidget(self.orders_status_filter_combo)
        # Сортировка справа от фильтра по статусу
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сначала новые", "Сначала выполненные", "Сначала отклонённые"])
        self.sort_combo.currentIndexChanged.connect(self.apply_orders_filter)
        filter_layout.addWidget(self.sort_combo)
        layout.addLayout(filter_layout)
        # Список заявок (карточки)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_container.setLayout(self.cards_layout)
        self.cards_container.setStyleSheet("background-color: #BBDCFA;")  # Фон контейнера карточек
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        # Кнопка удаления, сброса фильтра и количество найденных справа
        btn_layout = QHBoxLayout()
        delete_btn = QPushButton("Удалить заказ")
        delete_btn.clicked.connect(self.delete_selected_order)
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
        self.load_orders()

    def clear_cards(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def apply_orders_filter(self):
        self.load_orders(filter_val=self.orders_filter_input.text(), status_filter=self.orders_status_filter_combo.currentText())

    def load_orders(self, filter_col=None, filter_val=None, sort_col=None, sort_desc=False, status_filter="Все"):
        self.clear_cards()
        query = '''
        SELECT a.application_id, p.name, pt.name, p.legal_address, p.phone, p.rating, a.quantity, pr.min_price, a.status, (a.quantity * pr.min_price) as total_price,
               pr.name as product_name, pr.article as product_article
        FROM applications a
        LEFT JOIN partners p ON a.partner_id = p.partner_id
        LEFT JOIN partner_types pt ON p.partner_type_id = pt.partner_type_id
        LEFT JOIN products pr ON a.product_id = pr.product_id
        '''
        col_map = {
            "ID": "a.application_id",
            "Партнёр": "p.name",
            "Тип": "pt.name",
            "Адрес": "p.legal_address",
            "Телефон": "p.phone",
            "Рейтинг": "p.rating",
            "Количество": "a.quantity",
            "Цена за штуку": "pr.min_price",
            "Статус": "a.status",
            "Стоимость": "total_price"
        }
        params = []
        where_clauses = []
        if filter_val:
            where_clauses.append("(" + " OR ".join([f"{col} LIKE ?" for col in col_map.values()]) + ")")
            params.extend([f"%{filter_val}%"] * len(col_map))
        if status_filter and status_filter != "Все":
            where_clauses.append("a.status = ?")
            params.append(status_filter)
        where = ""
        if where_clauses:
            where = " WHERE " + " AND ".join(where_clauses)
        # Определяем порядок сортировки по статусу
        sort_index = self.sort_combo.currentIndex() if hasattr(self, 'sort_combo') else 0
        if sort_index == 0:
            order = " ORDER BY CASE a.status WHEN 'новая' THEN 0 WHEN 'выполнено' THEN 1 WHEN 'отклонено' THEN 2 ELSE 3 END, a.application_id DESC"
        elif sort_index == 1:
            order = " ORDER BY CASE a.status WHEN 'выполнено' THEN 0 WHEN 'новая' THEN 1 WHEN 'отклонено' THEN 2 ELSE 3 END, a.application_id DESC"
        else:
            order = " ORDER BY CASE a.status WHEN 'отклонено' THEN 0 WHEN 'новая' THEN 1 WHEN 'выполнено' THEN 2 ELSE 3 END, a.application_id DESC"
        query += where + order
        try:
            rows = self.db.execute_query(query, params) if params else self.db.execute_query(query)
            for row in rows:
                self.add_order_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки заявок: {e}")
            self.results_label.setText("")

    def add_order_card(self, row):
        (application_id, partner_name, partner_type, legal_address, phone, rating, quantity, min_price, status, total_price, product_name, product_article) = row
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: #fff;")  # Белый фон карточки
        card_layout = QHBoxLayout()
        # Левая часть: инфо о продукции и компании
        left = QVBoxLayout()
        # На что заявка и цена за штуку
        left.addWidget(QLabel(f"<b>Заявка на: {product_name}</b> (Артикул: {product_article})"))
        left.addWidget(QLabel(f"Цена за штуку: {min_price} руб."))
        # Название компании и рейтинг (не жирным)
        left.addWidget(QLabel(f"{partner_type} | {partner_name} (Рейтинг: {rating})"))
        card_layout.addLayout(left)
        # Правая часть: количество, сумма, кнопки
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        qty = quantity if quantity is not None else 0
        total = int(total_price) if total_price is not None else 0
        total_str = f"{total:,}".replace(",", " ")
        qty_price = QLabel(f"{qty} шт. | {total_str} руб.")
        qty_price.setAlignment(Qt.AlignRight)
        right.addWidget(qty_price)
        status_label = None
        # Кнопки и статусы
        if status == "новая":
            btn_complete = QPushButton("Выполнить")
            btn_complete.clicked.connect(lambda _, app_id=application_id: self.set_order_status(app_id, "выполнено"))
            btn_complete.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            btn_decline = QPushButton("Отклонить")
            btn_decline.clicked.connect(lambda _, app_id=application_id: self.set_order_status(app_id, "отклонено"))
            btn_decline.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            btn_row = QHBoxLayout()
            btn_row.addWidget(btn_complete)
            btn_row.addWidget(btn_decline)
            right.addLayout(btn_row)
        elif status == "выполнено":
            card.setStyleSheet("background-color: #e6f9e6;")
            status_label = QLabel("(выполнено)")
            status_label.setStyleSheet("font-size: 10px; color: #388e3c;")
            status_label.setAlignment(Qt.AlignHCenter)
        elif status == "отклонено":
            card.setStyleSheet("background-color: #f8d7da;")
            status_label = QLabel("(отклонена)")
            status_label.setStyleSheet("font-size: 10px; color: #a94442;")
            status_label.setAlignment(Qt.AlignHCenter)
        # Кнопка "Подробнее"
        details_btn = QPushButton("Подробнее")
        details_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        details_btn.clicked.connect(lambda _, row=row: self.show_order_details(row))
        right.addWidget(details_btn)
        if status_label:
            right.addWidget(status_label)
        card_layout.addLayout(right)
        card.setLayout(card_layout)
        card.setProperty('order_id', application_id)
        card.setProperty('selected', False)
        card.mousePressEvent = lambda event, c=card: self.select_order_card(c)
        self.cards_layout.addWidget(card)

    def show_order_details(self, row):
        (application_id, partner_name, partner_type, legal_address, phone, rating, quantity, min_price, status, total_price, product_name, product_article) = row
        dlg = QDialog(self)
        dlg.setWindowTitle("Информация о заказе")
        dlg.setMinimumWidth(400)
        layout = QVBoxLayout(dlg)  # Исправлено: используем QVBoxLayout вместо QVBL
        info = (
            f"<b>Заявка №:</b> {application_id}<br>"
            f"<b>Статус:</b> {status}<br>"
            f"<b>Продукт:</b> {product_name} (Артикул: {product_article})<br>"
            f"<b>Количество:</b> {quantity}<br>"
            f"<b>Цена за штуку:</b> {min_price} руб.<br>"
            f"<b>Сумма:</b> {int(total_price):,} руб.<br><br>"
            f"<b>Компания:</b> {partner_type} | {partner_name}<br>"
            f"<b>Рейтинг:</b> {rating}<br>"
            f"<b>Юр. адрес:</b> {legal_address}<br>"
            f"<b>Телефон:</b> {phone}<br>"
        )
        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml(info.replace(",", " "))
        layout.addWidget(text)
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.exec_()

    def select_order_card(self, card):
        for i in range(self.cards_layout.count()):
            c = self.cards_layout.itemAt(i).widget()
            if c:
                c.setProperty('selected', False)
                # Восстановить цвет по статусу
                status = None
                # Получаем статус из QLabel статуса (если есть)
                for j in range(c.layout().count()):
                    layout_item = c.layout().itemAt(j)
                    if isinstance(layout_item, QVBoxLayout):
                        vbox = layout_item
                        for k in range(vbox.count()):
                            widget = vbox.itemAt(k).widget()
                            if isinstance(widget, QLabel):
                                text = widget.text()
                                if text == "(выполнено)":
                                    status = "выполнено"
                                elif text == "(отклонена)":
                                    status = "отклонено"
                if status == "выполнено":
                    c.setStyleSheet("background-color: #e6f9e6;")
                elif status == "отклонено":
                    c.setStyleSheet("background-color: #f8d7da;")
                else:
                    c.setStyleSheet("background-color: #fff;")  # Всегда возвращаем белый фон
        card.setProperty('selected', True)
        # Поверх статусного цвета выделение
        card.setStyleSheet(card.styleSheet() + "background-color: #e3f2fd;")

    def get_selected_order_id(self):
        for i in range(self.cards_layout.count()):
            card = self.cards_layout.itemAt(i).widget()
            if card and card.property('selected'):
                return card.property('order_id')
        return None

    def delete_selected_order(self):
        order_id = self.get_selected_order_id()
        if not order_id:
            QMessageBox.warning(self, "Ошибка", "Выделите заказ для удаления")
            return
        if QMessageBox.question(self, "Удалить", "Удалить выбранный заказ?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.execute_non_query("DELETE FROM applications WHERE application_id=?", (order_id,))
                self.load_orders()
                QMessageBox.information(self, "Успех", "Заказ удалён")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def set_order_status(self, application_id, new_status):
        try:
            self.db.execute_non_query("UPDATE applications SET status=? WHERE application_id=?", (new_status, application_id))
            self.load_orders()
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка изменения статуса: {e}")

    def clear_filter(self):
        self.orders_filter_input.clear()
        self.orders_status_filter_combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        self.load_orders()
