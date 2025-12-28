"""文本文件处理器"""
from typing import List, Dict, Any
import chardet


class TextProcessor:
    """文本文件处理类"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, file_path: str) -> str:
        """从文本文件提取内容"""
        try:
            # 自动检测编码
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                encoding = chardet.detect(raw_data)['encoding']
            
            # 使用检测到的编码读取文件
            with open(file_path, 'r', encoding=encoding or 'utf-8') as file:
                return file.read()
        except Exception as e:
            # 如果自动检测失败，尝试常见编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        return file.read()
                except:
                    continue
            raise Exception(f"文本文件处理错误: {str(e)}")
    
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
        """处理文本文件并返回分块结果"""
        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        
        return [
            {
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "type": "text",
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]