import sys
import logging
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

print("Script started", flush=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)

# Add console handler explicitly
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger(__name__)
print("Logging configured", flush=True)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        print("Creating test window", flush=True)
        self.setWindowTitle("AirTouch Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget and layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Add test button
        button = QPushButton("Test Button")
        button.clicked.connect(self.on_click)
        layout.addWidget(button)
        
        print("Test window created", flush=True)
    
    def on_click(self):
        print("Button clicked", flush=True)
        sys.stdout.flush()

def main():
    try:
        print("Starting test application...", flush=True)
        
        # Add project root to Python path
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        print(f"Project root: {project_root}", flush=True)
        
        # Initialize Qt application
        app = QApplication(sys.argv)
        print("QApplication initialized", flush=True)
        
        # Create and show window
        window = TestWindow()
        window.show()
        print("Test window displayed", flush=True)
        
        # Force stdout flush
        sys.stdout.flush()
        
        return app.exec_()
        
    except Exception as e:
        print(f"Error: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    print("Starting main", flush=True)
    sys.stdout.flush()
    sys.exit(main())