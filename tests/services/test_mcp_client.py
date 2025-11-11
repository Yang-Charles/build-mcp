import pytest
import asyncio
import traceback
from datetime import timedelta
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamablehttp_client

# 编写客户端代码进行调试stdio协议的MCP服务
# @pytest.mark.asyncio
async def test_mcp_server():
    async with stdio_client(
            StdioServerParameters(command="uv", args=["run", "build_mcp"])
    ) as (read, write):
        print("启动服务端...")

        async with ClientSession(read, write) as session:
            await session.initialize()
            print("初始化完成")

            tools = await session.list_tools()
            print("可用工具：", tools)

            assert hasattr(tools, "tools")
            assert isinstance(tools.tools, list)
            assert any(tool.name == "locate_ip" for tool in tools.tools)

            result = await session.call_tool("locate_ip", {"ip": None})
            print("结果:", result.content[0].text)

# 编写客户端代码进行调试streamablehttp_client协议的MCP服务
# @pytest.mark.asyncio
async def test_streamable_http_main():
    # 测试 mcp 客户端的功能
    try:
        SERVER_URL = "http://127.0.0.1:8000/mcp"  # 与服务器路径保持一致
        # 1. 建立 Streamable-HTTP 长连接
        async with streamablehttp_client(SERVER_URL) as (read_stream, write_stream, _):
            # 2. 创建会话
            async with ClientSession(read_stream, write_stream) as session:
                # 3. 握手
                await session.initialize()

                # 4. 查看可用工具
                tools = await session.list_tools()
                print("可用工具:", [t.name for t in tools.tools])

                # 5. 调用工具示例（假设服务端注册了名为 get_time 的工具）
                res = await session.call_tool("locate_ip", {})
                print("工具返回 =>", res)

                list_prompts = await session.list_prompts()
                print("list_prompts:", list_prompts)

                list_resources = await session.list_resources()
                print("list_resources:", list_resources)
    except:
        print(f"traceback: {traceback.print_exc()}")


async def test_streamable_http_main_ok():
    # 项目中出现 tests_*.py / *_test.py 里的函数  PyCharm 默认把这类文件划进 Test Scope；
    # 只要函数名以 test_ 开头（或类以 Test 开头），就会被 Python Test Runner 识别,识别后自动标注为「可执行的测试用例」，于是左侧出现 ▶  Run Test
    await asyncio.sleep(0.1)
    print("test_streamable_http_main_ok")

async def streamable_http_main_fail():
    await asyncio.sleep(0.1)
    print("test_streamable_http_main_ok")