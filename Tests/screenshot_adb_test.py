import os
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


def save_screenshot(image, save_path_base, save_path_default, last_save_time,
                    genre='items', interval=None,
                    to_base_folder=False, file_format='png'):
    """
    保存截图到指定的文件夹路径。

    参数:
        image (np.ndarray): 要保存的图像数据。
        save_path_base (str): 基础文件夹路径。
        save_path_default (str): 默认文件夹路径。
        last_save_time (dict): 保存上一次保存时间的字典。
        genre (str, optional): 截图的类别。
        interval (int, float, optional): 两次保存之间的间隔时间（秒）。
        to_base_folder (bool, optional): 是否保存到基础文件夹。
        file_format (str, optional): 图像的文件格式，默认为'png'。

    返回:
        bool: 如果保存成功返回True，否则返回False。
    """
    now = time.time()
    interval = interval if interval is not None else 10  # 默认间隔10秒

    if now - last_save_time.get(genre, 0) > interval:
        timestamp = int(now * 1000)
        filename = f"{timestamp}.{file_format}"
        folder = save_path_base if to_base_folder else save_path_default
        genre_folder = os.path.join(folder, genre)
        if not os.path.exists(genre_folder):
            os.makedirs(genre_folder)

        filepath = os.path.join(genre_folder, filename)
        cv2.imwrite(filepath, image)  # 使用cv2保存图像
        last_save_time[genre] = now
        return True
    else:
        last_save_time[genre] = now
        return False


def set_screenshot_interval(config, interval_setting, interval=None):
    print("hello world")


# 使用示例
if __name__ == "__main__":
    screenshot = adb_screenshot()  # 获取屏幕截图
    cv2.imshow("Screenshot", screenshot)  # 显示截图
    cv2.waitKey(0)  # 等待按键后关闭窗口
