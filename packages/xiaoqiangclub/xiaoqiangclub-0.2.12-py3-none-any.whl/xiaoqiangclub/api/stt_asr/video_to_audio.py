# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/2/20 13:54
# 文件名称： video_to_audio.py
# 项目描述： 视频转语音：从视频中提取语音文件
# 开发工具： PyCharm
import os
import asyncio
import time
from moviepy import VideoFileClip
from typing import Union, List, Optional
from xiaoqiangclub.config.log_config import log
from contextlib import redirect_stdout, redirect_stderr


async def extract_audio_from_video(video_path: str, audio_path: str, audio_format: str = 'wav') -> bool:
    """
    从视频文件中提取音频并保存为指定格式。

    :param video_path: 视频文件路径
    :param audio_path: 音频输出路径
    :param audio_format: 输出音频的格式，默认为 wav
    :return: 提取成功返回 True，失败返回 False
    """
    for _ in range(3):
        try:
            # 使用虚拟设备重定向所有输出
            with open(os.devnull, 'w') as null:
                # 重定向标准输出和错误
                with redirect_stdout(null), redirect_stderr(null):
                    # 加载视频时添加 FFmpeg 静默参数
                    video_clip = VideoFileClip(video_path)
                    audio = video_clip.audio  # 获取视频的音频
                    codec = 'pcm_s16le' if audio_format == 'wav' else None

                    # 导出音频时
                    audio.write_audiofile(audio_path, codec=codec)
                # 提取成功
                log.debug(f"音频提取成功: {audio_path}", flush=True)
                return True  # 如果提取成功，直接返回 True
        except Exception as e:
            log.error(f"提取失败: {str(e)}", flush=True)
            time.sleep(1)  # 可以加点延时再重试，避免频繁请求导致失败

    # 如果重试三次都失败，返回 False
    return False


async def video_to_audio_single(video_path: str, output_dir: str, audio_format: str = 'wav') -> Optional[str]:
    """
    [单个]异步处理视频文件，将其转换为音频。

    :param video_path: 视频文件路径
    :param output_dir: 输出文件夹路径
    :param audio_format: 输出音频格式
    :return: 输出音频文件的路径
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 保持原视频文件名，生成音频文件路径，并使用指定的音频格式
    base_name = os.path.splitext(os.path.basename(video_path))[0]

    # 创建一个同名文件夹
    audio_folder = os.path.join(output_dir, base_name)
    os.makedirs(audio_folder, exist_ok=True)

    audio_path = os.path.join(audio_folder, f"{base_name}.{audio_format}")

    # 提取音频
    if await extract_audio_from_video(video_path, audio_path, audio_format):
        return audio_path


async def video_to_audio(videos: Union[str, List[str]], output_dir: str = None,
                         audio_format: str = 'wav') -> list:
    """
    异步批量处理视频文件，将其转换为音频文件。

    :param videos: 视频文件路径，单个文件或多个文件的路径列表
    :param output_dir: 输出文件夹路径，默认为当前目录
    :param audio_format: 音频输出格式，默认为 wav
    """

    output_dir = output_dir or os.getcwd()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        log.debug(f"创建导出目录: {output_dir}")

    # 如果传入的是单个文件路径，则转为列表
    if isinstance(videos, str):
        videos = [videos]

    # 异步处理每个视频文件
    tasks = [video_to_audio_single(video, output_dir, audio_format) for video in videos]
    return await asyncio.gather(*tasks)
