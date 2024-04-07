from module.base.button import Button
from module.base.decorator import run_once
from module.base.timer import Timer
from module.handler.info_handler import InfoHandler
from module.ocr.ocr import Ocr
from module.ui.assets import (BACK_ARROW, DORMMENU_GOTO_DORM, DORM_FEED_CANCEL, DORM_INFO, DORM_TROPHY_CONFIRM,
                              EVENT_LIST_CHECK, GOTO_MAIN, MAIN_GOTO_CAMPAIGN, MEOWFFICER_GOTO_DORMMENU,
                              MEOWFFICER_INFO, META_CHECK, PLAYER_CHECK, RAID_CHECK, SHIPYARD_CHECK,
                              SHOP_GOTO_SUPPLY_PACK)
from module.ui.page import (Page, page_campaign, page_event, page_main, page_sp)

'''这段代码中的UI类继承自InfoHandler类，专门用于处理与游戏用户界面（UI）相关的自动化任务。UI类通过识别和操作屏幕上的元素，实现在游戏内导航和执行特定操作的功能。下面详细介绍UI类的属性和方法：

类的属性
ui_current: Page类型，表示当前游戏页面。这个属性用来追踪自动化脚本当前处于游戏中的哪个页面。
_opsi_reset_fleet_preparation_click: 整型，用于记录在操作页面（可能是指某种特殊模式下的舰队重置操作）中点击重置舰队准备按钮的次数，以防止在错误状态下无限循环。
类的方法
ui_page_appear(self, page)
检查指定页面是否出现。
参数page是Page类型，表示要检查的页面。
返回布尔值，表示页面是否出现。
ensure_button_execute(self, button, offset=0)
确保按钮执行，即点击按钮或调用函数。
参数button可以是Button类型或可调用对象；offset用于调整点击位置。
返回布尔值，表示操作是否成功。
ui_click(...)
在UI上执行点击操作，并等待特定按钮出现或条件满足。
参数包括要点击的按钮、检查按钮、等待时间等。
没有返回值，主要用于执行操作并通过循环等待直到期望的结果出现。
ui_process_check_button(self, check_button, offset=(30, 30))
处理检查按钮的逻辑。
参数check_button可以是Button、可调用对象或它们的列表；offset调整识别区域。
返回布尔值，表示按钮是否出现。
ui_get_current_page(self, skip_first_screenshot=True)
获取当前游戏页面。
参数skip_first_screenshot表示是否跳过首次截图。
返回Page对象，表示当前页面。
ui_goto(self, destination, offset=(30, 30), skip_first_screenshot=True)
导航到指定的游戏页面。
参数destination是Page类型，表示目标页面。
没有返回值，用于改变当前页面。
ui_ensure(...)
确保当前页面是指定页面，如果不是则尝试导航到该页面。
参数包括目标页面等。
返回布尔值，表示是否进行了页面切换。
ui_goto_main(self), ui_goto_campaign(self), ui_goto_event(self), ui_goto_sp(self)
分别用于导航到游戏的主页面、战役页面、事件页面和特别页面。
没有参数。
返回布尔值，表示是否进行了页面切换。
ui_ensure_index(...)
确保在具有索引的页面上选中了正确的项。
参数包括索引值、OCR对象或函数、翻页按钮等。
没有返回值，用于选择页面上的特定项。
ui_back(...)
在UI中执行返回操作。
参数包括检查按钮、等待时间等。
用于返回到前一个页面或特定页面。
ui_page_main_popups(self, get_ship=True), ui_page_os_popups(self)
分别处理主页面和操作系统页面出现的弹窗。
参数get_ship用于控制是否处理领船弹窗。
返回布尔值，表示是否处理了弹窗。
ui_additional(self)
处理在UI切换过程中可能出现的所有烦人弹窗。
没有参数。
返回布尔值，表示是否处理了额外的弹窗。
ui_button_interval_reset(self, button)
重置特定按钮的点击间隔，以避免在错误状态下无限循环点击。

参数button是Button类型，表示需要重置点击间隔的按钮。
没有返回值，主要用于在一系列操作后重置按钮的状态，以确保后续操作的准确性。
这些方法的设计明显考虑到了游戏UI的动态性和不确定性，例如页面跳转延迟、弹窗随机出现等，
通过细致的条件判断和页面状态跟踪来保证自动化脚本的鲁棒性和可靠性。以下是一些特别注意的点：
页面状态跟踪：通过ui_current属性和各种ui_goto_方法，脚本能够知道自己当前处于游戏的哪个页面，并据此执行相应的操作。
这是自动化游戏操作中非常重要的部分，因为正确的页面状态是执行大多数操作的前提。
弹窗处理：游戏中的弹窗可能会随机出现，且种类繁多（如登录奖励、日常任务完成提示、特殊事件通知等）
ui_page_main_popups和ui_page_os_popups方法及其调用的其他方法，展示了脚本是如何识别和处理这些弹窗的，确保它们不会干扰到自动化流程的执行。
错误和异常处理：在自动化过程中可能会遇到各种异常情况，如游戏未运行、未知的页面状态、需要人工干预等，
通过定义和抛出特定的异常类（如GameNotRunningError, GamePageUnknownError等），脚本能够更好地管理这些异常情况，以及提供更清晰的错误信息。
交互抽象：通过将屏幕上的按钮、弹窗等UI元素抽象成Button对象和相应的操作方法（如ui_click, ui_back等），脚本的可读性和可维护性得到了提高。
这种抽象还使得对游戏UI的小幅改动（如按钮位置调整）能够通过修改Button对象的定义来快速适应，而不需要重写大量的代码。
'''

class UI(InfoHandler):
    ui_current: Page

    def ui_page_appear(self, page):
        """
        Args:
            page (Page):
        """
        return self.appear(page.check_button, offset=(30, 30))

    def ensure_button_execute(self, button, offset=0):
        if isinstance(button, Button) and self.appear(button, offset=offset):
            return True
        elif callable(button) and button():
            return True
        else:
            return False

    def ui_click(
            self,
            click_button,
            check_button,
            appear_button=None,
            additional=None,
            confirm_wait=1,
            offset=(30, 30),
            retry_wait=10,
            skip_first_screenshot=False,
    ):
        """
        Args:
            click_button (Button):
            check_button (Button, callable):
            appear_button (Button, callable):
            additional (callable):
            confirm_wait (int, float):
            offset (bool, int, tuple):
            retry_wait (int, float):
            skip_first_screenshot (bool):
        """
        if appear_button is None:
            appear_button = click_button

        click_timer = Timer(retry_wait, count=retry_wait // 0.5)
        confirm_wait = confirm_wait if additional is not None else 0
        confirm_timer = Timer(confirm_wait, count=confirm_wait // 0.5).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.adb.abd_screenshot()

            if self.ui_process_check_button(check_button, offset=offset):
                if confirm_timer.reached():
                    break
            else:
                confirm_timer.reset()

            if click_timer.reached():
                if (isinstance(appear_button, Button) and self.appear(appear_button, offset=offset)) or (
                        callable(appear_button) and appear_button()
                ):
                    click_adb(click_button)
                    click_timer.reset()
                    continue

            if additional is not None:
                if additional():
                    continue

    def ui_process_check_button(self, check_button, offset=(30, 30)):
        """
        Args:
            check_button (Button, callable, list[Button], tuple[Button]):
            offset:

        Returns:
            bool:
        """
        if isinstance(check_button, Button):
            return self.appear(check_button, offset=offset)
        elif callable(check_button):
            return check_button()
        elif isinstance(check_button, (list, tuple)):
            for button in check_button:
                if self.appear(button, offset=offset):
                    return True
            return False
        else:
            return self.appear(check_button, offset=offset)

    def ui_get_current_page(self, skip_first_screenshot=True):
        """
        Args:
            skip_first_screenshot:

        Returns:
            Page:
        """

        @run_once
        def rotation_check():
            self.device.get_orientation()

        timeout = Timer(10, count=20).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
                if not hasattr(self.device, "image") or self.device.image is None:
                    self.device.screenshot()
            else:
                self.device.screenshot()

            # End
            if timeout.reached():
                break

            # Known pages
            for page in Page.iter_pages():
                if page.check_button is None:
                    continue
                if self.ui_page_appear(page=page):
                    self.ui_current = page
                    return page

            # Unknown page but able to handle
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30), interval=2) or self.ui_additional():
                timeout.reset()
                continue

    def ui_goto(self, destination, offset=(30, 30), skip_first_screenshot=True):
        """
        Args:
            destination (Page):
            offset:
            skip_first_screenshot:
        """
        # Create connection
        Page.init_connection(destination)
        self.interval_clear(list(Page.iter_check_buttons()))
        while 1:
            GOTO_MAIN.clear_offset()
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            # Destination page
            if self.appear(destination.check_button, offset=offset):
                break

            # Other pages
            clicked = False
            for page in Page.iter_pages():
                if page.parent is None or page.check_button is None:
                    continue
                if self.appear(page.check_button, offset=offset, interval=5):
                    button = page.links[page.parent]
                    self.device.click(button)
                    self.ui_button_interval_reset(button)
                    clicked = True
                    break
            if clicked:
                continue

            # Additional
            if self.ui_additional():
                continue

        # Reset connection
        Page.clear_connection()

    def ui_ensure(self, destination, skip_first_screenshot=True):
        """
        Args:
            destination (Page):
            skip_first_screenshot:

        Returns:
            bool: If UI switched.
        """
        self.ui_get_current_page(skip_first_screenshot=skip_first_screenshot)
        if self.ui_current == destination:
            logger.info("Already at %s" % destination)
            return False
        else:
            logger.info("Goto %s" % destination)
            self.ui_goto(destination, skip_first_screenshot=True)
            return True

    def ui_goto_main(self):
        return self.ui_ensure(destination=page_main)

    def ui_goto_campaign(self):
        return self.ui_ensure(destination=page_campaign)

    def ui_goto_event(self):
        return self.ui_ensure(destination=page_event)

    def ui_goto_sp(self):
        return self.ui_ensure(destination=page_sp)

    def ui_ensure_index(
            self,
            index,
            letter,
            next_button,
            prev_button,
            skip_first_screenshot=False,
            fast=True,
            interval=(0.2, 0.3),
    ):
        """
        Args:
            index (int):
            letter (Ocr, callable): OCR button.
            next_button (Button):
            prev_button (Button):
            skip_first_screenshot (bool):
            fast (bool): Default true. False when index is not continuous.
            interval (tuple, int, float): Seconds between two click.
        """
        logger.hr("UI ensure index")
        retry = Timer(1, count=2)
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if isinstance(letter, Ocr):
                current = letter.ocr(self.device.image)
            else:
                current = letter(self.device.image)

            logger.attr("Index", current)
            diff = index - current
            if diff == 0:
                break

            if retry.reached():
                button = next_button if diff > 0 else prev_button
                if fast:
                    self.device.multi_click(button, n=abs(diff), interval=interval)
                else:
                    self.device.click(button)
                retry.reset()

    def ui_back(self, check_button, appear_button=None, offset=(30, 30), retry_wait=10, skip_first_screenshot=False):
        return self.ui_click(
            click_button=BACK_ARROW,
            check_button=check_button,
            appear_button=appear_button,
            offset=offset,
            retry_wait=retry_wait,
            skip_first_screenshot=skip_first_screenshot,
        )

    _opsi_reset_fleet_preparation_click = 0

    def ui_page_main_popups(self, get_ship=True):
        """
        Handle popups appear at page_main, page_reward
        """
        # Guild popup
        if self.handle_guild_popup_cancel():
            return True

        # Daily reset
        if self.appear_then_click(LOGIN_ANNOUNCE, offset=(30, 30), interval=3):
            return True
        if self.appear_then_click(GET_ITEMS_1, offset=True, interval=3):
            return True
        if self.appear_then_click(GET_ITEMS_2, offset=True, interval=3):
            return True
        if get_ship:
            if self.appear_then_click(GET_SHIP, interval=5):
                return True
        if self.appear_then_click(LOGIN_RETURN_SIGN, offset=(30, 30), interval=3):
            return True
        if self.appear(EVENT_LIST_CHECK, offset=(30, 30), interval=3):
            logger.info(f'UI additional: {EVENT_LIST_CHECK} -> {GOTO_MAIN}')
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30)):
                return True
        # Monthly pass is about to expire
        if self.appear_then_click(MONTHLY_PASS_NOTICE, offset=(30, 30), interval=3):
            return True
        # Battle pass is about to expire and player has uncollected battle pass rewards
        if self.appear_then_click(BATTLE_PASS_NOTICE, offset=(30, 30), interval=3):
            return True
        if self.appear_then_click(PURCHASE_POPUP, offset=(44, -77, 84, -37), interval=3):
            return True
        # Item expired offset=(37, 72), skin expired, offset=(24, 68)
        if self.handle_popup_single(offset=(-6, 48, 54, 88), name='ITEM_EXPIRED'):
            return True
        # Routed from confirm click
        if self.appear(SHIPYARD_CHECK, offset=(30, 30), interval=3):
            logger.info(f'UI additional: {SHIPYARD_CHECK} -> {GOTO_MAIN}')
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30)):
                return True
        if self.appear(META_CHECK, offset=(30, 30), interval=3):
            logger.info(f'UI additional: {META_CHECK} -> {GOTO_MAIN}')
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30)):
                return True
        # Mistaken click
        if self.appear(PLAYER_CHECK, offset=(30, 30), interval=3):
            logger.info(f'UI additional: {PLAYER_CHECK} -> {GOTO_MAIN}')
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30)):
                return True
            if self.appear_then_click(BACK_ARROW, offset=(30, 30)):
                return True

        return False

    def ui_page_os_popups(self):
        """
        Handle popups appear at page_os
        """
        # Opsi reset
        # - Opsi has reset, handle_story_skip() clicks confirm
        # - RESET_TICKET_POPUP
        # - Open exchange shop? handle_popup_confirm() click confirm
        # - EXCHANGE_CHECK, click BACK_ARROW
        if self._opsi_reset_fleet_preparation_click >= 5:
            logger.critical("Failed to confirm OpSi fleets, too many click on RESET_FLEET_PREPARATION")
            logger.critical("Possible reason #1: You haven't set any fleets in operation siren")
            logger.critical(
                "Possible reason #2: Your fleets haven't satisfied the level restrictions in operation siren")
            raise RequestHumanTakeover
        if self.appear_then_click(RESET_TICKET_POPUP, offset=(30, 30), interval=3):
            return True
        if self.appear_then_click(RESET_FLEET_PREPARATION, offset=(30, 30), interval=3):
            self._opsi_reset_fleet_preparation_click += 1
            self.interval_reset(FLEET_PREPARATION)
            self.interval_reset(RESET_TICKET_POPUP)
            return True
        if self.appear(EXCHANGE_CHECK, offset=(30, 30), interval=3):
            logger.info(f'UI additional: {EXCHANGE_CHECK} -> {GOTO_MAIN}')
            GOTO_MAIN.clear_offset()
            self.device.click(GOTO_MAIN)
            return True

        return False

    def ui_additional(self):
        """
        Handle all annoying popups during UI switching.
        """
        # Popups appear at page_os
        # Has a popup_confirm variant
        # so must take precedence
        if self.ui_page_os_popups():
            return True

        # Research popup, lost connection popup
        if self.handle_popup_confirm("UI_ADDITIONAL"):
            return True
        if self.handle_urgent_commission():
            return True

        # Popups appear at page_main, page_reward
        if self.ui_page_main_popups():
            return True

        # Story
        if self.handle_story_skip():
            return True

        # Game tips
        # Event commission in Vacation Lane.
        if self.appear(GAME_TIPS, offset=(30, 30), interval=3):
            logger.info(f'UI additional: {GAME_TIPS} -> {GOTO_MAIN}')
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30)):
                return True

        # Dorm popup
        if self.appear(DORM_INFO, offset=(30, 30), threshold=0.75, interval=3):
            self.device.click(DORM_INFO)
            return True
        if self.appear_then_click(DORM_FEED_CANCEL, offset=(30, 30), interval=3):
            return True
        if self.appear_then_click(DORM_TROPHY_CONFIRM, offset=(30, 30), interval=3):
            return True

        # Meowfficer popup
        if self.appear_then_click(MEOWFFICER_INFO, offset=(30, 30), interval=3):
            self.interval_reset(GET_SHIP)
            return True
        if self.appear(MEOWFFICER_BUY, offset=(30, 30), interval=3):
            logger.info(f'UI additional: {MEOWFFICER_BUY} -> {BACK_ARROW}')
            self.device.click(BACK_ARROW)
            return True

        # Campaign preparation
        if self.appear(MAP_PREPARATION, offset=(30, 30), interval=3) \
                or self.appear(FLEET_PREPARATION, offset=(20, 50), interval=3) \
                or self.appear(RAID_FLEET_PREPARATION, offset=(30, 30), interval=3) \
                or self.appear(COALITION_FLEET_PREPARATION, offset=(30, 30), interval=3):
            self.device.click(MAP_PREPARATION_CANCEL)
            return True
        if self.appear_then_click(AUTO_SEARCH_MENU_EXIT, offset=(200, 30), interval=3):
            return True
        if self.appear_then_click(AUTO_SEARCH_REWARD, offset=(50, 50), interval=3):
            return True
        if self.appear(WITHDRAW, offset=(30, 30), interval=3):
            # Poor wait here, to handle a game client bug after the game patch in 2022-04-07
            # To re-produce this game bug (100% success):
            # - Enter any stage, 12-4 for example
            # - Stop and restart game
            # - Run task `Main` in Alas
            # - Alas switches to page_campaign and retreat from an existing stage
            # - Game client freezes at page_campaign W12, clicking anywhere on the screen doesn't get responses
            # - Restart game client again fix the issue
            logger.info("WITHDRAW button found, wait until map loaded to prevent bugs in game client")
            self.device.sleep(3)
            if self.appear_then_click(WITHDRAW, offset=(30, 30)):
                self.interval_reset(WITHDRAW)
                return True
            else:
                logger.warning("WITHDRAW button does not exist anymore")
                self.interval_reset(WITHDRAW)

        # Login
        if self.appear_then_click(LOGIN_CHECK, offset=(30, 30), interval=3):
            return True
        if self.appear_then_click(MAINTENANCE_ANNOUNCE, offset=(30, 30), interval=3):
            return True

        # Mistaken click
        if self.appear(EXERCISE_PREPARATION, interval=3):
            logger.info(f'UI additional: {EXERCISE_PREPARATION} -> {GOTO_MAIN}')
            self.device.click(GOTO_MAIN)
            return True

        return False

    def ui_button_interval_reset(self, button):
        """
        Reset interval of some button to avoid mistaken clicks

        Args:
            button (Button):
        """
        if button == MEOWFFICER_GOTO_DORMMENU:
            self.interval_reset(GET_SHIP)
        for switch_button in page_main.links.values():
            if button == switch_button:
                self.interval_reset(GET_SHIP)
        if button == MAIN_GOTO_CAMPAIGN:
            self.interval_reset(GET_SHIP)
            # Shinano event has the same title as raid
            self.interval_reset(RAID_CHECK)
        if button == SHOP_GOTO_SUPPLY_PACK:
            self.interval_reset(EXCHANGE_CHECK)
        if button == DORMMENU_GOTO_DORM:
            self.interval_reset(GET_SHIP)
