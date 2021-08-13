import ctypes
import time
import threading
from queue import Queue
from wrapper import *

class LostArkFishing():
    def __init__(self):
        self.wrapper = APIWrapper('LOST ARK')
        self.skil_rgb = (0, 0, 0)
        self.throw_point = Point()
        self.count_trap = 0
        self.wrapper.getWindowHandle()
        self.wrapper.getWindowHandleDC()

    def run(self):
        self.initiateThrowPoint()
        self.initiateSkillRGB()
        flag = input('[*] Input Type [1(Norm) | 2(FT) | 3(PF)] : ')
        if flag not in ['1', '2', '3']:
            print('[-] Input \'Y\' or \'N\'')
            exit()
        while True:
            if flag in ['2', '3']:
                #threading.Thread(target=self.)
                self.fishingTrap()
            self.throwFishingrod()
            self.waitBite()
            time.sleep(1)

    def initiateThrowPoint(self):
        input('[*] Put the mouse pointer over throw point and press any key')
        self.wrapper.getMouseCursor(self.throw_point)
        print('[*] Throw point is {},{}'.format(self.throw_point.x, self.throw_point.y))
        return

    def initiateSkillRGB(self):
        #self.skil_rgb = self.wrapper.findSpecificPointRGB(760, 980)
        self.skil_rgb = (47, 52, 79)
        return

    def throwFishingrod(self):
        print('[*] Throw fishing rod')
        while True:
            backup_point = Point()
            self.wrapper.getMouseCursor(backup_point)
            self.wrapper.setMouseCursor(self.throw_point.x, self.throw_point.y)
            self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0100, 0x00000057, 0x00110001)
            self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0102, 0x00000077, 0x00110001)
            self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0101, 0x00000057, 0xC0110001)
            time.sleep(0.05)
            self.wrapper.setMouseCursor(backup_point.x, backup_point.y)
            time.sleep(3)
            if self.wrapper.findSpecificPointRGB(760, 980) != self.skil_rgb:
                return

    def waitBite(self):
        print('[*] Waiting...', end='')
        while True:
            rgb = self.wrapper.findSpecificPointRGB(960, 474)
            if rgb[0] >= 200 and rgb[1] > 100 and rgb[2] < 150:
                print('[*] FOUND --> RGB {}'.format(str(rgb)))
                self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0100, 0x00000057, 0x00110001)
                self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0102, 0x00000077, 0x00110001)
                self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0101, 0x00000057, 0xC0110001)
                time.sleep(3)
                if self.wrapper.findSpecificPointRGB(760, 980) == self.skil_rgb:
                    return
            time.sleep(0.5)

    def fishingTrapTask(self, task):
        print('[*] {} the fishing trap'.format(task))
        while True:
            self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0100, 0x00000047, 0x00220001)
            self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0102, 0x00000067, 0x00220001)
            self.wrapper.user32.PostMessageW(self.wrapper.hwnd, 0x0101, 0x00000047, 0xC0220001)
            time.sleep(3)
            # rgb = self.wrapper.findSpecificPointRGB(292, 17)
            #rgb[0] in range(215, 225) and rgb[1] in range(175, 185) and rgb[2] < 5
            if task == 'PUT' and (self.wrapper.findSpecificPointRGB(292, 17)[0] >= 200):
                self.count_trap = 0
                break
            elif task == 'GET' and (self.wrapper.findSpecificPointRGB(292, 17)[0] < 100):
                self.count_trap = 1
                break

    def fishingTrap(self):
        print('[*] Trap Count : {}'.format(self.count_trap))
        if self.count_trap == 0:
            if self.wrapper.findSpecificPointRGB(292, 17)[0] >= 200:
                print('[-] Already exist')
                self.count_trap = 1
            else:
                self.fishingTrapTask('PUT')
        elif self.count_trap == 14:
            self.fishingTrapTask('GET')
            time.sleep(2)
            self.fishingTrapTask('PUT')
        else:
            self.count_trap = self.count_trap + 1

if __name__=="__main__":
    obj = LostArkFishing()
    obj.run()