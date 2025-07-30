#!/bin/bash

# 获取环境变量，设置默认值
REPO_URL=${REPO_URL:-""}  # Git 仓库地址，默认为空
RUN_FILE=${RUN_FILE:-start.py}  # 默认启动文件
PULL_ON_RESTART=${PULL_ON_RESTART:-false}  # 默认不拉取最新代码
PORT=${PORT:-8000}  # 默认端口
PIP_MIRROR=${PIP_MIRROR:-"https://mirrors.aliyun.com/pypi/simple/"}  # 默认 pip 镜像源

# 提取项目名称作为根目录
PROJECT_NAME=$(basename -s .git $REPO_URL)
PROJECT_DIR="/app/$PROJECT_NAME"

# 输出容器启动的日志信息
echo "================= 容器启动配置 ================="
echo "Git 仓库地址: ${REPO_URL}"
echo "启动文件: ${RUN_FILE}"
echo "是否每次重启拉取最新代码: ${PULL_ON_RESTART}"
echo "端口号: ${PORT}"
echo "pip 镜像源: ${PIP_MIRROR}"

# 启动 SSH 服务（Dockerfile已经安装）
echo "启动 SSH 服务..."
service ssh start &

# 检查 REPO_URL 是否为空
if [ -z "$REPO_URL" ]; then
  echo "未提供 Git 仓库地址，跳过代码拉取和项目启动..."
  echo "容器保持运行..."
  tail -f /dev/null
  exit 0
fi

# 拉取代码的函数
pull_code() {
    if [ -d "$PROJECT_DIR/.git" ]; then
        echo "项目目录已存在，检查是否需要拉取最新代码..."
        if [ "$PULL_ON_RESTART" == "true" ]; then
            echo "正在丢弃本地更改和未跟踪的文件..."
            git -C "$PROJECT_DIR" reset --hard || { echo "git reset 失败，跳过"; }
            git -C "$PROJECT_DIR" clean -fd || { echo "git clean 失败，跳过"; }
            echo "强制拉取最新代码..."
            git -C "$PROJECT_DIR" pull || { echo "git pull 失败，跳过"; }
        fi
    else
        echo "项目目录不存在，正在克隆仓库: $REPO_URL ..."
        git clone $REPO_URL "$PROJECT_DIR" || { echo "git clone 失败，跳过"; }
    fi
}

# 检查并拉取代码
echo "检查并拉取代码..."
pull_code

# 创建虚拟环境
echo "创建虚拟环境..."
python3 -m venv /app/venv

# 激活虚拟环境并安装依赖
echo "安装依赖..."
source /app/venv/bin/activate

# 检查并安装依赖
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    echo "检测到 requirements.txt，正在安装项目依赖..."
    pip install --no-cache-dir -r "$PROJECT_DIR/requirements.txt" -i "$PIP_MIRROR" || { echo "pip 安装失败，跳过"; }
else
    echo "未找到 requirements.txt，跳过依赖安装..."
fi

# 移除路径开头的 `/`
RUN_FILE=${RUN_FILE#/}

# Python 命令
PYTHON_CMD="/app/venv/bin/python"

# 获取 RUN_FILE 的目录部分
RUN_FILE_DIR=$(dirname "$RUN_FILE")
RUN_FILE_NAME=$(basename "$RUN_FILE")

# 确保进入正确的目录
cd "$PROJECT_DIR/$RUN_FILE_DIR" || { echo "目录 $PROJECT_DIR/$RUN_FILE_DIR 不存在，退出"; exit 1; }

# 启动项目
echo "启动项目..."
exec $PYTHON_CMD "$RUN_FILE_NAME" || { echo "启动失败"; exit 1; }

# 容器保持运行
tail -f /dev/null
