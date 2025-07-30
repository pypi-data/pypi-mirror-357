from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from database import Database
from windows.users_tab import UsersTab
from windows.products_tab import ProductsTab
from windows.workshops_tab import WorkshopsTab
from windows.materials_tab import MaterialsTab

class AdminWindow(QWidget):
    switch_account_signal = pyqtSignal()
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = Database()
        self.setWindowTitle("Администратор")
        self.resize(800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Горизонтальный layout для приветствия и кнопки "Сменить аккаунт"
        top_layout = QHBoxLayout()
        welcome_label = QLabel(f"Добро пожаловать, {self.user['username']} (Администратор)")
        welcome_label.setStyleSheet("color: #0C4882; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        switch_btn = QPushButton("Сменить аккаунт")
        switch_btn.clicked.connect(self.switch_account_signal.emit)
        switch_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        top_layout.addWidget(welcome_label, alignment=Qt.AlignLeft)
        top_layout.addWidget(switch_btn, alignment=Qt.AlignRight)
        layout.addLayout(top_layout)

        tabs = QTabWidget()
        # Вкладка "Пользователи"
        self.users_tab = UsersTab(role=self.user['role'])
        tabs.addTab(self.users_tab, "Пользователи")
        # Вкладка "Продукция"
        self.products_tab = ProductsTab(role=self.user['role'])
        tabs.addTab(self.products_tab, "Продукция")
        # Вкладка "Цеха"
        self.workshops_tab = WorkshopsTab(role=self.user['role'])
        tabs.addTab(self.workshops_tab, "Цеха")
        # Вкладка "Материалы"
        self.materials_tab = MaterialsTab(role=self.user['role'])
        tabs.addTab(self.materials_tab, "Материалы")
        layout.addWidget(tabs)
        self.setLayout(layout)
        self.setStyleSheet("""
            * {
                font-family: 'Bahnschrift Light SemiCondensed';
                font-size: 13pt;
            }
        """)

    def switch_account(self):
        self.close()
        from login_window import LoginWindow
        self.login_window = LoginWindow(on_login_success=self._open_role_window)
        self.login_window.show()

    def _open_role_window(self, user):
        from manager_window import ManagerWindow
        from worker_window import WorkerWindow
        # from admin_window import AdminWindow  # УБРАНО, чтобы не было рекурсивного импорта
        if user['role'] == 'manager':
            win = ManagerWindow(user)
        elif user['role'] == 'worker':
            win = WorkerWindow(user)
        elif user['role'] == 'admin':
            win = AdminWindow(user)  # Класс уже определён
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Ошибка", f"Неизвестная роль: {user['role']}")
            return
        win.show()