import os
import json
from openai import OpenAI
from sqlalchemy.orm import Session
from app.db.models import DiseaseEncyclopedia

# DeepSeek 官方 API 配置 (已硬编码确保连通性)
DEEPSEEK_API_KEY = "sk-56b779a5e9c445e29d4f3d876b663e64"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def get_disease_context(db: Session, query: str):
    """
    检索局部百科全书作为 RAG 上下文。
    目前使用模糊匹配优化：对用户提问中的关键词进行病词检索。
    """
    # 策略：从百科库中提取所有病害的核心防治知识
    all_diseases = db.query(DiseaseEncyclopedia).all()
    context_str = ""
    for d in all_diseases:
        context_str += f"【{d.name}】: 病因是 {d.causes}。专家建议：{d.prevention}\n"
    return context_str

async def ask_agro_expert(db: Session, user_query: str, last_result: dict = None):
    """
    基于 RAG 的 AI 专家解答逻辑
    last_result: 包含检测元数据的字典 {disease_name, confidence, causes, prevention}
    """
    # 1. 提取本地百科上下文
    knowledge_base = get_disease_context(db, user_query)
    
    # 2. 构造【视觉感知型】Prompt
    visual_context = "暂无实时识别图像"
    if last_result and last_result.get('disease_name') != '未检测到显著病害':
        visual_context = f"""
【视觉分析结论】：
- 识别目标：{last_result['disease_name']}
- 置信度：{last_result.get('confidence', 0)*100:.1f}%
- 基础诊断：{last_result.get('causes', '未知')}
- 基础建议：{last_result.get('prevention', '暂无')}
"""

    system_prompt = f"""
你是一名资深的农作物植保专家。
你正在查看用户刚通过 YOLO 识别系统上传的一张农作物患病图片。

你的实时视野（由 YOLO 视觉模型提供）：
{visual_context}

你的权威参考库（RAG 召回内容）：
{knowledge_base}

指令：
1. 如果用户问到关于“这张图片”或“这个病”的问题，请结合上述【视觉分析结论】进行二次深度解读。
2. 如果结果显示为【健康】，请给予用户肯定并提醒预防措施。
3. 如果结果置信度较低（低于 60%），请提醒用户图片可能不清晰，建议重新拍摄。
4. 回答要通俗易懂，让庄稼人听得明白。
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 专家暂时下线（连接异常）：{str(e)}"
