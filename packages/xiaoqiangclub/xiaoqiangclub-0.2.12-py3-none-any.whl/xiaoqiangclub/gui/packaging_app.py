# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/12/28 11:14
# 文件名称： packaging_app.py
# 项目描述： 打包app
# 开发工具： PyCharm
import os
import platform
import subprocess
from xiaoqiangclub.utils.decorators import try_log_exceptions
from xiaoqiangclub.cmd.terminal_command_executor import run_command


@try_log_exceptions()
def open_directory(output_dir):
    """打开指定目录"""
    # 获取当前操作系统类型
    system_name = platform.system()

    if system_name == "Windows":
        # Windows 使用 os.startfile() 打开目录
        os.startfile(output_dir)
    elif system_name == "Linux":
        # Linux 使用 xdg-open 打开目录
        subprocess.run(["xdg-open", output_dir])
    elif system_name == "Darwin":  # macOS 系统
        # macOS 使用 open 命令打开目录
        subprocess.run(["open", output_dir])
    else:
        print(f"无法识别的操作系统: {system_name}, 无法自动打开目录。")


def packaging_app_with_pyinstaller(script_path: str,
                                   app_title: str,
                                   version: str = "v0.0.1",
                                   logo_path: str = None,
                                   upx_dir: str = None,
                                   create_single_file: bool = True,
                                   with_cmd_window: bool = False,
                                   modules: str | list = None,
                                   extra_args: str = "", run_cmd: bool = False) -> str:
    """
    通用打包函数，将 Python 脚本打包为可执行文件，并增加反编译保护措施。
    使用 pip install -i https://mirrors.aliyun.com/pypi/simple/ -U pyinstaller 安装 PyInstaller。
    upx下载: https://github.com/upx/upx/releases/

    :param script_path: 要打包的 Python 脚本路径
    :param app_title: 应用程序名称
    :param version: 应用程序版本
    :param logo_path: 应用程序图标路径，默认为 None（即不设置图标）
    :param upx_dir: UPX 的安装路径（如果使用 UPX 进行加壳）
    :param create_single_file: 是否生成单文件可执行文件，默认为 True
    :param with_cmd_window: 是否显示命令行窗口，默认为 False（即不显示）
    :param modules: 项目依赖文件路径或依赖列表，例如：requirements.txt，["PyQt5", "pandas"]
    :param extra_args: 传递给 PyInstaller 的额外参数，默认为空字符串，例如：--clean：清理构建目录和缓存。
    :param run_cmd: 是否直接执行打包命令，默认为 False（即不执行）
    """
    if run_cmd:
        input(
            "执行 pip install -i https://mirrors.aliyun.com/pypi/simple/ -U pyinstaller 安装 PyInstaller，安装完成后按任意键继续...")

    # 处理依赖文件或列表
    hidden_imports = []
    if isinstance(modules, str) and os.path.exists(modules):
        with open(modules, "r", encoding="utf-8") as f:
            hidden_imports = [line.strip() for line in f if line.strip()]
    elif isinstance(modules, list):
        hidden_imports = modules

    # 将依赖转换为 PyInstaller 的 --hidden-import 参数
    hidden_imports_args = " ".join([f"--hidden-import={lib}" for lib in hidden_imports])

    # 选择是否显示命令行窗口
    win_option = '' if with_cmd_window else '-w'

    # UPX 加壳选项
    upx_option = f'--upx-dir={upx_dir}' if upx_dir else ''

    # 设置图标选项
    logo_option = f'-i {logo_path}' if logo_path else ''

    # 单文件或多文件版本
    single_file_option = '--onefile' if create_single_file else ''

    # 构建 PyInstaller 命令
    command = (f'pyinstaller {win_option} --name "{app_title}{version}" {logo_option} {script_path} '
               f'{upx_option} {single_file_option} {hidden_imports_args} {extra_args}').strip()

    print(f"\n打包命令:\n{command}\n")

    if run_cmd:
        # 执行打包命令
        run_command(command)

        # 打开生成的文件所在目录
        open_dir = os.path.join(os.getcwd(), 'dist')
        # 打开生成的文件所在目录
        open_directory(open_dir)


def packaging_app_with_nuitka(script_path: str,
                              app_title: str,
                              version: str = "v0.0.1",
                              logo_path: str = None,
                              create_single_file: bool = True,
                              with_cmd_window: bool = False,
                              modules: str | list = None,
                              extra_args: str = "",
                              run_cmd: bool = False):
    """
    使用 Nuitka 打包函数，将 Python 脚本打包为可执行文件，并支持多种自定义选项。
    Nuitka 是一种高效的 Python 编译器，支持更高的性能和安全性。
    Nuitka 安装: pip install -i https://mirrors.aliyun.com/pypi/simple/ -U nuitka
    Windiws环境下如果本地没有安装 gcc 编译器，会需要你进行安装。
    linux环境下需要安装 patchelf：
    sudo apt update
    sudo apt install patchelf

    :param script_path: 要打包的 Python 脚本路径
    :param app_title: 应用程序名称
    :param version: 应用程序版本
    :param logo_path: 应用程序图标路径，默认为 None（即不设置图标）
    :param create_single_file: 是否生成单文件可执行文件，默认为 True
    :param with_cmd_window: 是否显示命令行窗口，默认为 False（即不显示）
    :param modules: 项目依赖文件路径或依赖列表，默认为 requirements.txt
    :param extra_args: 传递给 Nuitka 的额外参数，默认为空字符串
    :param run_cmd: 是否直接执行打包命令，默认为 False（即不执行）
    """
    if run_cmd:
        input(
            "终端执行 pip install -i https://mirrors.aliyun.com/pypi/simple/ -U nuitka 安装 Nuitka，安装完成后按任意键继续...")

    # 处理依赖文件或列表
    hidden_imports = []
    if isinstance(modules, str) and os.path.exists(modules):
        with open(modules, "r", encoding="utf-8") as f:
            hidden_imports = [line.strip() for line in f if line.strip()]
    elif isinstance(modules, list):
        hidden_imports = modules

    # 将依赖转换为 Nuitka 的 --include-module 参数
    hidden_imports_args = " ".join([f"--include-module={lib}" for lib in hidden_imports])

    # 选择是否显示命令行窗口
    console_option = "--windows-console-mode=force" if with_cmd_window else "--windows-console-mode=none"

    # 单文件选项
    single_file_option = "--onefile" if create_single_file else ""

    # 图标选项
    logo_option = f"--windows-icon-from-ico={logo_path}" if logo_path else ""

    # 输出目录设置
    output_dir = os.path.join(os.getcwd(), 'dist')
    os.makedirs(output_dir, exist_ok=True)
    output_option = f"--output-dir={output_dir}"

    # 构建 Nuitka 命令
    command = (
        f"python -m nuitka {console_option} {logo_option} {single_file_option} {hidden_imports_args} "
        f"{extra_args} --windows-product-name={app_title} --windows-product-version={version} {output_option} {script_path}"
    ).strip()

    print(f"\n打包命令:\n{command}\n")

    if run_cmd:
        # 执行打包命令
        run_command(command)

        # 打开生成的文件所在目录
        open_directory(output_dir)
