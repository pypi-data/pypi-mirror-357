# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2025/1/2 17:41
# 文件名称： config_sync.py
# 项目描述： 配置文件同步
# 开发工具： PyCharm
import os
from typing import Dict, Any
from xiaoqiangclub.data.file import read_file_async, write_file_async


async def config_ui_sort(dict_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    对字典进行排序，外层字典按顺序排列，内层字典根据 'order' 字段进行排序。

    :param dict_data: 需要排序的字典数据，字典的键为字符串，值可以是任何类型
    :return: 排序后的字典，外层字典按顺序排列，内层字典中的元素按 'order' 字段排序
    """
    first_order = []  # 存储外层字典的排序顺序
    dict_map = []  # 存储内层字典的排序信息

    # 处理外层字典
    for key, value in dict_data.items():
        if isinstance(value, dict):
            orders = []  # 存储内层字典中 'order' 的值
            second_order = []  # 存储内层字典的排序顺序

            # 获取内层字典的 'order' 值并排序
            for inner_key, inner_value in value.items():
                # 确保 inner_value 是字典类型
                if isinstance(inner_value, dict):
                    orders.append(int(inner_value.get('order', float('inf'))))  # 如果没有 'order'，设为无限大
                else:
                    orders.append(float('inf'))  # 如果不是字典，设为无限大

            # 只有当 orders 不为空时，才进行排序和记录
            if orders:
                # 对 'order' 值进行排序，并按排序后的顺序将键添加到 second_order
                sorted_inner_order = sorted(orders)
                for i in sorted_inner_order:
                    for inner_key, inner_value in value.items():
                        if isinstance(inner_value, dict) and i == inner_value.get('order', float('inf')):
                            second_order.append(inner_key)

                dict_map.append((key, sorted_inner_order[0], second_order))  # 记录外层字典的排序信息
            else:
                # 如果内层没有 'order' 字段，则直接将 key 添加到 first_order
                first_order.append(key)
        else:
            # 如果是普通字段（如 'title', 'logo'），直接添加到 first_order
            first_order.append(key)

    # 根据内层字典的 'order' 字段排序外层字典
    orders = [data[1] for data in dict_map]  # 获取排序的 'order' 值
    sorted_first_order = sorted(orders)  # 排序所有内层字典的 'order'

    # 将排序后的内层字典添加到 first_order 中
    for i in sorted_first_order:
        for data in dict_map:
            if data[1] == i:
                first_order.append(data)

    # 构建新的排序后的字典
    new_dict = {}
    for data in first_order:
        if isinstance(data, str):
            # 如果是普通字段，直接添加到新字典
            new_dict[data] = dict_data[data]
        elif isinstance(data, tuple):
            # 如果是包含字典的字段，按照排序后的顺序添加
            new_dict[data[0]] = {}
            for inner_key in data[2]:
                new_dict[data[0]][inner_key] = dict_data[data[0]][inner_key]

    return new_dict


def merge_recursive(user_config, default_config):
    """
    使用递归合并两个配置文件中的字段，保留用户配置的字段，并确保默认配置中的缺失字段被添加。
    对于嵌套的字典，将递归合并其内部的字段。

    :param user_config: 用户配置字典
    :param default_config: 默认配置字典
    :return: 合并后的配置字典
    """
    for key, value in default_config.items():
        if key not in user_config:
            user_config[key] = value  # 默认配置中的字段添加到用户配置中
        elif isinstance(value, dict):  # 如果字段值是字典类型，则递归合并
            if not isinstance(user_config[key], dict):
                user_config[key] = {}
            user_config[key] = merge_recursive(user_config[key], value)  # 递归调用合并子字典
    return user_config


async def sync_config(user_config_file: str, default_config_file: str, sort_config: bool = False):
    """
    确保默认配置的所有字段都存在于用户配置中，如果不存在就添加。
    - 如果用户配置文件存在且内容为空，使用默认配置替代。
    - 如果配置文件不存在，创建新的配置文件并保存。
    - 使用递归确保所有字段，包含嵌套字段都正确合并。

    :param user_config_file: 用户配置文件路径
    :param default_config_file: 默认配置文件路径
    :param sort_config: 是否对配置项进行排序，默认为False
    :return: 合并后的用户配置字典
    """

    # 读取默认配置
    default_config = await read_file_async(default_config_file)

    # 如果用户配置文件存在
    if os.path.exists(user_config_file):
        # 读取用户配置文件
        user_config = await read_file_async(user_config_file)

        # 如果用户配置内容为空或不是字典类型，则用默认配置替代
        if not isinstance(user_config, dict):
            user_config = default_config
        else:
            # 使用递归来确保所有字段合并
            user_config = merge_recursive(user_config, default_config)

            # 排序
            if sort_config:
                user_config = await config_ui_sort(user_config)
    else:
        # 如果用户配置文件不存在，直接使用默认配置
        user_config = default_config

    # 将合并后的用户配置写入文件
    await write_file_async(user_config_file, user_config)

    return user_config
