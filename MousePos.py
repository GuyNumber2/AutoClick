import pyautogui

print("To close this program press crtl + c");


#While loop to print the x and Y value of the mouse position to console. 

try:
    while True:
        x, y = pyautogui.position()
        mousePos = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        print(mousePos, end='')
        print('\b' * len(mousePos), end='', flush=True)

except KeyboardInterrupt:
    print('\n')
