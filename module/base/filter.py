import re

"""
Filter类主要用于基于正则表达式和对象属性进行复杂的数据过滤。它包含以下关键属性和方法：
属性:
regex：用于匹配的正则表达式。
attr：要在对象中匹配的属性名称。
preset：预设的字符串集合，用于特定的过滤条件。
filter_raw和filter：分别存储原始的过滤字符串和解析后的过滤条件。
方法:
load(string)：加载并解析过滤条件字符串。
is_preset(filter)：检查给定的过滤条件是否为预设条件之一。
apply(objs, func=None)：对对象列表应用过滤条件，可以选择性地提供一个函数对对象进行额外的过滤。
apply_filter_to_obj(obj, filter)：判断单个对象是否满足给定的过滤条件。
parse_filter(string)：从过滤条件字符串中解析出具体的过滤条件。
"""

class Filter:
    def __init__(self, regex, attr, preset=()):
        """
        Args:
            regex: Regular expression.
            attr: Attribute name.
            preset: Build-in string preset.
        """
        if isinstance(regex, str):
            regex = re.compile(regex)
        self.regex = regex
        self.attr = attr
        self.preset = tuple(list(p.lower() for p in preset))
        self.filter_raw = []
        self.filter = []

    def load(self, string):
        """
        Load a filter string, filters are connected with ">"

        There are also tons of unicode characters similar to ">"
        > \u003E correct
        ＞ \uFF1E
        ﹥ \uFE65
        › \u203a
        ˃ \u02c3
        ᐳ \u1433
        ❯ \u276F
        """
        string = str(string)
        string = re.sub(r'[ \t\r\n]', '', string)
        string = re.sub(r'[＞﹥›˃ᐳ❯]', '>', string)
        self.filter_raw = string.split('>')
        self.filter = [self.parse_filter(f) for f in self.filter_raw]

    def is_preset(self, filter):
        return len(filter) and filter.lower() in self.preset

    def apply(self, objs, func=None):
        """
        Args:
            objs (list): List of objects and strings
            func (callable): A function to filter object.
                Function should receive an object as arguments, and return a bool.
                True means add it to output.

        Returns:
            list: A list of objects and preset strings, such as [object, object, object, 'reset']
        """
        out = []
        for raw, filter in zip(self.filter_raw, self.filter):
            if self.is_preset(raw):
                raw = raw.lower()
                if raw not in out:
                    out.append(raw)
            else:
                for index, obj in enumerate(objs):
                    if self.apply_filter_to_obj(obj=obj, filter=filter) and obj not in out:
                        out.append(obj)

        if func is not None:
            objs, out = out, []
            for obj in objs:
                if isinstance(obj, str):
                    out.append(obj)
                elif func(obj):
                    out.append(obj)
                else:
                    # Drop this object
                    pass

        return out

    def apply_filter_to_obj(self, obj, filter):
        """
        Args:
            obj (object):
            filter (list[str]):

        Returns:
            bool: If an object satisfy a filter.
        """

        for attr, value in zip(self.attr, filter):
            if not value:
                continue
            if str(obj.__getattribute__(attr)).lower() != str(value):
                return False

        return True

    def parse_filter(self, string):
        """
        Args:
            string (str):

        Returns:
            list[strNone]:
        """
        string = string.replace(' ', '').lower()
        result = re.search(self.regex, string)

        if self.is_preset(string):
            return [string]

        if result and len(string) and result.span()[1]:
            return [result.group(index + 1) for index, attr in enumerate(self.attr)]

