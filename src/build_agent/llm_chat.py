from langchain_community.chat_models.tongyi import ChatTongyi
from typing import List, Optional
from langchain_core.messages import BaseMessage

class DashScopeChat(ChatTongyi):
    def _generate(self, messages: List[BaseMessage], **kwargs):
        # 只保留后端认识的两个值
        tc = kwargs.get("tool_choice")
        if tc is not None and not isinstance(tc, str):
            kwargs["tool_choice"] = "auto"
        return super()._generate(messages, **kwargs)

# model = DashScopeChat(model="qwen-max", temperature=0)
