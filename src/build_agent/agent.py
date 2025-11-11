from pydantic import BaseModel, Field
from langchain.agents import create_agent
from build_agent.llm_chat import DashScopeChat
from langchain.agents.structured_output import ToolStrategy
from build_agent.build_tools import Context, get_user_location, get_weather_for_location
import os
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model

# 加载环境变量
load_dotenv()

# 0. 配置 API-Key
os.environ["DASHSCOPE_API_KEY"] = os.getenv("DASHSCOPE_API_KEY")


class ResponseFormat(BaseModel):
    punny_response: str
    weather_conditions: str | None = None


# Add memory
def build_agent():
    checkpointer = InMemorySaver()

    # 初始化模型
    # model = init_chat_model(
    #     "claude-sonnet-4-5-20250929",
    #     temperature=0.5,
    #     timeout=10,
    #     max_tokens=1000
    # )

    # model = ChatTongyi(model="qwen-max", temperature=0.5, streaming=True)
    model = DashScopeChat(model="qwen-max", temperature=0.5, streaming=True)

    # PROMPT
    SYSTEM_PROMPT = """You are an expert weather forecaster, who speaks in puns.
    
    You have access to two tools:
    
    - get_weather_for_location: use this to get the weather for a specific location
    - get_user_location: use this to get the user's location
    
    If a user asks you for the weather, make sure you know the location. If you can tell from the question that they mean wherever they are, use the get_user_location tool to find their location.
    """

    tools = [get_user_location, get_weather_for_location]

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=tools,
        context_schema=Context,  #
        response_format=ResponseFormat,
        checkpointer=checkpointer
    )

    # `thread_id` is a unique identifier for a given conversation.
    config = {"configurable": {"thread_id": "1"}}

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "what is the weather outside?"}]},
        config=config,
        context=Context(user_id="1")  # Runtime 提供的动态上下文，例如 user_id, session_id 等运行时注入的变量。
    )

    print(response['structured_response'])
    # ResponseFormat(
    #     punny_response="Florida is still having a 'sun-derful' day! The sunshine is playing 'ray-dio' hits all day long! I'd say it's the perfect weather for some 'solar-bration'! If you were hoping for rain, I'm afraid that idea is all 'washed up' - the forecast remains 'clear-ly' brilliant!",
    #     weather_conditions="It's always sunny in Florida!"
    # )


if __name__ == '__main__':
    build_agent()