# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/11/14
# 文件名称： temp_file.py
# 项目描述： 提供生成临时文件和目录的工具函数
# 开发工具： PyCharm
import os
import atexit
import tempfile
from typing import Optional
from xiaoqiangclub.config.log_config import log
from xiaoqiangclub.data.file import write_file_async, format_path


async def create_custom_temp_file(
        file_name: Optional[str] = None,
        content: str = "",
        directory: Optional[str] = None,
        auto_delete: bool = False,
        only_return_path: bool = True) -> str:
    """
    创建一个具有自定义文件名或随机文件名的临时文件，并返回文件路径。

    :param file_name: 可选，自定义的文件名，例如 "example.txt"。若为 None 则自动生成随机文件名。
    :param content: 写入临时文件的内容，默认为空字符串。
    :param directory: 临时文件的存放目录。目录会在临时目录下创建子目录。
    :param auto_delete: 是否在程序结束时自动删除临时文件。默认为 False。
    :param only_return_path: 是否只返回文件路径，而不创建文件。默认为 True。
    :return: 临时文件的完整路径。
    :rtype: str
    """
    # 系统临时目录
    base_temp_dir = tempfile.gettempdir()

    # 使用系统临时目录或其子目录
    if directory:
        # 将子目录路径组合到系统临时目录下
        temp_dir = os.path.join(base_temp_dir, directory)
        # 如果子目录不存在，则创建
        os.makedirs(temp_dir, exist_ok=True)
    else:
        # 使用系统默认临时目录
        temp_dir = base_temp_dir

    if file_name:
        # 如果指定了文件名，构造完整路径
        file_path = os.path.join(temp_dir, file_name)
    else:
        # 如果未指定文件名，自动生成随机文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir)
        file_path = temp_file.name
        temp_file.close()  # 确保文件被关闭，方便后续操作

    # 防止自定义文件名重复
    if file_name and os.path.exists(file_path):
        raise FileExistsError(f"文件已存在：{file_path}")

    # 如果只需返回路径，不创建文件
    if only_return_path:
        log.info(f"文件路径已生成，请手动检查文件是否已存在，防止重复写入：{file_path}")
        return file_path

    # 创建文件并写入内容
    await write_file_async(file_path, content)

    # 如果设置了自动删除，注册删除逻辑
    if auto_delete:
        atexit.register(lambda: os.remove(file_path) if os.path.exists(file_path) else None)
        log.info(f"已设置程序退出时自动删除文件：{file_path}")

    return file_path


def create_temp_file(suffix: Optional[str] = None, prefix: Optional[str] = None,
                     directory: Optional[str] = None, delete: bool = False,
                     **kwargs) -> str:
    """
    创建临时文件

    :param suffix: 临时文件的后缀名，默认为空
    :param prefix: 临时文件的前缀
    :param directory: 临时文件存放的目录，默认为 None，表示使用系统默认的临时目录
    :param delete: 是否在文件关闭后自动删除文件，默认为 False
    :param kwargs: 其他额外的参数，可以传递给 tempfile.NamedTemporaryFile
    :return: 创建的临时文件路径
    """
    try:
        # 获取系统默认的临时目录
        temp_dir = tempfile.gettempdir()

        if directory is not None:
            # 如果用户提供了 directory 参数，将它视为相对于系统临时目录的子目录
            directory = os.path.join(temp_dir, directory.lstrip('/').lstrip('\\'))
            # 如果指定目录不存在，则创建它
            if not os.path.exists(directory):
                os.makedirs(directory)
            log.debug(f"指定的目录 {directory} 被创建或已经存在。")
        else:
            directory = temp_dir  # 如果没有指定，使用系统默认临时目录

        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, dir=directory, delete=delete, **kwargs)
        log.info(f"成功创建临时文件: {temp_file.name}")

        return temp_file.name
    except Exception as e:
        log.error(f"创建临时文件失败: {e}")
        raise


def create_temp_dir(prefix: Optional[str] = None, directory: Optional[str] = None, **kwargs) -> str:
    """
    创建临时目录，根据用户提供的 directory 参数创建相应子目录。

    :param prefix: 临时目录的前缀
    :param directory: 临时目录存放的目录，默认为 None，表示使用系统默认的临时目录
    :param kwargs: 其他额外的参数，可以传递给 tempfile.mkdtemp
    :return: 创建的临时目录路径，目录需要手动删除。
    """
    try:
        # 获取系统默认的临时目录
        temp_dir = tempfile.gettempdir()

        if directory is not None:
            # 如果用户提供了 directory 参数，将它视为相对于系统临时目录的子目录
            directory = os.path.join(temp_dir, directory.lstrip('/').lstrip('\\'))
            # 如果指定目录不存在，则创建它
            if not os.path.exists(directory):
                os.makedirs(directory)
            log.info(f"指定的目录 {directory} 被创建或已经存在。")
        else:
            directory = temp_dir  # 如果没有指定，使用系统默认临时目录

        # 创建临时目录
        temp_dir_path = tempfile.mkdtemp(prefix=prefix, dir=directory, **kwargs)
        log.info(f"成功创建临时目录: {temp_dir_path}")

        return format_path(temp_dir_path)
    except Exception as e:
        log.error(f"创建临时目录失败: {e}")
        raise


def get_current_system_tempdir() -> str:
    """获取当前系统的临时目录"""
    return tempfile.gettempdir()


if __name__ == '__main__':
    import asyncio


    async def main():
        print(await create_custom_temp_file('test.json', directory='xiaoqiangclub', only_return_path=True))


    asyncio.run(main())
