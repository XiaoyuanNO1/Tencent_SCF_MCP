import json
import asyncio
from orchestrator import handle_multi_agent_chat

def main_handler(event, context):
    """
    腾讯云函数入口 - 同时支持事件函数（API网关触发）和Web函数模式
    """
    try:
        # 判断函数类型
        # Web函数：event中有 path, httpMethod, headers, body 等字段，且 requestContext 为 None 或不存在
        # 事件函数（API网关触发）：event中有 requestContext 字段
        
        is_web_function = event.get('requestContext') is None
        
        # 解析body
        if is_web_function:
            # Web函数：body可能是字符串或已解析的对象
            body_str = event.get('body', '{}')
            if isinstance(body_str, str):
                body = json.loads(body_str) if body_str else {}
            else:
                body = body_str
        else:
            # 事件函数（API网关触发）：body是JSON字符串
            body_str = event.get('body', '{}')
            if isinstance(body_str, str):
                body = json.loads(body_str)
            else:
                body = body_str
        
        # 获取请求参数
        method = body.get('method')
        
        if method == 'tools/list':
            # 返回工具列表
            return {
                "isBase64Encoded": False,
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "tools": [
                        {
                            "name": "multi_agent_chat",
                            "description": "智能多Agent协同对话系统\n\n功能：\n- 自动识别问题涉及的领域\n- 将复杂问题拆解为多个子问题\n- 并行调用多个专业Agent\n- 整合答案返回统一结果\n\n适用场景：\n- 跨领域的复杂问题\n- 需要多方面信息的查询\n- 一次性询问多个事项",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "question": {
                                        "type": "string",
                                        "description": "用户问题（可以是复杂的、涉及多个领域的问题）"
                                    },
                                    "app_key": {
                                        "type": "string",
                                        "description": "ADP AppKey（用于调用各个子Agent）"
                                    }
                                },
                                "required": ["question", "app_key"]
                            }
                        }
                    ]
                })
            }
        
        elif method == 'tools/call':
            # 调用工具
            params = body.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == 'multi_agent_chat':
                # 异步执行
                result = asyncio.run(handle_multi_agent_chat(arguments))
                
                return {
                    "isBase64Encoded": False,
                    "statusCode": 200,
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "body": json.dumps({
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    })
                }
        
        return {
            "isBase64Encoded": False,
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": "Invalid method"})
        }
        
    except Exception as e:
        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": str(e)})
        }
