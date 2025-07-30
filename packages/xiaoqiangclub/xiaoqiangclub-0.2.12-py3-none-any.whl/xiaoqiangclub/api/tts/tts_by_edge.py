# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/3/24 16:16
# 文件名称： tts_by_edge.py
# 项目描述： 基于Edge-tts的语音合成：https://github.com/rany2/edge-tts
# 开发工具： PyCharm
import os

# 隐藏 pygame 的支持提示
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "XiaoqiangClub"
import asyncio
import edge_tts
import pygame
from io import BytesIO
import contextlib
import io
from typing import Optional
from xiaoqiangclub.config.log_config import log


def print_edge_tts_voices():
    """
    获取 Edge-tts 支持的语音列表。
    :return:
    """

    voices = asyncio.run(edge_tts.list_voices())
    from pprint import pprint
    pprint(voices)
    return voices


# 语音列表（EDGE_TTS_VOICES）
# 这里只列出了一些常用的中文音色，方便快速选择：
# - Yunyang-云扬
# - Xiaoxiao-晓晓
# - Xiaoyi-晓伊
# - Yunjian-云健
# - Yunxi-云希
# - Yunxia-云夏（陕西小妮）
#
# 注意：这不是全部音色。
# 安装 edge-tts 模块后，可以在终端执行以下命令来查看所有可用的语音：
# edge-tts --list-voices
EDGE_TTS_VOICES = {
    'Yunyang-云扬': 'zh-CN-YunyangNeural',
    'Xiaoxiao-晓晓': 'zh-CN-XiaoxiaoNeural',
    'Xiaoyi-晓伊': 'zh-CN-XiaoyiNeural',
    'Yunjian-云健': 'zh-CN-YunjianNeural',
    'Yunxi-云希': 'zh-CN-YunxiNeural',
    'Yunxia-云夏': 'zh-CN-shaanxi-XiaoniNeural',
}


async def process_segment(segment: str, voice: str, rate: int, volume: int,
                          submaker: Optional[edge_tts.SubMaker] = None) -> bytes:
    """
    处理单个文本段，生成音频数据，并可选处理字幕数据。

    :param segment: 文本段。
    :param voice: 使用的语音。
    :param rate: 语速调整值。
    :param volume: 音量调整值。
    :param submaker: 用于生成字幕的 SubMaker 实例，默认为 None。
    :return: 音频数据。
    """
    log.debug(f"开始处理文本段: {segment[:20]}...")  # 截取前20个字符显示
    rates = f"+{rate}%" if rate >= 0 else f"{rate}%"
    volumes = f"+{volume}%" if volume >= 0 else f"{volume}%"
    communicate = edge_tts.Communicate(segment, voice=voice, rate=rates, volume=volumes)
    segment_audio = b''
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            segment_audio += chunk["data"]
        # 如果传入了 submaker，则处理字幕的 WordBoundary 信息
        elif chunk["type"] == "WordBoundary" and submaker is not None:
            submaker.feed(chunk)
    log.debug(f"文本段处理完成: {segment[:20]}...")
    return segment_audio


async def play_audio(segment_audio: bytes) -> None:
    """
    内存中播放音频数据。

    :param segment_audio: 音频数据 (MP3 格式)。
    """
    log.debug("开始播放音频...")
    try:
        # 捕获 pygame 的初始化消息
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            pygame.mixer.init()
        # 直接从内存加载音频数据
        sound = pygame.mixer.Sound(BytesIO(segment_audio))
        # 播放音频
        sound.play()
        # 等待音频播放完成
        await asyncio.sleep(sound.get_length())
        log.debug("音频播放完成。")
    except Exception as e:
        log.error(f"播放音频时发生错误：{e}")
    finally:
        # 确保退出 Pygame 音频系统
        pygame.mixer.quit()


async def tts_by_edge(text: str, voice: str = 'zh-CN-XiaoxiaoNeural', rate: int = 0, volume: int = 0, play: bool = True,
                      save_to_file: Optional[str] = None, subtitle_file: Optional[str] = None) -> bool:
    """
    将文本转换为语音，并可选择播放和/或保存到文件，还可导出字幕到 .srt 文件。

    :param text: 要转换的文本。
    :param voice: 使用的语音 (默认为：'zh-CN-XiaoxiaoNeural')。
    :param rate: 语速调整值 (-100 到 100)，默认为 0。
    :param volume: 音量调整值 (-100 到 100)，默认为 0。
    :param play: 是否播放音频，默认为 True。
    :param save_to_file: 保存音频的文件路径，如果为 None 则不保存，默认为 None。
    :param subtitle_file: 保存字幕的 .srt 文件路径，如果为 None 则不导出字幕，默认为 None。
    :return: 成功返回 True，否则返回 False。
    """
    log.debug(
        f"开始 TTS 转换，文本：{text[:20]}..., 语音：{voice}, 语速：{rate}, 音量：{volume}, 播放：{play}, 保存到：{save_to_file}, 字幕文件：{subtitle_file}")
    try:
        # 如果需要导出字幕，则创建 SubMaker 实例
        submaker = edge_tts.SubMaker() if subtitle_file is not None else None

        # 处理文本段并获取音频数据，同时处理字幕数据（如果有）
        segment_audio = await process_segment(text, voice, rate, volume, submaker)

        if play:
            await play_audio(segment_audio)

        if save_to_file:
            log.debug(f"开始保存音频到文件：{save_to_file}")
            with open(save_to_file, "wb") as f:
                f.write(segment_audio)
            log.info(f"音频已成功保存到文件：{save_to_file}")

        # 导出字幕到 .srt 文件
        if subtitle_file and submaker is not None:
            log.debug(f"开始保存字幕到文件：{subtitle_file}")
            with open(subtitle_file, "w", encoding="utf-8") as f:
                f.write(submaker.get_srt())
            log.info(f"字幕已成功保存到文件：{subtitle_file}")

        log.debug("TTS 转换完成。")
        return True
    except Exception as e:
        log.error(f"TTS 转换过程中发生错误：{e}")
        return False
