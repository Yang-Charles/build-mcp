from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
# 加载环境变量
load_dotenv()

def qwen_model(model="qwen-max"):
    model = ChatOpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),  # 阿里云颁发的 key
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model=model,  # qwen-plus / qwen-turbo 均可
        temperature=0.5,
        max_retries=2
    )
    return model
