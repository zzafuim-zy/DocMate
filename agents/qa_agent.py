"""问答智能体 - AgentScope 1.0异步版本 + DashScope API"""
import asyncio
import os
from typing import List, Dict, Any, Optional, Union

from agentscope.agent import AgentBase
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.memory import InMemoryMemory
from agentscope.formatter import DashScopeChatFormatter

from utils.vector_store import VectorStore


class QAAgent(AgentBase):
    """问答智能体 - 基于AgentScope 1.0异步模式 + DashScope"""
    
    def __init__(
        self,
        name: str = "QAAgent",
        model: Optional[DashScopeChatModel] = None,
        vector_store: Optional[VectorStore] = None,
        **kwargs
    ):
        super().__init__()
        self.name = name

        # 初始化模型
        self.model = DashScopeChatModel(
            model_name="qwen-max",
            api_key=os.environ["DASHSCOPE_API_KEY"],
            stream=False,
            enable_thinking=False,
        )
        
        # 初始化格式化器
        self.formatter = DashScopeChatFormatter()
        
        # 初始化记忆
        self.memory = InMemoryMemory()
        
        # 初始化向量存储
        self.vector_store = vector_store or VectorStore()
        
        # 系统提示词
        self.sys_prompt = """你是一个智能文档问答助手。你的任务是基于用户提供的文档内容回答问题。

请遵循以下原则：
1. 仅基于提供的文档内容回答问题
2. 如果文档中没有相关信息，请明确说明
3. 回答要准确、简洁、有条理
4. 如果需要，可以引用具体的文档片段
5. 对于复杂问题，可以分步骤回答
6. 使用中文回答问题

当前可用的文档内容将在每次问答时提供给你。"""
    
    async def search_relevant_documents_async(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """异步搜索相关文档"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.vector_store.search, query, n_results)
    
    def search_relevant_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """同步搜索相关文档的包装方法"""
        return asyncio.run(self.search_relevant_documents_async(query, n_results))
    
    async def generate_answer_async(self, question: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """异步使用DashScope API基于相关文档生成答案"""
        if not relevant_docs:
            return "抱歉，我在文档中没有找到与您问题相关的信息。请确保已经上传了相关文档，或者尝试用不同的方式提问。"
        
        # 构建上下文
        context = "基于以下文档内容：\n\n"
        for i, doc in enumerate(relevant_docs, 1):
            source = doc["metadata"].get("source", "未知来源")
            content = doc["content"][:800] + "..." if len(doc["content"]) > 800 else doc["content"]
            context += f"文档片段 {i} (来源: {source}):\n{content}\n\n"
        
        # 构建消息
        messages = [
            Msg(name="system", content=self.sys_prompt, role="system"),
            Msg(name="user", content=f"{context}\n用户问题: {question}\n\n请基于上述文档内容回答用户的问题。如果文档中没有足够的信息来回答问题，请明确说明。", role="user")
        ]
        
        try:
            # 格式化消息
            formatted_messages = await self.formatter.format(messages)

            # 调用模型 (DashScopeChatModel 使用 __call__ 方法)
            response = await self.model(formatted_messages)

            # ChatResponse 是字典类型，尝试不同的键
            if response:
                # 尝试常见的响应键
                if 'text' in response:
                    return response['text']
                elif 'content' in response:
                    return response['content']
                elif 'message' in response:
                    return response['message']
                elif 'choices' in response and response['choices']:
                    return response['choices'][0]['message']['content']
                else:
                    # 如果响应为空，返回所有键用于调试
                    return f"响应为空或格式未知。可用键: {list(response.keys())}"
            else:
                return "模型返回空响应，请检查API密钥和网络连接"
                
        except Exception as e:
            return f"调用DashScope API时出现错误: {str(e)}"
    
    def generate_answer(self, question: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """同步生成答案的包装方法"""
        return asyncio.run(self.generate_answer_async(question, relevant_docs))
    
    async def __call__(self, x: Union[Msg, None] = None) -> Msg:
        """异步处理问题并回复答案"""
        if x is None:
            return Msg(
                name=self.name,
                content="我是智能问答助手，可以基于已处理的文档回答您的问题。请提出您的问题。",
                role="assistant"
            )
        
        # 添加到记忆
        await self.memory.add(x)
        
        question = x.content
        
        # 检查是否是问候或帮助请求
        if any(keyword in question.lower() for keyword in ["你好", "帮助", "help", "功能"]):
            response_msg = Msg(
                name=self.name,
                content="您好！我是智能文档问答助手。我可以基于已上传和处理的文档回答您的问题。请直接提出您想了解的问题，我会在文档中搜索相关信息并为您解答。",
                role="assistant"
            )
        else:
            try:
                # 异步搜索相关文档,可以在(question，n_results=10)自定义同时处理文件的数量
                relevant_docs = await self.search_relevant_documents_async(question)
                
                # 异步生成答案
                answer = await self.generate_answer_async(question, relevant_docs)
                
                # 添加来源信息
                if relevant_docs:
                    sources = set()
                    for doc in relevant_docs:
                        source = doc["metadata"].get("source", "未知来源")
                        sources.add(source)  # 确保 source 是完整的文件路径字符串

                    source_info = "\n\n📚 参考来源：\n" + "\n".join(f"• {source}" for source in sources)
                    if answer:
                        # 确保 answer 是字符串类型再进行拼接
                        if isinstance(answer, str):
                            answer += source_info
                        else:
                            # 如果 answer 不是字符串，先转换为字符串
                            answer = str(answer) + source_info
                    else:
                        answer = "生成回答时出现错误" + source_info
                
                response_msg = Msg(name=self.name, content=answer, role="assistant")
                
            except Exception as e:
                response_msg = Msg(
                    name=self.name,
                    content=f"处理问题时出现错误：{str(e)}。请稍后重试或联系管理员。",
                    role="assistant"
                )
        
        # 添加回复到记忆
        await self.memory.add(response_msg)
        
        return response_msg
    
    def reply(self, x: Union[Msg, None] = None) -> Msg:
        try:
            return asyncio.run(self.__call__(x))
        except RuntimeError as e:
            if "cannot be called from a running event loop" in str(e) or "This event loop is already running" in str(e):
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    return asyncio.run(self.__call__(x))
                except ImportError:
                    # 备用方案：创建新的事件循环
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        return loop.run_until_complete(self.__call__(x))
                    finally:
                        loop.close()
            else:
                raise
    
    async def get_conversation_summary_async(self, messages: List[Msg]) -> str:
        """异步生成对话摘要"""
        if not messages:
            return "暂无对话记录"
        
        conversation = "\n".join([f"{msg.name}: {msg.content}" for msg in messages[-10:]])  # 最近10条消息
        
        summary_messages = [
            Msg(name="system", content="请为以下对话生成一个简洁的摘要，包括主要讨论的话题、关键问题和答案、重要结论。请用中文回答，保持简洁明了。", role="system"),
            Msg(name="user", content=f"请为以下对话生成摘要：\n\n{conversation}", role="user")
        ]
        
        try:
            # 格式化消息
            formatted_messages = await self.formatter.format(summary_messages)

            # 调用模型 (DashScopeChatModel 使用 __call__ 方法)
            response = await self.model(formatted_messages)

            # ChatResponse 是字典类型，尝试不同的键
            if response:
                # 尝试常见的响应键
                if 'text' in response:
                    return response['text']
                elif 'content' in response:
                    return response['content']
                elif 'message' in response:
                    return response['message']
                elif 'choices' in response and response['choices']:
                    return response['choices'][0]['message']['content']
                else:
                    # 如果响应为空，返回所有键用于调试
                    return f"响应为空或格式未知。可用键: {list(response.keys())}"
            else:
                return "模型返回空响应，请检查API密钥和网络连接"

                
        except Exception as e:
            return f"生成摘要时出现错误：{str(e)}"
    
    def get_conversation_summary(self, messages: List[Msg]) -> str:
        """同步生成对话摘要的包装方法"""
        return asyncio.run(self.get_conversation_summary_async(messages))