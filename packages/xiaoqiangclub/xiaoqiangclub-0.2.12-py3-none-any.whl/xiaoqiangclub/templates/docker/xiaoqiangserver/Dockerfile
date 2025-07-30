FROM ubuntu:24.04

# 设置环境变量
ENV REPO_URL="" \
    RUN_FILE="start.py" \
    PULL_ON_RESTART="true" \
    PORT="8000" \
    PIP_MIRROR="https://mirrors.aliyun.com/pypi/simple/" \
    SSH_PASSWORD="xiaoqiangclub" \
    TZ="Asia/Shanghai"

# 设置工作目录
WORKDIR /app

# 复制 entrypoint.sh 脚本到容器的 /app 目录
COPY entrypoint.sh /entrypoint.sh

# 设置时区并安装基础依赖，安装 SSH 服务，合并所有 RUN 指令
RUN ln -snf /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo ${TZ} > /etc/timezone && \
    apt-get update && \
    apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    gcc \
    gfortran \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    libffi-dev \
    libssl-dev \
    git \
    curl \
    ca-certificates \
    openssh-server && \
    mkdir -p /run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "root:${SSH_PASSWORD}" | chpasswd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    chmod +x /entrypoint.sh

# 暴露应用和 SSH 端口
EXPOSE ${PORT} 22

# 设置容器启动时的执行命令
CMD /entrypoint.sh
