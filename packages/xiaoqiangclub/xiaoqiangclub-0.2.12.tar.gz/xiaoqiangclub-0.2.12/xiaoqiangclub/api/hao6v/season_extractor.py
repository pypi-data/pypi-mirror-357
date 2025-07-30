# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/12/26 14:06
# 文件名称： season_extractor.py
# 项目描述： 提取 季/部 的信息
# 开发工具： PyCharm
import re
from typing import Optional
from xiaoqiangclub.config.log_config import log

# 中文数字到阿拉伯数字的映射
chinese_numbers = {
    "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,
    "十": 10, "百": 100, "千": 1000, "万": 10000
}

# 罗马数字到阿拉伯数字的映射
roman_numbers = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9,
    "X": 10, "XX": 20, "XXX": 30, "XL": 40, "L": 50, "LX": 60, "LXX": 70, "LXXX": 80, "XC": 90,
    "C": 100
}


def chinese_to_arabic(chinese_str: str) -> int:
    """
    将中文数字字符串转换为阿拉伯数字。

    :param chinese_str: 中文数字字符串
    :return: 对应的阿拉伯数字
    """
    result = 0
    unit = 1
    temp = 0
    for char in reversed(chinese_str):
        if char in chinese_numbers:
            num = chinese_numbers[char]
            if num == 10 or num == 100 or num == 1000:
                if temp == 0:
                    temp = 1
                result += temp * num
                temp = 0
            else:
                temp += num * unit
                unit = num
    result += temp
    return result


def roman_to_arabic(roman_str: str) -> Optional[int]:
    """
    将罗马数字转换为阿拉伯数字。

    :param roman_str: 罗马数字字符串
    :return: 对应的阿拉伯数字，若无匹配返回 None
    """
    roman_str = roman_str.upper()
    return roman_numbers.get(roman_str, None)


def extract_season_number(text: str) -> Optional[int]:
    """
    从给定文本中提取并转换季节或部数信息，支持中文、英文数字和罗马数字格式。

    :param text: 输入的文本，包含季节或部数信息
    :return: 提取的第一个季节或部数的阿拉伯数字，若未找到返回 None
    """
    matched_numbers: list = []

    # 季节/部数的正则表达式模式，处理中文和英文数字格式
    season_patterns = [
        r'第\s*(一|二|三|四|五|六|七|八|九|十|零|\d{1,2})\s*季',  # 中文格式第xx季，只捕获数字部分
        r'S\s*(\d{1,2})',  # 英文格式Sxx，只捕获数字部分
        r'第\s*(一|二|三|四|五|六|七|八|九|十|零|\d{1,2})\s*部',  # 中文格式第xx部，只捕获数字部分
        r'Season\s*(\d{1,2})',  # 英文格式Season xx，只捕获数字部分
    ]

    # 匹配其他季节/部数格式
    for pattern in season_patterns:
        season_matches = re.findall(pattern, text, re.IGNORECASE)
        if season_matches:
            for match in season_matches:
                # 如果匹配项是元组（例如S02E02），只取第一个数字
                if isinstance(match, tuple):
                    matched_numbers.append(match[0])
                else:
                    matched_numbers.append(match)

    # 精确匹配罗马数字（确保前后不是英文字符）
    roman_pattern = r'(?<![a-zA-Z])(I{1,3}|IV|V?I{0,3}|II|III|IV|V|VI|VII|VIII|IX|X)(?![a-zA-Z])'
    roman_matches = re.findall(roman_pattern, text, re.IGNORECASE)
    roman_matches = [match.strip() for match in roman_matches if match.strip()]
    matched_numbers.extend(roman_matches)  # 保存匹配的罗马数字

    # 第二步：将所有捕获的数字转为阿拉伯数字
    arabic_numbers = []
    for num_str in matched_numbers:
        # 去掉前导零
        num_str = num_str.lstrip('0')

        # 判断数字是否为中文数字
        if any(char in chinese_numbers for char in num_str):
            arabic_numbers.append(chinese_to_arabic(num_str))

        # 如果是阿拉伯数字，直接转换
        elif num_str.isdigit():
            arabic_numbers.append(int(num_str))

        # 判断是否为罗马数字
        elif roman_to_arabic(num_str):
            arabic_numbers.append(roman_to_arabic(num_str))

    # 返回转化后的阿拉伯数字，假设优先提取第一个季节/部数信息
    if arabic_numbers:
        log.debug(f"{text} >>> {arabic_numbers[0]}")  # 打印提取到的数字
        return arabic_numbers[0]
    else:
        log.debug(f"未能从 {text} 提取到季节/部数信息。")  # 如果没有提取到信息
        return None
