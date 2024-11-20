import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QInputDialog, QWidget
from PyQt5.QtCore import Qt, QUrl, QEvent, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from src.logic import get_sessions

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 200)

        self.label = QLabel("Masukkan Password:", self)
        self.label.move(20, 20)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.move(20, 60)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.check_password)
        self.login_button.move(20, 100)

    def check_password(self):
        password = self.password_input.text()
        sessions = get_sessions()

        if sessions:
            for session in sessions['sessions']:
                if session['loginPassword'] == password:
                    self.accept()
                    return
        self.label.setText("Password Salah! Coba Lagi.")


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_password = None
        self.timer = None

    def init_ui(self):
        self.setWindowTitle("Aplikasi Ujian")
        self.setGeometry(0, 0, 1920, 1080)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        self.login_window = LoginWindow()
        if self.login_window.exec_() == QDialog.Accepted:
            self.setup_main_window()
        else:
            self.close()

    def setup_main_window(self):
        self.setWindowTitle("Aplikasi Ujian - Sesi Aktif")

        self.exit_button = QPushButton("Keluar", self)
        self.exit_button.clicked.connect(self.exit_app)
        self.exit_button.setGeometry(1600, 900, 100, 50)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        self.button_layout = QHBoxLayout()

        self.home_button = QPushButton("Home", self)
        self.reload_button = QPushButton("Reload", self)
        self.close_button = QPushButton("Close", self)

        self.button_layout.addWidget(self.home_button)
        self.button_layout.addWidget(self.reload_button)
        self.button_layout.addWidget(self.close_button)

        self.button_panel = QWidget(self)
        self.button_panel.setLayout(self.button_layout)
        self.button_panel.setGeometry(0, 0, 400, 50)

        self.home_button.clicked.connect(self.go_home)
        self.reload_button.clicked.connect(self.reload_page)
        self.close_button.clicked.connect(self.close_app)

        self.web_view = QWebEngineView(self)
        self.web_view.setGeometry(0, 50, self.width(), self.height() - 50)
        self.web_view.setFocusPolicy(Qt.StrongFocus)
        self.web_view.setUrl(QUrl("https://ujian.pages.dev/h0"))
        self.web_view.show()

        self.web_view.setFocus()

        # Debugging dropdown (Opsional)
        self.web_view.page().runJavaScript("""
            document.querySelectorAll('select').forEach(el => {
                el.addEventListener('click', () => {
                    console.log('Dropdown clicked');
                });
            });
        """)

        self.start_periodic_check()

    def resizeEvent(self, event):
        self.web_view.setGeometry(0, 50, self.width(), self.height() - 50)
        super().resizeEvent(event)

    def go_home(self):
        self.web_view.setUrl(QUrl("https://ujian.pages.dev/h0"))

    def reload_page(self):
        self.web_view.reload()

    def close_app(self):
        password, ok = QInputDialog.getText(self, "Password Keluar", "Masukkan password keluar:")
        if ok and self.verify_exit_password(password):
            QApplication.quit()
        else:
            self.statusBar().showMessage("Password keluar salah! Coba lagi.")

    def exit_app(self):
        self.close_app()

    def verify_exit_password(self, password):
        sessions = get_sessions()
        if sessions:
            for session in sessions['sessions']:
                if session['exitPassword'] == password:
                    return True
        return False

    def closeEvent(self, event):
        password, ok = QInputDialog.getText(self, "Password Keluar", "Masukkan password keluar:")
        if ok and self.verify_exit_password(password):
            event.accept()
        else:
            self.statusBar().showMessage("Password keluar salah! Coba lagi.")
            event.ignore()

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress or event.type() == QEvent.MouseButtonRelease:
            return False
        if event.type() == QEvent.KeyPress:
            if event.modifiers() == Qt.AltModifier:
                return True
            if event.key() == Qt.Key_F4 and event.modifiers() == Qt.AltModifier:
                self.exit_app()
                return True
            if event.key() == Qt.Key_Tab and event.modifiers() == Qt.AltModifier:
                return True
        return super().eventFilter(source, event)

    def start_periodic_check(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_sessions)
        self.timer.start(60000)

    def check_sessions(self):
        sessions = get_sessions()
        if sessions and 'sessions' in sessions:
            for session in sessions['sessions']:
                new_password = session.get('loginPassword')
                if new_password != self.current_password:
                    self.current_password = new_password
        else:
            print("Failed to retrieve sessions.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
