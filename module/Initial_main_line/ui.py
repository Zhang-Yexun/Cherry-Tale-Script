# 文件名：
# 功能：
# 作者：张业勋
# 日期：
# 思路：
from module.base.base import *
from module.Initial_main_line.assets import Adventure_Button
from module.base.base import ModuleBase

adb_instance = Adb()
adb_instance.adb_screenshot()
module_base_instance = ModuleBase(adb_instance)
module_base_instance.appear_then_click(Adventure_Button, screenshot=True)
