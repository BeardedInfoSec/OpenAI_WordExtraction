import pyautogui
import time

try:
    while True:
        x, y = pyautogui.position()
        positionStr = f'X: {x} Y: {y}'
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print('\nDone.')
