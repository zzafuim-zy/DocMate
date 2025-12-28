# **DocMate**智能文档问答助手 (简便版)

基于AgentScope 1.0框架和DashScope API构建的本地文档处理和智能问答系统，通过建立两个自定义agent(document_agent和qa_agent)及几个不同文档格式的processor来支持PDF、Word、文本、Markdown、图片OCR等多种格式的本地文件处理。 


## 🌟 主要特性

- **多格式文档支持**: PDF、Word(.docx/.doc)、文本(.txt)、Markdown(.md)
- **图片OCR识别**: 支持PNG、JPG、JPEG、TIFF、BMP、GIF等格式的文字识别
- **智能问答**: 基于文档内容的精准问答，使用DashScope API
- **向量存储**: 使用ChromaDB进行高效的语义搜索
- **简单易用**: 纯Python API，无需复杂的Web界面
- **异步处理**: 支持异步文档处理，提升处理效率

## 📋 系统要求

- Python 3.8+
- DashScope API密钥 (阿里云通义千问)
- Tesseract OCR (可选，用于图片文字识别)

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设置

编辑 `config/config.yaml` 文件，设置您的DashScope API密钥：

```yaml
model:
  model_type: "dashscope_chat"
  config_name: "qwen-turbo"
  model_name: "qwen-turbo"
  api_key: null  # api_key从环境变量解析得到，配置方法可在DashScope服务查找
```

### 3. 获取DashScope API密钥

1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 注册并登录阿里云账号
3. 开通DashScope服务
4. 获取API密钥并填入配置环境变量

### 4. 运行程序

**交互式使用:**
```bash
python simple_document_qa.py
```

## 📖 使用方法

### 交互式使用

运行 `python simple_document_qa.py` 后，按照提示选择操作：

1. **处理单个文件** - 输入本地文件路径
2. **批量处理文件** - 输入多个文件路径（逗号分隔）
3. **问答对话** - 基于已处理文档进行问答
4. **查看系统状态** - 查看已存储的文档数量
5. **清空存储** - 清除所有已处理的文档数据

### API使用

```python
from simple_document_qa import SimpleDocumentQA

# 初始化系统
qa_system = SimpleDocumentQA()

# 处理单个文件
qa_system.process_file("path/to/your/document.pdf")

# 批量处理文件
file_paths = ["file1.txt", "file2.pdf", "file3.docx"]
qa_system.process_files(file_paths)

# 问答
answer = qa_system.ask_question("文档的主要内容是什么？")
print(answer)

# 查看状态
status = qa_system.get_status()
print(f"已存储文档块: {status['count']} 个")
```

## 🤖 支持的模型

系统支持以下DashScope模型：

- **qwen-turbo** (默认) - 快速响应，适合日常问答
- **qwen-plus** - 平衡性能和效果
- **qwen-max** - 最强性能，适合复杂任务
- **qwen-max-longcontext** - 支持长文本处理

在配置文件中修改 `model_name` 来切换模型。

## 📁 支持的文件格式

- **PDF文件** (.pdf)
- **Word文档** (.docx, .doc)
- **文本文件** (.txt)
- **Markdown文件** (.md, .markdown)
- **图片文件** (.png, .jpg, .jpeg, .tiff, .bmp, .gif) - 通过OCR识别

## 🏗️ 项目结构

```
DocMate/
├── simple_document_qa.py     # 主程序 - 简单的文档问答系统
├── agents/                   # 智能体模块
│   ├── document_agent.py     # 文档处理智能体
│   └── qa_agent.py           # 问答智能体
├── processors/               # 文档处理器
│   ├── pdf_processor.py      # PDF处理
│   ├── word_processor.py     # Word文档处理
│   ├── text_processor.py     # 文本文件处理
│   ├── markdown_processor.py # Markdown处理
│   └── image_processor.py    # 图片OCR处理
├── utils/                    # 工具模块
│   └── vector_store.py       # 向量存储管理
├── config/                   # 配置文件
│   └── config.yaml
└── requirements.txt          # 依赖包列表
```

## 🔧 配置说明

### 模型配置
使用DashScope API，支持通义千问系列模型。

### 向量存储配置
使用ChromaDB作为向量数据库，支持持久化存储。

### OCR配置
支持中英文OCR识别，可配置Tesseract路径和语言包。

## 🆕 AgentScope 1.0 特性

- **异步支持**: 原生支持异步处理，提升并发性能
- **简洁API**: 基于 `AgentBase` 的新智能体架构
- **内置记忆**: `InMemoryMemory` 支持对话历史管理
- **更好的错误处理**: 优化的异常处理机制

## 🙏 致谢

- [AgentScope](https://github.com/modelscope/agentscope) - 多智能体框架
- [DashScope](https://dashscope.aliyun.com/) - 阿里云通义千问API
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库