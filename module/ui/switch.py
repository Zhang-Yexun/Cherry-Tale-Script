from module.base.base import ModuleBase
from module.base.button import Button
from module.base.timer import Timer




'''
这段代码定义了一个名为Switch的类，目的是为了在游戏自动化脚本中处理游戏内的开关操作。
这些开关可能是简单的二选一（比如开/关）或者是多选项中的选择。Switch类提供了一种灵活的方式来管理和操作这些游戏内的开关，
确保脚本能够根据需要改变开关的状态。

类的属性
name：开关的名称，类型为str，默认值为'Switch'。这个名称用于日志记录和调试。
is_choice：表示这个开关是否是多选一的选择器（selector），类型为bool。如果是，点击时会从多个选项中选择一个；
如果不是，则表示这个开关通过点击自身来改变状态（例如，从开到关）。
offset：全局偏移量，在当前开关中使用，类型可以是bool、int或tuple，默认值为0。这个偏移量用于调整检测或点击按钮时的位置。
status_list：存储开关状态信息的列表。每个状态是一个字典，包含状态名、检查按钮、点击按钮和偏移量。
类的方法
__init__(self, name='Switch', is_selector=False, offset=0)：构造函数，初始化开关对象。
add_status(self, status, check_button, click_button=None, offset=0)：向status_list添加一个新的状态。
每个状态包括状态名称、用于检测状态的按钮、用于改变状态的点击按钮（如果没有提供，则默认与检查按钮相同）、以及状态特定的偏移量。
appear(self, main)：检查开关的任意状态是否在当前页面出现。需要传入ModuleBase类型的对象main作为参数。如果任一状态出现，则返回True。
get(self, main)：获取当前的开关状态。通过检查status_list中每个状态的按钮是否出现来确定当前状态，返回状态名或'unknown'。
get_data(self, status)：根据给定的状态名返回对应的状态数据（一个字典）。如果状态无效，则抛出ScriptError异常。
handle_additional(self, main)：处理额外的弹窗或界面元素，需要在子类中实现具体逻辑。返回bool值，表示是否处理了额外的元素。
set(self, status, main, skip_first_screenshot=True)：设置开关的状态。
首先确认需要设置的状态是否有效，然后循环检查当前状态，直到开关状态改变为所需状态或达到重试限制。
在尝试改变状态之前，会调用handle_additional方法处理可能出现的额外弹窗。如果状态成功改变，
返回True；如果无法确定当前状态，可能会记录警告并最终返回False。
这个Switch类为游戏自动化提供了一个强大的工具，可以灵活地管理游戏内的各种开关状态，非常适合需要频繁改变设置或选项的游戏自动化场景。'''

class Switch:
    """
    A wrapper to handle switches in game.
    Set switch status with reties.

    Examples:
        # Definitions
        submarine_hunt = Switch('Submarine_hunt', offset=120)
        submarine_hunt.add_status('on', check_button=SUBMARINE_HUNT_ON)
        submarine_hunt.add_status('off', check_button=SUBMARINE_HUNT_OFF)

        # Change status to ON
        submarine_view.set('on', main=self)
    """

    def __init__(self, name='Switch', is_selector=False, offset=0):
        """
        Args:
            name (str):
            is_selector (bool): True if this is a multi choice, click to choose one of the switches.
                For example: | [Daily] | Urgent | -> click -> | Daily | [Urgent] |
                False if this is a switch, click the switch itself, and it changed in the same position.
                For example: | [ON] | -> click -> | [OFF] |
            offset (bool, int, tuple): Global offset in current switch
        """
        self.name = name
        self.is_choice = is_selector
        self.offset = offset
        self.status_list = []

    def add_status(self, status, check_button, click_button=None, offset=0):
        """
        Args:
            status (str):
            check_button (Button):
            click_button (Button):
            offset (bool, int, tuple):
        """
        self.status_list.append({
            'status': status,
            'check_button': check_button,
            'click_button': click_button if click_button is not None else check_button,
            'offset': offset if offset else self.offset
        })

    def appear(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            bool
        """
        for data in self.status_list:
            if main.appear(data['check_button'], offset=data['offset']):
                return True

        return False

    def get(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            str: Status name or 'unknown'.
        """
        for data in self.status_list:
            if main.appear(data['check_button'], offset=data['offset']):
                return data['status']

        return 'unknown'

    def get_data(self, status):
        """
        Args:
            status (str):

        Returns:
            dict: Dictionary in add_status

        Raises:
            ScriptError: If status invalid
        """
        for row in self.status_list:
            if row['status'] == status:
                return row

        logger.warning(f'Switch {self.name} received an invalid status {status}')
        raise ScriptError(f'Switch {self.name} received an invalid status {status}')

    def handle_additional(self, main):
        """
        Args:
            main (ModuleBase):

        Returns:
            bool: If handled
        """
        return False

    def set(self, status, main, skip_first_screenshot=True):
        """
        Args:
            status (str):
            main (ModuleBase):
            skip_first_screenshot (bool):

        Returns:
            bool:
        """
        self.get_data(status)

        counter = 0
        changed = False
        warning_show_timer = Timer(5, count=10).start()
        click_timer = Timer(1, count=3)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                main.device.screenshot()

            # Detect
            current = self.get(main=main)
            logger.attr(self.name, current)

            # Handle additional popups
            if self.handle_additional(main=main):
                continue

            # End
            if current == status:
                return changed

            # Warning
            if current == 'unknown':
                if warning_show_timer.reached():
                    logger.warning(f'Unknown {self.name} switch')
                    warning_show_timer.reset()
                    if counter >= 1:
                        logger.warning(f'{self.name} switch {status} asset has evaluated to unknown too many times, '
                                       f'asset should be re-verified')
                        return False
                    counter += 1
                continue

            # Click
            if click_timer.reached():
                click_status = status if self.is_choice else current
                main.device.click(self.get_data(click_status)['click_button'])
                click_timer.reset()
                changed = True

        return changed
