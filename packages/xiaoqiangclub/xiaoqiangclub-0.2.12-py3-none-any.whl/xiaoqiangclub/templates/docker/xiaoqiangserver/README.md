# Git Auto Runner

Git Auto Runner 是一个容器化的自动化项目管理工具，旨在通过 Docker 容器从 Git 仓库拉取代码、安装依赖并启动指定的 Python
脚本。该项目支持自动拉取最新代码、创建虚拟环境、安装依赖等功能，适用于各种 Python 项目的容器化部署。

## 项目文件结构

```
.
├── __init__.py
├── Dockerfile
├── entrypoint.sh
└── README.md
```

## 文件说明

### 1. `Dockerfile`

此文件定义了容器的构建过程，包括基础镜像的选择和所需的依赖安装。容器基于 `ubuntu:24.04` 构建，安装了 Python3、pip
和其他依赖项。容器启动时执行 `entrypoint.sh` 脚本。

### 2. `entrypoint.sh`

这是容器启动时执行的脚本，负责从 Git 仓库拉取代码、创建虚拟环境、安装依赖并启动指定的 Python 文件。脚本内容包含：

- 拉取最新的 Git 仓库代码
- 创建 Python 虚拟环境并安装依赖
- 切换到正确目录后执行指定的 Python 启动文件

### 3. `docker-compose.yml`

这是一个 Docker Compose 配置文件，定义了如何构建并运行容器。该文件中配置了 Git 仓库的 URL、启动文件、端口映射等环境变量。容器重启策略为
`always`，确保容器在崩溃后自动重启。

## 使用说明

### 构建镜像并运行容器

1. **构建镜像**：
   在项目根目录下运行以下命令构建 Docker 镜像：
   ```bash
   docker build -t xiaoqiangserver .
   ```

2. **运行容器**：
   使用 Docker Compose 启动服务：
   ```bash
   docker-compose up -d
   ```

   这将根据 `docker-compose.yml` 文件启动容器，并将 Git 仓库的 URL 以及其他必要配置传递给容器。

### 配置说明

- **REPO_URL**：Git 仓库的 URL，必须配置。
- **RUN_FILE**：启动的 Python 文件，默认为 `start.py`，可以根据项目需要修改。起始目录是`/app/git项目的名称`，是一个相对路径，例如
  `my_website/start.py`。
- **PULL_ON_RESTART**：是否在容器重启时拉取最新代码，默认为 `true`。
- **PORT**：容器内部的端口，默认是 `8000`。
- **PIP_MIRROR**：pip 镜像源，默认使用阿里云镜像源。

### 数据卷

- **volumes**：可以将宿主机的目录挂载到容器中，默认挂载 `./data` 到容器的 `/app/my_website/data` 目录。

### 保持容器活跃

- 配置了 `stdin_open: true` 和 `tty: true`，确保容器在后台持续运行，即使没有交互式操作。

## 示例

在 `docker-compose.yml` 中，你可以指定 Git 仓库地址、启动文件以及是否拉取最新代码。例如：

```yaml
environment:
  - REPO_URL=https://gitee.com/xiaoqiangclub/my_website.git
  - RUN_FILE=my_website/fastapi_view.py
  - PULL_ON_RESTART=true
  - PORT=8000
  - PIP_MIRROR=https://pypi.org/simple
```

## 常见问题

### 如何修改启动文件？

你可以通过设置 `RUN_FILE` 环境变量来指定启动文件。例如，如果你想启动 `my_website/fastapi_view.py`，可以在
`docker-compose.yml` 中这样配置：

```yaml
environment:
  - RUN_FILE=my_website/fastapi_view.py
```
### 如何修改启动命令？
参考文章 [docker run创建容器如何执行多条命令](https://xiaoqiangclub.blog.csdn.net/article/details/144048875)

### 如何查看容器日志？

你可以使用以下命令查看容器的日志输出：

```bash
docker logs my_website
```

### 容器停止后如何重新启动？

容器配置了 `restart: always`，当容器停止或崩溃时，会自动重启。

### 如果将git项目中的目录映射到宿主的目录？

以群晖为例，创建容器的时候不要映射，等容器启动成功后，再映射，否则容器会直接使用-v挂载目录中的文件启动项目。

## 结语

Git Auto Runner 简化了 Python 项目的容器化管理，自动化拉取代码、安装依赖并启动指定脚本，适用于需要频繁更新的项目部署。通过
Docker Compose 配置，可以轻松实现项目的容器化运行。

