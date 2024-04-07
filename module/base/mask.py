import cv2
import numpy as np
from module.base.template import Template
from module.base.utils import image_channel, load_image, rgb2gray

"""
Mask的类，它继承自一个名为Template的基类。Mask类用于表示和操作图像掩模（mask）。掩模可以只搜索图像中的某个区域
主要用于图像处理中，如应用掩模来隐藏或显示图像的特定部分。
属性
_image：这是一个私有属性，用于存储掩模图像。掩模图像可以是单通道（灰度图）或三通道（彩色图）。
方法
image 属性
这个属性是通过@property装饰器定义的，使得可以像访问属性一样调用image()方法，并通过@image.setter装饰器定义的方法设置_image属性的值。
当访问image属性时，如果_image是None，则会通过调用load_image(self.file)加载图像文件，然后根据图像的通道数，
使用rgb2gray函数将三通道的RGB图像转换为单通道的灰度图像，并存储在_image中。
image setter
这是image属性的设置器，允许用户直接为_image属性赋新值。
set_channel(self, channel)
这个方法用于设置掩模图像的通道数。参数channel指定了期望的通道数：0表示单通道（灰度图），3表示三通道（RGB图）。
方法首先检查当前图像的通道数。如果需要转换通道数（比如从单通道转为三通道或反之），它会使用cv2.split和cv2.merge函数来进行转换，
并返回True表示成功改变了通道数。如果不需要改变，方法返回False。
apply(self, image)
这个方法用于将当前的掩模应用到另一张图像上。参数image是需要应用掩模的目标图像。
方法首先调用set_channel以确保掩模图像的通道数与目标图像相同。然后，使用cv2.bitwise_and函数将掩模与目标图像相结合，
只有在掩模图像中像素值为非零的位置，目标图像的对应像素才会被保留。
方法返回应用掩模后的图像，这是一个np.ndarray类型的对象。
总结
Mask类提供了一种灵活的方式来处理图像掩模，包括加载和保存掩模图像、改变图像通道数、以及将掩模应用到其他图像上。
这对于图像处理任务来说是非常有用的，比如在进行背景去除、图像合成或者特定区域强调显示时，掩模的使用都是不可或缺的一部分。"""
class Mask(Template):
    @property
    def image(self):
        if self._image is None:
            image = load_image(self.file)
            if image_channel(image) == 3:
                image = rgb2gray(image)
            self._image = image

        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    def set_channel(self, channel):
        """
        Args:
            channel (int): 0 for monochrome, 3 for RGB.

        Returns:
            bool: If changed.
        """
        mask_channel = image_channel(self.image)
        if channel == 0:
            if mask_channel == 0:
                return False
            else:
                self._image, _, _ = cv2.split(self._image)
                return True
        else:
            if mask_channel == 0:
                self._image = cv2.merge([self._image] * 3)
                return True
            else:
                return False

    def apply(self, image):
        """
        Apply mask on image.

        Args:
            image:

        Returns:
            np.ndarray:
        """
        self.set_channel(image_channel(image))
        return cv2.bitwise_and(image, self.image)
