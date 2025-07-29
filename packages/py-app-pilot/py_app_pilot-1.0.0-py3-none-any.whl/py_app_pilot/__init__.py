import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from loguru import logger
from .py_app_pilot import PythonAppManager


app = QApplication(sys.argv)
# 设置全局字体大小为14
font = QFont()
font.setPointSize(12)
font.setFamily("SimHei")
app.setFont(font)
window = PythonAppManager()
window.show()
sys.exit(app.exec_())