from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTabWidget
from windows.products_tab import ProductsTab
from windows.workshops_tab import WorkshopsTab

class WorkerWindow(QWidget):
    switch_account_signal = pyqtSignal()
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Рабочий: {user['username']}")
        self.resize(800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        # Приветствие и кнопка смены аккаунта
        top_layout = QHBoxLayout()
        welcome_label = QLabel(f"Добро пожаловать, {self.user['username']} (Рабочий)")
        welcome_label.setStyleSheet("color: #0C4882; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 16pt;")
        switch_btn = QPushButton("Сменить аккаунт")
        switch_btn.clicked.connect(self.switch_account_signal.emit)
        switch_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 14pt; min-width: 160px; max-width: 200px;")
        top_layout.addWidget(welcome_label, alignment=Qt.AlignLeft)
        top_layout.addWidget(switch_btn, alignment=Qt.AlignRight)
        layout.addLayout(top_layout)
        # Вкладки только для просмотра
        tabs = QTabWidget()
        tabs.addTab(ProductsTab(role='worker'), "Продукция")
        tabs.addTab(WorkshopsTab(role='worker'), "Цеха")
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.setStyleSheet("""
            * {
                font-family: 'Bahnschrift Light SemiCondensed';
                font-size: 13pt;
            }
        """)
