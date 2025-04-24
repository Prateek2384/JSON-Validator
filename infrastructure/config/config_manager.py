import json
import os
from pathlib import Path


class ConfigManager:
    _instance = None
    _config = None
    _error_messages = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._load_config()
            cls._load_error_messages()
        return cls._instance

    @classmethod
    def _load_config(cls):
        config_path = Path(r"C:\Users\asus\OneDrive\Desktop\MCP_Project\infrastructure\config\config.json").parent / "config.json"
        try:
            with open(config_path, 'r') as f:
                cls._config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load config: {str(e)}")

    @classmethod
    def _load_error_messages(cls):
        error_path = Path(r"C:\Users\asus\OneDrive\Desktop\MCP_Project\infrastructure\config\error_msg.json").parent / "error_msg.json"
        try:
            with open(error_path, 'r') as f:
                cls._error_messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load error messages: {str(e)}")

    @property
    def logger_config(self):
        return self._config.get("logger", {})

    @property
    def server_config(self):
        return self._config.get("backend_server", {})

    def get_log_path(self):
        if os.name == 'posix':
            return self.logger_config["path"]["linux_logger_path"]
        return self.logger_config["path"]["windows_logger_path"]

    def get_error_message(self, status_code: int) -> str:
        return self._error_messages.get(str(status_code), "Unknown error occurred")