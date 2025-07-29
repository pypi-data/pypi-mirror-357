from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QComboBox, QInputDialog
from PyQt5.QtCore import Qt
from database import Database

class PartnerOrdersTab(QWidget):
    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
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
        filter_layout.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Все", "новая", "выполнено", "отменено"])
        self.status_combo.currentIndexChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addWidget(QLabel("Сумма от:"))
        self.sum_min_input = QLineEdit()
        self.sum_min_input.setPlaceholderText("0")
        self.sum_min_input.setFixedWidth(60)
        self.sum_min_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.sum_min_input)
        filter_layout.addWidget(QLabel("до:"))
        self.sum_max_input = QLineEdit()
        self.sum_max_input.setPlaceholderText("∞")
        self.sum_max_input.setFixedWidth(60)
        self.sum_max_input.textChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.sum_max_input)
        filter_layout.addWidget(QLabel("Сортировка:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сначала новые", "Сначала выполненные", "Сначала отменённые", "По сумме (убыв.)", "По сумме (возр.)"])
        self.sort_combo.currentIndexChanged.connect(self.apply_filter)
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
        # Кнопка удаления под списком (УДАЛИТЬ!)
        # btn_layout = QHBoxLayout()
        # self.delete_btn = QPushButton("Удалить заявку")
        # self.delete_btn.clicked.connect(self.delete_selected_order)
        # btn_layout.addWidget(self.delete_btn)
        # btn_layout.addStretch()
        # layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.load_orders()

    def apply_filter(self):
        self.load_orders()

    def clear_filter(self):
        self.filter_input.clear()
        self.status_combo.setCurrentIndex(0)
        self.sum_min_input.clear()
        self.sum_max_input.clear()
        self.sort_combo.setCurrentIndex(0)
        self.load_orders()

    def load_orders(self):
        self.clear_cards()
        query = '''
        SELECT a.application_id, pr.name, pr.article, a.quantity, pr.min_price, a.status, (a.quantity * pr.min_price) as total_price
        FROM applications a
        LEFT JOIN products pr ON a.product_id = pr.product_id
        WHERE a.partner_id = ?
        '''
        params = [self.user['partner_id']]
        where_clauses = []
        filter_val = self.filter_input.text()
        if filter_val:
            where_clauses.append("(" + " OR ".join([
                "pr.name LIKE ?", "pr.article LIKE ?", "a.status LIKE ?"
            ]) + ")")
            params.extend([f"%{filter_val}%"] * 3)
        status_val = self.status_combo.currentText() if hasattr(self, 'status_combo') else "Все"
        if status_val and status_val != "Все":
            where_clauses.append("a.status = ?")
            params.append(status_val)
        # Фильтр по сумме
        try:
            sum_min = float(self.sum_min_input.text()) if self.sum_min_input.text() else None
        except Exception:
            sum_min = None
        try:
            sum_max = float(self.sum_max_input.text()) if self.sum_max_input.text() else None
        except Exception:
            sum_max = None
        if sum_min is not None:
            where_clauses.append("(a.quantity * pr.min_price) >= ?")
            params.append(sum_min)
        if sum_max is not None:
            where_clauses.append("(a.quantity * pr.min_price) <= ?")
            params.append(sum_max)
        where = ""
        if where_clauses:
            where = " AND " + " AND ".join(where_clauses)
        # Сортировка
        sort_index = self.sort_combo.currentIndex() if hasattr(self, 'sort_combo') else 0
        if sort_index == 0:
            order = " ORDER BY CASE a.status WHEN 'новая' THEN 0 WHEN 'выполнено' THEN 1 WHEN 'отменено' THEN 2 ELSE 3 END, a.application_id DESC"
        elif sort_index == 1:
            order = " ORDER BY CASE a.status WHEN 'выполнено' THEN 0 WHEN 'новая' THEN 1 WHEN 'отменено' THEN 2 ELSE 3 END, a.application_id DESC"
        elif sort_index == 2:
            order = " ORDER BY CASE a.status WHEN 'отменено' THEN 0 WHEN 'новая' THEN 1 WHEN 'выполнено' THEN 2 ELSE 3 END, a.application_id DESC"
        elif sort_index == 3:
            order = " ORDER BY total_price DESC, a.application_id DESC"
        else:
            order = " ORDER BY total_price ASC, a.application_id DESC"
        full_query = query + where + order
        try:
            rows = self.db.execute_query(full_query, params)
            for row in rows:
                self.add_order_card(row)
            self.results_label.setText(f"Найдено: {len(rows)}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка загрузки заявок: {e}")
            self.results_label.setText("")

    def clear_cards(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def add_order_card(self, row):
        (application_id, product_name, article, quantity, min_price, status, total_price) = row
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet("background-color: #fff;")  # Белый фон карточки
        card_layout = QHBoxLayout()
        left = QVBoxLayout()
        left.addWidget(QLabel(f"<b>{product_name}</b>"))
        left.addWidget(QLabel(f"Артикул: {article}"))
        left.addWidget(QLabel(f"Количество: {quantity}"))
        left.addWidget(QLabel(f"Цена за штуку: {min_price}"))
        left.addWidget(QLabel(f"Сумма: {int(total_price) if total_price is not None else 0} руб."))
        card_layout.addLayout(left)
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        status_label = QLabel(status)
        if status == "новая":
            status_label.setStyleSheet("color: #1976d2;")
        elif status == "выполнено":
            card.setStyleSheet("background-color: #e6f9e6;")
            status_label.setStyleSheet("color: #388e3c;")
        elif status == "отменено":
            card.setStyleSheet("background-color: #f8d7da;")
            status_label.setStyleSheet("color: #a94442;")
        right.addWidget(status_label)
        if status == "новая":
            btn_edit = QPushButton("Редактировать")
            btn_edit.clicked.connect(lambda _, app_id=application_id, qty=quantity: self.edit_order(app_id, qty))
            btn_edit.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            right.addWidget(btn_edit)
            btn_delete = QPushButton("Удалить")
            btn_delete.clicked.connect(lambda _, app_id=application_id: self.delete_order(app_id))
            btn_delete.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed';")
            right.addWidget(btn_delete)
        card_layout.addLayout(right)
        card.setLayout(card_layout)
        self.cards_layout.addWidget(card)

    # Удаляем функцию выделения и получения выделенного id
    # def set_card_status_color(self, card, status):
    #     ...

    # def select_order_card(self, card):
    #     ...

    # def get_selected_order_id(self):
    #     ...

    def delete_order(self, order_id):
        if QMessageBox.question(self, "Удалить", "Удалить выбранную заявку?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                self.db.execute_non_query("DELETE FROM applications WHERE application_id=?", (order_id,))
                self.load_orders()
                QMessageBox.information(self, "Успех", "Заявка удалена")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    # def delete_selected_order(self):
    #     ...

    def edit_order(self, application_id, quantity):
        new_qty, ok = QInputDialog.getInt(self, "Редактировать заявку", "Новое количество:", value=quantity, min=1)
        if ok:
            try:
                self.db.execute_non_query("UPDATE applications SET quantity=? WHERE application_id=?", (new_qty, application_id))
                self.load_orders()
                QMessageBox.information(self, "Успех", "Количество обновлено")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка обновления: {e}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка удаления: {e}")

    def edit_order(self, application_id, quantity):
        new_qty, ok = QInputDialog.getInt(self, "Редактировать заявку", "Новое количество:", value=quantity, min=1)
        if ok:
            try:
                self.db.execute_non_query("UPDATE applications SET quantity=? WHERE application_id=?", (new_qty, application_id))
                self.load_orders()
                QMessageBox.information(self, "Успех", "Количество обновлено")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка обновления: {e}")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка обновления: {e}")
