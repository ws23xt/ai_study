# DeepSeek Agent 实战：小红书爆款文案生成助手

这是一个基于 DeepSeek LLM 构建的智能 Agent，能够生成小红书爆款文案。本项目展示了如何使用 ReAct (Thought-Action-Observation) 模式来构建一个具有工具调用能力的文案生成助手。

## 功能特点

- 🤖 **智能Agent**: 基于 DeepSeek LLM 的智能文案生成
- 🔧 **工具集成**: 模拟网页搜索、产品数据库查询、表情符号生成等工具
- 📝 **多样化输出**: 生成包含标题、正文、标签和表情符号的完整文案
- 🎨 **风格可控**: 支持多种文案风格（活泼甜美、知性温柔等）
- 📊 **结构化输出**: JSON格式输出，便于后续处理
- 📋 **格式化工具**: 提供 Markdown 格式化功能

## 环境要求

- Python 3.7+
- DeepSeek API Key

## 安装

1. 克隆或下载代码到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 设置环境变量：
   ```bash
   # Windows
   set DEEPSEEK_API_KEY=your_deepseek_api_key_here
   
   # Linux/Mac
   export DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```

## 使用方法

### 直接运行演示

```bash
python rednote.py
```

### 在代码中使用

```python
from rednote import setup_deepseek_client, generate_rednote, format_rednote_for_markdown

# 初始化客户端
client = setup_deepseek_client()

# 生成文案
result = generate_rednote(client, "深海蓝藻保湿面膜", "活泼甜美")

# 格式化为 Markdown
formatted = format_rednote_for_markdown(result)
print(formatted)
```

## 项目结构

```
rednote/
├── rednote.py          # 主程序文件
├── requirements.txt    # 依赖包列表
├── README.md          # 说明文档
└── rednote.ipynb      # 原始 Jupyter Notebook
```

## 核心模块

### 1. 系统提示词 (System Prompt)
定义了 Agent 的角色和行为准则，采用 ReAct 模式指导推理过程。

### 2. 工具定义 (Tools Definition)
- `search_web`: 网页搜索工具
- `query_product_database`: 产品数据库查询工具
- `generate_emoji`: 表情符号生成工具

### 3. 文案生成函数
`generate_rednote()` 是核心函数，实现了完整的 Agent 工作流。

### 4. 格式化工具
`format_rednote_for_markdown()` 将 JSON 格式的文案转换为 Markdown 格式。

## 配置说明

### API 配置
需要在环境变量中设置 `DEEPSEEK_API_KEY`：

```python
# 检查环境变量
import os
api_key = os.getenv("DEEPSEEK_API_KEY")
```

### 参数调整
可以通过修改以下参数来调整生成效果：

- `tone_style`: 文案风格（"活泼甜美"、"知性温柔"、"搞怪"等）
- `max_iterations`: 最大迭代次数（默认5次）
- `SYSTEM_PROMPT`: 系统提示词
- `TOOLS_DEFINITION`: 工具定义

## 示例输出

```markdown
## ✨ 28天逆袭冷白皮！这款美白精华让我告别暗沉痘印 🌟

姐妹们！我终于找到了我的本命美白精华！💖

作为一个常年熬夜➕痘印困扰的混油皮，肤色暗沉一直是我的心头大患。直到遇见了这款美白精华，简直打开了新世界的大门！🤩

🌟 核心成分：烟酰胺+VC衍生物，双管齐下，提亮肤色效果绝绝子！
💧 质地轻薄到爆炸，上脸秒吸收，完全不会黏腻，油皮姐妹放心冲！
🌿 用了28天，痘印肉眼可见变淡了，整张脸都透亮了起来，素颜也能打！

使用方法也很简单：早晚洁面后，滴2-3滴在手心，轻轻按压上脸，后续再叠加保湿产品就OK啦～

真心推荐给所有想要均匀肤色、告别暗沉的姐妹！入股不亏！💖

#美白精华 #提亮肤色 #淡化痘印 #护肤好物 #冷白皮
```

## 扩展功能

### 实际工具集成
目前使用的是模拟工具，在实际应用中可以替换为真实的 API：

- Google Search API
- 产品数据库 API
- 社交媒体趋势 API

### 优化建议
- 添加敏感词检测
- 集成更多数据源
- 实现 RAG (检索增强生成)
- 添加文案质量评估模块

## 注意事项

1. 确保 DeepSeek API Key 的安全性，不要在代码中硬编码
2. 模拟工具仅用于演示，实际使用需要真实的数据源
3. 生成的文案需要人工审核，确保内容合规
4. API 调用可能产生费用，请注意使用量控制

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进项目！
