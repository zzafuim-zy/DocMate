"""Word文档处理器"""
from docx import Document
from typing import List, Dict, Any


class WordProcessor:
    """Word文档处理类"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, file_path: str) -> str:
        """从Word文件提取文本"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Word文档处理错误: {str(e)}")
    
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
        """处理Word文件并返回分块结果"""
        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        
        return [
            {
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "type": "word",
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]