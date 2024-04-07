from scipy import signal

from module.base.base import ModuleBase
from module.base.button import Button
from module.base.timer import Timer
from module.base.utils import *
from module.handler.assets import *

'''
这段代码定义了InfoHandler类，继承自ModuleBase。InfoHandler类专门用于处理游戏中的各种信息栏
、弹窗、故事对话等界面元素。以下是一些主要特点和方法的解释：

图像预处理
info_letter_preprocess 函数对输入图像进行预处理，通过调整图像的亮度和对比度，使图像中的文字更加突出，以便于后续的图像识别或处理。
弹窗处理
handle_popup_confirm、handle_popup_cancel 和 handle_popup_single 方法分别处理确认、取消和单个按钮的弹窗。
popup_interval_clear 方法用于清除弹窗检测的间隔，以便快速重新检测。
特殊场景处理
handle_urgent_commission 方法处理紧急委托弹窗。
handle_combat_low_emotion 方法处理战斗中低士气的弹窗。
handle_use_data_key 方法处理使用数据钥匙的确认弹窗。
handle_vote_popup 和 handle_get_skin 方法处理投票和获取皮肤的弹窗。
公会相关
handle_guild_popup_confirm 和 handle_guild_popup_cancel 方法处理公会相关的确认和取消弹窗。
任务相关
handle_mission_popup_go 和 handle_mission_popup_ack 方法处理任务相关的前往和确认弹窗。
故事跳过
story_skip 和 handle_story_skip 方法用于处理和跳过游戏内的故事对话。包括处理多个故事选项和关闭故事窗口。
ensure_no_story 方法确保没有故事对话干扰，直到所有故事对话都被处理。
游戏提示
handle_game_tips 方法处理游戏中的提示信息。
这个类的主要目的是在自动化游戏过程中，自动处理各种可能出现的信息栏、弹窗和故事对话等元素，以确保自动化流程的顺畅进行。
通过在各个操作前后调用这些方法，可以最大程度地减少需要人工干预的情况，提高自动化脚本的效率和稳定性。
'''


def info_letter_preprocess(image):
    """
    Args:
        image (np.ndarray):

    Returns:
        np.ndarray
    """
    image = image.astype(float)
    image = (image - 64) / 0.75
    image[image > 255] = 255
    image[image < 0] = 0
    image = image.astype('uint8')
    return image


class InfoHandler(ModuleBase):
    """
    Class to handle all kinds of message.
    """

    """
    Popup info
    """
    _popup_offset = (3, 30)

    def handle_popup_confirm(self, name='', offset=None, interval=2):
        """

        :param name:
        :param offset:
        :param interval:
        :return:

        当确认弹窗出现时，此函数会处理它，并通过点击确认按钮来关闭弹窗。
        """
        if offset is None:
            offset = self._popup_offset
        if self.appear(POPUP_CANCEL, offset=offset) \
                and self.appear(POPUP_CONFIRM, offset=offset, interval=interval):
            POPUP_CONFIRM.name = POPUP_CONFIRM.name + '_' + name
            click_adb(POPUP_CONFIRM)
            POPUP_CONFIRM.name = POPUP_CONFIRM.name[:-len(name) - 1]
            return True
        return False

    def handle_popup_cancel(self, name='', offset=None, interval=2):
        if offset is None:
            offset = self._popup_offset
        if self.appear(POPUP_CONFIRM, offset=offset) \
                and self.appear(POPUP_CANCEL, offset=offset, interval=interval):
            POPUP_CANCEL.name = POPUP_CANCEL.name + '_' + name
            click_adb(POPUP_CANCEL)
            POPUP_CANCEL.name = POPUP_CANCEL.name[:-len(name) - 1]
            return True
        return False

    def handle_popup_single(self, name='', offset=None, interval=2):
        if offset is None:
            offset = self._popup_offset
        if self.appear(GET_MISSION, offset=offset, interval=interval):
            prev_name = GET_MISSION.name
            GET_MISSION.name = POPUP_CONFIRM.name + '_' + name
            click_adb(GET_MISSION)
            GET_MISSION.name = prev_name
            return True

        return False

    def popup_interval_clear(self):
        self.interval_clear([POPUP_CANCEL, POPUP_CONFIRM])

    _hot_fix_check_wait = Timer(6)

    def handle_use_data_key(self):
        if not self.config.USE_DATA_KEY:
            return False

        if not self.appear(POPUP_CONFIRM, offset=self._popup_offset) \
                and not self.appear(POPUP_CANCEL, offset=self._popup_offset, interval=2):
            return False

        if self.appear(USE_DATA_KEY, offset=(20, 20)):
            skip_first_screenshot = True
            while 1:
                if skip_first_screenshot:
                    skip_first_screenshot = False
                else:
                    self.adb.adb_screenshot()

                enabled = self.image_color_count(
                    USE_DATA_KEY_NOTIFIED, color=(140, 207, 66), threshold=180, count=10)
                if enabled:
                    break

                if self.appear(USE_DATA_KEY, offset=(20, 20), interval=5):
                    click_adb(USE_DATA_KEY_NOTIFIED)
                    continue

            self.config.USE_DATA_KEY = False  # Reset on success as task can be stopped before can be recovered
            return self.handle_popup_confirm('USE_DATA_KEY')

        return False

    def handle_vote_popup(self):
        """
        Dismiss vote pop-ups.

        Returns:
            bool:
        """
        # Vote popups are removed in 2023
        # return self.appear_then_click(VOTE_CANCEL, offset=(20, 20), interval=2)
        return False

    def handle_get_skin(self):
        """
        Returns:
            bool:
        """
        return self.appear_then_click(GET_SKIN, offset=(20, 20), interval=2)

    """
    Guild popup info
    """

    def handle_guild_popup_confirm(self):
        if self.appear(GUILD_POPUP_CANCEL, offset=self._popup_offset) \
                and self.appear(GUILD_POPUP_CONFIRM, offset=self._popup_offset, interval=2):
            self.device.click(GUILD_POPUP_CONFIRM)
            return True

        return False

    def handle_guild_popup_cancel(self):
        if self.appear(GUILD_POPUP_CONFIRM, offset=self._popup_offset) \
                and self.appear(GUILD_POPUP_CANCEL, offset=self._popup_offset, interval=2):
            self.device.click(GUILD_POPUP_CANCEL)
            return True

        return False

    """
    Mission popup info
    """

    def handle_mission_popup_go(self):
        if self.appear(MISSION_POPUP_ACK, offset=self._popup_offset) \
                and self.appear(MISSION_POPUP_GO, offset=self._popup_offset, interval=2):
            self.device.click(MISSION_POPUP_GO)
            return True

        return False

    def handle_mission_popup_ack(self):
        if self.appear(MISSION_POPUP_GO, offset=self._popup_offset) \
                and self.appear(MISSION_POPUP_ACK, offset=self._popup_offset, interval=2):
            self.device.click(MISSION_POPUP_ACK)
            return True

        return False

    """
    Story
    """
    story_popup_timeout = Timer(10, count=20)
    map_has_clear_mode = False  # Will be override in fast_forward.py
    map_is_threat_safe = False

    _story_confirm = Timer(0.5, count=1)
    _story_option_timer = Timer(2)
    _story_option_record = 0
    _story_option_confirm = Timer(0.3, count=0)

    def _story_option_buttons(self):
        """
        Returns:
            list[Button]: List of story options, from upper to bottom. If no option found, return an empty list.
        """
        # Area to detect the options, should include at least 3 options.
        story_option_area = (730, 188, 1140, 480)
        # Background color of the left part of the option.
        story_option_color = (99, 121, 156)
        image = color_similarity_2d(self.image_crop(story_option_area), color=story_option_color) > 225
        x_count = np.where(np.sum(image, axis=0) > 40)[0]
        if not len(x_count):
            return []
        x_min, x_max = np.min(x_count), np.max(x_count)

        parameters = {
            # Option is 300`320px x 50~52px.
            'height': 280,
            'width': 45,
            'distance': 50,
            # Chooses the relative height at which the peak width is measured as a percentage of its prominence.
            # 1.0 calculates the width of the peak at its lowest contour line,
            # while 0.5 evaluates at half the prominence height.
            # Must be at least 0.
            'rel_height': 5,
        }
        y_count = np.sum(image, axis=1)
        peaks, properties = signal.find_peaks(y_count, **parameters)
        buttons = []
        total = len(peaks)
        if not total:
            return []
        for n, bases in enumerate(zip(properties['left_bases'], properties['right_bases'])):
            area = (x_min, bases[0], x_max, bases[1])
            area = area_pad(area_offset(area, offset=story_option_area[:2]), pad=5)
            buttons.append(
                Button(area=area, color=story_option_color, button=area, name=f'STORY_OPTION_{n + 1}_OF_{total}'))

        return buttons

    def _story_option_buttons_2(self):
        """
        Returns:
            list[Button]: List of story options, from upper to bottom. If no option found, return an empty list.
        """
        # Area to detect the options, should include at least 3 options.
        story_option_area = (330, 200, 980, 465)
        story_detect_area = (330, 200, 355, 465)
        story_option_color = (247, 247, 247)

        image = color_similarity_2d(self.image_crop(story_detect_area), color=story_option_color)
        line = cv2.reduce(image, 1, cv2.REDUCE_AVG).flatten()
        line[line < 200] = 0
        line[line >= 200] = 255

        parameters = {
            # Option is 300`320px x 50~52px.
            'height': 200,
            'width': 40,
            'distance': 40,
            # Chooses the relative height at which the peak width is measured as a percentage of its prominence.
            # 1.0 calculates the width of the peak at its lowest contour line,
            # while 0.5 evaluates at half the prominence height.
            # Must be at least 0.
            # rel_height is about 240 / 48
            'rel_height': 4,
        }
        peaks, properties = signal.find_peaks(line, **parameters)
        buttons = []
        total = len(peaks)
        if not total:
            return []
        for n, bases in enumerate(zip(properties['left_bases'], properties['right_bases'])):
            area = (
                story_option_area[0], story_option_area[1] + bases[0],
                story_option_area[2], story_option_area[1] + bases[1],
            )
            area = area_pad(area, pad=5)
            buttons.append(
                Button(area=area, color=story_option_color, button=area, name=f'STORY_OPTION_{n + 1}_OF_{total}'))

        return buttons

    def _is_story_black(self):
        color = get_color(self.device.image, area=STORY_LETTER_BLACK.area)
        # Story with dark background and a few rows of letters
        # STORY_LETTER_BLACK.color is (16, 20, 16)
        if color_similar(color, STORY_LETTER_BLACK.color, threshold=10):
            return True
        # Story with black and a few rows of letters
        if color_similar(color, (0, 0, 0), threshold=10):
            return True

        return False

    def story_skip(self, drop=None):
        """
        2023.09.14 Story options changed with big white options in the middle,
            Check STORY_SKIP_3 but click the original STORY_SKIP.
        """
        if self.story_popup_timeout.started() and not self.story_popup_timeout.reached():
            if self.handle_popup_confirm('STORY_SKIP'):
                self.story_popup_timeout = Timer(10)
                self.interval_reset(STORY_SKIP_3)
                self.interval_reset(STORY_LETTERS_ONLY)
                return True
        if self._is_story_black():
            if self.appear_then_click(STORY_LETTERS_ONLY, offset=(20, 20), interval=2):
                self.story_popup_timeout.reset()
                return True
        if self._story_option_timer.reached() and self.appear(STORY_SKIP_3, offset=(20, 20), interval=0):
            options = self._story_option_buttons_2()
            options_count = len(options)
            if not options_count:
                self._story_option_record = 0
                self._story_option_confirm.reset()
            elif options_count == self._story_option_record:
                if self._story_option_confirm.reached():
                    try:
                        select = options[self.config.STORY_OPTION]
                    except IndexError:
                        select = options[0]
                    self.device.click(select)
                    self._story_option_timer.reset()
                    self.story_popup_timeout.reset()
                    self.interval_reset(STORY_SKIP_3)
                    self.interval_reset(STORY_LETTERS_ONLY)
                    self._story_option_record = 0
                    self._story_option_confirm.reset()
                    return True
            else:
                self._story_option_record = options_count
                self._story_option_confirm.reset()
        if self.appear(STORY_SKIP_3, offset=(20, 20), interval=2):
            # Confirm it's story
            # When story play speed is Very Fast, Alas clicked story skip but story disappeared
            # This click will interrupt auto search
            self.interval_reset([STORY_SKIP_3])
            if self._story_confirm.reached():
                if drop:
                    drop.handle_add(self, before=2)
                if self.config.STORY_ALLOW_SKIP:
                    self.device.click(STORY_SKIP)
                else:
                    self.device.click(OS_CLICK_SAFE_AREA)
                self._story_confirm.reset()
                self.story_popup_timeout.reset()
                return True
            else:
                self.interval_clear(STORY_SKIP_3)
        else:
            self._story_confirm.reset()
        if self.appear_then_click(GAME_TIPS, offset=(20, 20), interval=2):
            self.story_popup_timeout.reset()
            return True
        if self.appear_then_click(STORY_CLOSE, offset=(10, 10), interval=2):
            self.story_popup_timeout.reset()
            return True

        return False

    def handle_story_skip(self, drop=None):
        # Rerun events in clear mode but still have stories.
        # No stories in clear mode
        # but B3/D3 still have stories til threat safe
        # No more stories at threat safe
        if self.map_is_threat_safe and self.config.Campaign_Event != 'event_20201012_cn':
            return False

        return self.story_skip(drop=drop)

    def ensure_no_story(self, skip_first_screenshot=True):
        story_timer = Timer(3, count=6).start()
        while 1:
            if skip_first_screenshot:
                skip_first_screenshot = False
            else:
                self.device.screenshot()

            if self.story_skip():
                story_timer.reset()

            if story_timer.reached():
                break

    def handle_map_after_combat_story(self):
        if not self.config.MAP_HAS_MAP_STORY:
            return False

        self.ensure_no_story()

    """
    Game tips
    """

    def handle_game_tips(self):
        """
        Returns:
            bool: If handled
        """
        if self.appear(GAME_TIPS, offset=(20, 20), interval=2):
            self.device.click(GAME_TIPS)
            return True
        if self.appear(GAME_TIPS3, offset=(20, 20), interval=2):
            self.device.click(GAME_TIPS)
            return True
        if self.appear(GAME_TIPS4, offset=(20, 20), interval=2):
            self.device.click(GAME_TIPS)
            return True

        return False
