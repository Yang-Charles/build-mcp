# LangChain v1.0 中间件机制

&gt; 把“手写上下文”变成“可组装架构”

---

## 1. 中间件要解决的问题
在用户输入到达模型之前，作为信息协调层完成统一处理：

- 规范化输入格式  
- 注入相关背景知识  
- 过滤敏感信息  
- 限制工具调用权限  

最终保证模型收到的始终是**经过精心组织的上下文**。

---

## 2. 后端视角：与 FastAPI 1:1 映射

| FastAPI 中间件 | LangChain 中间件 |
|----------------|------------------|
| 拦截 HTTP 请求 | 拦截 Agent 调用 |
| 身份认证、请求日志、CORS | 上下文管理、安全控制、工具调度、运行时监控 |

**执行流程完全一致**  
FastAPI：Request → Middleware Stack → Endpoint Handler → Response  
LangChain：User Input → Middleware Stack → AI Model → Response  

按注册顺序依次执行，功能扩展直观。

---

## 3. v1.0 之前的技术痛点

1. 缺少灵活的上下文切换机制  
2. 长对话 Token 超限，历史管理困难  
3. 工具调用权限无法细粒度控制  
4. 任何复杂需求都得写自定义代码，无统一抽象  

→ **中间件机制把上下文工程变成系统化实践**

---

## 4. 引入中间件后的收益

- 代码组织规范：独立模块，无逻辑耦合  
- 复用性提升：写完即可跨项目共享  
- 组合灵活：像搭积木一样拼装复杂功能  
- 测试调试简化：单测、定位都方便  
- 生产适配好：常见需求有现成模式  

&gt; 新增能力只需往列表里加一项，结构清晰。

---

## 5. v1.0 内置常用中间件

| 中间件 | 功能简述 | 处理规则 |
|--------|----------|----------|
| PIIMiddleware | 个人敏感信息过滤 | 邮箱脱敏，电话阻断 |
| SummarizationMiddleware | 长对话摘要 | Token 超阈值自动生成摘要 |
| HumanInTheLoopMiddleware | 关键操作人工审核 | 例：发送邮件需人类批准 |

---

## 6. 其他开箱即用能力

- Token 统计与预算控制  
- 响应缓存机制  
- 错误处理与重试逻辑  
- 自定义日志记录  

---

## 7. 快速拼装示例

```python
agent = Agent(
    llm=chat_model,
    tools=[search, send_email],
    middleware=[
        PIIMiddleware(),
        SummarizationMiddleware(token_threshold=2048),
        HumanInTheLoopMiddleware(action_regex=r"send.*email"),
        TokenBudgetMiddleware(max_tokens=4096, max_cost=0.05),
        LoggingMiddleware(),
    ]
)