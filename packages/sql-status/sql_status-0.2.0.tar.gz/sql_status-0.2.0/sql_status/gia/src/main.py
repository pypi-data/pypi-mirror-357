from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from login_window import LoginWindow
from partner_window import PartnerWindow
from manager_window import ManagerWindow
from admin_window import AdminWindow 
from database import ping_db

def main():
    import sys
    if not ping_db():
        print("Нет доступа к базе данных. Проверьте настройки подключения.")
        return

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('src/logo.ico'))
    main_window = {'win': None}
    login_window = {'win': None}

    def open_role_window(user):
        role = user['role']
        if role == 'partner':
            win = PartnerWindow(user)
        elif role == 'manager':
            win = ManagerWindow(user)
        elif role == 'admin':
            win = AdminWindow(user)
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(None, "Ошибка", f"Неизвестная роль: {role}")
            return
        def new_switch():
            win.close()
            show_login()
        win.switch_account = new_switch
        main_window['win'] = win
        win.show()
        # После успешного входа сбрасываем ссылку на login_window, чтобы можно было снова открыть окно логина
        login_window['win'] = None

    def show_login():
        # Если окно уже существует, не создаём новое
        if login_window.get('win') is not None:
            login_window['win'].show()
            return
        login = LoginWindow(on_login_success=open_role_window)
        login_window['win'] = login
        login.show()

    show_login()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()