import argparse
import time
from ctypes import windll, WinDLL

import cv2
import numpy as np
import pyautogui
from keyboard import add_hotkey
from mss import mss

VK_XBUTTON1 = 0x05

ERROR = "\x1b[38;5;255m[\x1b[31m-\x1b[38;5;255m]"
SUCCESS = "\x1b[38;5;255m[\x1b[32m+\x1b[38;5;255m]"
INFO = "\x1b[38;5;255m[\x1b[35m*\x1b[38;5;255m]"

lower_ranges = {
    "red": np.array([80, 80, 100]),
    "purple": np.array([140, 110, 150]),
    "yellow": np.array([30, 125, 150]),
}

upper_ranges = {
    "red": np.array([130, 255, 255]),
    "purple": np.array([150, 195, 255]),
    "yellow": np.array([30, 255, 255]),
}

MOUSE_MOVEMENT_THRESHOLD = 5
WIDTH, HEIGHT = [windll.user32.GetSystemMetrics(0), windll.user32.GetSystemMetrics(1)]
ZONE = 3
GRAB_ZONE = (int(WIDTH / 2 - ZONE), int(HEIGHT / 2 - ZONE), int(WIDTH / 2 + ZONE), int(HEIGHT / 2 + ZONE))
monitor = {"top": GRAB_ZONE[1], "left": GRAB_ZONE[0], "width": GRAB_ZONE[2] - GRAB_ZONE[0], "height": GRAB_ZONE[3] - GRAB_ZONE[1]}

shcore = WinDLL("shcore", use_last_error=True)
shcore.SetProcessDpiAwareness(2)


class PopOff:
    def __init__(self, trigger, highlight, mode):
        self.prev_pos = np.array(pyautogui.position())
        self.active = False
        self.trigger = trigger
        self.highlight = highlight
        self.mode = mode
        self.sct = mss()

        kernel32 = WinDLL("kernel32", use_last_error=True)
        kernel32.Beep(440, 75), kernel32.Beep(200, 100)

    def switch(self):
        self.active = not self.active
        kernel32 = WinDLL("kernel32", use_last_error=True)
        kernel32.Beep(440, 75), kernel32.Beep(700, 100) if self.active else kernel32.Beep(440, 75), kernel32.Beep(200, 100)

    def get_key_state(self, v_key: int) -> bool:
        return bool(windll.user32.GetKeyState(v_key) & 0x80)

    def search(self, pmap, mask):
        start_time = time.perf_counter_ns()

        # Check if the mouse is moving
        current_pos = np.array(pyautogui.position())
        distance = np.linalg.norm(current_pos - self.prev_pos)
        if distance > MOUSE_MOVEMENT_THRESHOLD:
            self.prev_pos = current_pos
            return

        # Shoot if the player is standing still and a pixel is detected
        if np.any(mask) and distance <= MOUSE_MOVEMENT_THRESHOLD:
            print(f"\x1b[2A{SUCCESS} Reaction time: {(time.perf_counter_ns() - start_time) // 1000000}ms")
            pyautogui.FAILSAFE = False
            # click
            pyautogui.mouseDown()
            pyautogui.mouseUp()

    def hold(self):
        while True:
            img = np.array(self.sct.grab(monitor))
            pmap = cv2.cvtColor(img[..., :3], cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(pmap, lower_ranges[self.highlight], upper_ranges[self.highlight])

            # if mouse4 of the mouse is held down use pynput
            if self.get_key_state(VK_XBUTTON1):
                self.search(pmap, mask)

    def toggle(self):
        add_hotkey(self.trigger, self.switch)

        while True:
            img = np.array(self.sct.grab(monitor))
            pmap = cv2.cvtColor(img[..., :3], cv2.COLOR_BGR2HSV)

            if self.active:
                mask = cv2.inRange(pmap, lower_ranges[self.highlight], upper_ranges[self.highlight])
                self.search(pmap, mask)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Valorant Triggerbot")
    parser.add_argument("trigger", help="Hotkey to toggle the triggerbot")
    parser.add_argument("highlight", choices=["red", "purple", "yellow"], help="Enemy highlight color")
    parser.add_argument("mode", choices=["hold", "toggle"], help="Triggerbot mode")
    args = parser.parse_args()

    PopOff(args.trigger, args.highlight, args.mode).hold() if args.mode == "hold" else PopOff(args.trigger, args.highlight, args.mode).toggle()
