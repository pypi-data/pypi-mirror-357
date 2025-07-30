# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2024/12/18 16:26
# 文件名称： config_ui.py
# 项目描述： 一个快速简便生成配置页面的工具
# 开发工具： PyCharm
import os
import time
import uvicorn
import threading
import webbrowser
from typing import (Dict, Any)
from fastapi import (FastAPI, Request)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from xiaoqiangclub.config.log_config import log
from starlette.responses import RedirectResponse
from xiaoqiangclub.config.config_sync import sync_config
from xiaoqiangclub.data.file import (read_file_async, write_file_async)

# [自定义]配置文件路径：用于设置配置页面的控件布局和默认参数，必须是 JSON 和 YAML 文件。
default_config_file = "config_ui.json"

# 当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, "data")

# 生成和 default_config_file 相同后缀的 user_config_file
user_config_file_suffix = os.path.splitext(default_config_file)[1]
user_config_file = os.path.join(data_dir, f"default_config{user_config_file_suffix}")

app = FastAPI()

# 模板渲染器
templates = Jinja2Templates(directory="templates")




@app.get("/", response_class=HTMLResponse)
async def get_settings_page(request: Request):
    """配置页面"""
    settings = await sync_config(user_config_file, default_config_file)
    return templates.TemplateResponse("config_ui.html",
                                      {"request": request, "settings": settings})


@app.post("/config/save_settings")
async def save_settings(user_settings: dict):
    """保存修改的配置"""

    settings = await config_ui_sort(user_settings)
    await write_file_async(user_config_file, settings)  # 保存更新后的配置

    return {"status": "success", "message": "设置已保存！"}


@app.post("/config/reset_settings")
async def reset_settings():
    """重置配置"""
    # 读取初始配置
    initial_config = await read_file_async(default_config_file)  # 假设config_file是初始设置的文件

    # 重新写入初始配置到 user_config.json
    await write_file_async(user_config_file, initial_config)

    return {"status": "success", "message": "设置已恢复为初始状态！"}


@app.get("/{path:path}")
async def catch_all(path: str):
    """未匹配到路由，重定向到主页，注意：这条路由必须在末尾，否则会被其他路由拦截"""
    log.info(f"未匹配到路由，重定向到主页：{path} >>> /")
    return RedirectResponse(url="/")


def open_browser():
    """在浏览器中自动打开 FastAPI 项目首页"""
    # 等待 2 秒，以确保服务器已启动
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == '__main__':
    # 检查是否在 Windows 系统中
    if os.name == "nt":  # 'nt' 表示 Windows 系统
        # 使用线程打开浏览器，不阻塞 uvicorn 服务的启动
        threading.Thread(target=open_browser).start()

    # 启动 FastAPI 服务
    uvicorn.run(app, host="127.0.0.1", port=8000)
