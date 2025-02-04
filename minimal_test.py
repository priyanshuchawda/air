import sys
import os
import platform

def print_debug(msg):
    print(f"DEBUG: {msg}", flush=True)
    sys.stdout.flush()

print_debug("Starting script")
print_debug(f"Python version: {sys.version}")
print_debug(f"Platform: {platform.platform()}")
print_debug(f"Display env: {os.environ.get('DISPLAY', 'Not set')}")

try:
    print_debug("Importing PyQt5")
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt5.QtCore import Qt

    print_debug("Creating QApplication")
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    print_debug("Creating main window")
    window = QMainWindow()
    window.setWindowTitle("Minimal Test")
    window.setGeometry(100, 100, 400, 300)

    print_debug("Creating label")
    label = QLabel("Test Window")
    label.setAlignment(Qt.AlignCenter)
    window.setCentralWidget(label)

    print_debug("Showing window")
    window.show()

    print_debug("Starting event loop")
    sys.exit(app.exec_())

except Exception as e:
    print_debug(f"Error occurred: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)