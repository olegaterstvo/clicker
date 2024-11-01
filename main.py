import glob
import os
import sys
import logging
from logging.config import dictConfig
from PySide6.QtWidgets import QApplication
from app import Clicker
from common import example
import keys
import utils

if not os.path.exists('./__pycache__/'):
    os.makedirs("./__pycache__/")
if len(glob.glob('script_*.py')) == 0:
    with open('script_0.py', 'w+') as file:
        file.write(example)


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
                "filename": "./__pycache__/log.log",
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

