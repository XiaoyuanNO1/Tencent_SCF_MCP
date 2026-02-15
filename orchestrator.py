import json
import asyncio
import aiohttp
from typing import List, Dict
from agents_config import AGENTS

async def handle_multi_agent_chat(arguments: dict) -> str:
    """
    多Agent协同对话的主流程
    """
    user_question = arguments.get("question")
    app_key = arguments.get("app_key")
    
    if not user_question or not app_key:
        return "❌ 错误：缺少必要参数 question 或 app_key"
    
    try:
        # 步骤1：意图识别与拆解
        print("🔍 正在分析问题...")
        sub_questions = await analyze_and_split_question(user_question, app_key)
        
        print(f"📋 拆解为 {len(sub_questions)} 个子问题")
        
        # 步骤2：并行调度执行
        print("🚀 开始调用相关Agent...")
        sub_results = await execute_sub_questions(sub_questions, app_key)
        
        # 步骤3：结果汇总
        print("📝 正在整合答案...")
        final_answer = await summarize_results(user_question, sub_results, app_key)
        
        # 构建详细信息
        detail_info = "\n\n---\n\n**🔍 处理详情**\n\n"
        for i, r in enumerate(sub_results, 1):
            agent_name = AGENTS.get(r['agent_id'], {}).get('name', r['agent_id'])
            detail_info += f"{i}. **{agent_name}** 回答了 \"{r['sub_question']}\"\n"
        
        return f"{final_answer}\n{detail_info}"
    
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        print(f"错误详情：{error_detail}")
        return f"❌ 处理失败: {str(e)}"


async def analyze_and_split_question(user_question: str, app_key: str) -> List[Dict]:
    """分析并拆解问题"""
    
    agents_desc = "\n".join([
        f"{aid}（{info['name']}）：{info['description']}"
        for aid, info in AGENTS.items()
    ])
    
    prompt = f"""你是一个智能问题分析助手，需要将用户的复杂问题拆解成多个子问题。

可用的Agent及其能力：
{agents_desc}

用户问题：{user_question}

请分析这个问题，如果涉及多个领域，请拆解成多个独立的子问题。
返回JSON格式：
{{
  "sub_questions": [
    {{
      "sub_question": "拆解后的子问题",
      "agent_id": "负责的Agent ID",
      "priority": 1
    }}
  ]
}}

规则：
1. 如果问题只涉及一个领域，sub_questions只包含一项
2. priority数字越小优先级越高
3. 保持子问题的完整性和独立性
4. 只返回JSON，不要其他内容
"""
    
    response = await call_llm_async(prompt, app_key)
    
    try:
        # 尝试提取JSON
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        result = json.loads(response)
        return result.get("sub_questions", [])
    except Exception as e:
        print(f"解析失败：{e}, 原始响应：{response}")
        # 解析失败，返回原始问题
        return [{
            "sub_question": user_question,
            "agent_id": "finance",
            "priority": 1
        }]


async def execute_sub_questions(sub_questions: List[Dict], app_key: str) -> List[Dict]:
    """并行执行子问题"""
    
    tasks = []
    for sub_q in sub_questions:
        task = call_agent_async(
            agent_id=sub_q["agent_id"],
            question=sub_q["sub_question"],
            app_key=app_key
        )
        tasks.append(task)
    
    # 并行执行
    answers = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 组装结果
    results = []
    for sub_q, answer in zip(sub_questions, answers):
        if isinstance(answer, Exception):
            answer = f"[调用失败：{str(answer)}]"
        
        results.append({
            "sub_question": sub_q["sub_question"],
            "agent_id": sub_q["agent_id"],
            "answer": answer
        })
    
    return results


async def summarize_results(user_question: str, sub_results: List[Dict], app_key: str) -> str:
    """汇总结果"""
    
    results_text = "\n\n".join([
        f"【{AGENTS[r['agent_id']]['name']}】回答了\"{r['sub_question']}\"：\n{r['answer']}"
        for r in sub_results
    ])
    
    prompt = f"""你是一个信息整合助手，需要将多个专业Agent的回答整合成一个完整、连贯的答复。

用户原始问题：{user_question}

各Agent的回答：
{results_text}

请整合以上信息，生成一个完整的答复。要求：
1. 保持信息的准确性
2. 按逻辑顺序组织
3. 去除重复信息
4. 使用清晰的Markdown格式
5. 保持专业、简洁

直接返回整合后的答复。
"""
    
    return await call_llm_async(prompt, app_key)


async def call_llm_async(prompt: str, app_key: str) -> str:
    """异步调用LLM"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://adp.woa.com/v1/chat/completions",
            headers={
                "X-ADP-App-Key": app_key,
                "Content-Type": "application/json"
            },
            json={
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": 0.3
            },
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            result = await response.json()
            return result["choices"][0]["message"]["content"]


async def call_agent_async(agent_id: str, question: str, app_key: str) -> str:
    """异步调用Agent"""
    agent_config = AGENTS.get(agent_id)
    if not agent_config:
        return f"[Agent {agent_id} 不存在]"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://adp.woa.com/v1/chat/completions",
            headers={
                "X-ADP-App-Key": app_key,
                "Content-Type": "application/json"
            },
            json={
                "app_id": agent_config["app_id"],
                "messages": [{"role": "user", "content": question}],
                "stream": False
            },
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            result = await response.json()
            return result["choices"][0]["message"]["content"]
