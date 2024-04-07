import os
from PIL import Image
import numpy as np

# 设置输入输出文件夹的路径(路径可替换)
ASSETS_FOLDER = '../assets/Initial_main_line'  # 资产存放文件
OUTPUT_FOLDER = '../module/Initial_main_line'  # 资产输出文件
OUTPUT_FILE = 'assets.py'  # 资产文件名
BUTTON_FIND_FILE = '../../assets/Initial_main_line/'  # Button中file属性用于存放资产文件路径

# 如果输出文件夹不存在，则创建
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# 输出文件的完整路径
output_file_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)


def extract_bbox(image):
    """提取图像中非黑色部分的边界框"""
    # 将图像转换为numpy数组
    image_np = np.array(image)

    # 找到非黑色的像素点
    rows = np.any(image_np[:, :, :-1] > 0, axis=1)
    cols = np.any(image_np[:, :, :-1] > 0, axis=0)

    # 计算边界框的坐标
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]

    return x_min, y_min, x_max, y_max


def get_button_color(image_np, bbox):
    """提取按钮的颜色"""
    # 根据边界框裁剪图像
    cropped_image = image_np[bbox[1]:bbox[3], bbox[0]:bbox[2], :]
    # 计算非透明像素的平均颜色
    valid_pixels = cropped_image[cropped_image[:, :, 3] > 0]  # 忽略透明度为0的像素
    color = np.mean(valid_pixels[:, :3], axis=0).astype(int)  # 只取RGB三个通道的平均值
    return tuple(color)


# 开始处理图像并写入文件
with open(output_file_path, 'w') as file:
    # 写入文件头
    file.write("from module.base.button import Button\n\n")

    # 遍历assets文件夹中的所有图像文件
    for image_name in os.listdir(ASSETS_FOLDER):
        if image_name.endswith('.png'):
            image_path = os.path.join(ASSETS_FOLDER, image_name)
            image = Image.open(image_path).convert('RGBA')  # 确保图像为RGBA格式
            bbox = extract_bbox(image)
            button_color = get_button_color(np.array(image), bbox)

            # 去掉文件扩展名，生成Button表达式
            button_name = os.path.splitext(image_name)[0]
            button_expr = f"{button_name} = Button(area={bbox}, color={button_color}, button={bbox}, file='{os.path.join(BUTTON_FIND_FILE, image_name)}')\n"
            file.write(button_expr)
