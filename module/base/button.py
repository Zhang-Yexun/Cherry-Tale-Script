import os
import traceback

import imageio
from PIL import ImageDraw
import cv2
from module.base.decorator import cached_property
from module.base.resource import Resource
from module.base.utils import *

'''
这段代码定义了两个类，Button和ButtonGrid，用于表示和操作界面元素——即按钮。
这些类可以在游戏或应用的UI自动化中使用，例如自动点击按钮或检测按钮是否存在。

Button 类
Button类代表一个UI按钮，它继承自Resource类。按钮有以下主要属性和方法：
初始化：通过给定按钮的位置、颜色、点击区域（可能和位置区域一样），以及可选的文件路径和名称，创建Button对象。
缓存的属性：使用@cached_property装饰器缓存某些属性，以便多次访问时不需要重新计算，提高效率。
出现检测：appear_on方法检查按钮是否出现在给定的图像上，基于颜色相似度。
颜色加载：load_color方法从特定图像区域加载按钮颜色。
模板匹配：match、match_binary和match_luma方法执行模板匹配来检测按钮是否出现在屏幕上。
这些方法使用OpenCV的图像处理功能，支持普通图像、二值化图像和亮度图像的模板匹配。
资源释放：resource_release方法用于释放加载的图像资源，以免在不需要时占用内存。

ButtonGrid 类
ButtonGrid类用于表示和操作一组有规律排列的按钮，比如网格布局的菜单项。它有以下主要属性和方法：
初始化：通过指定起始点、每个按钮的位移增量、单个按钮的形状和整个网格的形状，创建ButtonGrid对象。
访问单个按钮：通过__getitem__方法可以用网格坐标访问单个按钮。
生成所有按钮：generate方法遍历整个网格，为每个网格位置生成一个Button实例。
缓存的按钮列表：buttons属性缓存了整个网格中所有的按钮。
裁剪和移动网格：crop和move方法用于基于原网格创建新的子网格或移动网格。
生成和显示掩码：gen_mask、show_mask和save_mask方法用于生成、显示和保存网格布局的视觉表示。
这些方法使用PIL（Python Imaging Library）来创建一个图像，其中每个按钮的区域被绘制为白色，背景为黑色，这对调试非常有用。
这些类被设计为高度可复用和扩展的组件，使它们适合在不同类型的UI自动化任务中使用。
代码的注释和示例提供了足够的信息，以理解每个方法的用途和工作方式。
'''


class Button(Resource):
    def __init__(self, area, color, button, file=None, name=None):
        """Initialize a Button instance.

        Args:
            area (dict[tuple], tuple): Area that the button would appear on the image.
                          (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
            color (dict[tuple], tuple): Color we expect the area would be.
                           (r, g, b)
            button (dict[tuple], tuple): Area to be click if button appears on the image.
                            (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
                            If tuple is empty, this object can be use as a checker.
        Examples:
            BATTLE_PREPARATION = Button(
                area=(1562, 908, 1864, 1003),
                color=(231, 181, 90),
                button=(1562, 908, 1864, 1003)
            )
        """
        self.raw_area = area
        self.raw_color = color
        self.raw_button = button
        self.raw_file = file
        self.raw_name = name

        self._button_offset = None
        self._match_init = False
        self._match_binary_init = False
        self._match_luma_init = False
        self.image = None
        self.image_binary = None
        self.image_luma = None

        if self.file:
            self.resource_add(key=self.file)

    cached = ['area', 'color', '_button', 'file', 'name', 'is_gif']

    @cached_property
    def area(self):
        return self.raw_area

    @cached_property
    def color(self):
        return self.raw_color

    @cached_property
    def _button(self):
        return self.raw_button

    @cached_property
    def file(self):
        return self.raw_file

    @cached_property
    def name(self):
        if self.raw_name:
            return self.raw_name
        elif self.file:
            return os.path.splitext(os.path.split(self.file)[1])[0]
        else:
            return 'BUTTON'

    @cached_property
    def is_gif(self):
        if self.file:
            return os.path.splitext(self.file)[1] == '.gif'
        else:
            return False

    def __str__(self):
        return self.name

    __repr__ = __str__

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(self.name)

    def __bool__(self):
        return True

    @property
    def button(self):
        if self._button_offset is None:
            return self._button
        else:
            return self._button_offset

    def appear_on(self, image, threshold=10):
        """Check if the button appears on the image.

        Args:
            image (np.ndarray): Screenshot.
            threshold (int): Default to 10.

        Returns:
            bool: True if button appears on screenshot.
        """
        return color_similar(
            color1=get_color(image, self.area),
            color2=self.color,
            threshold=threshold
        )

    def load_color(self, image):
        """Load color from the specific area of the given image.
        This method is irreversible, this would be only use in some special occasion.

        Args:
            image: Another screenshot.

        Returns:
            tuple: Color (r, g, b).
        """
        self.__dict__['color'] = get_color(image, self.area)
        self.image = crop(image, self.area)
        self.__dict__['is_gif'] = False
        return self.color

    def load_offset(self, button):
        """
        Load offset from another button.

        Args:
            button (Button):
        """
        offset = np.subtract(button.button, button._button)[:2]
        self._button_offset = area_offset(self._button, offset=offset)

    def clear_offset(self):
        self._button_offset = None

    def ensure_template(self):
        """
        Load asset image.
        If needs to call self.match, call this first.
        """
        if not self._match_init:
            if self.is_gif:
                self.image = []
                for image in imageio.mimread(self.file):
                    image = image[:, :, :3].copy() if len(image.shape) == 3 else image
                    image = crop(image, self.area)
                    self.image.append(image)
            else:
                self.image = load_image(self.file, self.area)
            self._match_init = True

    def ensure_binary_template(self):
        """
        Load asset image.
        If needs to call self.match, call this first.
        """
        if not self._match_binary_init:
            if self.is_gif:
                self.image_binary = []
                for image in self.image:
                    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    _, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                    self.image_binary.append(image_binary)
            else:
                image_gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
                _, self.image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            self._match_binary_init = True

    def ensure_luma_template(self):
        if not self._match_luma_init:
            if self.is_gif:
                self.image_luma = []
                for image in self.image:
                    luma = rgb2luma(image)
                    self.image_luma.append(luma)
            else:
                self.image_luma = rgb2luma(self.image)
            self._match_luma_init = True

    def resource_release(self):
        super().resource_release()
        self.image = None
        self.image_binary = None
        self.image_luma = None
        self._match_init = False
        self._match_binary_init = False
        self._match_luma_init = False

    def match(self, image, offset=30, threshold=0.75):
        """Detects button by template matching. To Some button, its location may not be static.

        Args:
            image: Screenshot.
            offset (int, tuple): Detection area offset.
            threshold (float): 0-1. Similarity.

        Returns:
            bool.
        """
        self.ensure_template()

        if isinstance(offset, tuple):
            if len(offset) == 2:
                offset = np.array((-offset[0], -offset[1], offset[0], offset[1]))
            else:
                offset = np.array(offset)
        else:
            offset = np.array((-3, -offset, 3, offset))
        image = crop(image, offset + self.area, copy=False)

        if self.is_gif:
            for template in self.image:
                res = cv2.matchTemplate(template, image, cv2.TM_CCOEFF_NORMED)
                _, similarity, _, point = cv2.minMaxLoc(res)
                print(f"GIF frame similarity: {similarity}")
                self._button_offset = area_offset(self._button, offset[:2] + np.array(point))
                if similarity > threshold:
                    return True
            return False
        else:
            res = cv2.matchTemplate(self.image, image, cv2.TM_CCOEFF_NORMED)
            _, similarity, _, point = cv2.minMaxLoc(res)
            print(f"Single image similarity: {similarity}")
            self._button_offset = area_offset(self._button, offset[:2] + np.array(point))
            return similarity > threshold

    def match_binary(self, image, offset=30, threshold=0.85):
        """Detects button by template matching. To Some button, its location may not be static.
           This method will apply template matching under binarization.

        Args:
            image: Screenshot.
            offset (int, tuple): Detection area offset.
            threshold (float): 0-1. Similarity.

        Returns:
            bool.
        """
        self.ensure_template()
        self.ensure_binary_template()

        if isinstance(offset, tuple):
            if len(offset) == 2:
                offset = np.array((-offset[0], -offset[1], offset[0], offset[1]))
            else:
                offset = np.array(offset)
        else:
            offset = np.array((-3, -offset, 3, offset))
        image = crop(image, offset + self.area, copy=False)

        if self.is_gif:
            for template in self.image_binary:
                # graying
                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # binarization
                _, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                # template matching
                res = cv2.matchTemplate(template, image_binary, cv2.TM_CCOEFF_NORMED)
                _, similarity, _, point = cv2.minMaxLoc(res)
                self._button_offset = area_offset(self._button, offset[:2] + np.array(point))
                if similarity > threshold:
                    return True
            return False
        else:
            # graying
            image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # binarization
            _, image_binary = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            # template matching
            res = cv2.matchTemplate(self.image_binary, image_binary, cv2.TM_CCOEFF_NORMED)
            _, similarity, _, point = cv2.minMaxLoc(res)
            self._button_offset = area_offset(self._button, offset[:2] + np.array(point))
            return similarity > threshold

    def match_luma(self, image, offset=30, threshold=0.85):
        """
        Detects button by template matching under Y channel (Luminance)

        Args:
            image: Screenshot.
            offset (int, tuple): Detection area offset.
            threshold (float): 0-1. Similarity.

        Returns:
            bool.
        """
        self.ensure_template()
        self.ensure_luma_template()

        if isinstance(offset, tuple):
            if len(offset) == 2:
                offset = np.array((-offset[0], -offset[1], offset[0], offset[1]))
            else:
                offset = np.array(offset)
        else:
            offset = np.array((-3, -offset, 3, offset))
        image = crop(image, offset + self.area, copy=False)

        if self.is_gif:
            image_luma = rgb2luma(image)
            for template in self.image_luma:
                res = cv2.matchTemplate(template, image_luma, cv2.TM_CCOEFF_NORMED)
                _, similarity, _, point = cv2.minMaxLoc(res)
                self._button_offset = area_offset(self._button, offset[:2] + np.array(point))
                if similarity > threshold:
                    return True
        else:
            image_luma = rgb2luma(image)
            res = cv2.matchTemplate(self.image_luma, image_luma, cv2.TM_CCOEFF_NORMED)
            _, similarity, _, point = cv2.minMaxLoc(res)
            self._button_offset = area_offset(self._button, offset[:2] + np.array(point))
            return similarity > threshold

    def match_appear_on(self, image, threshold=30):
        """
        Args:
            image: Screenshot.
            threshold: Default to 10.

        Returns:
            bool:
        """
        diff = np.subtract(self.button, self._button)[:2]
        area = area_offset(self.area, offset=diff)
        return color_similar(color1=get_color(image, area), color2=self.color, threshold=threshold)

    def crop(self, area, image=None, name=None):
        """
        Get a new button by relative coordinates.

        Args:
            area (tuple):
            image (np.ndarray): Screenshot. If provided, load color and image from it.
            name (str):

        Returns:
            Button:
        """
        if name is None:
            name = self.name
        new_area = area_offset(area, offset=self.area[:2])
        new_button = area_offset(area, offset=self.button[:2])
        button = Button(area=new_area, color=self.color, button=new_button, file=self.file, name=name)
        if image is not None:
            button.load_color(image)
        return button


class ButtonGrid:
    def __init__(self, origin, delta, button_shape, grid_shape, name=None):
        self.origin = np.array(origin)
        self.delta = np.array(delta)
        self.button_shape = np.array(button_shape)
        self.grid_shape = np.array(grid_shape)
        if name:
            self._name = name
        else:
            (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
            self._name = text[:text.find('=')].strip()

    def __getitem__(self, item):
        base = np.round(np.array(item) * self.delta + self.origin).astype(int)
        area = tuple(np.append(base, base + self.button_shape))
        return Button(area=area, color=(), button=area, name='%s_%s_%s' % (self._name, item[0], item[1]))

    def generate(self):
        for y in range(self.grid_shape[1]):
            for x in range(self.grid_shape[0]):
                yield x, y, self[x, y]

    @cached_property
    def buttons(self):
        return list([button for _, _, button in self.generate()])

    def crop(self, area, name=None):
        """
        Args:
            area (tuple): Area related to self.origin
            name (str): Name of the new ButtonGrid instance.

        Returns:
            ButtonGrid:
        """
        if name is None:
            name = self._name
        origin = self.origin + area[:2]
        button_shape = np.subtract(area[2:], area[:2])
        return ButtonGrid(
            origin=origin, delta=self.delta, button_shape=button_shape, grid_shape=self.grid_shape, name=name)

    def move(self, vector, name=None):
        """
        Args:
            vector (tuple): Move vector.
            name (str): Name of the new ButtonGrid instance.

        Returns:
            ButtonGrid:
        """
        if name is None:
            name = self._name
        origin = self.origin + vector
        return ButtonGrid(
            origin=origin, delta=self.delta, button_shape=self.button_shape, grid_shape=self.grid_shape, name=name)

    def gen_mask(self):
        """
        Generate a mask image to display this ButtonGrid object for debugging.

        Returns:
            PIL.Image.Image: Area in white, background in black.
        """
        image = Image.new("RGB", (1280, 720), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for button in self.buttons:
            draw.rectangle((button.area[:2], button.button[2:]), fill=(255, 255, 255), outline=None)
        return image

    def show_mask(self):
        self.gen_mask().show()

    def save_mask(self):
        """
        Save mask to {name}.png
        """
        self.gen_mask().save(f'{self._name}.png')
