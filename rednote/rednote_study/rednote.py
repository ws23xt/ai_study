#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek Agent 实战：小红书爆款文案生成助手

本脚本将指导您如何使用 DeepSeek LLM 构建一个能够生成小红书爆款文案的智能 Agent。
我们将从需求拆解开始，逐步定义 Agent 的系统提示词 (System Prompt)、外部工具 (Tools)，
并实现其核心的工作流程，最终生成符合小红书平台特点的文案。

使用方法:
    python rednote.py

作者: AI Assistant
日期: 2025年8月4日
"""

import os
import json
import re
import random
import time
from openai import OpenAI


# =============================================================================
# 1. 环境准备与DeepSeek API配置
# =============================================================================

def setup_deepseek_client():
    """
    初始化 DeepSeek 客户端
    
    Returns:
        OpenAI: DeepSeek 客户端实例
    """
    # 建议将 API Key 设置为环境变量，避免直接暴露在代码中
    # 从环境变量获取 DeepSeek API Key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")

    # 初始化 DeepSeek 客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",  # DeepSeek API 的基地址
    )
    
    return client


# =============================================================================
# 2. 需求拆解与Agent任务规划
# =============================================================================

"""
用户痛点与核心需求：
- 效率低下：人工创作周期长，难以满足高频发布需求。
- 创意瓶颈：难以持续产出新颖、吸引人的爆款创意。
- 趋势捕捉难：实时流行元素难以快速融入文案。
- 平台特性把握：小红书特有风格（标题、正文、标签、表情）难以精准复制。

"爆款"文案的特征：
- 强吸引力标题：制造好奇、痛点共鸣、利益点清晰。
- 沉浸式正文：真实体验分享、细节描述、情感共鸣。
- 精准且多样标签：热门话题、品牌词、产品词、垂直领域词。
- 生动表情符号：增强表达力，提升活泼感。
- 清晰的行动召唤 (CTA)。

Agent 任务规划：核心工作流
1. 用户指令接收：接收产品信息、主题、风格等。
2. 信息收集 (Web Search/DB Query)：实时搜索行业趋势、热门话题、竞品分析、产品卖点。
3. 内容构思与初稿生成 (LLM)：结合所有信息，撰写标题、正文、标签、表情符号。
4. 风格与格式优化 (LLM)：根据小红书平台特点和指定风格，对文案进行润色和结构调整。
5. 最终输出：呈现完整文案。
"""


# =============================================================================
# 3. 爆款文案生成逻辑与 Prompt 设计
# =============================================================================

# 3.1 System Prompt (系统提示词)
# System Prompt 是 Agent 的"大脑"和"行为准则"。它定义了 Agent 的角色、目标以及工作方式。
# 我们将采用 Thought-Action-Observation (ReAct) 模式来引导 DeepSeek 的推理过程。

SYSTEM_PROMPT = """
你是一个资深的小红书爆款文案专家，擅长结合最新潮流和产品卖点，创作引人入胜、高互动、高转化的笔记文案。

你的任务是根据用户提供的产品和需求，生成包含标题、正文、相关标签和表情符号的完整小红书笔记。

请始终采用'Thought-Action-Observation'模式进行推理和行动。文案风格需活泼、真诚、富有感染力。当完成任务后，请以JSON格式直接输出最终文案，格式如下：
```json
{
  "title": "小红书标题",
  "body": "小红书正文",
  "hashtags": ["#标签1", "#标签2", "#标签3", "#标签4", "#标签5"],
  "emojis": ["✨", "🔥", "💖"]
}
```
在生成文案前，请务必先思考并收集足够的信息。
"""

# 3.2 Tools (工具定义)
# Agent 的"双手"由一系列可调用的工具组成。这些工具扩展了 LLM 的能力，
# 使其能够获取实时信息、查询数据库或执行特定操作。

TOOLS_DEFINITION = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索互联网上的实时信息，用于获取最新新闻、流行趋势、用户评价、行业报告等。请确保搜索关键词精确，避免宽泛的查询。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要搜索的关键词或问题，例如'最新小红书美妆趋势'或'深海蓝藻保湿面膜 用户评价'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "query_product_database",
            "description": "查询内部产品数据库，获取指定产品的详细卖点、成分、适用人群、使用方法等信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "要查询的产品名称，例如'深海蓝藻保湿面膜'"
                    }
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_emoji",
            "description": "根据提供的文本内容，生成一组适合小红书风格的表情符号。",
            "parameters": {
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "文案的关键内容或情感，例如'惊喜效果'、'补水保湿'"
                    }
                },
                "required": ["context"]
            }
        }
    }
]


# =============================================================================
# 3.3 模拟工具实现
# =============================================================================

# 由于我们无法直接调用真实的外部 API (如Google Search或内部产品数据库)，
# 我们将创建一些模拟 (Mock) 工具函数来演示 Agent 的工作流程。
# 在实际应用中，您需要将这些模拟函数替换为真实的 API 调用。

def mock_search_web(query: str) -> str:
    """模拟网页搜索工具，返回预设的搜索结果。"""
    print(f"[Tool Call] 模拟搜索网页：{query}")
    time.sleep(1)  # 模拟网络延迟
    if "小红书美妆趋势" in query:
        return "近期小红书美妆流行'多巴胺穿搭'、'早C晚A'护肤理念、'伪素颜'妆容，热门关键词有#氛围感、#抗老、#屏障修复。"
    elif "保湿面膜" in query:
        return "小红书保湿面膜热门话题：沙漠干皮救星、熬夜急救面膜、水光肌养成。用户痛点：卡粉、泛红、紧绷感。"
    elif "深海蓝藻保湿面膜" in query:
        return "关于深海蓝藻保湿面膜的用户评价：普遍反馈补水效果好，吸收快，对敏感肌友好。有用户提到价格略高，但效果值得。"
    else:
        return f"未找到关于 '{query}' 的特定信息，但市场反馈通常关注产品成分、功效和用户体验。"


def mock_query_product_database(product_name: str) -> str:
    """模拟查询产品数据库，返回预设的产品信息。"""
    print(f"[Tool Call] 模拟查询产品数据库：{product_name}")
    time.sleep(0.5)  # 模拟数据库查询延迟
    if "深海蓝藻保湿面膜" in product_name:
        return "深海蓝藻保湿面膜：核心成分为深海蓝藻提取物，富含多糖和氨基酸，能深层补水、修护肌肤屏障、舒缓敏感泛红。质地清爽不粘腻，适合所有肤质，尤其适合干燥、敏感肌。规格：25ml*5片。"
    elif "美白精华" in product_name:
        return "美白精华：核心成分是烟酰胺和VC衍生物，主要功效是提亮肤色、淡化痘印、改善暗沉。质地轻薄易吸收，适合需要均匀肤色的人群。"
    else:
        return f"产品数据库中未找到关于 '{product_name}' 的详细信息。"


def mock_generate_emoji(context: str) -> list:
    """模拟生成表情符号，根据上下文提供常用表情。"""
    print(f"[Tool Call] 模拟生成表情符号，上下文：{context}")
    time.sleep(0.2)  # 模拟生成延迟
    if "补水" in context or "水润" in context or "保湿" in context:
        return ["💦", "💧", "🌊", "✨"]
    elif "惊喜" in context or "哇塞" in context or "爱了" in context:
        return ["💖", "😍", "🤩", "💯"]
    elif "熬夜" in context or "疲惫" in context:
        return ["😭", "😮‍💨", "😴", "💡"]
    elif "好物" in context or "推荐" in context:
        return ["✅", "👍", "⭐", "🛍️"]
    else:
        return random.sample(["✨", "🔥", "💖", "💯", "🎉", "👍", "🤩", "💧", "🌿"], k=min(5, len(context.split())))


# 将模拟工具函数映射到一个字典，方便通过名称调用
available_tools = {
    "search_web": mock_search_web,
    "query_product_database": mock_query_product_database,
    "generate_emoji": mock_generate_emoji,
}


# =============================================================================
# 4. 实战：构建小红书文案生成 Agent
# =============================================================================

# 现在，我们将把 System Prompt、工具定义和模拟工具函数整合起来，
# 构建出能够自动执行的 DeepSeek Agent 工作流。
# 核心是 generate_rednote 函数，它通过一个循环来模拟 Agent 的 Thought-Action-Observation 过程。

def generate_rednote(client, product_name: str, tone_style: str = "活泼甜美", max_iterations: int = 5) -> str:
    """
    使用 DeepSeek Agent 生成小红书爆款文案。
    
    Args:
        client: DeepSeek 客户端实例
        product_name (str): 要生成文案的产品名称。
        tone_style (str): 文案的语气和风格，如"活泼甜美"、"知性"、"搞怪"等。
        max_iterations (int): Agent 最大迭代次数，防止无限循环。
        
    Returns:
        str: 生成的爆款文案（JSON 格式字符串）。
    """
    
    print(f"\n🚀 启动小红书文案生成助手，产品：{product_name}，风格：{tone_style}\n")
    
    # 存储对话历史，包括系统提示词和用户请求
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"请为产品「{product_name}」生成一篇小红书爆款文案。要求：语气{tone_style}，包含标题、正文、至少5个相关标签和5个表情符号。请以完整的JSON格式输出，并确保JSON内容用markdown代码块包裹（例如：```json{{...}}```）。"}
    ]
    
    iteration_count = 0
    final_response = None
    
    while iteration_count < max_iterations:
        iteration_count += 1
        print(f"-- Iteration {iteration_count} --")
        
        try:
            # 调用 DeepSeek API，传入对话历史和工具定义
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=TOOLS_DEFINITION,  # 告知模型可用的工具
                tool_choice="auto"  # 允许模型自动决定是否使用工具
            )

            response_message = response.choices[0].message
            
            # **ReAct模式：处理工具调用**
            if response_message.tool_calls:  # 如果模型决定调用工具
                print("Agent: 决定调用工具...")
                messages.append(response_message)  # 将工具调用信息添加到对话历史
                
                tool_outputs = []
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    # 确保参数是合法的JSON字符串，即使工具不要求参数，也需要传递空字典
                    function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}

                    print(f"Agent Action: 调用工具 '{function_name}'，参数：{function_args}")
                    
                    # 查找并执行对应的模拟工具函数
                    if function_name in available_tools:
                        tool_function = available_tools[function_name]
                        tool_result = tool_function(**function_args)
                        print(f"Observation: 工具返回结果：{tool_result}")
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": str(tool_result)  # 工具结果作为字符串返回
                        })
                    else:
                        error_message = f"错误：未知的工具 '{function_name}'"
                        print(error_message)
                        tool_outputs.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "content": error_message
                        })
                messages.extend(tool_outputs)  # 将工具执行结果作为 Observation 添加到对话历史
                
            # **ReAct 模式：处理最终内容**
            elif response_message.content:  # 如果模型直接返回内容（通常是最终答案）
                print(f"[模型生成结果] {response_message.content}")
                
                # --- START: 添加 JSON 提取和解析逻辑 ---
                json_string_match = re.search(r"```json\s*(\{.*\})\s*```", response_message.content, re.DOTALL)
                
                if json_string_match:
                    extracted_json_content = json_string_match.group(1)
                    try:
                        final_response = json.loads(extracted_json_content)
                        print("Agent: 任务完成，成功解析最终JSON文案。")
                        return json.dumps(final_response, ensure_ascii=False, indent=2)
                    except json.JSONDecodeError as e:
                        print(f"Agent: 提取到JSON块但解析失败: {e}")
                        print(f"尝试解析的字符串:\n{extracted_json_content}")
                        messages.append(response_message)  # 解析失败，继续对话
                else:
                    # 如果没有匹配到 ```json 块，尝试直接解析整个 content
                    try:
                        final_response = json.loads(response_message.content)
                        print("Agent: 任务完成，直接解析最终JSON文案。")
                        return json.dumps(final_response, ensure_ascii=False, indent=2)
                    except json.JSONDecodeError:
                        print("Agent: 生成了非JSON格式内容或非Markdown JSON块，可能还在思考或出错。")
                        messages.append(response_message)  # 非JSON格式，继续对话
                # --- END: 添加 JSON 提取和解析逻辑 ---
            else:
                print("Agent: 未知响应，可能需要更多交互。")
                break
                
        except Exception as e:
            print(f"调用 DeepSeek API 时发生错误: {e}")
            break
    
    print("\n⚠️ Agent 达到最大迭代次数或未能生成最终文案。请检查Prompt或增加迭代次数。")
    return "未能成功生成文案。"


# =============================================================================
# 格式化小红书文案
# =============================================================================

def format_rednote_for_markdown(json_string: str) -> str:
    """
    将 JSON 格式的小红书文案转换为 Markdown 格式，以便于阅读和发布。

    Args:
        json_string (str): 包含小红书文案的 JSON 字符串。
                           预计格式为 {"title": "...", "body": "...", "hashtags": [...], "emojis": [...]}

    Returns:
        str: 格式化后的 Markdown 文本。
    """
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        return f"错误：无法解析 JSON 字符串 - {e}\n原始字符串：\n{json_string}"

    title = data.get("title", "无标题")
    body = data.get("body", "")
    hashtags = data.get("hashtags", [])
    # 表情符号通常已经融入标题和正文中，这里可以选择是否单独列出
    # emojis = data.get("emojis", []) 

    # 构建 Markdown 文本
    markdown_output = f"## {title}\n\n"  # 标题使用二级标题
    
    # 正文，保留换行符
    markdown_output += f"{body}\n\n"
    
    # Hashtags
    if hashtags:
        hashtag_string = " ".join(hashtags)  # 小红书标签通常是空格分隔
        markdown_output += f"{hashtag_string}\n"
        
    # 如果需要，可以单独列出表情符号，但通常它们已经包含在标题和正文中
    # if emojis:
    #     emoji_string = " ".join(emojis)
    #     markdown_output += f"\n使用的表情：{emoji_string}\n"
        
    return markdown_output.strip()  # 去除末尾多余的空白


# =============================================================================
# 5. 实际测试与文案生成
# =============================================================================

def demo_usage():
    """演示如何使用小红书文案生成助手"""
    
    # 初始化客户端
    try:
        client = setup_deepseek_client()
    except ValueError as e:
        print(f"错误：{e}")
        print("请确保设置了 DEEPSEEK_API_KEY 环境变量")
        return

    # 测试案例 1: 深海蓝藻保湿面膜
    print("=" * 50)
    print("测试案例 1: 深海蓝藻保湿面膜")
    print("=" * 50)
    
    product_name_1 = "深海蓝藻保湿面膜"
    tone_style_1 = "活泼甜美"
    result_1 = generate_rednote(client, product_name_1, tone_style_1)

    print("\n--- 生成的文案 1 (JSON格式) ---")
    print(result_1)
    
    # 格式化显示
    print("\n--- 生成的文案 1 (Markdown格式) ---")
    markdown_note_1 = format_rednote_for_markdown(result_1)
    print(markdown_note_1)

    # 测试案例 2: 美白精华
    print("\n" + "=" * 50)
    print("测试案例 2: 美白精华")
    print("=" * 50)
    
    product_name_2 = "美白精华"
    tone_style_2 = "知性温柔"
    result_2 = generate_rednote(client, product_name_2, tone_style_2)

    print("\n--- 生成的文案 2 (JSON格式) ---")
    print(result_2)
    
    # 格式化显示
    print("\n--- 生成的文案 2 (Markdown格式) ---")
    markdown_note_2 = format_rednote_for_markdown(result_2)
    print(markdown_note_2)


def demo_format_function():
    """演示格式化函数的使用"""
    print("\n" + "=" * 50)
    print("演示格式化函数")
    print("=" * 50)
    
    # --- 示例使用 ---
    # 假设这是 generate_rednote 函数的输出
    generated_json_output = """
{
  "title": "✨ 28天逆袭冷白皮！这款美白精华让我告别暗沉痘印 🌟",
  "body": "姐妹们！我终于找到了我的本命美白精华！💖\\n\\n作为一个常年熬夜➕痘印困扰的混油皮，肤色暗沉一直是我的心头大患。直到遇见了这款美白精华，简直打开了新世界的大门！🤩\\n\\n🌟 核心成分：烟酰胺+VC衍生物，双管齐下，提亮肤色效果绝绝子！\\n💧 质地轻薄到爆炸，上脸秒吸收，完全不会黏腻，油皮姐妹放心冲！\\n🌿 用了28天，痘印肉眼可见变淡了，整张脸都透亮了起来，素颜也能打！\\n\\n使用方法也很简单：早晚洁面后，滴2-3滴在手心，轻轻按压上脸，后续再叠加保湿产品就OK啦～\\n\\n真心推荐给所有想要均匀肤色、告别暗沉的姐妹！入股不亏！💖",
  "hashtags": ["#美白精华", "#提亮肤色", "#淡化痘印", "#护肤好物", "#冷白皮"],
  "emojis": ["✨", "💖", "🤩", "💧", "🌿"]
}
"""

    # 调用格式化函数
    markdown_note = format_rednote_for_markdown(generated_json_output)

    # 打印结果
    print("--- 格式化后的小红书文案 (Markdown) ---")
    print(markdown_note)

    # --- 另一个例子，假设JSON解析失败 ---
    invalid_json_output = "{'title': 'Test', 'body': 'This is not valid json'}"  # 使用单引号，非法
    markdown_error_note = format_rednote_for_markdown(invalid_json_output)
    print("\n--- 格式化错误示例 ---")
    print(markdown_error_note)


# =============================================================================
# 主程序入口
# =============================================================================

def main():
    """主程序入口"""
    print("DeepSeek Agent 实战：小红书爆款文案生成助手")
    print("=" * 60)
    
    # 演示格式化函数
    demo_format_function()
    
    # 演示实际使用（需要设置 DEEPSEEK_API_KEY 环境变量）
    print("\n如果您想测试实际的文案生成功能，请确保:")
    print("1. 设置 DEEPSEEK_API_KEY 环境变量")
    print("2. 取消注释下面的 demo_usage() 调用")
    print("\n# demo_usage()  # 取消注释来运行实际测试")
    
    # 如果设置了环境变量，可以运行实际测试
    if os.getenv("DEEPSEEK_API_KEY"):
        print("\n检测到 DEEPSEEK_API_KEY，开始运行实际测试...")
        demo_usage()
    else:
        print("\n未检测到 DEEPSEEK_API_KEY 环境变量，跳过实际测试。")


if __name__ == "__main__":
    main()


# =============================================================================
# 文档说明
# =============================================================================

"""
6. 评估与优化

文案生成并非一蹴而就，需要持续的评估和优化。本节讨论一些评估方法和优化策略。

评估文案质量：
- 客观量化评估 (数据)：
  - 点赞/收藏/评论/分享：基础互动
  - 曝光/阅读/点击/涨粉：流量与曝光
  - 停留时长/截图率：用户行为。
  - 商品页浏览/加购/ROI/成交转化：商业价值
  - 爆文率/同类横向对比：竞争对比
- 主观内部评估 (人工)：
  - 相关性：是否符合产品特点和主题。
  - 吸引力：标题是否抓人，内容是否流畅。
  - 合规性：是否有敏感词、违规宣传。
  - 风格匹配：是否符合小红书调性和指定语气。
  - 用户画像：目标人群年龄、地域、兴趣标签。

优化迭代方法：
- Prompt 调整：根据评估结果，精修 System Prompt、User Prompt，增加或修改 Few-shot 示例。
- 工具扩充：引入新的工具（如敏感词检测工具、竞品分析工具）。
- RAG (检索增强生成)：结合更精准的内部知识库，减少幻觉。

7. 总结与展望

通过本次实战，我们成功构建了一个基于 DeepSeek Agent 的小红书爆款文案生成助手。
我们学习了如何拆解需求、设计 Prompt、定义工具，并实现 Agent 的核心工作流。

Agent 在内容营销领域的潜力巨大，未来可以进一步拓展到：

- 超个性化内容：根据用户数据，生成一对一的定制文案。
- 多模态内容创作：结合图片、视频生成，实现图文音视频一体化。
- 智能营销决策：Agent 不仅生成内容，还能分析效果并给出投放建议。
- 跨平台适配：快速生成适应不同社交媒体平台风格的文案。

同时，我们也需关注挑战，如确保内容真实性、处理高度主观情感、与现有工作流的无缝集成等。
Agent 技术仍在快速发展，期待未来能带来更多惊喜！
"""
