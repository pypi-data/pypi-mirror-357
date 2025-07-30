import asyncio
from typing import Optional
from openai import AsyncOpenAI


async def chat_with_gemini_async(question: str, base_url: str, api_key: str = None,
                                 model: str = "gemini-2.0-flash-exp",
                                 stream: bool = False) -> Optional[str]:
    """
    异步聊天接口
    :param question: 用户的问题
    :param base_url: Gemini API的URL
    :param api_key: 用于访问API的密钥
    :param model: 使用的模型代号
    :param stream: 是否开启流式输出
    :return: 聊天生成的回答字符串
    """
    if not api_key:
        api_key = "AIzaSyBWQACSg828E3xy1SYUNW5U1s1JOz-thxs"

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


# 示例调用
async def main():
    base_url = "https://gemini.xiaoqiangtools.dpdns.org/v1"
    question = "什么是Gemini模型？"
    api_key = "AIzaSyBWQACSg828E3xy1SYUNW5U1s1JOz-thxs"

    # print("单次调用结果:")
    # result = await chat_with_gemini_async(question, base_url, api_key, stream=False)
    # print(result)

    print("\n流式调用结果:")
    result = await chat_with_gemini_async(question, base_url, api_key, stream=True)
    print("\n完整回答:", result)


if __name__ == "__main__":
    asyncio.run(main())
