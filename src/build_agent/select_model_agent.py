from dataclasses import dataclass
from typing import Callable
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import AgentMiddleware, ModelRequest
from langchain.agents.middleware.types import ModelResponse
from langchain.agents import create_agent
from langchain.agents.middleware import (
    PIIMiddleware,
    SummarizationMiddleware,
    HumanInTheLoopMiddleware
)

# First, define what you want to track about users
@dataclass
class Context:
    user_expertise: str = "beginner"  # Is user a beginner or expert?

from langchain.tools import tool, ToolRuntime

@tool
def advanced_search(city: str) -> str:
    """Get weather for a given city."""
    return f"It's advanced_search {city}!"

@tool
def data_analysis(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def simple_search(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

@tool
def basic_calculator(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# Create your custom middleware
class ExpertiseBasedToolMiddleware(AgentMiddleware):
    '''
    中间件实现了能力分级：
        先从运行时上下文读取用户的技术水平标识。
        如果是专家用户，分配更强的模型（gpt-5）和高级工具（advanced_search、data_analysis）。如果是初学者，使用轻量模型（gpt-5-nano）和基础工具（simple_search、basic_calculator）
    '''
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelResponse:

        # Check: Is this user a beginner or expert?
        user_level = request.runtime.context.user_expertise

        if user_level == "expert":
            # Experts get powerful AI and advanced tools
            model = ChatOpenAI(model="gpt-5")
            tools = [advanced_search, data_analysis]
        else:
            # Beginners get simpler AI and basic tools
            model = ChatOpenAI(model="gpt-5-nano")
            tools = [simple_search, basic_calculator]

        # Update what the AI sees
        request.model = model
        request.tools = tools

        # Send it forward to the AI
        return handler(request)


# Now use your custom middleware (just like the built-in ones!)
# 代码组织更规范。每个中间件都是独立模块，功能边界清晰，不会出现逻辑耦合的问题。
# 复用性大幅提升。写好的中间件可以在不同项目间共享，不用每次都重新实现。
# 组合灵活性很高。像搭积木一样组合不同的中间件，快速实现复杂功能。
# 测试和调试简化了。每个中间件可以单独测试，出问题也容易定位。
# 生产环境的适配性更好。常见的生产需求都有对应的模式，不需要从零开始摸索
# 每个中间件负责一个具体的功能，想添加新能力直接往列表里加就行，代码结构很清晰。
# 除了这几个以外，v1.0 还提供了其他常用中间件：
# PIIMiddleware 处理个人敏感信息，邮箱地址会被脱敏处理，电话号码直接阻断，确保隐私数据不会泄露给模型。
# SummarizationMiddleware 解决长对话的上下文管理问题。Token 数超过阈值后自动生成摘要，保持上下文简洁的同时不丢失关键信息。
# HumanInTheLoopMiddleware 在关键操作前加入人工审核。比如发送邮件这种操作，必须经过人类批准才能执行
# Token 统计和预算控制、响应缓存机制、错误处理和重试逻辑、自定义日志记录等
agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[simple_search, advanced_search, basic_calculator, data_analysis],
    middleware=[
        # Hide email addresses automatically (privacy protection)
        PIIMiddleware("email", strategy="redact"),

        # Block phone numbers completely (extra privacy)
        PIIMiddleware("phone_number", strategy="block"),

        # When conversation gets long, make a short summary
        # (like creating a highlight reel of a long movie)
        SummarizationMiddleware(
            model="claude-sonnet-4-5-20250929",
            max_tokens_before_summary=500
        ),

        # Before sending emails, ask a human "Is this okay?"
        # (like a safety check before hitting send)
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": {
                    "allowed_decisions": ["approve", "edit", "reject"]
                }
            }
        ),
        ExpertiseBasedToolMiddleware(),  # 自定义中间件
    ],  # Your custom middleware here!
    context_schema=Context
 )
