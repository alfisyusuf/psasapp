import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QPushButton, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QInputDialog, QWidget
from PyQt5.QtCore import Qt, QUrl
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
                    self.accept()  # If password is correct, close the login dialog
                    return
        self.label.setText("Password Salah! Coba Lagi.")

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Aplikasi Ujian")
        self.setGeometry(0, 0, 1920, 1080)  # Fullscreen mode

        # Fullscreen without window decorations (frameless)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowMaximized)  # To make it fullscreen
        self.setAttribute(Qt.WA_OpaquePaintEvent)  # Optional: making the app opaque

        # Tampilkan jendela login
        self.login_window = LoginWindow()
        if self.login_window.exec_() == QDialog.Accepted:
            self.setup_main_window()
        else:
            self.close()

    def setup_main_window(self):
        self.setWindowTitle("Aplikasi Ujian - Sesi Aktif")

        # Tombol keluar
        self.exit_button = QPushButton("Keluar", self)
        self.exit_button.clicked.connect(self.exit_app)
        self.exit_button.setGeometry(1600, 900, 100, 50)

        # Panel utama
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # Layout untuk tombol
        self.button_layout = QHBoxLayout()

        self.home_button = QPushButton("Home", self)
        self.reload_button = QPushButton("Reload", self)
        self.close_button = QPushButton("Close", self)

        self.button_layout.addWidget(self.home_button)
        self.button_layout.addWidget(self.reload_button)
        self.button_layout.addWidget(self.close_button)

        # Atur layout tombol di atas layar
        self.button_panel = QWidget(self)
        self.button_panel.setLayout(self.button_layout)
        self.button_panel.setGeometry(0, 0, 400, 50)  # Atur posisi dan ukuran tombol

        self.home_button.clicked.connect(self.go_home)
        self.reload_button.clicked.connect(self.reload_page)
        self.close_button.clicked.connect(self.close_app)

        # Web view untuk menampilkan halaman ujian
        self.web_view = QWebEngineView(self)
        self.web_view.setGeometry(0, 50, self.width(), self.height() - 50)  # Menyesuaikan dengan ukuran jendela
        self.web_view.setUrl(QUrl("https://ujian.pages.dev/h0"))
        self.web_view.show()

    def resizeEvent(self, event):
        """Menyesuaikan ukuran web view ketika jendela diubah ukurannya"""
        self.web_view.setGeometry(0, 50, self.width(), self.height() - 50)  # Menyesuaikan dengan ukuran jendela
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        """Override untuk menangani input keyboard"""
        if event.key() == Qt.Key_F4 and event.modifiers() == Qt.AltModifier:
            # Cegah aksi default untuk Alt + F4
            event.ignore()  # Mengabaikan event Alt+F4
            print("Alt + F4 tidak berfungsi.")
        else:
            super().keyPressEvent(event)  # Proses event lainnya

    def go_home(self):
        # Aksi untuk tombol Home
        self.web_view.setUrl(QUrl("https://ujian.pages.dev/h0"))  # Halaman utama ujian
        print("Home Button Pressed")

    def reload_page(self):
        # Aksi untuk tombol Reload
        self.web_view.reload()
        print("Reload Button Pressed")

    def close_app(self):
        # Meminta password keluar sebelum menutup aplikasi
        password, ok = QInputDialog.getText(self, "Password Keluar", "Masukkan password keluar:")
        if ok and self.verify_exit_password(password):
            self.close()  # Menutup aplikasi setelah password keluar benar
        else:
            self.statusBar().showMessage("Password keluar salah! Coba lagi.")

    def exit_app(self):
        # Aksi untuk tombol Keluar yang memverifikasi password keluar
        self.close_app()

    def verify_exit_password(self, password):
        sessions = get_sessions()
        if sessions:
            for session in sessions['sessions']:
                if session['exitPassword'] == password:
                    return True
        return False

    def closeEvent(self, event):
        """Override untuk menonaktifkan close window dengan Alt+F4"""
        # Pastikan jika event bukan dari tombol close atau Alt+F4
        if event.spontaneous():
            # Jika tombol keluar yang memerlukan password ditekan, tampilkan dialog password
            password, ok = QInputDialog.getText(self, "Password Keluar", "Masukkan password keluar:")
            if ok and self.verify_exit_password(password):
                event.accept()  # Lanjutkan menutup aplikasi
                print("Aplikasi ditutup dengan benar.")
            else:
                event.ignore()  # Abaikan penutupan jika password salah
                self.statusBar().showMessage("Password keluar salah! Coba lagi.")
        else:
            event.ignore()  # Jika Alt+F4 atau cara lain, batalkan
            print("Menonaktifkan tombol close melalui Alt+F4.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
