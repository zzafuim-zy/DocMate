#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的文档问答系统 - 仅支持本地文件处理
使用方法：python simple_document_qa.py
"""

import asyncio
import os
import yaml
from typing import Dict, Any, List

from agentscope.model import DashScopeChatModel
from agentscope.message import Msg

from agents.document_agent import DocumentAgent
from agents.qa_agent import QAAgent
from utils.vector_store import VectorStore


class SimpleDocumentQA:
    """简单的文档问答系统"""
    
    def __init__(self, config_path: str = "config\\config.yaml"):
        """初始化系统"""
        self.config = self.load_config(config_path)
        self.vector_store = VectorStore()
        self.document_agent = None
        self.qa_agent = None
        
        # 初始化智能体
        self.init_agents()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"❌ 加载配置文件失败: {str(e)}")
            return {}
    
    def init_agents(self):
        """初始化智能体"""
        try:

            # 1. 检查API密钥（现在是从环境变量解析后的值）
            api_key = os.environ["DASHSCOPE_API_KEY"]

            # 2. 验证API密钥
            if not api_key or api_key.strip() == "":
                print("❌ 错误: API密钥为空")
                print("   请设置环境变量 DASHSCOPE_API_KEY")
                print("   Windows: set DASHSCOPE_API_KEY=sk-xxx")
                print("   Linux/Mac: export DASHSCOPE_API_KEY=sk-xxx")
                print("   💡 获取API密钥: https://dashscope.console.aliyun.com/")
                return False

            # 3. 检查是否为环境变量占位符（没有被替换）
            if api_key.startswith("${") or api_key.startswith("$"):
                print("❌ 错误: 环境变量未被正确替换")
                print(f"   当前值: {api_key}")
                print("   请确保设置了环境变量 DASHSCOPE_API_KEY")
                return False

            # 4. 检查密钥格式
            if not api_key.startswith("sk-"):
                print("❌ 错误: API密钥格式不正确")
                print("   DashScope密钥应以 'sk-' 开头")
                print(f"   当前密钥: {api_key[:20]}...")
                return False
            
            # 设置环境变量，为了兼容性
            #os.environ["DASHSCOPE_API_KEY"] = api_key
            
            # 创建模型
            model = DashScopeChatModel(
                model_name=self.config["model"]["model_name"],
                api_key=api_key,
                stream=False,
                enable_thinking=False,
            )
            
            # 创建智能体
            self.document_agent = DocumentAgent(
                name="DocumentAgent",
                model=model,
                vector_store=self.vector_store
            )
            
            self.qa_agent = QAAgent(
                name="QAAgent",
                model=model,
                vector_store=self.vector_store
            )
            
            print(f"✅ 系统初始化成功 - 模型: {self.config['model']['model_name']}")
            return True
            
        except Exception as e:
            print(f"❌ 系统初始化失败: {str(e)}")
            return False
    
    def process_file(self, file_path: str) -> bool:
        """处理单个文件"""
        if not self.document_agent:
            print("❌ 系统未初始化")
            return False
        
        print(f"🔄 正在处理文件: {file_path}")
        
        try:
            result = self.document_agent.process_document(file_path)
            
            if result["success"]:
                print(f"✅ {result['message']}")
                return True
            else:
                print(f"❌ 处理失败: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ 处理异常: {str(e)}")
            return False
    
    def process_files(self, file_paths: List[str]) -> int:
        """批量处理文件"""
        if not self.document_agent:
            print("❌ 系统未初始化")
            return 0
        
        print(f"🔄 正在批量处理 {len(file_paths)} 个文件...")
        
        try:
            results = self.document_agent.batch_process_documents(file_paths)
            
            success_count = 0
            for i, result in enumerate(results):
                if result["success"]:
                    print(f"✅ 文件 {i+1}: {result['message']}")
                    success_count += 1
                else:
                    print(f"❌ 文件 {i+1}: {result['error']}")
            
            print(f"📊 批量处理完成: {success_count}/{len(results)} 个文件成功")
            return success_count
            
        except Exception as e:
            print(f"❌ 批量处理异常: {str(e)}")
            return 0
    
    def ask_question(self, question: str) -> str:
        """提问并获取答案"""
        if not self.qa_agent:
            return "❌ 系统未初始化"

        try:
            user_msg = Msg(name="user", content=question, role="user")
            # 直接使用 asyncio.run() 调用异步的 __call__ 方法
            response = asyncio.run(self.qa_agent(user_msg))
            return response.content

        except Exception as e:
            return f"❌ 问答异常: {str(e)}"
    
    def get_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        if not self.document_agent:
            return {"error": "系统未初始化"}
        
        return self.document_agent.get_vector_store_info()
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        if not self.document_agent:
            return []
        
        return self.document_agent.get_supported_formats()
    
    def clear_storage(self):
        """清空存储"""
        try:
            self.vector_store.delete_collection()
            self.vector_store = VectorStore()  # 重新创建
            print("✅ 存储已清空")
        except Exception as e:
            print(f"❌ 清空存储失败: {str(e)}")


def main():
    """主程序"""
    print("📚 简单文档问答系统")
    print("=" * 50)
    
    # 初始化系统
    qa_system = SimpleDocumentQA()
    
    if not qa_system.document_agent:
        print("❌ 系统初始化失败，程序退出")
        return
    
    print(f"\n📋 支持的文件格式: {', '.join(qa_system.get_supported_formats())}")
    
    while True:
        print("\n" + "=" * 50)
        print("请选择操作:")
        print("1. 处理单个文件")
        print("2. 批量处理文件")
        print("3. 问答对话")
        print("4. 查看系统状态")
        print("5. 清空存储")
        print("6. 退出")
        
        choice = input("\n请输入选项 (1-6): ").strip()
        
        if choice == "1":
            file_path = input("请输入文件路径: ").strip()
            if file_path:
                qa_system.process_file(file_path)
        
        elif choice == "2":
            file_paths_input = input("请输入文件路径 (用逗号分隔): ").strip()
            if file_paths_input:
                file_paths = [path.strip() for path in file_paths_input.split(',')]
                # 过滤存在的文件
                existing_files = [path for path in file_paths if os.path.exists(path)]
                if existing_files:
                    qa_system.process_files(existing_files)
                else:
                    print("❌ 没有找到有效的文件")
        
        elif choice == "3":
            print("\n💬 进入问答模式 (输入 'quit' 退出)")
            while True:
                question = input("\n🤔 您的问题: ").strip()
                if question.lower() == 'quit':
                    break
                
                if question:
                    print("🤖 正在思考...")
                    answer = qa_system.ask_question(question)
                    print(f"\n📝 回答:\n{answer}")
        
        elif choice == "4":
            status = qa_system.get_status()
            if "error" in status:
                print(f"❌ {status['error']}")
            else:
                print(f"📊 已存储文档块数量: {status['count']}")
        
        elif choice == "5":
            confirm = input("确认清空所有存储数据? (y/N): ").strip().lower()
            if confirm == 'y':
                qa_system.clear_storage()
        
        elif choice == "6":
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选项，请重新选择")


def demo_usage():
    """演示用法"""
    print("📚 文档问答系统演示")
    print("=" * 30)
    
    # 初始化系统
    qa_system = SimpleDocumentQA()
    
    if not qa_system.document_agent:
        print("❌ 系统初始化失败")
        return
    
    # 演示处理文件（需要实际文件路径）
    print("\n📝 演示用法:")
    print("1. 处理单个文件:")
    print("   qa_system.process_file('path/to/your/document.pdf')")
    
    print("\n2. 批量处理文件:")
    print("   qa_system.process_files(['file1.txt', 'file2.pdf', 'file3.docx'])")
    
    print("\n3. 问答:")
    print("   answer = qa_system.ask_question('文档的主要内容是什么？')")
    print("   print(answer)")
    
    print("\n4. 查看状态:")
    print("   status = qa_system.get_status()")
    print("   print(f'已存储文档块: {status[\"count\"]}个')")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_usage()
    else:
        main()