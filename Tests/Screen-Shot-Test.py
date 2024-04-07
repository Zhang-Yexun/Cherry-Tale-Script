import subprocess
import cv2
import numpy as np
import time


def adb_screenshot():
    # 执行ADB命令截取屏幕截图并获取二进制数据
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
    if result.stderr:
        raise Exception(f"ADB Error: {result.stderr}")
    # 从result.stdout中读取二进制数据并将其转换为NumPy数组，然后解码为图像
    nparr = np.frombuffer(result.stdout, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if image is None:
        raise Exception("无法解码图像。")
    return image


class Adb:

    def click_adb(self, x, y):
        """模拟在指定位置(x, y)上的点击操作。"""
        cmd = ['adb', 'shell', 'input', 'tap', str(x), str(y)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            raise Exception(f"ADB Error: {result.stderr}")

    def swipe_adb(self, p1, p2, duration=0.1):
        """模拟从点p1滑动到点p2的操作，持续时间为duration秒。"""
        duration_ms = int(duration * 1000)  # 将秒转换为毫秒
        cmd = ['adb', 'shell', 'input', 'swipe'] + list(map(str, p1 + p2)) + [str(duration_ms)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stderr:
            raise Exception(f"ADB Error: {result.stderr}")


# 示例用法
if __name__ == "__main__":
    adb = Adb()
    adb.click_adb(100, 200)  # 在屏幕上点击(100, 200)位置
    adb.swipe_adb((100, 200), (400, 800), duration=0.3)  # 从(100, 200)滑动到(400, 800)
    screenshot = adb_screenshot()  # 获取屏幕截图
    cv2.imshow("Screenshot", screenshot)  # 显示截图
    cv2.waitKey(0)  # 等待按键后关闭窗口
