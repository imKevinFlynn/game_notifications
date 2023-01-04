import asyncio
import pygame
from time import sleep
import cv2
import mss
import numpy as np
import os
import threading
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv, find_dotenv
from PyQt5 import QtWidgets, QtGui, QtCore

load_dotenv(find_dotenv())

bot = Bot(os.getenv("TOKEN"))
dp = Dispatcher(bot)

# Send notification message to chat ID
async def send_notification(chat_id, message):
    await bot.send_message(chat_id, message)

# Capture the video feed and check for low health
async def check_health(chat_id, pause_flag):
    # Set the low health threshold
    low_health_threshold = 0.2

    # Set the lower and upper bounds for the health bar color
    lower_bound = (0, 163, 196)
    upper_bound = (10, 220, 207)

    with mss.mss() as sct:
        monitor = {"top": 720, "left": 238, "width": 113, "height": 120}
        while "Screen capturing":
            # Check if the code should be paused
            if pause_flag.is_set():
                sleep(0.1)
                continue

            # Capture a frame from the screen
            img = np.array(sct.grab(monitor))

            # Convert the frame to HSV color space
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Create a mask for the health bar color
            mask = cv2.inRange(hsv, lower_bound, upper_bound)

            cv2.imshow("Mask", mask)
            cv2.waitKey(1)

            # Calculate the percentage of masked pixels
            mask_percentage = np.sum(mask) / (monitor['height'] * monitor['width'])

            # Check if the health bar is low
            if mask_percentage < low_health_threshold:
                # Show the frame
                cv2.imshow("Video Feed", img)
                pygame.init()
                pygame.mixer.init()
                # Load the sound file
                pygame.mixer.music.load("heal.wav")
                pygame.mixer.music.play(1)
                await send_notification(chat_id, "Health is low!")
                sleep(10)

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.thread = None
        self.pause_flag = None
        self.setWindowTitle('Notifications')
        self.setGeometry(100, 100, 200, 150)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.MSWindowsFixedSizeDialogHint)

        self.start_button = QtWidgets.QPushButton('Start', self)
        self.start_button.clicked.connect(self.start)
        self.stop_button = QtWidgets.QPushButton('Stop', self)
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)

        self.pause_button = QtWidgets.QPushButton('Pause', self)
        self.pause_button.clicked.connect(self.pause)
        self.pause_button.setEnabled(False)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.start_button)
        self.layout.addWidget(self.pause_button)
        self.layout.addWidget(self.stop_button)

        self.show()

    def start(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.pause_button.setEnabled(True)
        self.label.setText('Running...')
        self.pause_flag = threading.Event()
        self.thread = threading.Thread(target=self.run_check_health)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        self.label.setText('Stopped')
        self.thread.stop()

    def pause(self):
        if self.pause_button.text() == 'Pause':
            self.pause_button.setText('Resume')
            self.pause_flag.set()
        else:
            self.pause_button.setText('Pause')
            self.pause_flag.clear()

    def run_check_health(self):
        asyncio.run(check_health(chat_id=12345, pause_flag=self.pause_flag))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    app.exec_()
















