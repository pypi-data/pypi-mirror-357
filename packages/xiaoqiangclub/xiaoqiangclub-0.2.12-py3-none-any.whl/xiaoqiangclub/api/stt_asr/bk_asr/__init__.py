from .BcutASR import BcutASR

from .KuaiShouASR import KuaiShouASR

# https://github.com/WEIFENG2333/AsrTools
__all__ = ["BcutASR", "KuaiShouASR"]


def transcribe(audio_file, platform):
    assert platform in __all__
    asr = globals()[platform](audio_file)
    return asr.run()
