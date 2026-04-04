"""
日志格式配置和主程序入口
设置loguru日志格式，调用function_calls模块中的函数
不包含具体业务代码，仅负责日志格式配置和程序入口
"""

import sys
import os
from loguru import logger

# 导入业务函数模块
from function_calls import main as function_calls_main


def get_call_depth1(record):
    """获取当前调用深度（快速版）"""
    stack = ""
    frame = sys._getframe(4)  # 跳过 get_call_depth 和调用者
    while frame:
        filename = frame.f_code.co_filename
        # filename = os.path.basename(frame.f_code.co_filename)
        stack = frame.f_code.co_name + "@" + filename + "@" + str(frame.f_lineno) + "#" + stack
        frame = frame.f_back
    record["extra"]["depth"] = stack
    return True


# 配置日志格式
fmt = (
    "<cyan>tid:{thread.id}</cyan>|<yellow>{extra[depth]:<2}</yellow>\n"
    "<cyan>tid:{thread.id}</cyan>|<level>{message}</level>"
)

# 移除默认处理器，添加自定义格式
logger.remove()
logger.add(
    sink=sys.stdout,
    level="DEBUG",
    format=fmt,
    colorize=True,
    filter=get_call_depth1
)


if __name__ == "__main__":
    # 设置随机种子(可选,用于复现结果)
    # import random
    # random.seed(42)

    # 调用业务函数模块的main函数
    function_calls_main()
