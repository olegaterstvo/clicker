import os
import sys
import logging
from logging.config import dictConfig
from PySide6.QtWidgets import QApplication
from app import Clicker

if not os.path.exists('./cache/'):
    os.makedirs("./cache/")
if not os.path.exists('./images/'):
    os.makedirs("./images/")

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "./cache/log.log",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["console", "file"]},
    }
)
logger = logging.getLogger("root")

if __name__ == '__main__':
    app = QApplication()

    clicker = Clicker()
    clicker.show()

    sys.exit(app.exec())

