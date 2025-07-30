# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/12/17 10:15
# 文件名称： website_monitoring.py
# 项目描述： 网站监控
# 开发工具： PyCharm
import asyncio
from typing import List, Union
from xiaoqiangclub.config.log_config import log
from xiaoqiangclub.utils.network_utils import get_response_async


async def check_one_website(url: str) -> bool:
    """
    检查网站是否正常
    :param url: 网址
    :return:
    """
    response = await get_response_async(url, random_ua=True, raise_on_failure=False)
    if not response or response.status_code > 400:
        log.error(f'{url} 访问异常，请手动核查！')
        return False
    log.info(f'{url} 访问正常')
    return True


async def check_website(urls: Union[str, List[str]]) -> List[bool]:
    """
    检查网站是否正常
    :param urls: 网址
    :return:
    """
    if isinstance(urls, str):
        urls = [urls]

    return await asyncio.gather(*[check_one_website(url) for url in urls])
