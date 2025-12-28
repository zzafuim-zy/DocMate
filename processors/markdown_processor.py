"""Markdown文档处理器"""
import markdown
from typing import List, Dict, Any
import re


class MarkdownProcessor:
    """Markdown文档处理类"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.md = markdown.Markdown(extensions=['meta', 'toc'])
    
    def extract_text(self, file_path: str) -> str:
        """从Markdown文件提取文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 转换为HTML然后提取纯文本
            html = self.md.convert(content)
            # 移除HTML标签
            text = re.sub(r'<[^>]+>', '', html)
            # 清理多余的空白字符
            text = re.sub(r'\s+', ' ', text).strip()
            
            return text
        except Exception as e:
            raise Exception(f"Markdown文档处理错误: {str(e)}")
    
    def extract_sections(self, file_path: str) -> List[Dict[str, str]]:
        """按章节提取Markdown内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            sections = []
            current_section = {"title": "", "content": ""}
            
            for line in content.split('\n'):
                if line.startswith('#'):
                    # 如果当前章节有内容，保存它
                    if current_section["content"].strip():
                        sections.append(current_section.copy())
                    
                    # 开始新章节
                    current_section = {
                        "title": line.strip(),
                        "content": ""
                    }
                else:
                    current_section["content"] += line + "\n"
            
            # 添加最后一个章节
            if current_section["content"].strip():
                sections.append(current_section)
            
            return sections
        except Exception as e:
            raise Exception(f"Markdown章节提取错误: {str(e)}")
    
    def chunk_text(self, text: str) -> List[str]:
        """将文本分块"""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            if end > text_length:
                end = text_length
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            if end == text_length:
                break
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def process_file(self, file_path: str) -> List[Dict[str, Any]]:
        """处理Markdown文件并返回分块结果"""
        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        
        return [
            {
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "type": "markdown",
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]