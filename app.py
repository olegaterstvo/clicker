import os
import ctypes
import importlib.util
import json
import sys
import threading
import time
import subprocess
import multiprocessing
import pyautogui
import logging
from PIL import Image, ImageColor
from threading import Thread
from pynput.mouse import Button, Controller 
from pynput.keyboard import Listener, KeyCode, Key, GlobalHotKeys
from pynput.keyboard import Controller as Kb
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from PySide6.QtCore import (QDateTime, QDir, QLibraryInfo, QSysInfo, Qt,
                            QTimer, Slot, qVersion, QThread, Signal, QSize)
from PySide6.QtGui import (QCursor, QDesktopServices, QGuiApplication, QIcon,
                           QKeySequence, QShortcut, QStandardItem, QTextCharFormat, QTextCursor,
                           QStandardItemModel, QPixmap, QColor, QImage, QScreen)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox,
                               QCommandLinkButton, QDateTimeEdit, QDial,
                               QDialog, QDialogButtonBox, QFileSystemModel,
                               QGridLayout, QGroupBox, QHBoxLayout, QLabel,
                               QLineEdit, QListView, QMenu, QPlainTextEdit,
                               QProgressBar, QPushButton, QRadioButton,
                               QScrollBar, QSizePolicy, QSlider, QSpinBox,
                               QStyleFactory, QTableWidget, QTabWidget,
                               QTextBrowser, QTextEdit, QToolBox, QToolButton,
                               QTreeView, QVBoxLayout, QWidget)

functions = ['log','sleep','wait','holdKey','releaseKey','pressKey','getPixel',
             'isMatchesColor','leftClick','rightClick','middleClick','moveTo',
             'moveRel','dragTo','dragRel','scroll','write','screenshot',
             'locateOnImage','locateOnScreen','locateOnWindow','locateAllOnImage','locateAllOnScreen']

logger = logging.getLogger("root")

def class_name(o: QWidget):
    return o.metaObject().className()

def init_widget(w: QWidget, name: str, tooltip: str|None = None):
    """Init a widget for the gallery, give it a tooltip """
    w.setObjectName(name)
    if tooltip is not None:       
        w.setToolTip(tooltip)

def style_names():
    """Return a list of styles, default platform style first"""
    default_style_name = QApplication.style().objectName().lower()
    result = []
    for style in QStyleFactory.keys():
        if style.lower() == default_style_name:
            result.insert(0, style)
        else:
            result.append(style)
    return result


class Clicker(QDialog):
    def __init__(self):
        super().__init__()
        if not os.path.exists('./cache/pixel.png'):
            _p = Image.new("RGB", (16, 16), 0xffffff)
            _p.save('./cache/pixel.png')

        try:
            with open('./cache/cache.json', 'r') as f:
                _cache = json.load(f)
                _theme = _cache['theme']
                _style = _cache['style']
                _coords = _cache['coords']
                _pixel = _cache['pixel']
                _interval = _cache['interval']
                _iterate = _cache['iterate']
        except:
            with open('./cache/cache.json', 'w+') as f:
                _theme = style_names()[0]
                _style = "dracula"
                _coords = [0, 0]
                _pixel = [255, 255, 255]
                _interval = 1000
                _iterate = True
                _cache = {
                    "theme" : _theme,
                    "style" : _style,
                    "coords" : _coords,
                    "pixel" : _pixel,
                    "interval" : _interval,
                    "iterate" : _iterate
                }
                _cache = json.dumps(_cache)
                f.write(_cache)

        self.setWindowIcon(QIcon('./icon.png'))
        self.setWindowTitle(f"Chronos Project Advanced Klicker™️ Application (CPAKA)")
        self._style_combobox = QComboBox()
        init_widget(self._style_combobox, "theme_combobox")
        self._style_combobox.addItems(style_names())
        self._style_combobox.textActivated.connect(self.change_style)
        self._style_combobox.setCurrentText(_theme)
        self._style_combobox.textActivated.emit(_theme)
        theme_label = QLabel("Theme:")
        init_widget(theme_label, "theme_label")
        theme_label.setBuddy(self._style_combobox)


        self.code_style = QComboBox()
        init_widget(self.code_style, "style_combobox")
        self.code_style.addItems(['dracula', 'default', 'material', 'github-dark', 'emacs', 'friendly', 'friendly_grayscale', 'colorful', 'autumn', 'murphy', 'manni', 'monokai', 'perldoc', 
            'pastie', 'borland', 'trac', 'native', 'fruity', 'bw', 'vim', 'vs', 'tango', 'rrt', 'xcode', 'igor', 'paraiso-light', 'paraiso-dark', 
            'lovelace', 'algol', 'algol_nu', 'arduino', 'rainbow_dash', 'abap', 'solarized-dark', 'solarized-light', 'sas', 'staroffice', 'stata', 
            'stata-light', 'stata-dark', 'inkpot', 'zenburn', 'gruvbox-dark', 'gruvbox-light', 'one-dark', 'lilypond', 'nord', 'nord-darker'])
        self.code_style.setCurrentText(_style)

        style_label = QLabel("Style:")
        style_label.setBuddy(self.code_style)
        self.code_style.textActivated.connect(self.on_style_changed)
        

        self.coordinates = QPushButton(f"({_coords[0]}, {_coords[1]})")
        self.coordinates.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        init_widget(self.coordinates, "coordinates_button", "CTRL + A to get mouse position")
        coordinates_label = QLabel("Coordinates:")
        init_widget(coordinates_label, "coordinates_label", "CTRL + A to get mouse position")
        coordinates_label.setBuddy(self.coordinates)
        self.coordinates.pressed.connect(self.press_coodinates)

        self.pixel = QPushButton(f"({_pixel[0]}, {_pixel[1]}, {_pixel[2]})")
        self.pixel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pixel.setIcon(QIcon("./cache/pixel.png"))
        init_widget(self.pixel, "pixel_button", "CTRL + A to get pixel color at mouse position")
        pixel_label = QLabel("Pixel color:")
        init_widget(pixel_label, "pixel_label", "CTRL + A to get pixel color at mouse position")
        pixel_label.setBuddy(self.pixel)
        self.pixel.pressed.connect(self.press_pixel)

        self.delay_spin = QSpinBox()
        init_widget(self.delay_spin, "delay_spin", "Delay between iterations")
        delay_label = QLabel("Delay:")
        init_widget(delay_label, "delay_label", "Delay between iterations")
        ms_label = QLabel("ms")
        init_widget(ms_label, "ms_label", "Delay between iterations")
        delay_label.setBuddy(self.delay_spin)
        ms_label.setBuddy(self.delay_spin)
        self.delay_spin.setMaximum(999999)
        self.delay_spin.setValue(_interval)
        self.delay_spin.setFixedWidth(90)
        self.delay_spin.editingFinished.connect(self.on_delay_edit)

        self.iterate_checkbox = QCheckBox('Iterate')
        init_widget(self.iterate_checkbox, "iterate_checkbox", "If unchecked script runs only once")
        self.iterate_checkbox.setChecked(_iterate)
        self.iterate_checkbox.checkStateChanged.connect(self.on_iterate_edit)
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(theme_label)
        top_layout.addWidget(self._style_combobox)
        top_layout.addWidget(style_label)
        top_layout.addWidget(self.code_style)

        top_layout.addStretch(1)

        second_layout = QHBoxLayout()
        second_layout.addWidget(coordinates_label)
        second_layout.addWidget(self.coordinates)
        second_layout.addWidget(pixel_label)
        second_layout.addWidget(self.pixel)
        second_layout.addStretch(1)

        third_layout = QHBoxLayout()
        third_layout.addWidget(self.iterate_checkbox)
        third_layout.addWidget(delay_label)
        third_layout.addWidget(self.delay_spin)
        third_layout.addWidget(ms_label)
        third_layout.addStretch(1)

        with open('script.py', mode='r') as file:
            _text = file.read().split('\n')
            _text.pop(0)
            _text.pop(0)
            _text.pop(0)
            for i in range(14):
                _text.pop()

            
            for i in range(len(_text)):
                _text[i] = _text[i][4:]
            _code = self.format_python_code_to_html('\n'.join(_text))
            # self.code.setText(_code)

        self.code = QTextEdit(_code)
        # print(_code)
        init_widget(self.code, "code_text")
        self.code.setTabStopDistance(28.0)
        # self.code.setFontFamily('Consolas')
        self.code.setFont("Consolas, 'Courier New', monospace")
        self.code.textChanged.connect(self.on_text_changed)

        self.run_button = QPushButton('Run')
        init_widget(self.run_button, "run_button", "Ctrl + Q to start/stop")
        self.run_button.setCheckable(True)
        self.run_button.pressed.connect(self.run)



        main_layout = QGridLayout(self)
        main_layout.addLayout(top_layout, 0, 0, 1, 2)
        main_layout.addLayout(second_layout, 1, 0, 1, 2)
        main_layout.addWidget(self.code, 2, 0, 1, 2)
        # main_layout.addWidget(spin_box, 3, 0, 1, 2)
        main_layout.addLayout(third_layout, 3, 0, 1, 2)
        main_layout.addWidget(self.run_button, 4, 0, 1, 2)

        # bottom_layout = QVBoxLayout()
        # bottom_layout.addStretch()
        # main_layout.addLayout(bottom_layout , 10, 0, 1, 2)

        # self.tt = StoppableThread(target=self.update_coordinates)
        # self.tt.start()
        # self.update_coordinates()
        # self.listener = Listener(on_press=self.on_press)
        # self.listener.start()

        h = GlobalHotKeys({
                '<ctrl>+a': self.on_activate_a,
                '<ctrl>+q': self.on_activate_q})
        h.start()
        
        spec = importlib.util.spec_from_file_location('./script.py', './script.py')
        foo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(foo)
        self.t = StoppableThread(foo.f)
        # self.t = Thread(target=foo.f, args=[self.flag])
        # self.t = multiprocessing.Process(target=foo.f, args=())

    def on_activate_a(self):
        _coords = Controller().position
        self.coordinates.setText(str(_coords))
        subprocess.run("clip", text=True, input=str(_coords)[1:-1])

        _pix = pyautogui.pixel(*_coords)
        a = QImage('./cache/pixel.png')
        a.fill(QColor(*_pix))
        a.save("./cache/pixel.png")

        self.pixel.setText(f"{_pix}") 
        self.pixel.setIcon(QIcon('./cache/pixel.png'))

        with open('./cache/cache.json', 'r') as f:
            js: dict = json.loads(f.read())
            js.update({"coords":[_coords[0], _coords[1]]})
            js.update({"pixel":[_pix[0], _pix[1], _pix[2]]})
            js = json.dumps(js)
        with open('./cache/cache.json', 'w+') as f:
            f.write(js)
        

    def on_activate_q(self):
        # self.run_button.setChecked(not self.run_button.isChecked())
        self.run_button.click()
    
    @Slot(str)
    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))
        with open('./cache/cache.json', 'r') as f:
            js: dict = json.loads(f.read())
            js.update({"theme": style_name})
            js = json.dumps(js)
        with open('./cache/cache.json', 'w+') as f:
            f.write(js)

    @Slot(str)
    def reject(self):
        self.t.stop()
        QApplication.quit()

    # def on_press(self, key: Key):
    #     # print(key)
    #     # print(Kb().modifiers)
    #     # print(KeyCode.from_dead(Key.ctrl_l).join(Key.end))
    #     if key == KeyCode(char='\x01'): # ctrl+a

        
    def on_delay_edit(self):
        with open('./cache/cache.json', 'r') as f:
            js: dict = json.loads(f.read())
            js.update({"interval": self.delay_spin.value()})
            js = json.dumps(js)
        with open('./cache/cache.json', 'w+') as f:
            f.write(js)

    def on_iterate_edit(self):
        with open('./cache/cache.json', 'r') as f:
            js: dict = json.loads(f.read())
            js.update({"iterate": self.iterate_checkbox.isChecked()})
            js = json.dumps(js)
        with open('./cache/cache.json', 'w+') as f:
            f.write(js)
    
    @Slot(str)
    def press_coodinates(self):
        subprocess.run("clip", text=True, input=self.coordinates.text()[1:-1])
        self.code.insertPlainText(self.coordinates.text()[1:-1])

    @Slot(str)
    def press_pixel(self):
        subprocess.run("clip", text=True, input=self.pixel.text())
        self.code.insertPlainText(self.pixel.text())

    @Slot(str)
    def run(self):
        print('run')
        if self.run_button.text() == 'Stop':
            self.t.stop()
            self.run_button.setText('Run')

        else:
            self.run_button.setText('Stop')
            c = self.code.toPlainText().replace('	', '    ')
            self.code.setText(c)
            c = c.split('\n')
            for i in range(len(c)):
                c[i] = f"    {c[i]}"
            c.insert(0, 'from utils import *\n\ndef main():')
            c.append(
                """
def f(timeout: int, iterate: bool):
    if iterate:
        while True:
            try:
                main()
                sleep(timeout)
            except Exception as e:
                logger.error(f'{e}')
    else:
        try:
            main()
        except Exception as e:
            logger.error(f"{e}")""")

            with open('./script.py', mode='w') as file:
                file.write('\n'.join(c))

            spec = importlib.util.spec_from_file_location('./script.py', './script.py')
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            self.t = StoppableThread(foo.f, self.delay_spin.value(), self.iterate_checkbox.isChecked())            
            self.t.start()
    

    def format_python_code_to_html(self, code: str) -> str:
        # Создаем объект лексера для Python
        lexer = get_lexer_by_name('python')
        # Создаем объект форматтера для HTML    
        # print(list(styles.get_all_styles()))
        formatter = HtmlFormatter(full=False, noclasses=True, nobackground=True, style=self.code_style.currentText())
        # Подсвечиваем код
        highlighted_code: str = highlight(code, lexer, formatter)
        for _f in functions:
            if _f in highlighted_code:
                highlighted_code = highlighted_code.replace(f'{_f}(', f'<span style="color:#dccd79">{_f}</span>(')
        return highlighted_code

    def on_style_changed(self):
        with open('./cache/cache.json', 'r') as f:
            js: dict = json.loads(f.read())
            js.update({"style" : self.code_style.currentText()})
            js = json.dumps(js)
        with open('./cache/cache.json', 'w+') as f:
            f.write(js)

        self.on_text_changed()

    def on_text_changed(self):
        self.code.textChanged.disconnect()
        pos = self.code.textCursor().position()
        text = self.format_python_code_to_html(self.code.toPlainText())
        self.code.setText(text)
        cursor = self.code.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, n=pos)
        self.code.setTextCursor(cursor)
        self.code.textChanged.connect(self.on_text_changed)
        

class StoppableThread(Thread):
    def __init__(self, target: callable, *args):
        Thread.__init__(self)
        self.target = target
        self.args = args
            
    def run(self):
        self.target(*self.args)
         
    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
 
    def stop(self):
        print("stop")
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            logger.error('Exception raise failure')
