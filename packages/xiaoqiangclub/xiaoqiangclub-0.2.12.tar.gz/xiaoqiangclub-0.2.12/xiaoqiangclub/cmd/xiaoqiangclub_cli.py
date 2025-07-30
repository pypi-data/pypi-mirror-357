# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/11/17 10:14
# 文件名称： xiaoqiangclub_cli.py
# 项目描述： xiaoqiangclub 命令行工具
# 开发工具： PyCharm
import asyncio
import argparse
from xiaoqiangclub.config.constants import VERSION
# from ..api.wechat.chatbot_csv_to_json import chatbot_convert_cli
from .commands.create_docker_project import create_docker_project
from .commands.create_python_project_template import create_python_project
from .commands.create_config_page_project import create_config_page_project
from .commands.cli_tool_template_generator import generate_cli_tool_template


def main():
    parser = argparse.ArgumentParser(prog='xiaoqiangclub', description=f'XiaoqiangClub 命令行工具 v{VERSION}',
                                     epilog='微信公众号：XiaoqiangClub',
                                     formatter_class=argparse.RawTextHelpFormatter)  # RawTextHelpFormatter 保留描述符串中的换行符

    # 添加 version 选项
    parser.add_argument('-v', '--version', action='version', version=VERSION,
                        help="版本信息")

    subparsers = parser.add_subparsers(title='子命令', dest='command')  # 添加子命令：只能有一个add_subparsers方法

    # 生成Python项目目录结构
    project_template = subparsers.add_parser('project_template', help='生成 Python 项目模板',
                                             description='生成Python项目模板')
    project_template.add_argument('-n', '--name', type=str, required=True, help='项目名称')
    project_template.add_argument('-d', '--directory', type=str, default=None, help='项目路径，默认为当前目录')
    project_template.set_defaults(func=create_python_project)  # 设置默认函数

    # 生成 Docker 镜像项目目录结构
    docker_template = subparsers.add_parser('docker_template', help='生成 Docker 镜像项目模板',
                                            description='生成 Docker 镜像项目模板')
    docker_template.add_argument('-n', '--name', type=str, required=True,
                                 help='支持的项目参数：xiaoqiangserver,\nredis_db')  # 使用多行字符串
    docker_template.add_argument('-d', '--directory', type=str, default=None, help='生成项目保存的路径，默认为当前目录')
    docker_template.set_defaults(func=create_docker_project)  # 设置默认函数

    # 生成命令行工具模板
    cli_template = subparsers.add_parser('cli_template', help='生成命令行工具模板文件',
                                         description='生成命令行工具模板文件')
    cli_template.add_argument('-n', '--name', type=str, default='cli_tool_template',
                              help='模板名称，默认为 "cli_tool_template.py"')
    cli_template.add_argument('-d', '--directory', type=str, default=None,
                              help='生成的模板存放目录路径，默认为当前目录')
    cli_template.set_defaults(func=generate_cli_tool_template)

    # 生成 fastapi 配置页面模板
    docker_template = subparsers.add_parser('config_ui_template', help='生成 fastapi 配置页面模板',
                                            description='生成 fastapi 配置页面模板')
    docker_template.add_argument('-d', '--directory', type=str, default=None, help='生成项目保存的路径，默认为当前目录')
    docker_template.set_defaults(func=create_config_page_project)  # 设置默认函数

    # # 新增子命令：转换 Chatbot 知识库 CSV 为 JSON
    # chatbot_convert = subparsers.add_parser('chatbot_convert', help='将 Chatbot 知识库 CSV 文件转换为 JSON 文件',
    #                                         description='将 Chatbot 导出的知识库 CSV 文件转换为 JSON 文件')
    # chatbot_convert.add_argument('-i', '--input', type=str, required=True, help='要转换的 CSV 或 Excel 文件路径')
    # chatbot_convert.add_argument('-o', '--output', type=str, required=True, help='保存到 JSON 文件的路径')
    # chatbot_convert.set_defaults(func=chatbot_convert_cli)  # 设置对应的处理函数

    # 命令行参数解析
    args = parser.parse_args()
    if args.command:
        print(vars(args))
        if not vars(args):  # 如果没有提供任何子命令的参数
            parser.print_help()  # 打印命令行工具的帮助
        else:
            # 判断是否是异步函数
            if asyncio.iscoroutinefunction(args.func):
                # 异步执行
                asyncio.run(args.func(args))  # 使用 asyncio.run 来调用异步函数
            else:
                # 同步执行
                args.func(args)  # 直接执行同步函数
    else:
        parser.print_help()
