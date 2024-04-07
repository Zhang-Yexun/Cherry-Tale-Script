import os

import imageio

from module.base.button import Button
from module.base.decorator import cached_property
from module.base.resource import Resource
from module.base.utils import *
"""
这段代码定义了一个Template类，它继承自Resource。
该类主要用于处理图像模板匹配的任务，特别是在自动化测试和游戏机器人开发中非常有用。类的属性和方法如下：

属性：
raw_file：模板文件的路径。
_image：加载的图像数据，可能是单个图像或GIF的每一帧。
_image_binary：二值化处理后的图像数据。

方法：
__init__：初始化方法，加载模板文件。
file、name、is_gif：通过@cached_property装饰器缓存的属性，分别代表文件路径、模板名称和是否为GIF图像。
image、image_binary：属性，分别获取处理后的图像和二值化图像。
resource_release：释放图像资源。
pre_process：预处理图像的方法，可被子类重写。
size：获取图像的尺寸。
match：使用模板匹配技术检查给定图像是否与模板相似。
match_binary：在二值化的图像上进行模板匹配。
_point_to_button：将匹配点转换为Button对象。
match_result：返回匹配的相似度和匹配点转换的Button对象。
类主要处理图像加载、预处理、匹配及其结果的转换。通过模板匹配，可以识别屏幕截图中的特定元素，非常适合自动化操作中的图像识别任务。"""


class Template(Resource):
    def __init__(self, file):
        """
        Args:
            file (dict[str], str): Filepath of template file.
        """
        self.raw_file = file
        self._image = None
        self._image_binary = None

        self.resource_add(self.file)

    cached = ['file', 'name', 'is_gif']

    @cached_property
    def file(self):
        return self.parse_property(self.raw_file)

    @cached_property
    def name(self):
        return os.path.splitext(os.path.basename(self.file))[0].upper()

    @cached_property
    def is_gif(self):
        return os.path.splitext(self.file)[1] == '.gif'

    @property
    def image(self):
        if self._image is None:
            if self.is_gif:
                self._image = []
                channel = 0
                for image in imageio.mimread(self.file):
                    if not channel:
                        channel = len(image.shape)
                    if channel == 3:
                        image = image[:, :, :3].copy()
                    elif len(image.shape) == 3:
                        # Follow the first frame
                        image = image[:, :, 0].copy()

                    image = self.pre_process(image)
                    self._image += [image, cv2.flip(image, 1)]
            else:
                self._image = self.pre_process(load_image(self.file))

        return self._image

    @property
    def image_binary(self):
        if self._image_binary is None:
            if self.is_gif:
                self._image_binary = []
                for image in self.image:
                    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    _, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                    self._image_binary.append(image_binary)
            else:
                image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                _, self._image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        return self._image_binary

    @image.setter
    def image(self, value):
        self._image = value

    def resource_release(self):
        super().resource_release()
        self._image = None

    def pre_process(self, image):
        """
        Args:
            image (np.ndarray):

        Returns:
            np.ndarray:
        """
        return image

    @cached_property
    def size(self):
        if self.is_gif:
            return self.image[0].shape[0:2][::-1]
        else:
            return self.image.shape[0:2][::-1]

    def match(self, image, scaling=1.0, similarity=0.85):
        """
        Args:
            image:
            scaling (int, float): Scale the template to match image
            similarity (float): 0 to 1.

        Returns:
            bool: If matches.
        """
        scaling = 1 / scaling
        if scaling != 1.0:
            image = cv2.resize(image, None, fx=scaling, fy=scaling)

        if self.is_gif:
            for template in self.image:
                res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
                _, sim, _, _ = cv2.minMaxLoc(res)
                # print(self.file, sim)
                if sim > similarity:
                    return True

            return False

        else:
            res = cv2.matchTemplate(image, self.image, cv2.TM_CCOEFF_NORMED)
            _, sim, _, _ = cv2.minMaxLoc(res)
            # print(self.file, sim)
            return sim > similarity

    def match_binary(self, image, similarity=0.85):
        """
        Use template match after binarization.

        Args:
            image:
            similarity (float): 0 to 1.

        Returns:
            bool: If matches.
        """
        if self.is_gif:
            for template in self.image_binary:
                # graying
                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # binarization
                _, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                # template matching
                res = cv2.matchTemplate(image_binary, template, cv2.TM_CCOEFF_NORMED)
                _, sim, _, _ = cv2.minMaxLoc(res)
                # print(self.file, sim)
                if sim > similarity:
                    return True

            return False

        else:
            # graying
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # binarization
            _, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            # template matching
            res = cv2.matchTemplate(image_binary, self.image_binary, cv2.TM_CCOEFF_NORMED)
            _, sim, _, _ = cv2.minMaxLoc(res)
            # print(self.file, sim)
            return sim > similarity

    def _point_to_button(self, point, image=None, name=None):
        """
        Args:
            point:
            image (np.ndarray): Screenshot. If provided, load color and image from it.
            name (str):

        Returns:
            Button:
        """
        if name is None:
            name = self.name
        area = area_offset(area=(0, 0, *self.size), offset=point)
        button = Button(area=area, color=(), button=area, name=name)
        if image is not None:
            button.load_color(image)
        return button

    def match_result(self, image, name=None):
        """
        Args:
            image:
            name (str):

        Returns:
            float: Similarity
            Button:
        """
        res = cv2.matchTemplate(image, self.image, cv2.TM_CCOEFF_NORMED)
        _, sim, _, point = cv2.minMaxLoc(res)
        # print(self.file, sim)

        button = self._point_to_button(point, image=image, name=name)
        return sim, button


