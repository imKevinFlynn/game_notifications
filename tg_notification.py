"""Работа программы: в случае понижения до определенного предела индикатора жизни в игре,
выполняется автоматическая отправка сообщений в приватный чат ТГ,
а так же воспроизводится звуковое уведомление в самой ОС."""

import asyncio
import os
import pygame
from time import sleep
import cv2
import mss
import numpy as np
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

bot = Bot(os.getenv("TOKEN"))

dp = Dispatcher(bot)


# Send notification message to chat ID
async def send_notification(chat_id, message):
    await bot.send_message(chat_id, message)

# Capture the video feed and check for low health
async def check_health(chat_id):
    # Set the low health threshold
    low_health_threshold = 0.2

    # Set the lower and upper bounds for the health bar color
    lower_bound = (0, 163, 196)
    upper_bound = (10, 220, 207)

    with mss.mss() as sct:
        monitor = {"top": 720, "left": 238, "width": 113, "height": 120}
        while "Screen capturing":
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



if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(check_health(chat_id=5136458800))
    except KeyboardInterrupt:
        pass