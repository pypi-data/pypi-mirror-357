# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/1/8 15:14
# 文件名称： openai_gemini.py
# 项目描述： https://blog.csdn.net/xiaoqiangclub/article/details/145001184
# 开发工具： PyCharm
import requests
from typing import Optional
from openai import OpenAI, AsyncOpenAI

# 修改为自己的BASE_URL和GEMINI_API_KEY
GEMINI_API_KEY = "AIzaSyBWQACSg828E3xy1SYUNW5U1s1JOz-thxs"


def get_gemini_models(base_url: str = None, api_key: str = None) -> Optional[list]:
    """
    获取Gemini支持的模型列表
    :param base_url: 国内可用的BASE_URL
    :param api_key: Gemini API密钥
    :return: ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-exp-1206']
    """
    api_key = api_key or GEMINI_API_KEY
    if not base_url or not api_key:
        print("请提供有效的BASE_URL和API_KEY。")
        return None

    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(f"{base_url.split('/v1')[0]}/v1/models", headers=headers)
    if response.status_code == 200:
        try:
            return [model["id"] for model in response.json()["data"]]
        except Exception as e:
            print(f"错误: {e}")
            return None


def chat_with_gemini(question: str, base_url: str = None, api_key: str = None,
                     model: str = "gemini-2.0-flash-exp",
                     stream: bool = False) -> Optional[str]:
    """
    聊天接口
    :param question: 用户的问题
    :param base_url: 国内可用的BASE_URL
    :param api_key: 用于访问API的密钥
    :param model: 使用的模型代号，可以调用 get_gemini_models 查看支持的模型
    :param stream: 使用流式输出
    :return:
    """
    api_key = api_key or GEMINI_API_KEY
    if not base_url or not api_key:
        print("请提供有效的BASE_URL和API_KEY。")
        return None

    messages = [{"role": "user", "content": question}]

    client = OpenAI(api_key=api_key, base_url=base_url.split("/v1")[0] + "/v1")

    try:
        if stream:
            answer = ""
            stream_response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    answer_chunk = chunk.choices[0].delta.content
                    answer += answer_chunk
                    print(answer_chunk, end="", flush=True)
        else:
            completion = client.chat.completions.create(model=model, messages=messages)
            answer = completion.choices[0].message.content

        return answer
    except Exception as e:
        print(f"错误: {e}")
        return None


async def chat_with_gemini_async(question: str, base_url: str = None, api_key: str = None,
                                 model: str = "gemini-2.0-flash-exp",
                                 stream: bool = False) -> Optional[str]:
    """
    异步聊天接口
    :param question: 用户的问题
    :param base_url: 国内可用的BASE_URL
    :param api_key: 用于访问API的密钥
    :param model: 使用的模型代号
    :param stream: 是否开启流式输出
    :return: 聊天生成的回答字符串
    """
    api_key = api_key or GEMINI_API_KEY
    if not base_url or not api_key:
        print("请提供有效的BASE_URL和API_KEY。")
        return None

    messages = [{"role": "user", "content": question}]

    # 初始化客户端
    client = AsyncOpenAI(api_key=api_key, base_url=base_url.split("/v1")[0] + "/v1")

    try:
        if stream:
            answer = ""
            # 异步流式输出
            stream_response = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            async for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    chunk_content = chunk.choices[0].delta.content
                    print(chunk_content, end="", flush=True)
                    answer += chunk_content
            return answer
        else:
            # 异步单次调用
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
            )
            return response.choices[0].message.content
    except Exception as e:
        print(f"错误: {e}")
        return None