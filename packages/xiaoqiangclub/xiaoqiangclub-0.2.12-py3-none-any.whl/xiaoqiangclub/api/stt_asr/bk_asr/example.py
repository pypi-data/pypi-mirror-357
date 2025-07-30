# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/2/24 16:21
# 文件名称： example.py
# 项目描述： 使用示例
# 开发工具： PyCharm
import BcutASR, JianYingASR, KuaiShouASR

if __name__ == '__main__':
    audio_file = r"D:\001_MyArea\002_MyCode\001_PythonProjects\2025\video_to_text\dist\一个url就能克隆你的的网站 #ai #前端#vue #react #人工智能\一个url就能克隆你的的网站 #ai #前端#vue #react #人工智能.wav"
    asr = JianYingASR(audio_file)
    result = asr.run()
    # result.to_srt()
    print(result.to_srt())
