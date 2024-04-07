import numpy as np

from module.base.base import ModuleBase
from module.base.button import Button
from module.base.timer import Timer
from module.base.utils import color_similarity_2d, random_rectangle_point
'''
这段代码定义了一个名为Scroll的类，旨在处理游戏自动化脚本中的滚动操作。Scroll类提供了一套方法来识别滚动条的颜色、定位、
以及在滚动区域内进行上下或左右滑动的功能。这对于自动化需要在长列表或页面中导航的任务尤其有用。
类的属性
color_threshold: 用于匹配滚动条颜色的阈值。
drag_threshold: 触发拖拽操作的位置变化阈值，以滚动条位置的百分比表示。
edge_threshold: 判断滚动条是否到达边缘的阈值。
edge_add: 边缘位置调整的增量，用于边缘滑动操作。
area: 定义滚动区域的四元组，或者是一个Button对象。
color: 滚动条的RGB颜色。
is_vertical: 指示滚动方向是否为垂直。
name: 滚动对象的名称。
total: 滚动区域的总长度。
length: 滚动条的长度。
drag_interval 和 drag_timeout: 控制拖拽操作的间隔和超时的计时器。
类的方法
match_color(self, main): 在给定的滚动区域中匹配指定颜色的滚动条，并返回一个布尔型数组，表示哪些像素行（或列）匹配了颜色。
cal_position(self, main): 计算当前滚动条的位置，返回一个0到1之间的值，0表示顶部，1表示底部。
position_to_screen(self, position, random_range): 将滚动位置转换为屏幕坐标，用于确定滑动操作的起点和终点。
appear(self, main): 检查滚动条是否出现在指定区域内。
at_top(self, main) 和 at_bottom(self, main): 判断滚动条是否处于顶部或底部位置。
set(self, position, main, random_range, distance_check, skip_first_screenshot): 将滚动条设置到指定的位置。
set_top(self, main, random_range, skip_first_screenshot) 和 set_bottom(self, main, random_range, skip_first_screenshot): 
分别将滚动条移动到顶部或底部。
drag_page(self, page, main, random_range, skip_first_screenshot): 将滚动条向前或向后拖动指定的页面数量。
next_page(self, main, page, random_range, skip_first_screenshot) 和 prev_page(self, main, page, random_range,
 skip_first_screenshot): 分别实现向前翻页和向后翻页的操作。
'''

class Scroll:
    color_threshold = 221
    drag_threshold = 0.05
    edge_threshold = 0.05
    edge_add = (0.3, 0.5)

    def __init__(self, area, color, is_vertical=True, name='Scroll'):
        """
        Args:
            area (Button, tuple): A button or area of the whole scroll.
            color (tuple): RGB of the scroll
            is_vertical (bool): True if vertical, false if horizontal.
            name (str):
        """
        if isinstance(area, Button):
            name = area.name
            area = area.area
        self.area = area
        self.color = color
        self.is_vertical = is_vertical
        self.name = name

        if self.is_vertical:
            self.total = self.area[3] - self.area[1]
        else:
            self.total = self.area[2] - self.area[0]
        # Just default value, will change in match_color()
        self.length = self.total / 2
        self.drag_interval = Timer(1, count=2)
        self.drag_timeout = Timer(5, count=10)

    def match_color(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            np.ndarray: Shape (n,), dtype bool.
        """
        image = main.image_crop(self.area)
        image = color_similarity_2d(image, color=self.color)
        mask = np.max(image, axis=1 if self.is_vertical else 0) > self.color_threshold
        self.length = np.sum(mask)
        return mask

    def cal_position(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            float: 0 to 1.
        """
        mask = self.match_color(main)
        middle = np.mean(np.where(mask)[0])

        position = (middle - self.length / 2) / (self.total - self.length)
        position = position if position > 0 else 0.0
        position = position if position < 1 else 1.0
        return position

    def position_to_screen(self, position, random_range=(-0.05, 0.05)):
        """
        Convert scroll position to screen coordinates.
        Call cal_position() or match_color() to get length, before calling this.

        Args:
            position (int, float):
            random_range (tuple):

        Returns:
            tuple[int]: (upper_left_x, upper_left_y, bottom_right_x, bottom_right_y)
        """
        position = np.add(position, random_range)
        middle = position * (self.total - self.length) + self.length / 2
        middle = middle.astype(int)
        if self.is_vertical:
            middle += self.area[1]
            while np.max(middle) >= 720:
                middle -= 2
            while np.min(middle) <= 0:
                middle += 2
            area = (self.area[0], middle[0], self.area[2], middle[1])
        else:
            middle += self.area[0]
            while np.max(middle) >= 1280:
                middle -= 2
            while np.min(middle) <= 0:
                middle += 2
            area = (middle[0], self.area[1], middle[1], self.area[3])
        return area

    def appear(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            bool
        """
        return np.mean(self.match_color(main)) > 0.1

    def at_top(self, main):
        return self.cal_position(main) < self.edge_threshold

    def at_bottom(self, main):
        return self.cal_position(main) > 1 - self.edge_threshold

    def set(self, position, main, random_range=(-0.05, 0.05), distance_check=True, skip_first_screenshot=True):
        """
        Set scroll to a specific position.

        Args:
            position (float, int): 0 to 1.
            main (ModuleBase):
            random_range (tuple(int, float)):
            distance_check (bool): Whether to drop short swipes
            skip_first_screenshot:

        Returns:
            bool: If dragged.
        """
        self.drag_interval.clear()
        self.drag_timeout.reset()
        dragged = 0
        if position <= self.edge_threshold:
            random_range = np.subtract(0, self.edge_add)
        if position >= 1 - self.edge_threshold:
            random_range = self.edge_add

        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                main.device.screenshot()

            current = self.cal_position(main)
            if abs(position - current) < self.drag_threshold:
                break
            if self.length:
                self.drag_timeout.reset()
            else:
                if self.drag_timeout.reached():
                    break
                else:
                    continue

            if self.drag_interval.reached():
                p1 = random_rectangle_point(self.position_to_screen(current), n=1)
                p2 = random_rectangle_point(self.position_to_screen(position, random_range=random_range), n=1)
                main.device.swipe(p1, p2, name=self.name, distance_check=distance_check)
                self.drag_interval.reset()
                dragged += 1

        return dragged

    def set_top(self, main, random_range=(-0.05, 0.05), skip_first_screenshot=True):
        return self.set(0.00, main=main, random_range=random_range, skip_first_screenshot=skip_first_screenshot)

    def set_bottom(self, main, random_range=(-0.05, 0.05), skip_first_screenshot=True):
        return self.set(1.00, main=main, random_range=random_range, skip_first_screenshot=skip_first_screenshot)

    def drag_page(self, page, main, random_range=(-0.05, 0.05), skip_first_screenshot=True):
        """
        Drag scroll forward or backward.

        Args:
            page (int, float): Relative position to drag. 1.0 means next page, -1.0 means previous page.
            main (ModuleBase):
            random_range (tuple[float]):
            skip_first_screenshot:
        """
        if not skip_first_screenshot:
            main.device.screenshot()
        current = self.cal_position(main)

        multiply = self.length / (self.total - self.length)
        target = current + page * multiply
        target = round(min(max(target, 0), 1), 3)
        return self.set(target, main=main, random_range=random_range, skip_first_screenshot=True)

    def next_page(self, main, page=0.8, random_range=(-0.01, 0.01), skip_first_screenshot=True):
        return self.drag_page(page, main=main, random_range=random_range, skip_first_screenshot=skip_first_screenshot)

    def prev_page(self, main, page=0.8, random_range=(-0.01, 0.01), skip_first_screenshot=True):
        return self.drag_page(-page, main=main, random_range=random_range, skip_first_screenshot=skip_first_screenshot)
