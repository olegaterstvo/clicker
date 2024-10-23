from utils import *

def main():
    #x, y = locateOnWindow('test1.png', 'Visual')
    #x, y = locateOnScreen('test1.png')
    #print(x,y)
    #leftClick(x, y)
    
    a = locateAllOnImage('test1.png', 'screenshot.png', grayscale=False)
    if a:
        print(1)
    else:
        for i in range(2):
            print(2)
    for i in range(10):
        print(1)
    
                                                                                                                                          

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