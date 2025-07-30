# _*_ coding : UTF-8 _*_
# 开发人员： XiaoqiangClub
# 微信公众号: XiaoqiangClub
# 开发时间：2024年06月13日
# 文件名称： igot_sender.py
# 项目描述： 发送IGot消息的模块

import httpx
from typing import Dict
from xiaoqiangclub.config.log_config import log


class IGotSender:
    @staticmethod
    async def send_igot_message(igot_key: str, message: str) -> bool:
        """
        发送IGot消息。

        :param igot_key: IGot密钥，字符串类型。
        :param message: 消息内容，字符串类型。
        获取IGot参数：https://push.hellyw.com/
        :return: 消息发送成功返回 True，否则返回 False。
        """
        async with httpx.AsyncClient() as client:
            try:
                send_url = f"https://push.hellyw.com/{igot_key}"
                data = {
                    "title": "Message",
                    "content": message
                }
                response = await client.post(send_url, json=data)
                if response.status_code == 200:
                    log.info("IGot消息发送成功")
                    return True
                else:
                    log.error(f"IGot消息发送失败: {response.status_code}")
                    return False
            except Exception as e:
                log.error(f"IGot消息发送失败: {e}")
                return False

    @staticmethod
    async def send_igot_message_with_config(config: Dict[str, Dict[str, str]], message: str) -> bool:
        """
        使用配置文件发送IGot消息。

        :param config: 配置字典，字典类型，包含 igot 的配置信息。
        :param message: 消息内容，字符串类型。
        :return: 消息发送成功返回 True，否则返回 False。
        """
        igot_config = config['igot']
        return await IGotSender.send_igot_message(
            igot_key=igot_config['igot_key'],
            message=message
        )
