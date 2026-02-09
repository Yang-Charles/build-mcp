import os
import logging
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent
from dotenv import load_dotenv
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend, FilesystemBackend
from langgraph.store.memory import InMemoryStore
from langchain_community.chat_models import ChatZhipuAI
from pathlib import Path
from llm_chat import qwen_model
import asyncio
from langchain_core.messages import HumanMessage

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def internet_search(
        query: str,
        max_results: int = 5,
        topic: Literal["general", "news", "finance"] = "general",
        include_raw_content: bool = False,
):
    """Run a web search"""
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    logging.info(f"internet_search query: {query}")
    search_result = tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )
    return search_result





def make_backend(runtime):
    '''
    CompositeBackend (路由器),
    文件系统后端:
    StateBackend：Agent的State作为存储，仅在本次线程有效。可用来在一次对话中卸载临时的中间结果，优化上下文空间。
    FileSystemBackend：本地文件系统目录作为存储，可长期保存。比如保存AI生成的创作文档或代码文件。
    StoreBackend：Store是LangGraph实现跨线程持久记忆的机制（可以是Redis、Postgres等实现）。你可以配置Store作为虚拟文件系统。
    CompositeBackend：复合后端。比如默认使用StateBackend；但存储到"/memories/"的数据则使用StoreBackend以实现跨线程持久。

    复合的CompositeBackend：默认使用本地文件系统做后端；但如果路由路径是/memories/，
    则使用LangGraph Store作为后端（默认类型InMemoryStore)。

    实际应用中，该功能可以用来实现诸如用户偏好记忆、知识积累、研究结果保存，以在不同会话中共享
    :param runtime:
    :return:
    '''
    base_dir = Path(__file__).parent / "local_file_path"
    return CompositeBackend(
        default=FilesystemBackend(root_dir=str(base_dir), virtual_mode=True),
        routes={
            "/memories/": StoreBackend(runtime)  # 复合后端。比如默认使用StateBackend；但存储到"/memories/"的数据则使用StoreBackend以实现跨线程持久
        }
    )

def create_agent():

    # === 系统指令 ===
    SYSTEM_PROMPT = """你是一个助手。
    你的任务是帮助用户分析天气信息，使用 search 工具搜索相关信息。
    你有一个旅游建议师可以协助你做旅游攻略
    工作流程：
    1. 理解用户要分析的天气信息 是哪个城市
    2. 使用 search 搜索该城市的相关信息
    3. 基于搜索结果和旅游建议师的建议，提供清晰的结论
    注意：
    - 把结论保存成在路径为 /consultion 下面的Markdown格式文件
    - 把搜索信息保存到/memories/search_info.md中，方便下次调用
    """
    main_tools = [
        internet_search,  # 通用网络搜索工具
    ]

    travel_advice = {
        "name": "旅游建议师",
        "description": "根据天气情况，给出适合旅游的建议",
        "system_prompt": "你是一个旅游建议大师，能够根据城市的天气，给出对应的旅游攻略",
        "tools": [],
        "model": qwen_model(model="qwen-max")
    }

    store = InMemoryStore()

    agent = create_deep_agent(
        model=qwen_model(model="qwen-max"),
        tools=main_tools,
        backend=make_backend,  # Optional backend for file storage and execution
        system_prompt=SYSTEM_PROMPT,
        subagents=[travel_advice],
        debug=True,
        store=store  # 传入 store 实例
    ).with_config({"recursion_limit": 1000})
    return agent

async def ok_agent():
    try:
        # 运行 agent - 使用正确的消息格式
        #  tool_calls=[{'name': 'write_todos', 'args': {'todos': [
        #  {'content': '搜索青岛的天气信息', 'status': 'pending'},
        #  {'content': '基于天气信息，使用旅游建议师做旅行计划', 'status': 'pending'},
        #  {'content': '将搜索到的信息保存到/memories/search_info.md中', 'status': 'pending'},
        #  {'content': '将旅行计划以Markdown格式保存到/consultation/青岛旅行计划.md中', 'status': 'pending'}]}
        # 触发DeepAgent的第一个特性：任务规划
        # 在执行前先列步骤、做计划，然后逐一跟踪执行；并在必要时做调整
        # DeepAgents中的任务规划能力是通过一个内置工具 write_todos 来实现的。
        # 它会在以下条件下触发：任务目标比较复杂，特别是涉及较多的步骤用户明确提示要求LLM先规划执行每完成一个步骤，需要修订任务清单 - 标记状态或调整任务
        query = ("首先搜索深圳 香港 澳门 珠海天气 ；然后做一个5天旅行计划 囊括这个4城市的核心景区景点 以及推荐的美食，其中深圳1天， 香港2天（1天主要行程是迪士尼），澳门1天 珠海1天； "
                 "要求：先规划执行每完成一个步骤，需要修订任务清单 - 标记状态或调整任务")
        agent = create_agent()
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=query)]
        })
        print(f"result: {result}")
        # 获取最后一条消息
        if result and "messages" in result:
            last_message = result["messages"][-1]
            if hasattr(last_message, "content"):
                print("分析结果：", last_message.content)
            else:
                print("分析结果2：", last_message)
        else:
            print("未获取到分析结果")

    except Exception as e:
        logging.error(f"出错: {str(e)}", exc_info=True)


# === 测试运行 ===
if __name__ == "__main__":
    print('file', Path(__file__).parent)
    # 运行异步测试
    asyncio.run(ok_agent())