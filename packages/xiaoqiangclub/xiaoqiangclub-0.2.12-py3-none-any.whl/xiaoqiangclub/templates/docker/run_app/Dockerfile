FROM ubuntu:24.04

# 复制启动脚本到容器中
COPY start.sh /start.sh

# 给启动脚本添加可执行权限，安装必要的工具，如 find 和 bash
RUN chmod +x /start.sh && apt-get update && apt-get install -y findutils bash tzdata && rm -rf /var/lib/apt/lists/*

# 设置时区和可执行文件的默认名称
ENV TZ=Asia/Shanghai APP_FILE="run_app*"

# 创建工作目录
WORKDIR /app

# 挂载本地目录到容器的 /app 目录
VOLUME /app

# 暴露容器的 8000 端口
EXPOSE 8000

# 容器启动时运行启动脚本
CMD ["/start.sh"]
