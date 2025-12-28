"""图片OCR处理器"""
from PIL import Image
import pytesseract
from typing import List, Dict, Any
import os


class ImageProcessor:
    """图片OCR处理类"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, tesseract_cmd: str = None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 设置tesseract路径（如果提供）
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_text(self, file_path: str, lang: str = 'chi_sim+eng') -> str:
        """从图片文件提取文本"""
        try:
            # 打开图片
            image = Image.open(file_path)
            
            # 使用OCR提取文本
            text = pytesseract.image_to_string(image, lang=lang)
            
            return text.strip()
        except Exception as e:
            raise Exception(f"图片OCR处理错误: {str(e)}")
    
    def preprocess_image(self, image_path: str) -> Image.Image:
        """预处理图片以提高OCR准确性"""
        try:
            image = Image.open(image_path)
            
            # 转换为灰度图
            if image.mode != 'L':
                image = image.convert('L')
            
            # 可以添加更多预处理步骤，如降噪、二值化等
            
            return image
        except Exception as e:
            raise Exception(f"图片预处理错误: {str(e)}")
    
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
    
    def process_file(self, file_path: str, lang: str = 'chi_sim+eng') -> List[Dict[str, Any]]:
        """处理图片文件并返回OCR分块结果"""
        text = self.extract_text(file_path, lang)
        chunks = self.chunk_text(text)
        
        return [
            {
                "content": chunk,
                "metadata": {
                    "source": file_path,
                    "type": "image_ocr",
                    "chunk_index": i,
                    "ocr_language": lang
                }
            }
            for i, chunk in enumerate(chunks)
        ]
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的图片格式"""
        return ['.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif']