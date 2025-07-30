# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/2/20 13:54
# 文件名称： stt.py
# 项目描述： 语音转文字：从音频中提取文字
# 开发工具： PyCharm
import os
import random
import asyncio
from typing import Optional, List, Union
from xiaoqiangclub.config.log_config import log
from xiaoqiangclub.data.file import get_file_name_and_extension
from xiaoqiangclub.api.stt_asr.bk_asr import BcutASR, KuaiShouASR


async def audio_to_text_single(audio: str, save_dir: Optional[str] = None, open_dir: bool = False) -> Optional[str]:
    """
    [单个任务处理]将 "flac", "m4a", "mp3", "wav" 格式的音频转化为文字
    :param audio: 音频文件的路径
    :param save_dir: 保存结果到指定的文件夹，默认为 None，不保存
    :param open_dir: 是否打开目录
    :return: 转换结果，如果失败则返回 None
    """

    # 判断文件是否存在
    if not os.path.exists(audio):
        log.error(f"文件 {audio} 不存在！")
        return None

    # ASR 引擎的顺序
    asr_engines = [BcutASR, KuaiShouASR]
    result = None

    for attempt in range(3):  # 外层重试机制
        log.debug(f"第 {attempt + 1} 轮重试")

        # 每轮重试时打乱引擎顺序
        random.shuffle(asr_engines)

        # 循环尝试不同的引擎，直到成功或用尽所有引擎
        for engine in asr_engines:
            try:
                log.info(f"正在使用 {engine.__name__} 模型进行音频转文字，请稍等...")
                loop = asyncio.get_event_loop()
                # 使用 run_in_executor 异步执行同步的 ASR 引擎
                result = await loop.run_in_executor(None, lambda: engine(audio).run())

                # 如果成功获得结果，则退出引擎循环
                if result:
                    break
            except Exception as e:
                log.error(f"使用 {engine.__name__} 时出错: {e}")
                # 如果当前引擎失败，继续尝试下一个引擎
                continue

        # 如果成功获取到结果，退出外层重试循环
        if result is not None:
            break
    else:
        # 如果所有轮次均未成功，返回 None
        log.error("所有 ASR 引擎均未成功转换音频，请检查音频文件或引擎配置。")
        return None

    # 获取文件名
    file_name, _ = get_file_name_and_extension(audio)

    # 如果指定了保存路径，则将转录结果保存
    if save_dir:
        save_dir = os.path.join(save_dir, file_name)
        os.makedirs(save_dir, exist_ok=True)

        save_to_file = os.path.join(save_dir, file_name + ".txt")
        result.save(save_to_file)
        log.info(f"转录完成，已保存至 {save_to_file}")
        if open_dir:
            os.startfile(save_dir)

    return result.to_txt()


async def stt(audios: Union[str, List[str]],
              save_path: Optional[str] = None,
              save_to_clipboard: bool = False) -> list:
    """
    [批量任务处理]将 "flac", "m4a", "mp3", "wav" 格式的音频转化为文字
    :param audios: 音频文件的路径，单个文件或多个文件的路径列表
    :param save_path: 保存转换结果到指定的文件，默认为 None，不保存
    :param save_to_clipboard: 是否将结果复制到剪贴板，默认为 False
    :return: None
    """
    if isinstance(audios, str):
        audios = [audios]

    tasks = [audio_to_text_single(audio, save_path, save_to_clipboard) for audio in audios]
    results = await asyncio.gather(*tasks)
    return results
