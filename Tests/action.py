import subprocess

# 设置期望的分辨率
resolution = "720x1280"
# ADB 可执行文件的路径
adb_path = "C:\\leidian\\LDPlayer9\\adb.exe"


# 获取设备列表
def get_adb_devices(adb_path):
    result = subprocess.run([adb_path, "devices"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("Error getting adb devices: ", result.stderr)
        exit()
    devices = result.stdout.strip().split('\n')[1:]  # 第一行是标题，所以跳过
    device_ids = [device.split('\t')[0] for device in devices if 'device' in device]  # 只保留 "device" 状态的设备
    return device_ids


# 设置分辨率
def set_resolution(adb_path, device_id, resolution):
    comm = [adb_path, "-s", device_id, "shell", "wm", "size", resolution]
    result = subprocess.run(comm, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        print(f"成功将设备 {device_id} 的分辨率设置为 {resolution}.")
    else:
        print(f"设置设备 {device_id} 分辨率时出错: {result.stderr}")


# 主函数
def main():
    devices = get_adb_devices(adb_path)
    if not devices:
        print("没有找到设备。")
        return
    for i, device in enumerate(devices):
        print(f"{i + 1}: {device}")

    # 让用户选择设备
    choice = int(input("请输入要设置分辨率的设备编号: ")) - 1
    if 0 <= choice < len(devices):
        set_resolution(adb_path, devices[choice], resolution)
    else:
        print("输入的设备编号不正确。")


# 运行主函数
if __name__ == "__main__":
    main()
