from module.base.base import ModuleBase
from module.base.button import ButtonGrid
from module.base.timer import Timer
from module.combat.assets import GET_ITEMS_1, GET_ITEMS_2, GET_SHIP
from module.logger import logger
from module.shop.assets import SHOP_CLICK_SAFE_AREA

'''
这段代码定义了一个名为Navbar的类，用于处理和操作游戏内导航栏（Navbar）的自动化。
这个类通过分析导航栏按钮的颜色来判断哪个按钮是活动的（即当前选中的），并提供了方法来改变导航栏的状态或导航到特定的部分。
类的属性
grids: ButtonGrid类型，代表导航栏的按钮集合。
active_color 和 inactive_color: 分别代表活动按钮和非活动按钮的RGB颜色。
active_threshold 和 inactive_threshold: 分别代表判断按钮为活动或非活动状态时的颜色阈值。
active_count 和 inactive_count: 分别代表颜色匹配计数的阈值，用于判断按钮是否为活动或非活动状态。
name: 导航栏的名称。
类的方法
is_button_active 和 is_button_inactive: 通过比较按钮区域内的颜色与预定义的活动/非活动颜色来判断按钮是否处于活动/非活动状态。
get_info: 返回当前活动的导航项索引、最左侧和最右侧导航项的索引。
get_active: 返回当前活动的导航项索引。
get_total: 返回导航栏中可见的导航项总数。
_shop_obstruct_handle: 特定于“商店”视图，用于处理可能遮挡导航栏按钮的弹窗或其他UI元素。
set: 根据提供的索引（从左、右、上或下方计数）来激活特定的导航项。
这个类主要被用于需要在游戏内的多个不同界面之间导航时，比如从主界面切换到商店界面、任务界面或其他任何通过导航栏访问的界面。
Navbar类通过提供一套方法来识别当前活动的按钮，并能够根据需要点击特定的按钮来改变当前界面，极大地简化了游戏自动化脚本在处理导航栏操作时的复杂性。
'''

class Navbar:
    def __init__(self, grids, active_color=(247, 251, 181), inactive_color=(140, 162, 181), active_threshold=180,
                 inactive_threshold=180, active_count=100, inactive_count=50, name=None):
        """
        Args:
            grids (ButtonGrid):
            active_color (tuple[int, int, int]):
            inactive_color (tuple[int, int, int]):
            active_threshold (int):
            inactive_threshold (int):
            active_count (int):
            inactive_count (int):
            name (str):
        """
        self.grids = grids
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.active_threshold = active_threshold
        self.inactive_threshold = inactive_threshold
        self.active_count = active_count
        self.inactive_count = inactive_count
        self.name = name if name is not None else grids._name

    def is_button_active(self, button, main):
        """
        Args:
            button (Button):
            main (ModuleBase):

        Returns:
            bool:
        """
        return main.image_color_count(
                    button, color=self.active_color, threshold=self.active_threshold, count=self.active_count)

    def is_button_inactive(self, button, main):
        """
        Args:
            button (Button):
            main (ModuleBase):

        Returns:
            bool:
        """
        return main.image_color_count(
            button, color=self.inactive_color, threshold=self.inactive_threshold, count=self.inactive_count)

    def get_info(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            int, int, int: Index of the active nav item, leftmost nav item, and rightmost nav item.
        """
        total = []
        active = []
        for index, button in enumerate(self.grids.buttons):
            if self.is_button_active(button, main=main):
                total.append(index)
                active.append(index)
            elif self.is_button_inactive(button, main=main):
                total.append(index)

        if len(active) == 0:
            # logger.warning(f'No active nav item found in {self.name}')
            active = None
        elif len(active) == 1:
            active = active[0]
        else:
            logger.warning(f'Too many active nav items found in {self.name}, items: {active}')
            active = active[0]

        if len(total) < 2:
            logger.warning(f'Too few nav items found in {self.name}, items: {total}')
        if len(total) == 0:
            left, right = None, None
        else:
            left, right = min(total), max(total)

        return active, left, right

    def get_active(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            int: Index of the active nav item.
        """
        return self.get_info(main=main)[0]

    def get_total(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            int: Numbers of nav items that appears
        """
        _, left, right = self.get_info(main=main)
        if left is None or right is None:
            return 0
        return right - left + 1

    def _shop_obstruct_handle(self, main):
        """
        IFF in shop, then remove obstructions
        in shop view if any

        Args:
            main (ModuleBase):

        Returns:
            bool:
        """
        # Check name, identifies if NavBar
        # instance belongs to shop module
        if self.name not in ['SHOP_BOTTOM_NAVBAR', 'GUILD_SIDE_NAVBAR']:
            return False

        # Handle shop obstructions
        if main.appear(GET_SHIP, interval=1):
            main.device.click(SHOP_CLICK_SAFE_AREA)
            return True
        if main.appear(GET_ITEMS_1, offset=(30, 30), interval=1):
            main.device.click(SHOP_CLICK_SAFE_AREA)
            return True
        if main.appear(GET_ITEMS_2, offset=(30, 30), interval=1):
            main.device.click(SHOP_CLICK_SAFE_AREA)
            return True

        return False

    def set(self, main, left=None, right=None, upper=None, bottom=None, skip_first_screenshot=True):
        """
        Set nav bar from 1 direction.

        Args:
            main (ModuleBase):
            left (int): Index of nav item counted from left. Start from 1.
            right (int): Index of nav item counted from right. Start from 1.
            upper (int): Index of nav item counted from upper. Start from 1.
            bottom (int): Index of nav item counted from bottom. Start from 1.
            skip_first_screenshot (bool):

        Returns:
            bool: If success
        """
        if left is None and right is None and upper is None and bottom is None:
            logger.warning('Invalid index to set, must set an index from 1 direction')
            return False
        text = ''
        if left is None and upper is not None:
            left = upper
        if right is None and bottom is not None:
            right = bottom
        for k in ['left', 'right', 'upper', 'bottom']:
            if locals().get(k, None) is not None:
                text += f'{k}={locals().get(k, None)} '
        logger.info(f'{self.name} set to {text.strip()}')

        interval = Timer(2, count=4)
        timeout = Timer(10, count=20).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                main.device.screenshot()

            if timeout.reached():
                logger.warning(f'{self.name} failed to set {text.strip()}')
                return False

            if self._shop_obstruct_handle(main=main):
                interval.reset()
                timeout.reset()
                continue

            active, minimum, maximum = self.get_info(main=main)
            logger.info(f'Nav item active: {active} from range ({minimum}, {maximum})')
            # Get None when receiving a pure black screenshot.
            if minimum is None or maximum is None:
                continue

            index = minimum + left - 1 if left is not None else maximum - right + 1
            if not minimum <= index <= maximum:
                logger.warning(
                    f'Index to set ({index}) is not within the nav items that appears ({minimum}, {maximum})')
                continue

            # End
            if active == index:
                return True

            if interval.reached():
                main.device.click(self.grids.buttons[index])
                interval.reset()
