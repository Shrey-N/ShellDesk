import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from editor.app import ShellDeskWindow
from editor.styles import STYLESHEET
def main():
    if hasattr(Qt, 'AA_ShareOpenGLContexts'):
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setApplicationName("ShellDesk")
    app.setStyleSheet(STYLESHEET)
    window = ShellDeskWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()
