import glob
import os
import ctypes
import importlib.util
import json
import threading
import pyperclip
import time
import pyautogui
import logging
from PIL import Image
from threading import Thread
from pynput.mouse import Controller 
from pynput.keyboard import GlobalHotKeys
from pygments import highlight
from pygments.lexers.python import PythonLexer
from pygments.formatters import HtmlFormatter
from common import description, color_f
from PySide6.QtCore import (Qt, Slot)
from PySide6.QtGui import (QIcon, QTextCursor, QColor, QImage, QPixmap, QPainter, QTransform, QBrush)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QPushButton,
                               QSpinBox, QStyleFactory, QTextBrowser, QTextEdit, QVBoxLayout, QWidget, QDialog, QTabWidget, QSizePolicy)

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


def sorted_glob():
    scripts = glob.glob('script_*.py')
    for i in range(len(scripts) - 1):
        for j in range(i + 1, len(scripts)):
            if int(scripts[j].replace('script_', '')[:-3]) < int(scripts[i].replace('script_', '')[:-3]):
                _script = scripts[j]
                scripts[j] = scripts[i]
                scripts[i] = _script
    return scripts

class Clicker(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs_dict: list[dict[QTextEdit, QSpinBox, QCheckBox, QPushButton, StoppableThread|None]] = []

        if not os.path.exists('./__pycache__/pixel.png'):
            _p = Image.new("RGB", (16, 16), 0xffffff)
            _p.save('./__pycache__/pixel.png')

        try:
            with open('./__pycache__/cache.json', 'r') as f:
                self.cache = json.load(f)
        except:
            with open('./__pycache__/cache.json', 'w+') as f:
                self.cache = {
                    "theme" : style_names()[0],
                    "style" : "dracula",
                    "coords" : [0, 0],
                    "pixel" : [255, 255, 255],
                    "window_properties": [0, 0, 400, 300],
                    "tabs": [{"interval":1000, "iterate" : True}]
                }
                _cache = json.dumps(self.cache)
                f.write(_cache)

        # Define the QPixmap (24x24 pixels)
        self.icon_pixmap = QPixmap(24, 24)
        self.icon_pixmap.fill(QColor(0, 0, 0, 0))  # Fill with a transparent background
        # Start painting on the QPixmap
        _painter = QPainter(self.icon_pixmap)
        _painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Transformation for rotation
        _transform = QTransform()
        _transform.translate(8,8)
        _transform.rotate(45)  # Rotate by 45 degrees
        # Draw the bottom white rectangle
        _painter.setBrush(QBrush(QColor("white")))
        _painter.setPen(Qt.PenStyle.NoPen)  # Remove border
        _painter.setTransform(_transform, True)  # Apply the transformation
        # Draw white rectangle with offset 
        rect_size = 12  # Size of the rectangles
        _painter.drawRoundedRect(-rect_size // 2 + 6, -rect_size // 2 + 6, rect_size, rect_size, 3, 3)
        # Draw the top rectangle
        _painter.setBrush(QBrush(QColor("#6374ce")))
        _painter.drawRoundedRect(-rect_size // 2, -rect_size // 2, rect_size, rect_size, 3, 3)
        # Finish painting
        _painter.end()        
        
        self.setWindowIcon(self.icon_pixmap)
        self.setWindowTitle(f"Chronos Project Advanced Klicker™️ Application (CPAKA)")
        self.setGeometry(self.cache['window_properties'][0], self.cache['window_properties'][1], self.cache['window_properties'][2], self.cache['window_properties'][3])
        self.style_combobox = QComboBox()
        init_widget(self.style_combobox, "theme_combobox")
        self.style_combobox.addItems(style_names())
        self.style_combobox.textActivated.connect(self.change_theme)
        self.style_combobox.setCurrentText(self.cache['theme'])
        self.style_combobox.textActivated.emit(self.cache['theme'])
        theme_label = QLabel("Theme:")
        init_widget(theme_label, "theme_label")
        theme_label.setBuddy(self.style_combobox)


        self.code_style = QComboBox()
        init_widget(self.code_style, "style_combobox")
        self.code_style.addItems(['dracula', 'default', 'material', 'github-dark', 'emacs', 'friendly', 'friendly_grayscale', 'colorful', 'autumn', 'murphy', 'manni', 'monokai', 'perldoc', 
            'pastie', 'borland', 'trac', 'native', 'fruity', 'bw', 'vim', 'vs', 'tango', 'rrt', 'xcode', 'igor', 'paraiso-light', 'paraiso-dark', 
            'lovelace', 'algol', 'algol_nu', 'arduino', 'rainbow_dash', 'abap', 'solarized-dark', 'solarized-light', 'sas', 'staroffice', 'stata', 
            'stata-light', 'stata-dark', 'inkpot', 'zenburn', 'gruvbox-dark', 'gruvbox-light', 'one-dark', 'lilypond', 'nord', 'nord-darker'])
        self.code_style.setCurrentText(self.cache['style'])

        style_label = QLabel("Style:")
        style_label.setBuddy(self.code_style)
        self.code_style.textActivated.connect(self.on_text_changed)
        

        self.coordinates = QPushButton(f"({self.cache['coords'][0]}, {self.cache['coords'][1]})")
        self.coordinates.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        init_widget(self.coordinates, "coordinates_button", "Ctrl + A to get mouse position")
        coordinates_label = QLabel("Coordinates:")
        init_widget(coordinates_label, "coordinates_label", "Ctrl + A to get mouse position")
        coordinates_label.setBuddy(self.coordinates)
        self.coordinates.pressed.connect(self.press_coodinates)

        self.pixel = QPushButton(f"({self.cache['pixel'][0]}, {self.cache['pixel'][1]}, {self.cache['pixel'][2]})")
        self.pixel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pixel.setIcon(QIcon("./__pycache__/pixel.png"))
        init_widget(self.pixel, "pixel_button", "Ctrl + A to get pixel color at mouse position")
        pixel_label = QLabel("Pixel color:")
        init_widget(pixel_label, "pixel_label", "Ctrl + A to get pixel color at mouse position")
        pixel_label.setBuddy(self.pixel)
        self.pixel.pressed.connect(self.press_pixel)

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

        self.tabs = QTabWidget()
        init_widget(self.tabs, "tabs_widget")
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tabs.setMovable(False)
        self.tabs.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # tabs.set
        scripts = sorted_glob()
        for script in scripts:
            with open(script, mode='r') as file:
                _text = file.read().split('\n')
                _text.pop(0)
                _text.pop(0)
                _text.pop(0)
                for i in range(18):
                    _text.pop()            
                for i in range(len(_text)):
                    _text[i] = _text[i][4:]
                _code = self.format_python_code_to_html('\n'.join(_text))

                self.tabs.addTab(self.make_tab(text=_code), script.replace('script_', '')[:-3])
        
        adrm = QHBoxLayout()
        add_button = QPushButton('Add Tab')
        add_button.setFixedWidth(100)
        add_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        add_button.clicked.connect(self.add_tab_clicked)
        self.rm_button =  QPushButton('Remove Tab')
        self.rm_button.setFixedWidth(100)
        self.rm_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.rm_button.clicked.connect(self.rm_tab_clicked)
        adrm.addWidget(add_button)
        adrm.addWidget(self.rm_button)
        adrm.addStretch(1)
        
        main_layout = QGridLayout(self)
        main_layout.addLayout(top_layout, 0, 0, 1, 2)
        main_layout.addLayout(second_layout, 1, 0, 1, 2)

        main_layout.addLayout(adrm, 2, 0, 1, 2)
        main_layout.addWidget(self.tabs, 3, 0, 1, 2)

        h = GlobalHotKeys({
                '<ctrl>+a': self.on_activate_a,
                '<ctrl>+q': self.on_activate_q,
                '<alt>+q': self.on_activate_q_alt})
        h.start()
        
        self.logs_thread = None


    @Slot()
    def add_tab_clicked(self):
        new_tab = self.make_tab()
        self.tabs.addTab(new_tab, f"{self.tabs.count()}")
        self.save_code(self.tabs.count() - 1, f"script_{self.tabs.count() - 1}")
    
    @Slot()
    def rm_tab_clicked(self):
        scripts = sorted_glob()
        for i in range(len(scripts)):
            if scripts[i] == f"script_{self.tabs.currentIndex()}.py":
                os.remove(scripts[i])
                for j in range(i + 1, len(scripts)):
                    os.rename(scripts[j], f"script_{int(scripts[j][7:-3])-1}.py")
                self.tabs.removeTab(self.tabs.currentIndex())
                for x in range(i, self.tabs.count()):
                    self.tabs.setTabText(x, f"{int(self.tabs.tabText(x))-1}")
                break


    def make_tab(self, text: str = ''):
        code = QTextEdit(text)
        init_widget(code, "code_text")
        code.setTabStopDistance(28.0)
        code.setFont("Consolas, 'Courier New', monospace")
        code.textChanged.connect(self.on_text_changed)

        delay_spin = QSpinBox()
        init_widget(delay_spin, "delay_spin", "Delay between iterations")
        delay_label = QLabel("Delay:")
        init_widget(delay_label, "delay_label", "Delay between iterations")
        ms_label = QLabel("ms")
        init_widget(ms_label, "ms_label", "Delay between iterations")
        delay_label.setBuddy(delay_spin)
        ms_label.setBuddy(delay_spin)
        delay_spin.setMaximum(999999)
        delay_spin.setValue(self.cache['tabs'][self.tabs.count()]['interval'] if len(self.cache['tabs']) > self.tabs.count() else 1000)
        delay_spin.setFixedWidth(90)

        iterate_checkbox = QCheckBox('Iterate')
        init_widget(iterate_checkbox, "iterate_checkbox", "If unchecked script runs only once")
        iterate_checkbox.setChecked(self.cache['tabs'][self.tabs.count()]['iterate'] if len(self.cache['tabs']) > self.tabs.count() else True)

        run_button = QPushButton('Run')
        init_widget(run_button, "run_button", "Ctrl + Q to start/stop\nAlt + Q to stop all")
        run_button.setCheckable(True)
        run_button.pressed.connect(self.run)

        third_layout = QHBoxLayout()
        third_layout.addWidget(iterate_checkbox)
        third_layout.addWidget(delay_label)
        third_layout.addWidget(delay_spin)
        third_layout.addWidget(ms_label)
        third_layout.addStretch(1)

        tabs_widget = QWidget()
        tabs_layout = QVBoxLayout(tabs_widget)
        tabs_layout.addWidget(code)
        tabs_layout.addLayout(third_layout)
        tabs_layout.addWidget(run_button)

        self.tabs_dict.append({
            'code' : code,
            'delay_spin' : delay_spin,
            'iterate_checkbox' : iterate_checkbox,
            'run_button' : run_button,
            'thread' : None
        })
        return tabs_widget
        

    @Slot(str)
    def run(self):
        i = self.tabs.currentIndex()
        if self.tabs_dict[i]['run_button'].text() == 'Stop':
            if self.tabs_dict[i]['thread'] is not None: self.tabs_dict[i]['thread'].stop()
            self.tabs_dict[i]['run_button'].setText('Run')
        else:
            self.tabs_dict[i]['run_button'].setText('Stop')

            self.save_code(self.tabs.currentIndex(), f"script_{i}")

            spec = importlib.util.spec_from_file_location(f'./script_{i}.py', f'./script_{i}.py')
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            self.tabs_dict[i]['thread'] = StoppableThread(foo.f, self.tabs_dict[i]['delay_spin'].value(), self.tabs_dict[i]['iterate_checkbox'].isChecked())            
            self.tabs_dict[i]['thread'].start()


    def save_code(self, index: int, name: str):
        c = self.tabs_dict[index]['code'].toPlainText().replace('	', '    ')
        self.tabs_dict[index]['code'].setText(c)
        c = c.split('\n')
        for i in range(len(c)):
            c[i] = f"    {c[i]}"
        c.insert(0, 'from utils import *\n\ndef main():')
        c.append("""
def f(timeout: int, iterate: bool):
    if iterate:
        while True:
            try:
                m = main()
                if m is not None: 
                    logger.warning(f"{m}")
                    return
                sleep(timeout)
            except Exception as e:
                logger.error(f'{e}')
    else:
        try:
            m = main()
            if m is not None: logger.warning(f"{m}")
        except Exception as e:
            logger.error(f"{e}")""")

        with open(f'./{name}.py', mode='w') as file:
            file.write('\n'.join(c))


    def save_all(self):
        for i in range(self.tabs.count()):
            self.save_code(i, f'script_{i}')


    @Slot(str)
    def on_text_changed(self):
        i = self.tabs.currentIndex()
        self.tabs_dict[i]['code'].textChanged.disconnect()
        pos = self.tabs_dict[i]['code'].textCursor().position()
        text = self.format_python_code_to_html(self.tabs_dict[i]['code'].toPlainText())
        self.tabs_dict[i]['code'].setText(text)

        text = self.tabs_dict[i]['code'].toPlainText()

        cursor = self.tabs_dict[i]['code'].textCursor()
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

        self.tabs_dict[i]['code'].setTextCursor(cursor)
        self.tabs_dict[i]['code'].textChanged.connect(self.on_text_changed)


    def on_activate_a(self):
        _coords = Controller().position
        self.coordinates.setText(str(_coords))
        pyperclip.copy(str(_coords)[1:-1])

        _pix = pyautogui.pixel(*_coords)
        a = QImage('./__pycache__/pixel.png')
        a.fill(QColor(*_pix))
        a.save("./__pycache__/pixel.png")

        self.pixel.setText(f"{_pix}") 
        self.pixel.setIcon(QIcon('./__pycache__/pixel.png'))
        

    def on_activate_q(self):
        i = self.tabs.currentIndex()
        self.tabs_dict[i]['run_button'].click()


    def on_activate_q_alt(self):
        for i in range(len(self.tabs_dict)):
            if self.tabs_dict[i]['thread'] is not None:
                self.tabs_dict[i]['thread'].stop()

    
    @Slot(str)
    def change_theme(self, style_name):
        QApplication.setStyle(QStyleFactory.create(style_name))


    @Slot(str)
    def closeEvent(self, close_event):
        if self.logs_thread is not None: self.logs_thread.stop()        
        _tabs = []
        for tab in self.tabs_dict:
            if tab['thread'] is not None: tab['thread'].stop()
            _tabs.append({
                'interval' : int(tab['delay_spin'].text()),
                'iterate' : tab['iterate_checkbox'].isChecked()
            })
        self.save_all()
        with open('./__pycache__/cache.json', 'r') as f:
            js: dict = json.loads(f.read())
            _g = self.geometry()
            _c = self.coordinates.text()[1:-1].split(', ')
            _p = self.pixel.text()[1:-1].split(', ')
            js.update({
                "theme": self.style_combobox.currentText(),
                "style": self.code_style.currentText(),
                "coords": [int(_c[0]), int(_c[1])],
                "pixel": [int(_p[0]), int(_p[1]), int(_p[2])],
                "window_properties":[_g.x(), _g.y(), _g.width(), _g.height()],
                "tabs": _tabs
            })
            js = json.dumps(js)
        with open('./__pycache__/cache.json', 'w+') as f:
            f.write(js)
        QApplication.quit()

    
    @Slot(str)
    def press_coodinates(self):
        pyperclip.copy(self.coordinates.text()[1:-1])
        self.tabs_dict[self.tabs.currentIndex()]['code'].insertPlainText(self.coordinates.text()[1:-1])


    @Slot(str)
    def press_pixel(self):
        pyperclip.copy(self.pixel.text())
        self.tabs_dict[self.tabs.currentIndex()]['code'].insertPlainText(self.pixel.text())


    def format_python_code_to_html(self, code: str) -> str:
        lexer = PythonLexer()
        formatter = HtmlFormatter(full=False, noclasses=True, nobackground=True, style=self.code_style.currentText())
        highlighted_code: str = highlight(code, lexer, formatter)
        for _f in functions:
            if _f in highlighted_code:
                highlighted_code = highlighted_code.replace(f'{_f}(', f'<span style="color:{color_f}">{_f}</span>(')
        return highlighted_code


    @Slot()
    def show_logs(self):
        class LogsWindow(QWidget):
            def __init__(self_logs):
                super().__init__()
                self_logs.setWindowIcon(self.icon_pixmap)
                self_logs.setWindowTitle('CPAKA logs')
                layout = QVBoxLayout()
                self_logs.text = QTextBrowser()
                self_logs.text.backwardAvailable.connect(self_logs.do_update)
                layout.addWidget(self_logs.text)                
                self_logs.setLayout(layout)

                self.logs_thread = StoppableThread(self_logs.update_logs)
                self.logs_thread.start()

            def do_update(self_logs):
                with open('./__pycache__/log.log', 'r') as f:
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
                self_cheat.setWindowIcon(self.icon_pixmap)
                self_cheat.setWindowTitle('CPAKA cheatsheet')
                self_cheat.setGeometry(self.geometry().x(), self.geometry().y(), 800, 600)
                layout = QVBoxLayout()
                self_cheat.text = QTextBrowser()

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
