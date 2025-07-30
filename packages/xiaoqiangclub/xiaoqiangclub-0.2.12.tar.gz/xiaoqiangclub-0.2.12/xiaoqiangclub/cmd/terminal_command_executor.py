import io
import sys
import asyncio
import subprocess
import re
from typing import Optional
from xiaoqiangclub.config.log_config import log


def decode_output(output: bytes) -> str:
    """
    尝试使用utf-8和gbk解码输出字节

    :param output: 输出字节
    :return: 解码后的字符串
    """
    try:
        return output.decode('utf-8')
    except UnicodeDecodeError:
        return output.decode('gbk')


def detect_prompt_for_user_input(output: str) -> bool:
    """
    检测输出内容中是否包含需要用户输入确认的提示，例如 '[y/n]'。

    :param output: 命令输出的字符串
    :return: 如果存在用户输入确认的提示，返回True；否则返回False。
    """
    return bool(re.search(r'\[([yY]/[nN])\]', output))


async def run_command_async(cmd: str, stream_stdout: bool = True, auto_select: bool = False) -> Optional[str]:
    """
    异步运行给定的终端命令，并返回命令的输出作为Python字符串
    示例命令: await run_command_async('ls -l')

    :param cmd: 要执行的shell命令
    :param stream_stdout: 是否使用流式打印
    :param auto_select: 是否自动选择（如果出现手动选择提示），只对 Y/N 的提示有效
    :return: 命令的输出作为Python字符串，若发生错误则返回None
    """
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE
        )

        if stream_stdout:
            async for line in process.stdout:
                output = decode_output(line)
                print(output, end='')

                # 自动选择用户输入确认的提示
                if auto_select and detect_prompt_for_user_input(output):
                    # 自动选择 'y' 继续
                    process.stdin.write(b'y\n')
                    await process.stdin.drain()

                await asyncio.sleep(0)  # 刷新缓冲区
        else:
            stdout, _ = await process.communicate()
            return decode_output(stdout)
    except Exception as e:
        log.error(f"执行命令时发生错误: {e}")
        return None


def run_command(cmd: str, stream_stdout: bool = True, auto_select: bool = False) -> Optional[str]:
    """
    同步方式运行给定的终端命令，并返回命令的输出作为Python字符串
    示例命令: run_command('ls -l')

    :param cmd: 要执行的shell命令
    :param stream_stdout: 是否使用流式打印
    :param auto_select: 是否自动选择（如果出现手动选择提示），只对 Y/N 的提示有效
    :return: 命令的输出作为Python字符串，若发生错误则返回None
    """
    try:
        if stream_stdout:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       stdin=subprocess.PIPE)
            for line in iter(process.stdout.readline, b''):
                output = decode_output(line)
                sys.stdout.write(output)  # 使用解码输出
                sys.stdout.flush()  # 刷新缓冲区

                # 自动选择用户输入确认的提示
                if auto_select and detect_prompt_for_user_input(output):
                    # 自动选择 'y' 继续
                    process.stdin.write(b'y\n')
                    process.stdin.flush()  # 确保写入命令流

            process.wait()  # 等待命令执行完成
        else:
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return decode_output(result.stdout)
    except Exception as e:
        log.error(f"运行命令时发生错误: {e}")
        return None


# Windows系统下可设置控制台编码为utf-8
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
