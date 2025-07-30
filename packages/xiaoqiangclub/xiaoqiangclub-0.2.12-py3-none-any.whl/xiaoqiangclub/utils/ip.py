# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/1/6 08:37
# 文件名称： ip.py
# 项目描述： IP相关
# 开发工具： PyCharm
import socket
import asyncio
from typing import Optional

from xiaoqiangclub.utils.network_utils import get_response_async


async def get_local_ip() -> str:
    """
    获取局域网IP
    :return: 局域网IP地址
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # 通过UDP连接公共DNS服务，获取局域网IP
            local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "无法获取局域网IP"
    return local_ip


async def get_ipv4() -> Optional[str]:
    """
    获取公网IPv4地址
    :return: 公网IPv4地址
    """
    ipv4_services = [
        "https://httpbin.org/ip",  # 返回JSON格式 {"origin": "123.45.67.89"}
        "https://api64.ipify.org?format=json"  # 返回JSON格式 {"ip": "123.45.67.89"}
    ]
    ipv4 = None
    for service in ipv4_services:
        try:
            json_data = await get_response_async(service, timeout=5, return_json=True)
            if json_data:
                if service == "https://httpbin.org/ip":
                    ipv4 = json_data.get("origin", "").strip()
                elif service == "https://api64.ipify.org?format=json":
                    ipv4 = json_data.get("ip", "").strip()

                if ipv4:
                    break
        except Exception:
            continue
    return ipv4


async def get_ipv6() -> Optional[str]:
    """
    获取公网IPv6地址
    :return: 公网IPv6地址
    """
    ipv6_services = [
        "https://icanhazip.com",  # 返回纯文本格式 "2001:db8::1"
        "https://ifconfig.co/ip"  # 返回纯文本格式 "2001:db8::1"
    ]
    ipv6 = None
    for service in ipv6_services:
        try:
            response = await get_response_async(service, timeout=5)
            if response.status_code == 200:
                ipv6 = response.text.strip()
                if ipv6:
                    break
        except Exception:
            continue
    return ipv6


async def get_ip():
    """
    获取局域网IP和公网IP（支持IPv4和IPv6），并行请求加速
    :return: 一个字典，包括局域网IP（local_ip）、公网IPv4地址（ipv4）和公网IPv6地址（ipv6）
    """
    # 使用gather方法并发执行多个任务
    local_ip, ipv4, ipv6 = await asyncio.gather(
        get_local_ip(),  # 获取局域网IP
        get_ipv4(),  # 获取公网IPv4地址
        get_ipv6()  # 获取公网IPv6地址
    )

    result = {
        "local_ip": local_ip,
        "ipv4": ipv4,
        "ipv6": ipv6
    }
    return result


if __name__ == '__main__':
    async def main():
        print(await get_ip())


    asyncio.run(main())
