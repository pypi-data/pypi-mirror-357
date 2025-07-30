#!/bin/bash

# 从环境变量中获取可执行文件名，默认为 run_app*
APP_FILE="${APP_FILE:-run_app*}"

while true; do
    # 使用 eval 扩展通配符，使得它可以被 find 命令识别
    latest_file=$(eval "find /app -maxdepth 1 -type f -name '$APP_FILE' -printf '%T@ %p\n'" | sort -n | tail -1 | cut -d' ' -f2-)

    if [ -n "$latest_file" ]; then
        # 给找到的文件添加可执行权限
        chmod +x "$latest_file"
        # 运行该文件
        "$latest_file"
        break
    else
        # 等待一段时间后重试
        echo "Not found $APP_FILE, waiting..."
        sleep 10
    fi
done
