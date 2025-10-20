## 如何从零开始构建一个高德地图的MCP服务，涵盖了以下内容：

### MCP服务的基本概念和配置
### 如何使用高德地图API进行IP定位和周边搜索
### 如何编写MCP服务的核心功能，包括配置管理、日志系统和高德地图SDK
### 如何编写MCP服务的主程序和入口
### 如何调试MCP服务，包括使用Inspector和编写测试代码
### 如何使用Makefile管理项目命令
### 如何配置MCP客户端连接到我们的服务



## 配置开发环境

**⚠ 请务必根据自己的操作系统调整命令，powershell 和 bash 的命令语法有所不同。**

作者使用的是windows+git终端。
本教程前半段与官方基本无异，可查考官方文档中[server开发示例](https://modelcontextprotocol.io/quickstart/server)。

### 安装UV

```shell
# Linux or macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```shell
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 创建虚拟环境初始化项目

```shell
# 使用UV创建并进入项目目录
uv init build-mcp
cd build-mcp

# 创建虚拟环境
uv venv
source .venv/Scripts/activate

# 安装相关依赖
uv add mcp[cli] httpx pytest
```
在 `src/build_mcp/config.yaml` 文件中添加以下内容：

```yaml
# 高德地图API配置
api_key: test
# 高德地图API的基础URL
base_url: https://restapi.amap.com
# 代理设置
proxy: 
# 日志等级
log_level: INFO
# 接口重试次数
max_retries: 5
# 接口重试间隔时间（秒）
retry_delay: 1
# 指数退避因子
backoff_factor: 2
# 日志文件路径
log_dir: /var/log/build_mcp
```

⚠ `config.yaml` 文件需要放在 `src/build_mcp/` 目录下，这样在加载配置时可以正确找到。

### 安装代码

⚠ 首次安装代码时需要使用 `pip install -e .` 命令，这样可以将当前目录作为一个可编辑的包安装到虚拟环境中。这样在开发过程中对代码的修改会立即生效，无需重新安装。

```shell
uv pip install -e .
```

### 2.使用Inspector进行测试
Inspector是官方提供的一个MCP服务调试工具，可以通过它来启动一个本地web界面，在界面中可以直接调用MCP服务的工具。
相对更加直观和易用，比较推荐这种方式，详情可以查看[官方文档](https://modelcontextprotocol.io/docs/tools/inspector)。

```shell
# 使用Inspector调试stdio协议的MCP服务
API_KEY=你的KEY mcp dev src/build_mcp/__init__.py
```

## 如何使用这个MCP服务？
首先你得拥有一个MCP客户端，目前市场上各种类型得MCP客户端层出不穷，至于用什么全凭你的爱好了。

这里有一份非常详细的MCP客户端使用攻略，是github上一个非常棒的项目：[MCP客户端使用攻略](https://github.com/yzfly/Awesome-MCP-ZH)

选择一个客户端下载安装，然后我们对我们开发的服务进行配置。

### 配置Stdio协议的MCP服务

```shell
{
    "mcpServers": {
        "build_mcp": {
            "command": "uv",
            "args": [
                "run",
                "-m"
                "build_mcp"
            ],
            "env": {
                "API_KEY": "你的高德API Key"
            }
        }
    }
}
```
⚠ 要注意本地UV环境，如果安装了多个UV可能会导致环境混乱，这是开发过程中比较头疼的一点，要自己注意。

### 配置Streamable-HTTP协议的MCP服务

#### 启动项目
```shell
make streamable-http
```

```shell
$ make streamable-http
Starting MCP service with streamable-http protocol...
uv run build_mcp streamable-http

INFO: 🚀 Starting MCP server with transport type: streamable-http
INFO:     Started server process [6064]
INFO:     Waiting for application startup.
INFO:    StreamableHTTP session manager started                                                                                                                                     streamable_http_manager.py:109
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

```
启动成功后会在8000端口启动一个HTTP服务。


#### 客户端配置
```shell
{
    "mcpServers": {
        "build_mcp_http": {
            "url": "http://localhost:8000/mcp"
        }
    }
}
```