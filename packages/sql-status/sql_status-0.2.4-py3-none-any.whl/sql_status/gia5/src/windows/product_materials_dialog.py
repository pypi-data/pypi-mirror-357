from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QSpinBox, QHBoxLayout, QPushButton, QMessageBox, QHeaderView
from database import Database

class ProductMaterialsDialog(QDialog):
    def __init__(self, product_id=None, parent=None, readonly=False, on_save=None):
        super().__init__(parent)
        self.db = Database()
        self.product_id = product_id
        self.readonly = readonly
        self.on_save = on_save
        self.setWindowTitle("Материалы продукции")
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Состав продукции:"))
        material_rows = self.db.execute_query("SELECT material_id, name FROM materials")
        used_materials = {}
        if self.product_id is not None:
            used_materials = {mid: qty for mid, qty in self.db.execute_query(
                "SELECT material_id, required_qty FROM product_materials WHERE product_id=?", (self.product_id,))}
        self.table = QTableWidget(len(material_rows), 2)
        self.table.setHorizontalHeaderLabels(["Материал", "Требуемое количество"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i, (mid, mname) in enumerate(material_rows):
            self.table.setItem(i, 0, QTableWidgetItem(mname))
            spin = QSpinBox(); spin.setMinimum(0); spin.setMaximum(100000)
            if mid in used_materials:
                spin.setValue(int(used_materials[mid]))
            if self.readonly:
                spin.setReadOnly(True)
                spin.setButtonSymbols(QSpinBox.NoButtons)
            self.table.setCellWidget(i, 1, spin)
        vbox.addWidget(self.table)
        btns = QHBoxLayout()
        if not self.readonly:
            save_btn = QPushButton("Сохранить")
            save_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14pt;")
            save_btn.clicked.connect(self.save_materials)
            btns.addWidget(save_btn)
        close_btn = QPushButton("Закрыть")
        close_btn.setStyleSheet("background-color: #B22222; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14pt;")
        close_btn.clicked.connect(self.reject)
        btns.addWidget(close_btn)
        vbox.addLayout(btns)
        self.setLayout(vbox)
        self.material_rows = material_rows

    def save_materials(self):
        any_material = False
        if self.product_id is not None:
            self.db.execute_non_query("DELETE FROM product_materials WHERE product_id=?", (self.product_id,))
        for i, (mid, mname) in enumerate(self.material_rows):
            qty = self.table.cellWidget(i, 1).value()
            if qty > 0:
                any_material = True
                if self.product_id is not None:
                    self.db.execute_non_query(
                        "INSERT INTO product_materials (product_id, material_id, required_qty) VALUES (?, ?, ?)",
                        (self.product_id, mid, qty)
                    )
        if not any_material:
            QMessageBox.warning(self, "Ошибка", "Укажите хотя бы один материал!")
            return
        if self.on_save:
            self.on_save()
        self.accept()
