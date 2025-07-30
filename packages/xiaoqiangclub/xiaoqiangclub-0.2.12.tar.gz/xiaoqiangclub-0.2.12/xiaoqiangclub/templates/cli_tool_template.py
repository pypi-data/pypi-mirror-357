# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/11/3 19:46
# 文件名称： cli_tool_template.py
# 项目描述： 命令行工具模板文件
# 开发工具： PyCharm
import argparse


def cli_tool() -> None:
    """
    命令行工具模板函数
    参考文章：https://xiaoqiangclub.blog.csdn.net/article/details/132832514
    """
    parser = argparse.ArgumentParser(prog='cli_tool_template', description='这是一个自动生成的命令行工具模板')

    # 字符串参数示例
    parser.add_argument('-n', '--name', type=str, required=True, help='模板名称，必填')

    # 布尔值参数示例
    parser.add_argument('-v', '--verbose', action='store_true', help='启用详细输出，默认关闭')

    # 整数参数示例
    parser.add_argument('-i', '--iterations', type=int, default=1, help='执行次数，默认为1')

    # 目录参数示例
    parser.add_argument('-d', '--directory', type=str, default='.', help='生成模板的目录路径，默认为当前目录')

    args = parser.parse_args()

    # 在这里添加你要执行的功能
    print(f"模板名称: {args.name}")
    print(f"生成目录: {args.directory}")
    print(f"详细输出: {'开启' if args.verbose else '关闭'}")
    print(f"执行次数: {args.iterations}")


if __name__ == '__main__':
    cli_tool()
