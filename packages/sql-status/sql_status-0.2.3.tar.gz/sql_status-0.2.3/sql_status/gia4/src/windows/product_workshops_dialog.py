from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QListWidget, QListWidgetItem, QWidget, QFormLayout
from PyQt5.QtCore import Qt
from database import Database

class ProductWorkshopsDialog(QDialog):
    def __init__(self, product_id, parent=None, role='admin'):
        super().__init__(parent)
        self.db = Database()
        self.product_id = product_id
        self.role = role
        self.setWindowTitle("Выбор цехов для продукции")
        self.setMinimumWidth(400)
        self.selected_workshops = []  # (workshop_id, name, time)
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        workshops = self.db.get_workshops()
        form_layout = self.layout().itemAt(1).layout()  # form = QFormLayout
        while form_layout.rowCount() > 0:
            form_layout.removeRow(0)
        if self.role != 'worker':
            self.cb = QComboBox()
            for wid, name, type_, staff_count in workshops:
                self.cb.addItem(f"{name} ({type_})", wid)
            self.cb.setStyleSheet("font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px;")
            self.time_input = QDoubleSpinBox()
            self.time_input.setMinimum(0.1)
            self.time_input.setMaximum(1000)
            self.time_input.setDecimals(2)
            self.time_input.setValue(1.0)
            self.time_input.setStyleSheet("font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px;")
            add_btn = QPushButton("Добавить цех")
            add_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px;")
            add_btn.clicked.connect(lambda: self.add_workshop(self.cb, self.time_input))
            form_layout.addRow(QLabel("Цех:"), self.cb)
            form_layout.addRow(QLabel("Время (ч):"), self.time_input)
            form_layout.addRow(add_btn)
        # Пересобираем список выбранных цехов
        self.selected_list.clear()
        existing_workshops = self.db.get_product_workshops(self.product_id)
        for pw_id, w_name, time_hours in existing_workshops:
            wid = None
            for wid_row in workshops:
                if wid_row[1] == w_name:
                    wid = wid_row[0]
                    break
            item = QListWidgetItem(f"{w_name} — {time_hours} ч")
            item.setData(1000, wid)
            item.setData(1001, time_hours)
            self.selected_list.addItem(item)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        # Заголовок
        title = QLabel("Добавление цехов к продукции")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0C4882; font-family: 'Bahnschrift Light SemiCondensed';")
        layout.addWidget(title)
        # Структурированный блок для выбора цеха и времени
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        # Изначально пустой, будет заполнен в showEvent
        self.cb = QComboBox()
        self.cb.setStyleSheet("font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px;")
        self.time_input = QDoubleSpinBox()
        self.time_input.setMinimum(0.1)
        self.time_input.setMaximum(1000)
        self.time_input.setDecimals(2)
        self.time_input.setValue(1.0)
        self.time_input.setStyleSheet("font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px;")
        add_btn = QPushButton("Добавить цех")
        add_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px;")
        add_btn.clicked.connect(lambda: self.add_workshop(self.cb, self.time_input))
        if self.role != 'worker':
            form.addRow(QLabel("Цех:"), self.cb)
            form.addRow(QLabel("Время (ч):"), self.time_input)
            form.addRow(add_btn)
        layout.addLayout(form)
        # Список выбранных цехов
        selected_label = QLabel("Выбранные цеха:")
        selected_label.setStyleSheet("font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px; color: #0C4882;")
        layout.addWidget(selected_label)
        self.selected_list = QListWidget()
        self.selected_list.setStyleSheet("font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14px; background-color: #fff; border: 1px solid #0C4882;")
        self.selected_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.selected_list)
        if self.role != 'worker':
            btns_h = QHBoxLayout()
            del_btn = QPushButton("Удалить")
            del_btn.setStyleSheet("background-color: #B22222; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13px;")
            up_btn = QPushButton("Вверх")
            up_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13px;")
            down_btn = QPushButton("Вниз")
            down_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13px;")
            btns_h.addWidget(del_btn)
            btns_h.addWidget(up_btn)
            btns_h.addWidget(down_btn)
            layout.addLayout(btns_h)
            def delete_selected():
                row = self.selected_list.currentRow()
                if row >= 0:
                    self.selected_list.takeItem(row)
            def move_up():
                row = self.selected_list.currentRow()
                if row > 0:
                    item = self.selected_list.takeItem(row)
                    self.selected_list.insertItem(row-1, item)
                    self.selected_list.setCurrentRow(row-1)
            def move_down():
                row = self.selected_list.currentRow()
                if row < self.selected_list.count()-1 and row >= 0:
                    item = self.selected_list.takeItem(row)
                    self.selected_list.insertItem(row+1, item)
                    self.selected_list.setCurrentRow(row+1)
            del_btn.clicked.connect(delete_selected)
            up_btn.clicked.connect(move_up)
            down_btn.clicked.connect(move_down)
        btn_hbox = QHBoxLayout()
        if self.role != 'worker':
            save_btn = QPushButton("Сохранить")
            save_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 15px; padding: 6px 18px;")
            save_btn.clicked.connect(self.save_workshops)
            btn_hbox.addWidget(save_btn)
        cancel_btn = QPushButton("Закрыть" if self.role == 'worker' else "Отмена")
        cancel_btn.setStyleSheet("background-color: #B22222; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 15px; padding: 6px 18px;")
        cancel_btn.clicked.connect(self.reject)
        btn_hbox.addWidget(cancel_btn)
        layout.addLayout(btn_hbox)
        self.setLayout(layout)

    def add_workshop(self, cb, time_input):
        if self.role == 'worker':
            return
        wid = cb.currentData()
        name = cb.currentText()
        time = time_input.value()
        for i in range(self.selected_list.count()):
            if self.selected_list.item(i).data(1000) == wid:
                QMessageBox.warning(self, "Ошибка", "Этот цех уже добавлен")
                return
        item = QListWidgetItem(f"{name} — {time} ч")
        item.setData(1000, wid)
        item.setData(1001, time)
        self.selected_list.addItem(item)

    def save_workshops(self):
        if self.role == 'worker':
            return
        if self.selected_list.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один цех")
            return
        self.db.execute_non_query("DELETE FROM product_workshops WHERE product_id=?", (self.product_id,))
        for i in range(self.selected_list.count()):
            wid = self.selected_list.item(i).data(1000)
            time = self.selected_list.item(i).data(1001)
            self.db.add_product_workshop(self.product_id, wid, time)
        self.accept()
