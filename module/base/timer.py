import time
from datetime import datetime, timedelta
from functools import wraps
'''
这段代码定义了一系列与时间相关的实用工具函数和一个Timer类，旨在帮助进行时间测量、时间比较以及时间管理。下面是各个部分的详细解释：

timer 装饰器
一个装饰器，用于测量任何函数运行所需的时间。它在被装饰的函数运行前后记录时间，然后打印出函数名称及其运行耗时。可以用于性能分析。
future_time 函数
输入一个时间字符串（如"14:59"），返回一个datetime对象，表示今天或未来某一天的这个时间点。如果给定的时间已经过去，则返回明天的这个时间点。
past_time 函数
与future_time相反，返回一个datetime对象，表示过去某一天的给定时间点。如果给定的时间点还未到达，则返回昨天的这个时间点。
future_time_range 函数
输入一个时间范围字符串（如"23:30-06:30"），返回一个包含两个datetime对象的元组，表示未来的起始和结束时间点。如果起始时间晚于结束时间，则起始时间会被设定为前一天，以保证时间范围的连续性。
time_range_active 函数
输入一个由两个datetime对象组成的元组，表示一个时间范围。函数返回一个布尔值，表示当前时间是否处于这个时间范围内。
Timer 类
一个灵活的计时器类，可用于各种场景，如限制操作的频率、测量特定操作的耗时等。
__init__ 方法初始化计时器，接受一个时间限制limit和一个可选的确认计数count。
start 方法启动计时器。
started 方法检查计时器是否已启动。
current 方法返回自计时器启动以来的时间。
reached 方法检查计时器是否达到了其时间限制，且确认计数超过了设定值。
reset 方法重置计时器。
clear 方法清除计时器的当前状态，恢复计数。
reached_and_reset 方法检查计时器是否达到了时间限制，并在达到时自动重置。
wait 方法让调用者等待直到计时器达到设定的时间限制。
__str__ 和 __repr__ 方法提供了类的字符串表示，用于打印和调试。
这些工具的组合使用可以帮助在应用程序中精确地管理和测量时间，进行性能调试，以及控制事件的执行频率。'''

def timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()

        result = function(*args, **kwargs)
        t1 = time.time()
        print('%s: %s s' % (function.__name__, str(round(t1 - t0, 10))))
        return result

    return function_timer


def future_time(string):
    """
    Args:
        string (str): Such as 14:59.

    Returns:
        datetime.datetime: Time with given hour, minute in the future.
    """
    hour, minute = [int(x) for x in string.split(':')]
    future = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    future = future + timedelta(days=1) if future < datetime.now() else future
    return future


def past_time(string):
    """
    Args:
        string (str): Such as 14:59.

    Returns:
        datetime.datetime: Time with given hour, minute in the past.
    """
    hour, minute = [int(x) for x in string.split(':')]
    past = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
    past = past - timedelta(days=1) if past > datetime.now() else past
    return past


def future_time_range(string):
    """
    Args:
        string (str): Such as 23:30-06:30.

    Returns:
        tuple(datetime.datetime): (time start, time end).
    """
    start, end = [future_time(s) for s in string.split('-')]
    if start > end:
        start = start - timedelta(days=1)
    return start, end


def time_range_active(time_range):
    """
    Args:
        time_range(tuple(datetime.datetime)): (time start, time end).

    Returns:
        bool:
    """
    return time_range[0] < datetime.now() < time_range[1]


class Timer:
    def __init__(self, limit, count=0):
        """
        Args:
            limit (int, float): Timer limit
            count (int): Timer reach confirm count. Default to 0.
                When using a structure like this, must set a count.
                Otherwise it goes wrong, if screenshot time cost greater than limit.

                if self.appear(MAIN_CHECK):
                    if confirm_timer.reached():
                        pass
                else:
                    confirm_timer.reset()

                Also, It's a good idea to set `count`, to make alas run more stable on slow computers.
                Expected speed is 0.35 second / screenshot.
        """
        self.limit = limit
        self.count = count
        self._current = 0
        self._reach_count = count

    def start(self):
        if not self.started():
            self._current = time.time()
            self._reach_count = 0

        return self

    def started(self):
        return bool(self._current)

    def current(self):
        """
        Returns:
            float
        """
        if self.started():
            return time.time() - self._current
        else:
            return 0.

    def reached(self):
        """
        Returns:
            bool
        """
        self._reach_count += 1
        return time.time() - self._current > self.limit and self._reach_count > self.count

    def reset(self):
        self._current = time.time()
        self._reach_count = 0
        return self

    def clear(self):
        self._current = 0
        self._reach_count = self.count
        return self

    def reached_and_reset(self):
        """
        Returns:
            bool:
        """
        if self.reached():
            self.reset()
            return True
        else:
            return False

    def wait(self):
        """
        Wait until timer reached.
        """
        diff = self._current + self.limit - time.time()
        if diff > 0:
            time.sleep(diff)

    def __str__(self):
        return f'Timer(limit={round(self.current(), 3)}/{self.limit}, count={self._reach_count}/{self.count})'

    __repr__ = __str__
