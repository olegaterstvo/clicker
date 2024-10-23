import os
import ctypes
import importlib.util
import json
import threading
import subprocess
import time
import pyautogui
import logging
from PIL import Image
from threading import Thread
from pynput.mouse import Controller 
from pynput.keyboard import GlobalHotKeys
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from PySide6.QtCore import (Qt, Slot)
from PySide6.QtGui import (QIcon, QTextCursor, QColor, QImage)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QSpinBox, QStyleFactory, QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QDialog)

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


class Clicker(QWidget):
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
                _window_properties = _cache['window_properties']                
        except:
            with open('./cache/cache.json', 'w+') as f:
                _theme = style_names()[0]
                _style = "dracula"
                _coords = [0, 0]
                _pixel = [255, 255, 255]
                _interval = 1000
                _iterate = True
                _window_properties = [0, 0, 400, 300]
                _cache = {
                    "theme" : _theme,
                    "style" : _style,
                    "coords" : _coords,
                    "pixel" : _pixel,
                    "interval" : _interval,
                    "iterate" : _iterate,
                    "window_properties": _window_properties
                }
                _cache = json.dumps(_cache)
                f.write(_cache)

        self.setWindowIcon(QIcon('./icon.png'))
        self.setWindowTitle(f"Chronos Project Advanced Klicker™️ Application (CPAKA)")
        self.setGeometry(_window_properties[0], _window_properties[1], _window_properties[2], _window_properties[3])
        self.style_combobox = QComboBox()
        init_widget(self.style_combobox, "theme_combobox")
        self.style_combobox.addItems(style_names())
        self.style_combobox.textActivated.connect(self.change_style)
        self.style_combobox.setCurrentText(_theme)
        self.style_combobox.textActivated.emit(_theme)
        theme_label = QLabel("Theme:")
        init_widget(theme_label, "theme_label")
        theme_label.setBuddy(self.style_combobox)


        self.code_style = QComboBox()
        init_widget(self.code_style, "style_combobox")
        self.code_style.addItems(['dracula', 'default', 'material', 'github-dark', 'emacs', 'friendly', 'friendly_grayscale', 'colorful', 'autumn', 'murphy', 'manni', 'monokai', 'perldoc', 
            'pastie', 'borland', 'trac', 'native', 'fruity', 'bw', 'vim', 'vs', 'tango', 'rrt', 'xcode', 'igor', 'paraiso-light', 'paraiso-dark', 
            'lovelace', 'algol', 'algol_nu', 'arduino', 'rainbow_dash', 'abap', 'solarized-dark', 'solarized-light', 'sas', 'staroffice', 'stata', 
            'stata-light', 'stata-dark', 'inkpot', 'zenburn', 'gruvbox-dark', 'gruvbox-light', 'one-dark', 'lilypond', 'nord', 'nord-darker'])
        self.code_style.setCurrentText(_style)

        style_label = QLabel("Style:")
        style_label.setBuddy(self.code_style)
        self.code_style.textActivated.connect(self.on_text_changed)
        

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

        self.iterate_checkbox = QCheckBox('Iterate')
        init_widget(self.iterate_checkbox, "iterate_checkbox", "If unchecked script runs only once")
        self.iterate_checkbox.setChecked(_iterate)

        self.logs_button = QPushButton("Logs")
        init_widget(self.logs_button, "logs_button", "Show logs")
        self.logs_button.pressed.connect(self.show_logs)
        self.logs_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.logs_window = None

        self.cheatsheet_button = QPushButton("Cheatsheet")
        init_widget(self.cheatsheet_button, "cheatsheet_button", "Show cheatsheet")
        self.cheatsheet_button.pressed.connect(self.show_cheatsheet)
        self.cheatsheet_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.cheatsheet_window = None
        
        top_layout = QHBoxLayout()
        top_layout.addWidget(theme_label)
        top_layout.addWidget(self.style_combobox)
        top_layout.addWidget(style_label)
        top_layout.addWidget(self.code_style)
        top_layout.addWidget(self.logs_button)
        top_layout.addStretch(1)

        second_layout = QHBoxLayout()
        second_layout.addWidget(coordinates_label)
        second_layout.addWidget(self.coordinates)
        second_layout.addWidget(pixel_label)
        second_layout.addWidget(self.pixel)
        second_layout.addWidget(self.cheatsheet_button)
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

        self.code = QTextEdit(_code)
        init_widget(self.code, "code_text")
        self.code.setTabStopDistance(28.0)
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
        main_layout.addLayout(third_layout, 3, 0, 1, 2)
        main_layout.addWidget(self.run_button, 4, 0, 1, 2)

        h = GlobalHotKeys({
                '<ctrl>+a': self.on_activate_a,
                '<ctrl>+q': self.on_activate_q})
        h.start()
        
        self.t = None
        self.logs_thread = None


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
        

    def on_activate_q(self):
        self.run_button.click()

    
    @Slot(str)
    def change_style(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))


    @Slot(str)
    def closeEvent(self, close_event):
        if self.t is not None: self.t.stop()
        if self.logs_thread is not None: self.logs_thread.stop()        
        self.save_code()
        with open('./cache/cache.json', 'r') as f:
            js: dict = json.loads(f.read())
            _g = self.geometry()
            _c = self.coordinates.text()[1:-1].split(', ')
            _p = self.pixel.text()[1:-1].split(', ')
            js.update({
                "theme": self.style_combobox.currentText(),
                "style": self.code_style.currentText(),
                "coords": [int(_c[0]), int(_c[1])],
                "pixel": [int(_p[0]), int(_p[1]), int(_p[2])],
                "interval": int(self.delay_spin.text()),
                "iterate": self.iterate_checkbox.isChecked(),
                "window_properties":[_g.x(), _g.y(), _g.width(), _g.height()]
                })
            js = json.dumps(js)
        with open('./cache/cache.json', 'w+') as f:
            f.write(js)
        QApplication.quit()

    
    @Slot(str)
    def press_coodinates(self):
        subprocess.run("clip", text=True, input=self.coordinates.text()[1:-1])
        self.code.insertPlainText(self.coordinates.text()[1:-1])


    @Slot(str)
    def press_pixel(self):
        subprocess.run("clip", text=True, input=self.pixel.text())
        self.code.insertPlainText(self.pixel.text())


    def save_code(self):
        c = self.code.toPlainText().replace('	', '    ')
        self.code.setText(c)
        c = c.split('\n')
        for i in range(len(c)):
            c[i] = f"    {c[i]}"
        c.insert(0, 'from utils import *\n\ndef main():')
        c.append("""
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


    @Slot(str)
    def run(self):
        if self.run_button.text() == 'Stop':
            if self.t is not None: self.t.stop()
            self.run_button.setText('Run')
        else:
            self.run_button.setText('Stop')
            self.save_code()

            spec = importlib.util.spec_from_file_location('./script.py', './script.py')
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            self.t = StoppableThread(foo.f, self.delay_spin.value(), self.iterate_checkbox.isChecked())            
            self.t.start()
    

    def format_python_code_to_html(self, code: str) -> str:
        lexer = get_lexer_by_name('python')
        formatter = HtmlFormatter(full=False, noclasses=True, nobackground=True, style=self.code_style.currentText())
        highlighted_code: str = highlight(code, lexer, formatter)
        for _f in functions:
            if _f in highlighted_code:
                highlighted_code = highlighted_code.replace(f'{_f}(', f'<span style="color:#dccd79">{_f}</span>(')
        return highlighted_code


    @Slot(str)
    def on_text_changed(self):
        self.code.textChanged.disconnect()
        pos = self.code.textCursor().position()
        text = self.format_python_code_to_html(self.code.toPlainText())
        self.code.setText(text)

        text = self.code.toPlainText()

        cursor = self.code.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor, n=pos)
        
        if text[pos-1:pos] == '\n':
            count = 0
            for space in (l:=text[:pos-1].split('\n')[-1]):
                if space != ' ':
                    break
                count += 1
            if any(kw in l for kw in ['break', 'continue', 'return', 'raise']):
                count -= 4
            indent = ''
            for _ in range(count):
                indent += ' '
            if text[pos-2:pos] == ':\n':
                indent +='    '
            cursor.insertText(indent)   # TODO figure out how to handle deletions

        self.code.setTextCursor(cursor)
        self.code.textChanged.connect(self.on_text_changed)

    @Slot()
    def show_logs(self):
        class LogsWindow(QWidget):
            def __init__(self_logs):
                super().__init__()
                self_logs.setWindowIcon(QIcon('./icon.png'))
                self_logs.setWindowTitle('CPAKA logs')
                layout = QVBoxLayout()
                self_logs.text = QTextBrowser()
                self_logs.text.backwardAvailable.connect(self_logs.do_update)
                layout.addWidget(self_logs.text)                
                self_logs.setLayout(layout)

                self.logs_thread = StoppableThread(self_logs.update_logs)
                self.logs_thread.start()

            def do_update(self_logs):
                with open('./cache/log.log', 'r') as f:
                    _l = f.read().split('\n')
                    _l.reverse()
                    _l = '<br>'.join(_l)
                    _l = _l.replace('[', '<span style="color:#ababab">[')\
                        .replace(']', ']</span>').replace('INFO', '<span style="color:#6374ce">INFO</span>')\
                        .replace('WARNING', '<span style="color:#f6ba6f">WARNING</span>').replace('ERROR', '<span style="color:#d34748">ERROR</span>')
                    _pos = self_logs.text.verticalScrollBar().value()
                    self_logs.text.setText(_l)
                    self_logs.text.verticalScrollBar().setValue(_pos)

            def update_logs(self_logs):
                while True:
                    self_logs.text.backwardAvailable.emit(False)
                    time.sleep(1)
            
            def closeEvent(self_logs, close_event):
                self.logs_thread.stop()
                self_logs.close()   


        if self.logs_window is None or not self.logs_window.isVisible():
            self.logs_window = LogsWindow()
            self.logs_window.show()
        else:
            if self.logs_thread is not None: self.logs_thread.stop()
            self.logs_window.close()
            self.logs_window = None

    @Slot()
    def show_cheatsheet(self):
        class CheatsheetWindow(QWidget):
            def __init__(self_cheat):
                super().__init__()
                self_cheat.setWindowIcon(QIcon('./icon.png'))
                self_cheat.setWindowTitle('CPAKA cheatsheet')
                self_cheat.setGeometry(self.geometry().x(), self.geometry().y(), 800, 600)
                layout = QVBoxLayout()
                self_cheat.text = QTextBrowser()

                from common import description
                self_cheat.text.setText(description.replace('\n', '<br>'))

                layout.addWidget(self_cheat.text)                
                self_cheat.setLayout(layout)
            
        if self.cheatsheet_window is None or not self.cheatsheet_window.isVisible():
            self.cheatsheet_window = CheatsheetWindow()
            self.cheatsheet_window.show()
        else:
            self.cheatsheet_window.close()
            self.cheatsheet_window = None


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
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            logger.error('Exception raise failure')
