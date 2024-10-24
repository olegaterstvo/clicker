import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_TAB  = 0x09
VK_MENU = 0x12

KEY_E = 0x45
KEY_W = 0x57

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize


example = \
"""from utils import *

def main():
    cpaka = pygetwindow.getWindowsWithTitle('(CPAKA)')[0]
    cpaka.activate()
    leftClick(cpaka.left+360, cpaka.top+80)
    
    return "Hello world"    # any not None return will stop main loop                                          

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
            logger.error(f"{e}")"""

_color_f = '#dccd79'
_color_v = '#8cdcfe'
_color_t = '#44c9b0'
_color_m = '#4fc1ff'

description = \
f"""<body style="font-size:14px"><span style="color:{_color_f}">log</span>(<code style="color:{_color_v}">message: <span style="color:{_color_t}">str</span></code>) - Write message into logs

<span style="color:{_color_f}">sleep</span>(<code style="color:{_color_v}">milliseconds: <span style="color:{_color_t}">int</span></code>) - Delay execution for a given time in <i>milliseconds</i>

<span style="color:{_color_f}">wait</span>(<code style="color:{_color_v}">milliseconds: <span style="color:{_color_t}">int</span></code>) - Alias for sleep()

<span style="color:{_color_f}">holdKey</span>(<code style="color:{_color_v}">hex_key_code: <span style="color:{_color_t}">Key</span>|<span style="color:{_color_t}">int</span></code>) - Performs button push action

<span style="color:{_color_f}">releaseKey</span>(<code style="color:{_color_v}">hex_key_code: <span style="color:{_color_t}">Key</span>|<span style="color:{_color_t}">int</span></code>) - Performs button release action

<span style="color:{_color_f}">pressKey</span>(<code style="color:{_color_v}">hex_key_code: <span style="color:{_color_t}">Key</span>|<span style="color:{_color_t}">int</span>, interval: <span style="color:{_color_t}">int</span> = 10</code>) - Performs push and then release actions
    <code style="color:{_color_v}">interval</code> : The amount of time to wait between push and release actions in <i>milliseconds</i>. Defafults to <code style="color:{_color_v}">10</code>ms

<span style="color:{_color_f}">getPixel</span>(<code style="color:{_color_v}">x: <span style="color:{_color_t}">int</span>, y:<span style="color:{_color_t}">int</span></code>) - Returns the color of the screen pixel at <code style="color:{_color_v}">x</code>, <code style="color:{_color_v}">y</code> as an RGB <span style="color:{_color_t}">tuple</span>, each color represented from 0 to 255.

<span style="color:{_color_f}">isMatchesColor</span>(<code style="color:{_color_v}">x: <span style="color:{_color_t}">int</span>, y:<span style="color:{_color_t}">int</span>, color: <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_t}">int</span>,<span style="color:{_color_t}">int</span>,<span style="color:{_color_t}">int</span>], tolerance: <span style="color:{_color_t}">int</span> = 0</code>) - Return <span style="color:{_color_m}">True</span> if the pixel at <code style="color:{_color_v}">x</code>, <code style="color:{_color_v}">y</code> is matches the expected color of the <i>RGB <span style="color:{_color_t}">tuple</span></i>, each color represented from 0 to 255, within an optional <code style="color:{_color_v}">tolerance</code>.

<span style="color:{_color_f}">leftClick</span>(<code style="color:{_color_v}">x: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, y: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, clicks_count: <span style="color:{_color_t}">int</span> = 1, interval: <span style="color:{_color_t}">float</span> = 0.0</code>) - Performs pressing a left mouse button click at given coordinates. If no arguments are passed, the button is clicked at the mouse cursor's current location.
    The <code style="color:{_color_v}">clicks_count</code> argument is an <span style="color:{_color_t}">int</span> of how many clicks to make, and defaults to 1.
    The <code style="color:{_color_v}">interval</code> argument is an <span style="color:{_color_t}">int</span> or <span style="color:{_color_t}">float</span> of how many seconds to wait in between each click

<span style="color:{_color_f}">rightClick</span>(<code style="color:{_color_v}">x: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, y: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, clicks_count: <span style="color:{_color_t}">int</span> = 1, interval: <span style="color:{_color_t}">float</span> = 0.0</code>) - Performs pressing a right mouse button click at given coordinates. If no arguments are passed, the button is clicked at the mouse cursor's current location.
    The <code style="color:{_color_v}">clicks_count</code> argument is an <span style="color:{_color_t}">int</span> of how many clicks to make, and defaults to 1.
    The <code style="color:{_color_v}">interval</code> argument is an <span style="color:{_color_t}">int</span> or <span style="color:{_color_t}">float</span> of how many seconds to wait in between each click

<span style="color:{_color_f}">middleClick</span>(<code style="color:{_color_v}">x: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, y: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, clicks_count: <span style="color:{_color_t}">int</span> = 1, interval: <span style="color:{_color_t}">float</span> = 0.0</code>) - Performs pressing a middle mouse button click at given coordinates. If no arguments are passed, the button is clicked at the mouse cursor's current location.
    The <code style="color:{_color_v}">clicks_count</code> argument is an <span style="color:{_color_t}">int</span> of how many clicks to make, and defaults to 1.
    The <code style="color:{_color_v}">interval</code> argument is an <span style="color:{_color_t}">int</span> or <span style="color:{_color_t}">float</span> of how many seconds to wait in between each click

<span style="color:{_color_f}">moveTo</span>(<code style="color:{_color_v}">x: <span style="color:{_color_t}">int</span>, y: <span style="color:{_color_t}">int</span>, duration: <span style="color:{_color_t}">int</span> = 0</code>) - Moves the mouse cursor to a point on the screen.
    <code style="color:{_color_v}">duration</code> : The amount of time in <i>milliseconds</i> it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default.

<span style="color:{_color_f}">moveRel</span>(<code style="color:{_color_v}">x_offset: <span style="color:{_color_t}">int</span>, y_offset: <span style="color:{_color_t}">int</span>, duration: <span style="color:{_color_t}">int</span> = 0</code>) - Moves the mouse cursor to a point on the screen, relative to its current position.
    <code style="color:{_color_v}">x_offset</code> : How far left (for negative values) or right (for positive values) to move the cursor.
    <code style="color:{_color_v}">y_offset</code> : How far up (for negative values) or down (for positive values) to move the cursor.
    <code style="color:{_color_v}">duration</code> : The amount of time in <i>milliseconds</i> it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default.

<span style="color:{_color_f}">dragTo</span>(<code style="color:{_color_v}">x: <span style="color:{_color_t}">int</span>, y: <span style="color:{_color_t}">int</span>, duration: <span style="color:{_color_t}">int</span> = 0, button: <span style="color:{_color_t}">Literal</span>['left', 'right', 'middle'] = 'left'</code>) - Performs a mouse drag (mouse movement while a button is held down) to a point on the screen.
    <code style="color:{_color_v}">duration</code> : The amount of time in <i>milliseconds</i> it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default.    
    <code style="color:{_color_v}">button</code> : The mouse button to perform drag with. Might be one of the folowing: <code style="color:{_color_v}">'left'</code>, <code style="color:{_color_v}">'right'</code>, <code style="color:{_color_v}">'middle'</code> 

<span style="color:{_color_f}">dragRel</span>(<code style="color:{_color_v}">x_offset: <span style="color:{_color_t}">int</span>, y_offset: <span style="color:{_color_t}">int</span>, duration: <span style="color:{_color_t}">int</span> = 0, button: <span style="color:{_color_t}">Literal</span>['left', 'right', 'middle'] = 'left'</code>) - Performs a mouse drag (mouse movement while a button is held down) to a point on the screen.
    <code style="color:{_color_v}">x_offset</code> : How far left (for negative values) or right (for positive values) to move the cursor.
    <code style="color:{_color_v}">y_offset</code> : How far up (for negative values) or down (for positive values) to move the cursor.
    <code style="color:{_color_v}">duration</code> : The amount of time in <i>milliseconds</i> it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default.    
    <code style="color:{_color_v}">button</code> : The mouse button to perform drag with. Might be one of the folowing: <code style="color:{_color_v}">'left'</code>, <code style="color:{_color_v}">'right'</code>, <code style="color:{_color_v}">'middle'</code> 

<span style="color:{_color_f}">scroll</span>(<code style="color:{_color_v}">clicks: <span style="color:{_color_t}">float</span>, x: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, y: <span style="color:{_color_t}">int</span>|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span></code>) - Performs a scroll of the mouse scroll wheel.
    <code style="color:{_color_v}">clicks</code> : The amount of scrolling to perform.
    The <code style="color:{_color_v}">x</code> and <code style="color:{_color_v}">y</code> parameters detail where the mouse event happens. If <i><span style="color:{_color_m}">None</span></i>, the current mouse position is used.

<span style="color:{_color_f}">write</span>(<code style="color:{_color_v}">message: <span style="color:{_color_t}">str</span>, interval: <span style="color:{_color_t}">int</span> = 0</code>) - Performs a keyboard key press down, followed by a release, for each of the characters in message.
    <code style="color:{_color_v}">message</code> : The characters to be pressed.
    <code style="color:{_color_v}">interval</code> : The number of <i>milliseconds</i> in between each press. 0 by default, for no pause in between presses.

<span style="color:{_color_f}">screenshot</span>(<code style="color:{_color_v}">image_file_name: <span style="color:{_color_t}">str</span> = 'screenshot.png', region: <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_t}">int</span>,<span style="color:{_color_t}">int</span>,<span style="color:{_color_t}">int</span>,<span style="color:{_color_t}">int</span>]|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, all_screens: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">False</span></code>) - Takes screenshot and saves it with given <code style="color:{_color_v}">image_file_name</code>
    <code style="color:{_color_v}">image_file_name</code> : Image file name to be saved with.    
    <code style="color:{_color_v}">region</code> : Part of screen to capture. <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x_start, y_start, x_offset, y_offset]</code>.    
    <code style="color:{_color_v}">all_screens</code> : If <i><span style="color:{_color_m}">True</span></i> captures all screens, otherwise only main screen. Defaults to <i><span style="color:{_color_m}">False</span></i>

<span style="color:{_color_f}">locateOnImage</span>(<code style="color:{_color_v}">what_to_find: <span style="color:{_color_t}">str</span>, where_to_find: <span style="color:{_color_t}">str</span>, grayscale: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span>, region: <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>]|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, confidence: <span style="color:{_color_t}">float</span> = 0.999, return_center: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span></code>) - Locates one image on the other image.
    <code style="color:{_color_v}">what_to_find</code> : Path to image to find.
    <code style="color:{_color_v}">where_to_find</code> : Path to image where to find first image.
    <code style="color:{_color_v}">grayscale</code> : Whether to convert images to grayscale. Defaults to <i><span style="color:{_color_m}">True</span></i>.
    <code style="color:{_color_v}">region</code> : Part of image where to find. <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x_start, y_start, x_offset, y_offset]</code>.
    <code style="color:{_color_v}">confidence</code> : Between 0 and 1.
    <code style="color:{_color_v}">return_center</code> : If <i><span style="color:{_color_m}">True</span></i> retuns <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x, y]</code> of the center of located image, otherwise returns <span style="color:{_color_t}">tuple</span> of xy of top left of the image and width and height (<code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x, y, w, h]</code>)
    
    If image not found returns <b><code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>] | <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>]</code></b>

<span style="color:{_color_f}">locateAllOnImage</span>(<code style="color:{_color_v}">what_to_find: <span style="color:{_color_t}">str</span>, where_to_find: <span style="color:{_color_t}">str</span>, grayscale: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span>, 
                     region: <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>]|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>,
                     confidence: <span style="color:{_color_t}">float</span> = 0.999, return_center: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span>
                    </code>) - Locates one image on the other image.    
    <code style="color:{_color_v}">what_to_find</code> : Path to image to find.
    <code style="color:{_color_v}">where_to_find</code> : Path to image where to find first image.
    <code style="color:{_color_v}">grayscale</code> : Whether to convert images to grayscale. Defaults to <i><span style="color:{_color_m}">True</span></i>.
    <code style="color:{_color_v}">region</code> : Part of image where to find. <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x_start, y_start, x_offset, y_offset]</code>.
    <code style="color:{_color_v}">confidence</code> : Between 0 and 1.
    <code style="color:{_color_v}">return_center</code> : If <i><span style="color:{_color_m}">True</span></i> retuns <code style="color:{_color_v}"><span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[x, y]]</code> of the center of located image, otherwise returns <span style="color:{_color_t}">list</span> of <span style="color:{_color_t}">tuple</span> of xy of top left of the image and width and height (<code style="color:{_color_v}"><span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[x, y, w, h]]</code>)
    
    If image not found returns <b><code style="color:{_color_v}"><span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>]] | <span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>]]</code></b>

<span style="color:{_color_f}">locateOnScreen</span>(<code style="color:{_color_v}">image: <span style="color:{_color_t}">str</span>, min_search_time: <span style="color:{_color_t}">int</span> = 0, grayscale: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span>, region: <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>]|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>, confidence: <span style="color:{_color_t}">float</span> = 0.999, return_center: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span></code>) - Locates image on screen
    <code style="color:{_color_v}">image</code> : Path to image to find.
    <code style="color:{_color_v}">min_search_time</code> : Amount of time in <i>milliseconds</i> to repeat taking screenshots and trying to locate a match. The default of 0 performs a single search.
    <code style="color:{_color_v}">grayscale</code> : Whether to convert images to grayscale. Defaults to <i><span style="color:{_color_m}">True</span></i>.
    <code style="color:{_color_v}">region</code> : Part of image where to find. <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x_start, y_start, x_offset, y_offset]</code>.
    <code style="color:{_color_v}">confidence</code> : Between 0 and 1.
    <code style="color:{_color_v}">return_center</code> : If <i><span style="color:{_color_m}">True</span></i> retuns <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x, y]</code> of the center of located image, otherwise returns <span style="color:{_color_t}">tuple</span> of xy of top left of the image and width and height (<code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x, y, w, h]</code>)
    
    If image not found returns <b><code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>] | <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>]</code></b>

<span style="color:{_color_f}">locateAllOnScreen</span>(<code style="color:{_color_v}">image: <span style="color:{_color_t}">str</span>, grayscale: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span>, 
                     region: <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>, <span style="color:{_color_t}">int</span>]|<span style="color:{_color_m}">None</span> = <span style="color:{_color_m}">None</span>,
                     confidence: <span style="color:{_color_t}">float</span> = 0.999, return_center: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span>
                    </code>) - Locates image on window
    <code style="color:{_color_v}">image</code> : Path to image to find.
    <code style="color:{_color_v}">grayscale</code> : Whether to convert images to grayscale. Defaults to <i><span style="color:{_color_m}">True</span></i>.
    <code style="color:{_color_v}">region</code> : Part of image where to find. <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x_start, y_start, x_offset, y_offset]</code>.
    <code style="color:{_color_v}">confidence</code> : Between 0 and 1.
    <code style="color:{_color_v}">return_center</code> : If <i><span style="color:{_color_m}">True</span></i> retuns <code style="color:{_color_v}"><span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[x, y]]</code> of the center of located image, otherwise returns <span style="color:{_color_t}">list</span> of <span style="color:{_color_t}">tuple</span> of xy of top left of the image and width and height (<code style="color:{_color_v}"><span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[x, y, w, h]]</code>)
    
    If image not found returns <b><code style="color:{_color_v}"><span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>]] | <span style="color:{_color_t}">list</span>[<span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>]]</code></b>

<span style="color:{_color_f}">locateOnWindow</span>(<code style="color:{_color_v}">image: <span style="color:{_color_t}">str</span>, window_title: <span style="color:{_color_t}">str</span>, grayscale: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span>, confidence: <span style="color:{_color_t}">float</span> = 0.999, return_center: <span style="color:{_color_t}">bool</span> = <span style="color:{_color_m}">True</span></code>) - Locates image on window
    <code style="color:{_color_v}">image</code> : Path to image to find.
    <code style="color:{_color_v}">min_search_time</code> : Amount of time in <i>milliseconds</i> to repeat taking screenshots and trying to locate a match. The default of 0 performs a single search.
    <code style="color:{_color_v}">grayscale</code> : Whether to convert images to grayscale. Defaults to <i><span style="color:{_color_m}">True</span></i>.
    <code style="color:{_color_v}">region</code> : Part of image where to find. <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x_start, y_start, x_offset, y_offset]</code>.
    <code style="color:{_color_v}">confidence</code> : Between 0 and 1.
    <code style="color:{_color_v}">return_center</code> : If <i><span style="color:{_color_m}">True</span></i> retuns <code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x, y]</code> of the center of located image, otherwise returns <span style="color:{_color_t}">tuple</span> of xy of top left of the image and width and height (<code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[x, y, w, h]</code>)
    
    If image not found returns <b><code style="color:{_color_v}"><span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>] | <span style="color:{_color_t}">tuple</span>[<span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>, <span style="color:{_color_m}">None</span>]</code></b>
</body>
"""
