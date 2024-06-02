from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QStyleFactory, QTextEdit, QToolBar, QFileDialog, QLineEdit, QMessageBox, QListWidget, QHBoxLayout, QStyle, QLabel
import sys, os, argparse, subprocess

from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QIcon
from PySide6.QtCore import Qt, QRegularExpression, QTimer

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initWindow(self):
        self.setWindowTitle("uRunner")
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 500, 30)

    def initUI(self):
        self.initWindow()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.textbox_layout = QHBoxLayout()
        self.layout.addLayout(self.textbox_layout)
        self.search_icon = QPushButton()
        self.search_icon.setIcon(QIcon.fromTheme("edit-find"))
        self.search_icon.setStyleSheet("border: none;")
        self.textbox_layout.addWidget(self.search_icon)
        self.textbox = QLineEdit()
        self.textbox.setPlaceholderText("Search...")
        self.textbox.textChanged.connect(self.on_text_changed)
        self.textbox.returnPressed.connect(self.run_app)
        self.textbox_layout.addWidget(self.textbox)

        self.close_button = QPushButton()
        self.close_button.setFixedSize(30, 30)
        # use icon from icon theme, by name
        self.close_button.setIcon(QIcon.fromTheme("window-close"))
        self.close_button.clicked.connect(self.close)
        self.textbox_layout.addWidget(self.close_button)

        self.results = QListWidget()
        self.results.hide()
        self.layout.addWidget(self.results)

        self.layout.addStretch()

        self.textbox.setFocus()

        self.timer = QTimer()
        self.timer.timeout.connect(self.toggle_window_socket_check)
        self.timer.start(100)

        self.generate_apps_list()

    def generate_apps_list(self):
        self.commands = {}
        current_name = None  # Variable to store the current application name
        for root, dirs, files in os.walk("/usr/share/applications"):
            for file in files:
                if file.endswith(".desktop"):
                    with open(os.path.join(root, file), "r") as f:
                        for line in f.readlines():
                            if line.startswith("Name="):
                                current_name = line[5:].strip()
                            if line.startswith("Exec=") and current_name:
                                command = line[5:].strip()
                                self.commands[current_name] = command
                                current_name = None  # Reset the current name

    def get_results(self):
        for key in self.commands:
            if self.textbox.text().lower() in key.lower():
                self.results.addItem(key)
        if self.results.count() == 0 or self.textbox.text() == "":
            self.results.hide()
            self.setGeometry(100, 100, 500, 30)
        else:
            self.results.show()
            self.setGeometry(100, 100, 500, 200)

    def run_app(self):
        selected_item = self.results.item(0)
        if selected_item is not None:
            command = self.commands[selected_item.text().replace(" ", "")]
            subprocess.Popen(command.split())
        self.toggle_window()
        self.textbox.clear()

    def on_text_changed(self):
        self.results.clear()
        self.get_results()

    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def toggle_window_socket_check(self):
        user = os.getenv("USER")
        try:
            with open(f"/home/{user}/.config/urunner/toggle-window-socket", "r") as f:
                if f.read() == "1":
                    self.toggle_window()
                    with open(f"/home/{user}/.config/urunner/toggle-window-socket", "w") as f:
                        f.write("0")
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    user = os.getenv("USER")
    try:
        with open(f"/home/{user}/.config/urunner/toggle-window-socket", "w") as f:
            f.write("0")
    except:
        pass
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.processEvents()
    sys.exit(app.exec())
