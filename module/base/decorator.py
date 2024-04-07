import random
import re
from functools import wraps
from typing import Callable, Generic, TypeVar

T = TypeVar("T")

""""
Config 类：提供了一个基于配置条件动态选择不同函数执行路径的装饰器。例如，根据配置中的某个选项为真或假，可以决定调用类中的哪个方法。
cached_property 装饰器：用于将类方法的返回值缓存为实例属性，使得属性值只计算一次并在后续访问中直接返回，适用于计算成本高的属性。
function_drop 装饰器：模拟随机丢弃函数调用的装饰器，用于测试和模拟不稳定的环境，例如模拟网络请求失败。
run_once 装饰器：确保被装饰的函数不论被调用多少次，只执行一次，适用于需要单次执行的初始化操作。"""


class Config:
    """
    Decorator that calls different function with a same name according to config.

    func_list likes:
    func_list = {
        'func1': [
            {'options': {'ENABLE': True}, 'func': 1},
            {'options': {'ENABLE': False}, 'func': 1}
        ]
    }
    """
    func_list = {}

    @classmethod
    def when(cls, **kwargs):
        """
        Args:
            **kwargs: Any option in AzurLaneConfig.

        Examples:
            @Config.when(USE_ONE_CLICK_RETIREMENT=True)
            def retire_ships(self, amount=None, rarity=None):
                pass

            @Config.when(USE_ONE_CLICK_RETIREMENT=False)
            def retire_ships(self, amount=None, rarity=None):
                pass
        """
        options = kwargs

        def decorate(func):
            name = func.__name__
            data = {'options': options, 'func': func}
            if name not in cls.func_list:
                cls.func_list[name] = [data]
            else:
                override = False
                for record in cls.func_list[name]:
                    if record['options'] == data['options']:
                        record['func'] = data['func']
                        override = True
                if not override:
                    cls.func_list[name].append(data)

            @wraps(func)
            def wrapper(self, *args, **kwargs):
                """
                Args:
                    self: ModuleBase instance.
                    *args:
                    **kwargs:
                """
                for record in cls.func_list[name]:

                    flag = [value is None or self.config.__getattribute__(key) == value
                            for key, value in record['options'].items()]
                    if not all(flag):
                        continue

                    return record['func'](self, *args, **kwargs)

                return func(self, *args, **kwargs)

            return wrapper

        return decorate


class cached_property(Generic[T]):
    """
    cached-property from https://github.com/pydanny/cached-property
    Add typing support

    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """

    def __init__(self, func: Callable[..., T]):
        self.func = func

    def __get__(self, obj, cls) -> T:
        if obj is None:
            return self

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def del_cached_property(obj, name):
    """
    Delete a cached property safely.

    Args:
        obj:
        name (str):
    """
    try:
        del obj.__dict__[name]
    except KeyError:
        pass


def has_cached_property(obj, name):
    """
    Check if a property is cached.

    Args:
        obj:
        name (str):
    """
    return name in obj.__dict__


def function_drop(rate=0.5, default=None):
    """
    Drop function calls to simulate random emulator stuck, for testing purpose.

    Args:
        rate (float): 0 to 1. Drop rate.
        default: Default value to return if dropped.

    Examples:
        @function_drop(0.3)
        def click(self, button, record_check=True):
            pass

        30% possibility:
        INFO | Dropped: module.device.device.Device.click(REWARD_GOTO_MAIN, record_check=True)
        70% possibility:
        INFO | Click (1091,  628) @ REWARD_GOTO_MAIN
    """

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if random.uniform(0, 1) > rate:
                return func(*args, **kwargs)
            else:
                cls = ''
                arguments = [str(arg) for arg in args]
                if len(arguments):
                    matched = re.search('<(.*?) object at', arguments[0])
                    if matched:
                        cls = matched.group(1) + '.'
                        arguments.pop(0)
                arguments += [f'{k}={v}' for k, v in kwargs.items()]
                arguments = ', '.join(arguments)
                return default

        return wrapper

    return decorate


def run_once(f):
    """
    Run a function only once, no matter how many times it has been called.

    Examples:
        @run_once
        def my_function(foo, bar):
            return foo + bar

        while 1:
            my_function()

    Examples:
        def my_function(foo, bar):
            return foo + bar

        action = run_once(my_function)
        while 1:
            action()
    """

    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper
