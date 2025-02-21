from utils import *

def main():
    cpaka = getWindow('(CPAKA)')
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
            logger.error(f"{e}")