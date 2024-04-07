from module.base.button import Button
from module.base.decorator import cached_property
from module.base.timer import Timer
from module.base.utils import *
from module.base.screenshot import Adb

"""
属性:
interval_timer: 一个字典，用于存储与按钮相关的间隔定时器。
方法:
__init__: 构造函数，初始化配置和设备。
ensure_button: 确保传入的button是可操作的，如果是字符串，则转换为HierarchyButton。(已经删除)
appear: 检查指定的按钮或元素是否出现在界面上。
appear_then_click: 如果指定的按钮或元素出现，则进行点击操作。
wait_until_appear/wait_until_appear_then_click/wait_until_disappear: 这些方法提供等待界面元素出现或消失的功能，并在条件满足时执行相应操作。
wait_until_stable: 等待直到一个界面元素变得稳定（不再改变位置或状态）。
image_crop: 从当前屏幕截图中裁剪出指定区域的图像。
image_color_count/image_color_button: 这些方法涉及到在指定区域内根据颜色进行图像分析，用于检测特定颜色的按钮或元素。
interval_reset/interval_clear: 这些方法用于管理和重置指定按钮的触发间隔。
"""
# base.py_config
COLOR_SIMILAR_THRESHOLD = 10
BUTTON_OFFSET = 30
BUTTON_MATCH_SIMILARITY = 0.75
WAIT_BEFORE_SAVING_SCREEN_SHOT = 1


class ModuleBase:

    def __init__(self, adb=None):
        if isinstance(adb, Adb):
            self.adb = adb
        elif adb is None:
            self.adb = Adb()
        else:
            print("你没有创建Adb实例，不能使用其中的例子")
        # else:
        #     self.adb=Adb() #如果没有传递Adb实例，则创建一个新的

        self.interval_timer = {}

    '''adb_instance = Adb()
    adb_instance.adb_screenshot()
    button_instance = Button(area=(...), color=(...), button=(...))  # 这里假设Button类已经定义
    appeared = module_base_instance.appear(button_instance)module_base_instance = ModuleBase(adb=adb_instance)'''

    def match(self, button, offset=0, threshold=0):
        match = button.match(self.adb.image, offset=offset,
                             threshold=BUTTON_MATCH_SIMILARITY if threshold is None else threshold)
        return match

    def match_then_click(self, button, screenshot=False, offset=0, interval=0, threshold=None):
        match = self.match(button, offset=offset, threshold=threshold)
        if match:
            self.adb.sleep(WAIT_BEFORE_SAVING_SCREEN_SHOT)
            self.adb.click(button)
            print("click Yes")
        else:
            print("match_then_click函数没有match到Button")
        return match

    def appear(self, button, offset=0, interval=0, threshold=None):
        """
        Args:
            button (Button, Template, HierarchyButton(以删除), str):
            offset (bool, int):
            interval (int, float): interval between two active events.
            threshold (int, float): 0 to 1 if use offset, bigger means more similar,
                0 to 255 if not use offset, smaller means more similar

        Returns:
            bool:

        Examples:
            Image detection:
            ```
            self.adb.adb_screenshot()
            self.appear(Button(area=(...), color=(...), button=(...))
            self.appear(Template(file='...')
            ```
        """

        if interval:
            if button.name in self.interval_timer:
                if self.interval_timer[button.name].limit != interval:
                    self.interval_timer[button.name] = Timer(interval)
            else:
                self.interval_timer[button.name] = Timer(interval)
            if not self.interval_timer[button.name].reached():
                return False

        if offset:
            if isinstance(offset, bool):
                offset = BUTTON_OFFSET
            appear = button.match(self.adb.image, offset=offset,
                                  threshold=BUTTON_MATCH_SIMILARITY if threshold is None else threshold)

        else:
            appear = button.appear_on(self.adb.image,
                                      threshold=COLOR_SIMILAR_THRESHOLD if threshold is None else threshold)

        if appear and interval:
            self.interval_timer[button.name].reset()

        return appear

    def appear_then_click(self, button, screenshot=False, genre='items', offset=0, interval=0, threshold=None):
        appear = self.appear(button, offset=offset, interval=interval, threshold=threshold)
        if appear:
            if screenshot:
                self.adb.sleep(WAIT_BEFORE_SAVING_SCREEN_SHOT)
                self.adb.adb_screenshot()
                self.adb.click(button)
        else:
            print("appear_then_click函数没有appear到Button")
        return appear

    def wait_until_appear(self, button, offset=0, skip_first_screenshot=False):
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.adb.adb_screenshot()
            if self.match(button, offset=offset):
                break

    def wait_until_appear_then_click(self, button, offset=0):
        self.wait_until_appear(button, offset=offset)
        self.adb.click(button)

    def wait_until_disappear(self, button, offset=0):
        while 1:
            self.adb.adb_screenshot()
            if not self.appear(button, offset=offset):
                break

    def wait_until_stable(self, button, timer=Timer(0.3, count=1), timeout=Timer(8, count=10),
                          skip_first_screenshot=True):
        button._match_init = False
        timeout.reset()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.adb.adb_screenshot()

            if button._match_init:
                if button.match(self.adb.image, offset=(0, 0)):
                    if timer.reached():
                        break
                else:
                    button.load_color(self.adb.image)
                    timer.reset()
            else:
                button.load_color(self.adb.image)
                button._match_init = True

            if timeout.reached():
                print(f'wait_until_stable({button}) timeout')
                break

    def image_crop(self, button, copy=True):
        """Extract the area from image.

        Args:
            button(Button, tuple): Button instance or area tuple.
            copy:
        """
        if isinstance(button, Button):
            return crop(self.adb.image, button.area, copy=copy)
        elif hasattr(button, 'area'):
            return crop(self.adb.image, button.area, copy=copy)
        else:
            return crop(self.adb.image, button, copy=copy)

    def image_color_count(self, button, color, threshold=221, count=50):
        """
        Args:
            button (Button, tuple): Button instance or area.
            color (tuple): RGB.
            threshold: 255 means colors are the same, the lower the worse.
            count (int): Pixels count.

        Returns:
            bool:
        """
        if isinstance(button, np.ndarray):
            image = button
        else:
            image = self.image_crop(button, copy=False)
        mask = color_similarity_2d(image, color=color)
        cv2.inRange(mask, threshold, 255, dst=mask)
        sum_ = cv2.countNonZero(mask)
        return sum_ > count

    # def image_color_button(self, area, color, color_threshold=250, encourage=5, name='COLOR_BUTTON'):
    #     """
    #     Find an area with pure color on image, convert into a Button.
    #
    #     Args:
    #         area (tuple[int]): Area to search from
    #         color (tuple[int]): Target color
    #         color_threshold (int): 0-255, 255 means exact match
    #         encourage (int): Radius of button
    #         name (str): Name of the button
    #
    #     Returns:
    #         Button: Or None if nothing matched.
    #     """
    #     image = color_similarity_2d(self.image_crop(area), color=color)
    #     points = np.array(np.where(image > color_threshold)).T[:, ::-1]
    #     if points.shape[0] < encourage ** 2:
    #         # Not having enough pixels to match
    #         return None
    #
    #     point = fit_points(points, mod=image_size(image), encourage=encourage)
    #     point = ensure_int(point + area[:2])
    #     button_area = area_offset((-encourage, -encourage, encourage, encourage), offset=point)
    #     color = get_color(self.device.image, button_area)
    #     return Button(area=button_area, color=color, button=button_area, name=name)

    def interval_reset(self, button, interval=3):
        if isinstance(button, (list, tuple)):
            for b in button:
                self.interval_reset(b)
            return

        if button is not None:
            if button.name in self.interval_timer:
                self.interval_timer[button.name].reset()
            else:
                self.interval_timer[button.name] = Timer(interval).reset()

    def interval_clear(self, button, interval=3):
        if isinstance(button, (list, tuple)):
            for b in button:
                self.interval_clear(b)
            return

        if button is not None:
            if button.name in self.interval_timer:
                self.interval_timer[button.name].clear()
            else:
                self.interval_timer[button.name] = Timer(interval).clear()

    _image_file = ''

    @property
    def image_file(self):
        return self._image_file

    @image_file.setter
    def image_file(self, value):
        """
        For development.
        Load image from local file system and set it to self.adb.image
        Test an image without taking a screenshot from emulator.
        """
        if isinstance(value, Image.Image):
            value = np.array(value)
        elif isinstance(value, str):
            value = load_image(value)

        self.adb.image = value
