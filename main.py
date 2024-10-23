# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the widgets/gallery example from Qt v5.15"""

import sys
import logging
from logging.config import dictConfig
from PySide6.QtWidgets import QApplication
from app import Clicker

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

