import copy
import typing as t

from module.base.base import ModuleBase
from module.base.button import Button, ButtonGrid
from module.base.timer import Timer
from module.config.utils import dict_to_kv
from module.exception import ScriptError
from module.logger import logger
'''
这段代码定义了一个名为Setting的类，用于管理和设置游戏内的各种设置选项。Setting类通过与ModuleBase（基础模块类）的交互，
允许自动化脚本动态调整游戏设置，比如排序方式或筛选条件等。以下是对这个类及其方法的详细解释：
类属性和构造函数
name: 设置组的名称。
main: ModuleBase的实例，用于执行游戏内操作，如点击按钮或读取屏幕信息。
reset_first: 在应用新设置之前是否重置到默认设置的标志。
settings: 一个字典，键为(设置名, 选项名)的元组，值为对应的Button对象。
settings_default: 一个字典，记录每个设置的默认选项名称。
方法
add_setting: 添加一个设置及其选项按钮、选项名称和默认选项。
is_option_active: 判断给定的选项是否处于激活状态，基于选项按钮颜色的计数判断。
_product_setting_status: 根据给定的设置需求生成一个状态字典，键为选项按钮，值为该选项是否应该被激活。
show_active_buttons: 显示当前激活的设置选项。
get_buttons_to_click: 根据期望的设置状态，确定需要点击的按钮列表。
_set_execute: 执行设置更改，包括重试机制和超时检查。
set: 公共接口方法，用于应用一组设置。如果reset_first为True，则会先重置设置再应用新设置。
功能流程
初始化：通过构造函数初始化实例，可指定设置组的名称及关联的ModuleBase实例。
添加设置：通过add_setting方法，为实例添加一组设置，包括设置的名称、相关的按钮（可以是ButtonGrid产生的按钮列表）、选项名称列表以及默认选项。
设置应用：set方法是应用设置的主入口，它允许指定一组设置及其期望的选项。方法内部会计算哪些按钮需要点击来达到期望的设置状态，并执行相应的点击操作。
应用场景
这个Setting类可以广泛应用于需要动态调整游戏设置的自动化脚本中。比如，在自动执行任务、刷图或其他游戏内活动前，
根据任务的具体需求动态调整排序、筛选等设置，以优化自动化流程的效率和效果。通过预定义设置选项和与ModuleBase的交互，Setting类提供了一种灵活且高效的方式来控制游戏内的各种设置。
'''

class Setting:
    def __init__(self, name='Setting', main: ModuleBase = None):
        self.name = name
        # Alas module object
        self.main: ModuleBase = main
        # Reset options before setting any options
        self.reset_first = True
        # (setting, opiton_name): option_button
        # {
        #     ('sort', 'rarity'): Button(),
        #     ('sort', 'level'): Button(),
        #     ('sort', 'total'): Button(),
        # }
        self.settings: t.Dict[(str, str), Button] = {}
        # setting: option_name
        # {
        #     'sort': 'rarity',
        #     'index': 'all',
        # }
        self.settings_default: t.Dict[str, str] = {}

    def add_setting(self, setting, option_buttons, option_names, option_default):
        """
        Args:
            setting (str):
                Name of the setting
            option_buttons (list[Button], ButtonGrid):
                List of buttons produced by ButtonGrid.buttons
            option_names (list[str]):
                Name of each options, `option_names` and `options` must has the same length.
            option_default (str):
                Name of the default option, must in `option_names`
        """
        if isinstance(option_buttons, ButtonGrid):
            option_buttons = option_buttons.buttons
        for option, option_name in zip(option_buttons, option_names):
            self.settings[(setting, option_name)] = option

        if option_default not in option_names:
            raise ScriptError(f'Define option_default="{option_default}", '
                              f'but default is not in option_names={option_names}')
        self.settings_default[setting] = option_default

    def is_option_active(self, option: Button) -> bool:
        return self.main.image_color_count(option, color=(181, 142, 90), threshold=235, count=250) \
               or self.main.image_color_count(option, color=(74, 117, 189), threshold=235, count=250)

    def _product_setting_status(self, **kwargs) -> t.Dict[Button, bool]:
        """
        Args:
            **kwargs: Key: setting, value: required option or a list of them
                `sort=['rarity', 'level'], ...` or `sort='rarity'`,
                or `sort=None` means don't change this setting

        Returns:
            dict: Key: option_button, value: whether should be active
        """
        # Add defaults
        required_options = copy.deepcopy(self.settings_default)
        required_options.update(kwargs)

        # option_button: Whether should be active
        # {BUTTON_1: True, BUTTON_2: False, ...}
        status: t.Dict[Button, bool] = {}
        for key, option_button in self.settings.items():
            setting, option_name = key
            required = required_options[setting]
            if required is not None:
                required = required if isinstance(required, list) else [required]
                status[option_button] = option_name in required

        return status

    def show_active_buttons(self):
        """
        Logs:
            [Setting] sort/rarity, sort/level
        """
        active = []
        for key, option_button in self.settings.items():
            setting, option_name = key
            if self.is_option_active(option_button):
                active.append(f'{setting}/{option_name}')

        logger.attr(self.name, ', '.join(active))

    def get_buttons_to_click(self, status: t.Dict[Button, bool]) -> t.List[Button]:
        """
        Args:
            status: Key: option_button, value: whether should be active

        Returns:
            Buttons to click
        """
        click = []
        for option_button, enable in status.items():
            active = self.is_option_active(option_button)
            if enable and not active:
                click.append(option_button)
        return click

    def _set_execute(self, **kwargs):
        """
        Args:
            **kwargs: Key: setting, value: required option or a list of them
                `sort=['rarity', 'level'], ...` or `sort='rarity'`,
                or `sort=None` means don't change this setting

        Returns:
            bool: If success the set
        """
        status = self._product_setting_status(**kwargs)

        logger.info(f'Setting {self.name} options, {dict_to_kv(kwargs)}')
        skip_first_screenshot = True
        retry = Timer(1, count=2)
        timeout = Timer(10, count=20).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.main.device.screenshot()

            if timeout.reached():
                logger.warning(f'Set {self.name} options timeout, assuming current options are correct.')
                return False

            self.show_active_buttons()
            clicks = self.get_buttons_to_click(status)
            if clicks:
                if retry.reached():
                    for button in clicks:
                        self.main.device.click(button)
                    retry.reset()
            else:
                return True

    def set(self, **kwargs):
        """
        Args:
            **kwargs: Key: setting, value: required option or a list of them
                `sort=['rarity', 'level'], ...` or `sort='rarity'`,
                or `sort=None` means don't change this setting

        Returns:
            bool: If success the set
        """
        if self.reset_first:
            self._set_execute()  # Reset options
        self._set_execute(**kwargs)
