"""PDF文档处理器"""
import PyPDF2
from typing import List, Dict, Any
import io


class PDFProcessor:
    """PDF文档处理类"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, file_path: str) -> str:
        """从PDF文件提取文本"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"PDF处理错误: {str(e)}")
    
    def extract_text_from_bytes(self, file_bytes: bytes) -> str:
        """从PDF字节流提取文本"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF字节流处理错误: {str(e)}")
    
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
        """处理PDF文件并返回分块结果"""
        text = self.extract_text(file_path)
        chunks = self.chunk_text(text)
        
        return [
            {
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "type": "pdf",
                    "chunk_index": i
                }
            }
            for i, chunk in enumerate(chunks)
        ]