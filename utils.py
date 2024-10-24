import time
import pyautogui
import pygetwindow
import pynput.keyboard as kb
import pynput.mouse as ms
import ctypes
import logging
from typing import Literal
from keys import Key
from common import *

IS_OPENCV_INSTALLED: bool = False
try:
    import cv2  # type:ignore
    IS_OPENCV_INSTALLED = True
except ImportError:
    pass

logger = logging.getLogger("root")

def log(message: str):
    """write message into logs"""
    logger.info(f"{message}")

def sleep(milliseconds: int):
    """Delay execution for a given time in *milliseconds*"""
    _timeout = milliseconds/1000
    time.sleep(_timeout)

def wait(milliseconds: int):
    """Alias for sleep()"""
    sleep(milliseconds)

def holdKey(hex_key_code: Key|int):
    """Performs button push action"""
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hex_key_code))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def releaseKey(hex_key_code: Key|int):
    """Performs button release action"""
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hex_key_code,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def pressKey(hex_key_code: Key|int, interval: int = 10):
    """Performs push and then release actions
    
    `interval` : The amount of time to wait between push and release actions in *milliseconds*. Defafults to `10`ms"""
    holdKey(hex_key_code)
    time.sleep(interval/1000)
    releaseKey(hex_key_code)

def getPixel(x: int, y:int) -> tuple[int, int, int]:
    """Returns the color of the screen pixel at `x`, `y` as an RGB tuple, each color represented from *0* to *255*."""
    return pyautogui.pixel(x, y)

def isMatchesColor(x: int, y:int, color: tuple[int,int,int], tolerance: int = 0) -> bool:
    """Return True if the pixel at `x`, `y` is matches the expected color of the *RGB tuple*, each color represented from 0 to 255, within an optional `tolerance`."""
    return pyautogui.pixelMatchesColor(x=x, y=y, expectedRGBColor=color, tolerance=tolerance)

def leftClick(x: int|None = None, y: int|None = None, clicks_count: int = 1, interval: float = 0.0):
    """Performs pressing a left mouse button click at given coordinates. If no arguments are passed, the button is clicked at the mouse cursor's current location.

    The `clicks_count` argument is an int of how many clicks to make, and defaults to 1.

    The `interval` argument is an int or float of how many seconds to wait in between each click"""
    pyautogui.click(x=x, y=y, clicks=clicks_count, interval=interval, button="left")

def rightClick(x: int|None = None, y: int|None = None, clicks_count: int = 1, interval: float = 0.0):
    """Performs pressing a right mouse button click at given coordinates. If no arguments are passed, the button is clicked at the mouse cursor's current location.

    The `clicks_count` argument is an int of how many clicks to make, and defaults to 1.

    The `interval` argument is an int or float of how many seconds to wait in between each click"""
    pyautogui.click(x=x, y=y, clicks=clicks_count, interval=interval, button="right")

def middleClick(x: int|None = None, y: int|None = None, clicks_count: int = 1, interval: float = 0.0):
    """Performs pressing a middle mouse button click at given coordinates. If no arguments are passed, the button is clicked at the mouse cursor's current location.

    The `clicks_count` argument is an int of how many clicks to make, and defaults to 1.

    The `interval` argument is an int or float of how many seconds to wait in between each click"""
    pyautogui.click(x=x, y=y, clicks=clicks_count, interval=interval, button="middle")

def moveTo(x: int, y: int, duration: int = 0):
    """Moves the mouse cursor to a point on the screen.

    `duration` : The amount of time in *milliseconds* it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default."""
    pyautogui.moveTo(x=x, y=y, duration=duration/1000)

def moveRel(x_offset: int, y_offset: int, duration: int = 0):
    """Moves the mouse cursor to a point on the screen, relative to its current position.
    
    `x_offset` : How far left (for negative values) or right (for positive values) to move the cursor.
    `y_offset` : How far up (for negative values) or down (for positive values) to move the cursor.
    `duration` : The amount of time in *milliseconds* it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default."""
    pyautogui.moveRel(xOffset=x_offset, yOffset=y_offset, duration=duration/1000)

def dragTo(x: int, y: int, duration: int = 0, button: Literal['left', 'right', 'middle'] = 'left'):
    """Performs a mouse drag (mouse movement while a button is held down) to a point on the screen.

    `duration` : The amount of time in *milliseconds* it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default.    
    `button` : The mouse button to perform drag with. Might be one of the folowing: `'left'`, `'right'`, `'middle'` """
    pyautogui.dragTo(x=x, y=y, duration=duration/1000, button=button)

def dragRel(x_offset: int, y_offset: int, duration: int = 0, button: Literal['left', 'right', 'middle'] = 'left'):
    """Performs a mouse drag (mouse movement while a button is held down) to a point on the screen.

    `x_offset` : How far left (for negative values) or right (for positive values) to move the cursor.
    `y_offset` : How far up (for negative values) or down (for positive values) to move the cursor.
    `duration` : The amount of time in *milliseconds* it takes to move the mouse cursor to the xy coordinates. If 0, then the mouse cursor is moved instantaneously. 0 by default.    
    `button` : The mouse button to perform drag with. Might be one of the folowing: `'left'`, `'right'`, `'middle'` """
    pyautogui.dragRel(xOffset=x_offset, yOffset=y_offset, duration=duration/1000, button=button)

def scroll(clicks: float, x: int|None = None, y: int|None = None):
    """Performs a scroll of the mouse scroll wheel.

    `clicks` : The amount of scrolling to perform.

    The `x` and `y` parameters detail where the mouse event happens. If *None*, the current mouse position is used."""
    pyautogui.scroll(clicks=clicks, x=x, y=y)

def write(message: str, interval: int = 0):
    """Performs a keyboard key press down, followed by a release, for each of the characters in message.
    
    `message` : The characters to be pressed.
    `interval` : The number of *milliseconds* in between each press. 0 by default, for no pause in between presses."""

    pyautogui.typewrite(message=message, interval=interval/1000)

def screenshot(image_file_name: str = 'screenshot.png', region: tuple[int,int,int,int]|None = None, all_screens: bool = False):
    """Takes screenshot and saves it with given `image_file_name`
    
    `image_file_name` : Image file name to be saved with.    
    `region` : Part of screen to capture. `tuple[x_start, y_start, x_offset, y_offset]`.    
    `all_screens` : If *True* captures all screens, otherwise only main screen. Defaults to *False*"""
    pyautogui.screenshot(imageFilename=f"./images/{image_file_name}", region=region, allScreens=all_screens)

def locateOnImage(what_to_find: str, where_to_find: str, grayscale: bool = True, region: tuple[int, int, int, int]|None = None, confidence: float = 0.999, return_center: bool = True):
    """Locates one image on the other image.
    
    `what_to_find` : Path to image to find.
    `where_to_find` : Path to image where to find first image.
    `grayscale` : Whether to convert images to grayscale. Defaults to *True*.
    `region` : Part of image where to find. `tuple[x_start, y_start, x_offset, y_offset]`.
    `confidence` : Between 0 and 1.
    `return_center` : If *True* retuns `tuple[x, y]` of the center of located image, otherwise returns tuple of xy of top left of the image and width and height (`tuple[x, y, w, h]`)
    
    If image not found returns **`tuple[None, None] | tuple[None, None, None, None]`**"""
    try:
        if IS_OPENCV_INSTALLED:
            a = pyautogui.locate(needleImage=f"./images/{what_to_find}", haystackImage=f"./images/{where_to_find}", grayscale=grayscale, region=region, confidence=confidence)
        else:
            a = pyautogui.locate(needleImage=f"./images/{what_to_find}", haystackImage=f"./images/{where_to_find}", grayscale=grayscale, region=region)
    except pyautogui.ImageNotFoundException as e:
        logger.warning('Image not found')
        if return_center:
            return None, None
        else :
            return None, None, None, None
    
    if return_center:
        return a.left + a.width//2, a.top + a.height//2 
    else:
        return a.left, a.top, a.width, a.height
    
def locateOnScreen(image: str, min_search_time: int = 0, grayscale: bool = True, region: tuple[int, int, int, int]|None = None, confidence: float = 0.999, return_center: bool = True):
    """Locates image on screen
    
    `image` : Path to image to find.
    `min_search_time` : Amount of time in *milliseconds* to repeat taking screenshots and trying to locate a match. The default of 0 performs a single search.
    `grayscale` : Whether to convert images to grayscale. Defaults to *True*.
    `region` : Part of image where to find. `tuple[x_start, y_start, x_offset, y_offset]`.
    `confidence` : Between 0 and 1.
    `return_center` : If *True* retuns `tuple[x, y]` of the center of located image, otherwise returns tuple of xy of top left of the image and width and height (`tuple[x, y, w, h]`)
    
    If image not found returns **`tuple[None, None] | tuple[None, None, None, None]`**"""
    try:
        if IS_OPENCV_INSTALLED:
            a = pyautogui.locateOnScreen(image=f"./images/{image}", minSearchTime=min_search_time/1000, grayscale=grayscale, region=region, confidence=confidence)
        else:
            a = pyautogui.locateOnScreen(image=f"./images/{image}", minSearchTime=min_search_time/1000, grayscale=grayscale, region=region)
    except pyautogui.ImageNotFoundException as e:
        logger.warning('Image not found')
        if return_center:
            return None, None
        else :
            return None, None, None, None
    
    if return_center:
        return a.left + a.width//2, a.top + a.height//2 
    else:
        return a.left, a.top, a.width, a.height
    
def locateOnWindow(image: str, window_title: str, grayscale: bool = True, confidence: float = 0.999, return_center: bool = True):
    """Locates image on window
    
    `image` : Path to image to find.
    `min_search_time` : Amount of time in *milliseconds* to repeat taking screenshots and trying to locate a match. The default of 0 performs a single search.
    `grayscale` : Whether to convert images to grayscale. Defaults to *True*.
    `region` : Part of image where to find. `tuple[x_start, y_start, x_offset, y_offset]`.
    `confidence` : Between 0 and 1.
    `return_center` : If *True* retuns `tuple[x, y]` of the center of located image, otherwise returns tuple of xy of top left of the image and width and height (`tuple[x, y, w, h]`)
    
    If image not found returns **`tuple[None, None] | tuple[None, None, None, None]`**"""

    try:
        if IS_OPENCV_INSTALLED:
            a = pyautogui.locateOnWindow(image=f"./images/{image}", title=window_title, grayscale=grayscale, confidence=confidence)
        else:
            a = pyautogui.locateOnWindow(image=f"./images/{image}", title=window_title, grayscale=grayscale)
    except pyautogui.ImageNotFoundException:
        logger.warning('Image not found')
        if return_center:
            return None, None
        else :
            return None, None, None, None
    
    if return_center:
        return a.left + a.width//2, a.top + a.height//2 
    else:
        return a.left, a.top, a.width, a.height

def locateAllOnImage(what_to_find: str, where_to_find: str, grayscale: bool = True, 
                     region: tuple[int, int, int, int]|None = None,
                     confidence: float = 0.999, return_center: bool = True
                    ) -> list[tuple[int, int]] | list[tuple[int, int, int, int]] | list[tuple[None, None]] | list[tuple[None, None, None, None]]:
    """Locates one image on the other image.
    
    `what_to_find` : Path to image to find.
    `where_to_find` : Path to image where to find first image.
    `grayscale` : Whether to convert images to grayscale. Defaults to *True*.
    `region` : Part of image where to find. `tuple[x_start, y_start, x_offset, y_offset]`.
    `confidence` : Between 0 and 1.
    `return_center` : If *True* retuns `list[tuple[x, y]]` of the center of located image, otherwise returns list of tuple of xy of top left of the image and width and height (`list[tuple[x, y, w, h]]`)
    
    If image not found returns **`list[tuple[None, None]] | list[tuple[None, None, None, None]]`**"""
    try:
        if IS_OPENCV_INSTALLED:
            a = list(pyautogui.locateAll(needleImage=f"./images/{what_to_find}", haystackImage=f"./images/{where_to_find}", grayscale=grayscale, region=region, confidence=confidence))
        else:
            a = list(pyautogui.locateAll(needleImage=f"./images/{what_to_find}", haystackImage=f"./images/{where_to_find}", grayscale=grayscale, region=region))
    except pyautogui.ImageNotFoundException as e:
        logger.warning('Image not found')
        if return_center:
            return [(None, None)]
        else :
            return [(None, None, None, None)]
    
    if return_center:
        for i in range(len(a)):
            a[i] = (a[i].left + a[i].width//2, a[i].top + a[i].height//2)
    else:
        for i in range(len(a)):
            a[i] = tuple(a[i])
    return a

def locateAllOnScreen(image: str, grayscale: bool = True, 
                     region: tuple[int, int, int, int]|None = None,
                     confidence: float = 0.999, return_center: bool = True
                    ) -> list[tuple[int, int]] | list[tuple[int, int, int, int]] | list[tuple[None, None]] | list[tuple[None, None, None, None]]:
    """Locates image on window
    
    `image` : Path to image to find.
    `grayscale` : Whether to convert images to grayscale. Defaults to *True*.
    `region` : Part of image where to find. `tuple[x_start, y_start, x_offset, y_offset]`.
    `confidence` : Between 0 and 1.
    `return_center` : If *True* retuns `list[tuple[x, y]]` of the center of located image, otherwise returns list of tuple of xy of top left of the image and width and height (`list[tuple[x, y, w, h]]`)
    
    If image not found returns **`list[tuple[None, None]] | list[tuple[None, None, None, None]]`**"""
    try:
        if IS_OPENCV_INSTALLED:
            a = list(pyautogui.locateAllOnScreen(image=f"./images/{image}", grayscale=grayscale, region=region, confidence=confidence))
        else:
            a = list(pyautogui.locateAllOnScreen(image=f"./images/{image}", grayscale=grayscale, region=region))
    except pyautogui.ImageNotFoundException:
        logger.warning('Image not found')
        if return_center:
            return [(None, None)]
        else :
            return [(None, None, None, None)]
    
    if return_center:
        for i in range(len(a)):
            a[i] = (a[i].left + a[i].width//2, a[i].top + a[i].height//2)
    else:
        for i in range(len(a)):
            a[i] = tuple(a[i])
    return a

def get_functions() -> list[dict[str, str]]:
    func: list[callable] = [log, sleep, wait, holdKey, releaseKey, pressKey, getPixel, isMatchesColor, leftClick, rightClick, middleClick, moveTo, moveRel, dragTo, dragRel, scroll, write, screenshot, locateOnImage, locateAllOnImage, locateOnScreen, locateAllOnScreen, locateOnWindow]
    l = []
    print(moveRel.__annotations__)
    for f in func:
        l.append(
            {
                f.__name__ : f.__doc__,
            }
        )
    return l

