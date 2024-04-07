import subprocess
import cv2
import numpy as np
import time
from module.base.utils import ensure_time
import os
from module.base.timer import Timer
from module.base.utils import *
from module.base.button import Button


def click_adb(x, y):
    """模拟在指定位置(x, y)上的点击操作。"""
    start = time.time()
    cmd = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if time.time() - start <= 0.05:
        Adb.sleep(0.05)
    if result.stderr:
        raise Exception(f"ADB Error: {result.stderr}")


class Adb:
    img: np.ndarray

    def __init__(self):
        self.image = None

    @staticmethod
    def sleep(second):
        """
        Args:
            second(int, float, tuple):
        """
        time.sleep(ensure_time(second))

    def click(self, button):
        """Method to click a button.

        Args:
            button (button.Button): Button instance to click.
        """
        x, y = random_rectangle_point(button.button)
        x, y = ensure_int(x, y)
        click_adb(x, y)

    def swipe_adb(self, p1, p2, duration=0.1):
        """模拟从点p1滑动到点p2的操作，持续时间为duration秒。"""
        duration_ms = int(duration * 1000)  # 将秒转换为毫秒
        cmd = ['adb', 'shell', 'input', 'swipe'] + list(map(str, p1 + p2)) + [str(duration_ms)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            raise Exception(f"ADB Error: {result.stderr}")

    def multi_click(self, button, n, interval=(0.1, 0.2)):
        click_timer = Timer(0.1)
        for _ in range(n):
            remain = ensure_time(interval) - click_timer.current()
            if remain > 0:
                self.sleep(remain)
            click_timer.reset()
            self.click(button)

    def long_click(self, button, duration=(1, 1.2)):
        """Method to long click a button.

        Args:
            button (button.Button): AzurLane Button instance.
            duration(int, float, tuple):
        """
        x, y = random_rectangle_point(button.button)
        x, y = ensure_int(x, y)
        duration = ensure_time(duration)
        self.swipe_adb((x, y), (x, y), duration)

    def adb_screenshot(self):
        _screenshot_interval = Timer(0.1)
        _last_save_time = {}
        image: np.ndarray

        _screenshot_interval.wait()
        _screenshot_interval.reset()

        # 执行ADB命令截取屏幕截图并获取二进制数据
        result = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
        if result.stderr:
            raise Exception(f"ADB Error: {result.stderr}")
        # 从result.stdout中读取二进制数据并将其转换为NumPy数组，然后解码为图像
        nparr = np.frombuffer(result.stdout, np.uint8)
        self.image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if self.image is None:
            raise Exception("无法解码图像。")

        return self.image

    def save_screenshot(self, save_folder="E:\\Project\\xju\\Cherry-Tale-Script\\module\\Debug"):
        """Save a screenshot with current time as file name.

        Args:
            image (np.ndarray): The screenshot image to save.
            save_folder (str): Path to the folder where the screenshot will be saved.

        Returns:
            str: The path to the saved screenshot file.
        """

        _screenshot_interval = Timer(0.1)
        _last_save_time = {}
        image: np.ndarray

        _screenshot_interval.wait()
        _screenshot_interval.reset()

        # 执行ADB命令截取屏幕截图并获取二进制数据
        result = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
        if result.stderr:
            raise Exception(f"ADB Error: {result.stderr}")
        # 从result.stdout中读取二进制数据并将其转换为NumPy数组，然后解码为图像
        nparr = np.frombuffer(result.stdout, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # Create the folder if it doesn't exist.
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        # Generate the file name using the current time.
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        file_name = f"{timestamp}.png"
        file_path = os.path.join(save_folder, file_name)

        # Save the screenshot.
        cv2.imwrite(file_path, image)

        return file_path


# 示例用法
if __name__ == "__main__":
    adb = Adb()
    click_adb(100, 200)  # 在屏幕上点击(100, 200)位置
    adb.swipe_adb((100, 200), (400, 800), duration=0.3)  # 从(100, 200)滑动到(400, 800)
    screenshot = adb.adb_screenshot()  # 获取屏幕截图
    cv2.imshow("Screenshot", screenshot)  # 显示截图
    cv2.waitKey(0)  # 等待按键后关闭窗口
