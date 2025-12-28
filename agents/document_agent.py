"""文档处理智能体 - 简化版本，仅支持本地文件"""
import asyncio
import os
from typing import List, Dict, Any, Optional, Union

from agentscope.agent import AgentBase
from agentscope.message import Msg
from agentscope.model import DashScopeChatModel
from agentscope.memory import InMemoryMemory

from processors.pdf_processor import PDFProcessor
from processors.word_processor import WordProcessor
from processors.text_processor import TextProcessor
from processors.markdown_processor import MarkdownProcessor
from processors.image_processor import ImageProcessor
from utils.vector_store import VectorStore


class DocumentAgent(AgentBase):
    """文档处理智能体 - 仅支持本地文件处理"""
    
    def __init__(
        self,
        name: str = "DocumentAgent",
        model: Optional[DashScopeChatModel] = None,
        vector_store: Optional[VectorStore] = None,
        **kwargs
    ):
        super().__init__()
        self.name = name

        # 初始化模型
        self.model = model
        
        # 初始化记忆
        self.memory = InMemoryMemory()
        
        # 初始化向量存储
        self.vector_store = vector_store or VectorStore()
        
        # 初始化文档处理器（移除网页处理器）
        self.processors = {
            'pdf': PDFProcessor(),
            'word': WordProcessor(),
            'text': TextProcessor(),
            'markdown': MarkdownProcessor(),
            'image': ImageProcessor()
        }
        
        # 支持的文件扩展名
        self.supported_extensions = {
            '.pdf': 'pdf',
            '.docx': 'word',
            '.doc': 'word',
            '.txt': 'text',
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.tiff': 'image',
            '.bmp': 'image',
            '.gif': 'image'
        }
    
    async def process_document_async(self, file_path: str) -> Dict[str, Any]:
        """异步处理单个文档"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"文件不存在: {file_path}"
                }
            
            # 获取文件扩展名
            _, ext = os.path.splitext(file_path.lower())
            
            if ext not in self.supported_extensions:
                return {
                    "success": False,
                    "error": f"不支持的文件类型: {ext}",
                    "supported_types": list(self.supported_extensions.keys())
                }
            
            # 选择对应的处理器
            processor_type = self.supported_extensions[ext]
            processor = self.processors[processor_type]
            
            # 异步处理文档
            loop = asyncio.get_event_loop()
            chunks = await loop.run_in_executor(None, processor.process_file, file_path)
            
            # 存储到向量数据库
            texts = [chunk["content"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            
            await loop.run_in_executor(None, self.vector_store.add_documents, texts, metadatas)
            
            return {
                "success": True,
                "file_path": file_path,
                "processor_type": processor_type,
                "chunks_count": len(chunks),
                "message": f"成功处理文档 {file_path}，生成 {len(chunks)} 个文本块"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """同步处理文档的包装方法"""
        return asyncio.run(self.process_document_async(file_path))
    
    async def batch_process_documents_async(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """异步批量处理文档"""
        tasks = [self.process_document_async(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks)
        return results
    
    def batch_process_documents(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """同步批量处理文档的包装方法"""
        return asyncio.run(self.batch_process_documents_async(file_paths))
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """获取向量存储信息"""
        return self.vector_store.get_collection_info()
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return list(self.supported_extensions.keys())
    
    async def __call__(self, x: Union[Msg, None] = None) -> Msg:
        """异步处理消息并回复"""
        if x is None:
            return Msg(
                name=self.name,
                content="我是文档处理智能体，可以帮您处理本地文档文件。支持的格式：" + ", ".join(self.get_supported_formats()),
                role="assistant"
            )
        
        # 添加到记忆
        await self.memory.add(x)
        
        content = x.content
        
        # 解析用户请求
        if "处理文档" in content or "上传文档" in content:
            response_msg = Msg(
                name=self.name,
                content=f"请提供要处理的文档文件路径。我支持以下格式：{', '.join(self.get_supported_formats())}",
                role="assistant"
            )
        elif "状态" in content or "信息" in content:
            info = self.get_vector_store_info()
            response_msg = Msg(
                name=self.name,
                content=f"当前向量存储状态：已存储 {info['count']} 个文档块",
                role="assistant"
            )
        else:
            response_msg = Msg(
                name=self.name,
                content="我可以帮您处理本地文档文件。请提供文件路径，或者询问当前的存储状态。",
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
                # 安装并使用 nest_asyncio
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                    return asyncio.run(self.__call__(x))
                except ImportError:
                    # 如果没有 nest_asyncio，使用备用方案
                    return self._sync_fallback(x)
            else:
                raise