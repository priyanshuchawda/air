import yaml
from PyQt5.QtCore import QFileSystemWatcher, QObject, pyqtSignal

class ConfigManager(QObject):
    config_updated = pyqtSignal(dict)

    def __init__(self, config_path='config.yaml'):
        super().__init__()
        self.config_path = config_path
        self.watcher = QFileSystemWatcher()
        self.watcher.addPath(config_path)
        self.watcher.fileChanged.connect(self._reload_config)
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_path) as f:
                self.config = yaml.safe_load(f)
                self.config_updated.emit(self.config)
        except Exception as e:
            print(f"Config load error: {str(e)}")

    def get(self, key, default=None):
        return self.config.get(key, default)