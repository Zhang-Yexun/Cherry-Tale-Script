import re
from module.base.decorator import cached_property, del_cached_property

'''
这段代码实现了一个名为Resource的类，它是一个资源管理器，用于在自动化任务中管理UI元素（如按钮和模板）的资源。代码中还包含了PreservedAssets和release_resources函数，这些用于处理资源保留和释放的逻辑。

Resource 类
instances: 类属性，用于记录所有的按钮和模板实例。
cached: 实例属性，用于记录实例的缓存属性。
resource_add: 将资源（如按钮或模板）添加到instances字典中。
resource_release: 释放对象的资源，特别是从缓存中删除相关属性。
is_loaded: 检查资源（如图片）是否已经加载。
resource_show: 打印已加载的资源信息。
parse_property: 解析按钮或模板对象输入的属性，如area、color和button。
PreservedAssets 类
使用@cached_property装饰器缓存ui属性，它表示需要保留的UI资源集合。

release_resources 函数
接受一个next_task参数，根据即将执行的任务，释放不再需要的资源，以减少内存占用。释放资源包括：

OCR模型
UI相关的缓存图像
地图检测中使用的缓存图像
与Button类的关系
Button类可能继承自Resource类，使用Resource类中定义的资源管理方法。Button实例可以使用resource_add添加到资源管理器中，使用resource_release释放资源。
Button类的实例在需要时可以从Resource的instances中检索，以避免重复加载同一个资源。
当不再需要Button时（例如，当自动化任务切换到不同的UI界面时），可以调用release_resources函数来释放Button所占用的资源。
代码中展示了资源管理在UI自动化和游戏脚本开发中的重要性，它可以帮助优化资源使用，提高效率和性能。'''


def get_assets_from_file(file, regex):
    assets = set()
    with open(file, 'r', encoding='utf-8') as f:
        for row in f.readlines():
            result = regex.search(row)
            if result:
                assets.add(result.group(1))
    return assets


class PreservedAssets:
    @cached_property
    def ui(self):
        assets = set()
        assets |= get_assets_from_file(
            file='./module/ui/assets.py',
            regex=re.compile(r'^([A-Za-z][A-Za-z0-9_]+) = ')
        )
        assets |= get_assets_from_file(
            file='./module/ui/ui.py',
            regex=re.compile(r'\(([A-Z][A-Z0-9_]+),')
        )
        assets |= get_assets_from_file(
            file='./module/handler/info_handler.py',
            regex=re.compile(r'\(([A-Z][A-Z0-9_]+),')
        )
        # MAIN_CHECK == MAIN_GOTO_CAMPAIGN
        assets.add('MAIN_GOTO_CAMPAIGN')
        return assets


_preserved_assets = PreservedAssets()


class Resource:
    # Class property, record all button and templates
    instances = {}
    # Instance property, record cached properties of instance
    cached = []

    def resource_add(self, key):
        Resource.instances[key] = self

    def resource_release(self):
        for cache in self.cached:
            del_cached_property(self, cache)

    @classmethod #类方法，用于操作类属性，类属性不同于实例属性，实例属性是类的实例，类属性是所有实例共用的。
    def is_loaded(cls, obj):
        if hasattr(obj, '_image') and obj._image is None:
            return False
        elif hasattr(obj, 'image') and obj.image is None:
            return False
        return True


#   !!!  遗留问题，方便下次查找


# def release_resources(next_task=''):
#     # Release all OCR models
#     # Usually to have 2 models loaded and each model takes about 20MB
#     # This will release 20-40MB
#         # Release only when using per-instance OCR
#
#         #from module.ocr.ocr import OCR_MODEL
#         if 'Opsi' in next_task or 'commission' in next_task:
#             # OCR models will be used soon, don't release
#             models = []
#         elif next_task:
#             # Release OCR models except 'azur_lane'
#             models = ['cnocr', 'jp', 'tw']
#         else:
#             models = ['azur_lane', 'cnocr', 'jp', 'tw']
#         for model in models:
#             del_cached_property(OCR_MODEL, model)
#
#     # Release assets cache
#     # module.ui has about 80 assets and takes about 3MB
#     # Alas has about 800 assets, but they are not all loaded.
#     # Template images take more, about 6MB each
#     for key, obj in Resource.instances.items():
#         # Preserve assets for ui switching
#         if next_task and str(obj) in _preserved_assets.ui:
#             continue
#         # if Resource.is_loaded(obj):
#         #     logger.info(f'Release {obj}')
#         obj.resource_release()

if __name__ == "__main__":
    # 定义正则表达式，匹配所有以_BUTTON结尾的资源名称
    regex = re.compile(r'^([A-Za-z0-9_]+_Button)')
    # 调用get_assets_from_file函数，从ui.py文件中提取资源
    assets = get_assets_from_file(file='E:\\Project\\xju\\Cherry-Tale-Script\\module\\Initial_main_line\\assets.py',
                                  regex=regex)
    # 打印提取的资源名称
    print(assets)
