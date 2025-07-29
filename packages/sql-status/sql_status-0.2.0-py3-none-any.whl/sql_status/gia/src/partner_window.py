from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from windows.partner_orders_tab import PartnerOrdersTab
from windows.partner_products_tab import PartnerProductsTab

class PartnerWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Партнер")
        self.resize(800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Верхний layout с приветствием и кнопкой смены аккаунта
        top_layout = QHBoxLayout()
        welcome_label = QLabel(f"Добро пожаловать, {self.user['username']} (Партнер)")
        welcome_label.setStyleSheet("color: #0C4882; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        switch_btn = QPushButton("Сменить аккаунт")
        switch_btn.clicked.connect(self.switch_account)
        switch_btn.setStyleSheet("background-color: #0C4882; color: white; font-family: 'Bahnschrift Light SemiCondensed'; font-size: 13pt;")
        top_layout.addWidget(welcome_label, alignment=Qt.AlignLeft)
        top_layout.addWidget(switch_btn, alignment=Qt.AlignRight)
        layout.addLayout(top_layout)

        tabs = QTabWidget()
        self.orders_tab = PartnerOrdersTab(self.user)
        self.products_tab = PartnerProductsTab(self.user, self.orders_tab)
        tabs.addTab(self.orders_tab, "Мои заявки")
        tabs.addTab(self.products_tab, "Продукция")
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
        from login_window import LoginWindow
        def open_role_window(user):
            from partner_window import PartnerWindow
            from manager_window import ManagerWindow
            from admin_window import AdminWindow
            if user['role'] == 'partner':
                win = PartnerWindow(user)
            elif user['role'] == 'manager':
                win = ManagerWindow(user)
            elif user['role'] == 'admin':
                win = AdminWindow(user)
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Ошибка", f"Неизвестная роль: {user['role']}")
                return
            self.role_window = win
            win.show()
            if hasattr(self, 'login_window') and self.login_window is not None:
                self.login_window.close()
                self.login_window = None
        self.close()
        self.login_window = LoginWindow(on_login_success=open_role_window)
        self.login_window.show()