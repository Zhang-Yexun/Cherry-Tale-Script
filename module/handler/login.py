from typing import Union

#!!! Login功能目前还不需要过于关注，这个login功能继承自UI类，还是先把UI搞好再说



import numpy as np
from scipy.signal import find_peaks
from uiautomator2 import UiObject
from uiautomator2.exceptions import XPathElementNotFoundError
from uiautomator2.xpath import XPath, XPathSelector

import module.config.server as server
from module.base.timer import Timer
from module.base.utils import color_similarity_2d, crop, random_rectangle_point
from module.config.utils import get_server_next_update
from module.exception import (GameStuckError, GameTooManyClickError,
                              RequestHumanTakeover)
from module.handler.assets import *
from module.logger import logger
from module.map.assets import *
from module.ui.assets import *
from module.ui.page import MAIN_CHECK
from module.ui.ui import UI

'''
这段代码定义了LoginHandler类，它继承自UI类并用于处理游戏登录流程及相关弹窗。
LoginHandler类的主要职责是自动化处理登录游戏的过程，包括确认登录按钮、处理登录后可能出现的弹窗、以及处理用户协议等。
下面是一些关键部分的详细解释：
_handle_app_login 方法
功能：自动处理登录流程，从启动游戏到成功进入主页面。
流程：方法内部通过不断检测屏幕上的特定元素（如登录按钮、公告弹窗等）来判断当前状态，并采取相应的点击操作来推进登录流程。
handle_cn_user_agreement 方法
功能：专门用于处理中国服务器上出现的用户协议确认弹窗。
实现：通过滑动确认条款并点击同意按钮来完成用户协议的确认。
handle_app_login 方法
功能：封装了_handle_app_login，加入了失败重试机制。
流程：如果登录失败，会尝试重启游戏并重新登录，最多重试3次。如果超过尝试次数仍失败，则抛出RequestHumanTakeover异常，
请求人工介入。
其他辅助方法
handle_user_agreement、handle_user_login 等方法用于处理特定的界面元素或流程。
get_for_any_ele 方法用于查找给定的一组UI路径中的任意一个元素，并返回其界面坐标。
get_cn_xp_hierarchy 方法获取当前界面的XML层次结构，常用于XPath查询。
XPS 类
扩展：从XPathSelector类扩展而来，用于方便地处理XPath选择器。
目的：提供了一个构造函数，允许直接传入XPath表达式、父级对象和源代码来创建一个XPath选择器实例。
整体而言，LoginHandler类提供了一套完整的机制来自动处理游戏的登录过程，尤其是针对可能出现的多种弹窗和特殊情况（如用户协议），
确保自动化脚本能够顺利地从游戏启动进入到主界面。'''


class LoginHandler(UI):
    def _handle_app_login(self):
        """
        Pages:
            in: Any page
            out: page_main
        """
        logger.hr('App login')

        confirm_timer = Timer(1.5, count=4).start()
        orientation_timer = Timer(5)
        login_success = False

        while 1:
            # Watch device rotation
            if not login_success and orientation_timer.reached():
                # Screen may rotate after starting an app
                self.device.get_orientation()
                orientation_timer.reset()

            self.device.screenshot()

            # End
            if self.appear(MAIN_CHECK, offset=(30, 30)):
                if confirm_timer.reached():
                    logger.info('Login to main confirm')
                    break
            else:
                confirm_timer.reset()

            # Login
            if self.appear(LOGIN_CHECK, offset=(30, 30), interval=5) and LOGIN_CHECK.match_appear_on(self.device.image):
                self.device.click(LOGIN_CHECK)
                if not login_success:
                    logger.info('Login success')
                    login_success = True
            if self.appear_then_click(LOGIN_ANNOUNCE, offset=(30, 30), interval=5):
                continue
            if self.appear(EVENT_LIST_CHECK, offset=(30, 30), interval=5):
                self.device.click(BACK_ARROW)
                continue
            # Updates and maintenance
            if self.appear_then_click(MAINTENANCE_ANNOUNCE, offset=(30, 30), interval=5):
                continue
            if self.appear_then_click(LOGIN_GAME_UPDATE, offset=(30, 30), interval=5):
                continue
            if server.server == 'cn' and not login_success:
                if self.handle_cn_user_agreement():
                    continue
            # Player return
            if self.appear_then_click(LOGIN_RETURN_SIGN, offset=(30, 30), interval=5):
                continue
            if self.appear_then_click(LOGIN_RETURN_INFO, offset=(30, 30), interval=5):
                continue
            # Popups
            if self.handle_popup_confirm('LOGIN'):
                continue
            if self.handle_urgent_commission():
                continue
            # Popups appear at page_main
            if self.ui_page_main_popups(get_ship=login_success):
                return True
            # Always goto page_main
            if self.appear_then_click(GOTO_MAIN, offset=(30, 30), interval=5):
                continue

        return True

    _user_agreement_timer = Timer(1, count=2)

    def handle_cn_user_agreement(self):
        if not self._user_agreement_timer.reached():
            return False

        confirm = self.image_color_button(
            area=(640, 360, 1280, 720), color=(78, 189, 234),
            color_threshold=245, encourage=25, name='AGREEMENT_CONFIRM')
        if confirm is None:
            return False
        scroll = self.image_color_button(
            area=(640, 0, 1280, 720), color=(182, 189, 202),
            color_threshold=245, encourage=5, name='AGREEMENT_SCROLL'
        )
        if scroll is not None:
            # User agreement
            p1 = random_rectangle_point(scroll.button)
            p2 = random_rectangle_point(scroll.move((0, 350)).button)
            self.device.swipe(p1, p2, name='AGREEMENT_SCROLL')
            self.device.click(confirm)
            self._user_agreement_timer.reset()
            return True
        else:
            # User login
            self.device.click(confirm)
            self._user_agreement_timer.reset()
            return True

    def handle_app_login(self):
        """
        Returns:
            bool: If login success

        Raises:
            RequestHumanTakeover: If login failed more than 3
        """
        for _ in range(3):
            self.device.stuck_record_clear()
            self.device.click_record_clear()
            try:
                self._handle_app_login()
                return True
            except (GameTooManyClickError, GameStuckError) as e:
                logger.warning(e)
                self.device.app_stop()
                self.device.app_start()
                continue

        logger.critical('Login failed more than 3')
        logger.critical('Azur Lane server may be under maintenance, or you may lost network connection')
        raise RequestHumanTakeover

    def app_stop(self):
        logger.hr('App stop')
        self.device.app_stop()

    def app_start(self):
        logger.hr('App start')
        self.device.app_start()
        self.handle_app_login()
        # self.ensure_no_unfinished_campaign()

    def app_restart(self):
        logger.hr('App restart')
        self.device.app_stop()
        self.device.app_start()
        self.handle_app_login()
        # self.ensure_no_unfinished_campaign()
        self.config.task_delay(server_update=True)

    def ensure_no_unfinished_campaign(self, confirm_wait=3):
        """
        Pages:
            in: page_main
            out: page_main
        """

        def ensure_campaign_retreat():
            if self.appear_then_click(WITHDRAW, offset=(30, 30), interval=5):
                return True
            if self.handle_popup_confirm('WITHDRAW'):
                return True

        def in_campaign():
            return self.appear(CAMPAIGN_CHECK, offset=(30, 30)) \
                   or self.appear(CAMPAIGN_MENU_CHECK, offset=(30, 30)) \
                   or self.appear(EVENT_CHECK, offset=(30, 30)) \
                   or self.appear(SP_CHECK, offset=(30, 30))

        self.ui_click(MAIN_GOTO_CAMPAIGN, check_button=in_campaign, additional=ensure_campaign_retreat,
                      confirm_wait=confirm_wait, skip_first_screenshot=True)
        self.ui_goto_main()

    def handle_user_agreement(self, xp, hierarchy):
        """
        For CN only.
        CN client is bugged. User Agreement and Privacy Policy may popup again even you have agreed with it.
        This method scrolls to the bottom and click AGREE.

        Returns:
            bool: If handled.
        """

        if server.server == 'cn':
            area_wait_results = self.get_for_any_ele([
                XPS('//*[@text="sdk协议"]', xp, hierarchy),
                XPS('//*[@content-desc="sdk协议"]', xp, hierarchy)])
            if area_wait_results is False:
                return False
            agree_wait_results = self.get_for_any_ele([
                XPS('//*[@text="同意"]', xp, hierarchy),
                XPS('//*[@content-desc="同意"]', xp, hierarchy)])
            start_padding_results = self.get_for_any_ele([
                XPS('//*[@text="隐私政策"]', xp, hierarchy), XPS('//*[@content-desc="隐私政策"]', xp, hierarchy),
                XPS('//*[@text="用户协议"]', xp, hierarchy), XPS('//*[@content-desc="用户协议"]', xp, hierarchy)])
            start_margin_results = self.get_for_any_ele([
                XPS('//*[@text="请滑动阅读协议内容"]', xp, hierarchy),
                XPS('//*[@content-desc="请滑动阅读协议内容"]', xp, hierarchy)])

            test_image_original = self.device.image
            image_handle_crop = crop(test_image_original, (start_padding_results[2], 0, start_margin_results[2], 720))
            # Image.fromarray(image_handle_crop).show()
            sims = color_similarity_2d(image_handle_crop, color=(182, 189, 202))
            points = np.sum(sims >= 255)
            if points == 0:
                return False
            sims_height = np.mean(sims, axis=1)
            # pyplot.plot(sims_height, color='r')
            # pyplot.show()
            peaks, __ = find_peaks(sims_height, height=225)
            if len(peaks) == 2:
                peaks = (peaks[0] + peaks[1]) / 2
            start_pos = [(start_padding_results[2] + start_margin_results[2]) / 2, float(peaks)]
            end_pos = [(start_padding_results[2] + start_margin_results[2]) / 2, area_wait_results[3]]
            logger.info("user agreement position find result: " + ', '.join('%.2f' % _ for _ in start_pos))
            logger.info("user agreement area expect:          " + 'x:963-973, y:259-279')

            self.device.drag(start_pos, end_pos, segments=2, shake=(0, 25), point_random=(0, 0, 0, 0),
                             shake_random=(0, -5, 0, 5))
            AGREE = Button(area=agree_wait_results, color=(), button=agree_wait_results, name='AGREE')
            self.device.click(AGREE)
            return True

    def handle_user_login(self, xp, hierarchy) -> bool:
        login_wait_results = self.get_for_any_ele([
            XPS('//*[@text="登录"]', xp, hierarchy),
            XPS('//*[@content-desc="登录"]', xp, hierarchy)])
        if login_wait_results is False:
            return False
        else:
            USER_LOGIN_BTN = Button(area=login_wait_results, color=(), button=login_wait_results, name='USER_LOGIN_BTN')
            self.device.click(USER_LOGIN_BTN)
            return True

    @staticmethod
    def get_for_any_ele(list_u2_path: list) -> Union[bool, tuple]:
        """
        Args:
            list_u2_path (list): [UiObject or XPathSelector]  In this case, len(list_u2_path) >= 1
        Returns:
            bool: False if wait failed
            tuple: (bounds): if wait success
        """
        for path in list_u2_path:
            try:
                if isinstance(path, UiObject):
                    if path.exists():
                        return path.bounds()
                    elif not path.exists():
                        continue
                elif isinstance(path, XPathSelector):
                    if path.exists:
                        return path.bounds
                    elif not path.exists:
                        continue
            except XPathElementNotFoundError:
                continue
        return False

    def get_cn_xp_hierarchy(self) -> tuple:
        d = self.device.u2
        xp = XPath(d)
        hierarchy = d.dump_hierarchy()
        return xp, hierarchy


class XPS(XPathSelector):
    def __init__(self, xpath, parent, source):
        super().__init__(parent, xpath, source)
