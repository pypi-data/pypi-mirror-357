import os
import sys
import yaml
import logging
from dotenv import load_dotenv
from datetime import datetime
from typing import Optional, Union, Dict, Any
from logging import StreamHandler, FileHandler

class CustomFormatter:
    def format(self, record) -> str:
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} | {record.levelname} | {record.getMessage()}"

class Logger:
    def __init__(self, config: Optional[Union[Dict[str, Any], object]] = None) -> None:
        if config is None:
            self.name = "core.general"
            self.handlers = []
            self.log_file_path = "logs/general.log"
            self.console = True
            self.logLevel = logging.DEBUG
        elif isinstance(config, dict):
            self.name = config.get("name", "core.general")
            self.handlers = config.get("handlers", [])
            self.log_file_path = config.get("filepath", None)
            self.console = config.get("console", True)
            self.logLevel = config.get("logLevel", logging.DEBUG)
        else:
            raise ValueError("Invalid Config Type")
        
        self._logger = logging.getLogger(self.name)
        self._logger.setLevel(self.logLevel)

        self._setup_handlers(self.handlers)
    
    def debug(self, message: Optional[str] = None) -> None:
        self._logger.debug(message)
    
    def info(self, message: Optional[str] = None) -> None:
        self._logger.info(message)

    def warning(self, message: Optional[str] = None) -> None:
        self._logger.warning(message)

    def error(self, message: Optional[str] = None) -> None:
        self._logger.error(message)

    def fatal(self, message: Optional[str] = None) -> None:
        self._logger.fatal(message)
        exit()

    def _setup_handlers(self, handlers: Optional[list[str]] = None):
        # self._setup_format_handler()
        if self.log_file_path is not None:
            self._setup_file_handler()
        if self.console:
            self._setup_console_handler()

    def _setup_format_handler(self):
        stream_handler = StreamHandler()
        stream_handler.setFormatter(CustomFormatter())
        self._logger.addHandler(stream_handler)

    def _setup_file_handler(self):
        if not self.console:
            log_dir = self.log_file_path.strip('/')
            log_dir = log_dir[:len(log_dir)]
            os.makedirs(os.path.dirname(log_dir), exist_ok=True)
            file_handler = FileHandler(self.log_file_path)
            file_handler.setFormatter(CustomFormatter())
            self._logger.addHandler(file_handler)

    def _setup_console_handler(self):
        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(CustomFormatter())
        self._logger.addHandler(sh)
