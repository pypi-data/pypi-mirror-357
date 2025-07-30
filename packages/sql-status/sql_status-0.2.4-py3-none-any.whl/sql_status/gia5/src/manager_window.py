from PyQt5.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from windows.materials_tab import MaterialsTab
from windows.products_tab import ProductsTab

class ManagerWindow(QMainWindow):
    switch_account_signal = pyqtSignal()
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Менеджер: склад")
        self.resize(1000, 650)
        central = QWidget()
        layout = QVBoxLayout()
        # Верхняя панель с приветствием и кнопкой смены аккаунта
        top_layout = QHBoxLayout()
        welcome_label = QLabel(f"Добро пожаловать, {self.user['username']} (Менеджер)")
        welcome_label.setStyleSheet("color: #0C4882; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        switch_btn = QPushButton("Сменить аккаунт")
        switch_btn.clicked.connect(self.switch_account_signal.emit)
        switch_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        top_layout.addWidget(welcome_label, alignment=Qt.AlignLeft)
        top_layout.addWidget(switch_btn, alignment=Qt.AlignRight)
        layout.addLayout(top_layout)
        # Вкладки
        tabs = QTabWidget()
        tabs.addTab(MaterialsTab(role='manager'), "Материалы")
        tabs.addTab(ProductsTab(role='manager'), "Продукция")
        layout.addWidget(tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)
        self.setStyleSheet("""
            * {
                font-family: 'Bahnschrift Light SemiCondensed';
                font-size: 13pt;
            }
        """)