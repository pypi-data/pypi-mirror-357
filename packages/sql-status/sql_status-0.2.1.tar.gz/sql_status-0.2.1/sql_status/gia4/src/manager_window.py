from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from windows.products_tab import ProductsTab
from windows.workshops_tab import WorkshopsTab
from windows.materials_tab import MaterialsTab

class ManagerWindow(QWidget):
    switch_account_signal = pyqtSignal()
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Менеджер")
        self.resize(800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Верхний layout с приветствием и кнопкой смены аккаунта
        top_layout = QHBoxLayout()
        welcome_label = QLabel(f"Добро пожаловать, {self.user['username']} (Менеджер)")
        welcome_label.setStyleSheet("color: #0C4882; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        switch_btn = QPushButton("Сменить аккаунт")
        switch_btn.clicked.connect(self.switch_account_signal.emit)
        switch_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        top_layout.addWidget(welcome_label, alignment=Qt.AlignLeft)
        top_layout.addWidget(switch_btn, alignment=Qt.AlignRight)
        layout.addLayout(top_layout)

        tabs = QTabWidget()
        self.products_tab = ProductsTab(role=self.user['role'])
        tabs.addTab(self.products_tab, "Продукция")
        self.workshops_tab = WorkshopsTab(role=self.user['role'])
        tabs.addTab(self.workshops_tab, "Цеха")
        self.materials_tab = MaterialsTab(role=self.user['role'])
        tabs.addTab(self.materials_tab, "Материалы")
        layout.addWidget(tabs)
        self.setLayout(layout)
        # Глобальный стиль для окна
        self.setStyleSheet("""
            * {
                font-family: 'Bahnschrift Light SemiCondensed';
                font-size: 13pt;
            }
        """)

    def switch_account(self):
        self.close()
        from login_window import LoginWindow
        login = LoginWindow(on_login_success=self._open_role_window)
        login.show()

    def _open_role_window(self, user):
        from manager_window import ManagerWindow
        from admin_window import AdminWindow
        from worker_window import WorkerWindow
        if user['role'] == 'manager':
            win = ManagerWindow(user)
        elif user['role'] == 'worker':
            win = WorkerWindow(user)
        elif user['role'] == 'admin':
            win = AdminWindow(user)
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Ошибка", f"Неизвестная роль: {user['role']}")
            return
        win.show()