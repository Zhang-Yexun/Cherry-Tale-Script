# 文件名：
# 功能：
# 作者：张业勋
# 日期：
# 思路：
import unittest
from unittest.mock import MagicMock, patch
from module.handler import info_handler  # 假设函数在YourClass类中定义


class TestPopupHandler(unittest.TestCase):
    def setUp(self):
        self.your_class_instance = info_handler.InfoHandler()
        self.your_class_instance._popup_offset = (0, 0)  # 设置测试期间使用的默认值
        self.your_class_instance.adb = MagicMock()

        # 模拟POPUP_CANCEL和POPUP_CONFIRM对象
        global POPUP_CANCEL, POPUP_CONFIRM
        POPUP_CANCEL = MagicMock()
        POPUP_CONFIRM = MagicMock()

    @patch('module.handler.POPUP_CANCEL')
    @patch('module.handler.POPUP_CONFIRM')
    def test_handle_popup_confirm(self, mock_confirm, mock_cancel):
        # 设置模拟对象的行为
        self.your_class_instance.appear = MagicMock(side_effect=[True, True])
        self.your_class_instance.adb.click_adb = MagicMock()

        # 调用测试方法
        result = self.your_class_instance.handle_popup_confirm(name='test_name')

        # 断言预期结果
        self.assertTrue(result)
        click_adb.assert_called_with(POPUP_CONFIRM)
        self.assertEqual(POPUP_CONFIRM.name, 'original_name')  # 假设POPUP_CONFIRM的原始名字是'original_name'

    # 其他测试用例...


if __name__ == '__main__':
    unittest.main()
