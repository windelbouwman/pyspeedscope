
import speedscope

import time

def func1(x):
    for y in range(15):
        # print('func1 %s - %s' % (x, y))
        time.sleep(0.001)

def func2(x):
    for y in range(4):
        # print('func2 %s - %s' % (x, y))
        func1(x)
        time.sleep(0.002)

def main():
    for x in range(3):
        time.sleep(0.003)
        print('standby! %s' % x)
        func1(x)
        func2(x)


with speedscope.track('speedscope.json'):
    main()
