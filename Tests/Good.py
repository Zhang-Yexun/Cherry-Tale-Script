# 文件名：
# 功能：
# 作者：张业勋
# 日期：
# 思路：
def run_simple_screenshot_benchmark(self):
    """
    Perform a screenshot method benchmark, test 3 times on each method.
    The fastest one will be set into config.
    """
    logger.info('run_simple_screenshot_benchmark')
    # Check resolution first
    self.resolution_check_uiautomator2()
    # Perform benchmark
    from module.daemon.benchmark import Benchmark
    bench = Benchmark(config=self.config, device=self)
    method = bench.run_simple_screenshot_benchmark()
    # Set
    self.config.Emulator_ScreenshotMethod = method