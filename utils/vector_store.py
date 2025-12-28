"""向量存储工具类"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid


class VectorStore:
    """向量存储管理类"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "documents"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]] = None, ids: List[str] = None):
        """添加文档到向量存储"""
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if metadatas is None:
            metadatas = [{"source": "unknown"} for _ in texts]
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """搜索相关文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "id": doc_id
            }
            for doc, meta, doc_id in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["ids"][0]
            )
        ]
    
    def delete_collection(self):
        """删除集合"""
        self.client.delete_collection(name=self.collection_name)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """获取集合信息"""
        return {
            "count": self.collection.count(),
            "name": self.collection_name
        }