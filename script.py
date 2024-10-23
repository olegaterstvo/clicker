from utils import *

def main():
    cpaka = pygetwindow.getWindowsWithTitle('(CPAKA)')[0]
    cpaka.activate()
    leftClick(cpaka.left+25, cpaka.top+110)
    sleep(100)
    write("log('Hello world!')\nexit()\n")
    raise Exception('End of script')                               

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
            logger.error(f"{e}")