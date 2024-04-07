# 文件名：
# 功能：
# 作者：zyx
# 日期：
# 思路：
from module.Initial_main_line.assets import *
from module.base.base import ModuleBase
from module.base.screenshot import Adb
from module.base.button import Button

print(test_Adventure.name)
adb_instance = Adb()
screenshot = adb_instance.adb_screenshot()
Base_instance = ModuleBase(adb_instance)
Base_instance.wait_until_appear_then_click(ADVENTURE_BUTTON)
Base_instance.wait_until_stable(CRUSADE_BUTTON)
Base_instance.match_then_click(CRUSADE_BUTTON)
Base_instance.wait_until_stable(FIRST_BATTLE_BUTTON)
Base_instance.match_then_click(FIRST_BATTLE_BUTTON)
Base_instance.wait_until_stable(FIGHT_PREPARE_BUTTON)
Base_instance.match_then_click(FIGHT_PREPARE_BUTTON)
Base_instance.wait_until_stable(FIGHT_START_BUTTON)
Base_instance.match_then_click(FIGHT_START_BUTTON)
