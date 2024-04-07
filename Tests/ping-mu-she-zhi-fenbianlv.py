# 文件名：
# 功能：
# 作者：张业勋
# 日期：
# 思路：
import cv2,time,os,random,sys,mss,copy,subprocess,pyautogui
import numpy
from PIL import ImageGrab

def startup():
    #检测雷电模拟器ADB
    if sys.platform=='win32':
        print('windows系统，开始检测模拟器')
        ld_path="C:\\leidian\\LDPlayer9\\adb.exe"
        if os.path.isfile(ld_path):
            print('检测到雷电模拟器')
            adb_path=ld_path
        else:
            print("未检测到雷电模拟器")
    else:
        print("非windows操作系统")
        exit()

    #将屏幕分辨率设置为1280*720
    resolution="720x1280"
    # 构建ADB代码
    comm = [adb_path, "shell", "wm", "size", resolution]
    # Run the command
    result = subprocess.run(comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Check if the command was successful
    if result.returncode == 0:
        print(f"Resolution set to {resolution}.")
    else:
        print(f"Failed to set resolution: {result.stderr}")

startup()

