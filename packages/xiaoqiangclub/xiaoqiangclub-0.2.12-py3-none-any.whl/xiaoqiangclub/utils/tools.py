# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/12/25 10:33
# 文件名称： tools.py
# 项目描述： 工具类
# 开发工具： PyCharm
import atexit
from typing import Callable, List, Any


class ExitHandler:
    def __init__(self):
        """
        负责管理退出时执行的回调任务。
        """
        # 存储所有注册的回调函数及其参数
        self.tasks = []

    def register(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        """
        注册一个在程序退出时执行的回调函数。

        :param func: 要注册的函数
        :param args: 函数的位置参数
        :param kwargs: 函数的关键字参数
        """
        self.tasks.append((func, args, kwargs))  # 将任务和参数保存在列表中
        atexit.register(func, *args, **kwargs)  # 注册到 atexit

    def list_registered_tasks(self) -> List[str]:
        """
        列出所有已注册的退出任务，便于调试和查看。

        :return: 所有已注册回调函数的名称和它们的参数
        """
        return [f"{task[0].__name__}, args: {task[1]}, kwargs: {task[2]}" for task in self.tasks]

    def execute_tasks(self):
        """
        手动触发所有注册的退出任务。这通常是用于调试或希望程序提前结束时查看结果。
        """
        for func, args, kwargs in self.tasks:
            func(*args, **kwargs)
