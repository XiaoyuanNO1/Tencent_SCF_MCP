#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地测试脚本 - 模拟腾讯云API网关触发器
"""

import json
from index import main_handler

def test_tools_list():
    """测试 tools/list 接口"""
    print("=" * 60)
    print("测试1: tools/list")
    print("=" * 60)
    
    # 模拟API网关的event结构
    event = {
        "body": json.dumps({
            "method": "tools/list"
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "httpMethod": "POST",
        "path": "/mcp"
    }
    
    result = main_handler(event, None)
    
    print(f"状态码: {result['statusCode']}")
    print(f"Headers: {result['headers']}")
    print(f"\n响应Body:")
    
    # 解析并美化输出
    body = json.loads(result['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    return result['statusCode'] == 200


def test_tools_call_without_appkey():
    """测试 tools/call 接口（不提供AppKey）"""
    print("\n" + "=" * 60)
    print("测试2: tools/call (缺少AppKey)")
    print("=" * 60)
    
    event = {
        "body": json.dumps({
            "method": "tools/call",
            "params": {
                "name": "multi_agent_chat",
                "arguments": {
                    "question": "公司的经营情况怎么样？"
                }
            }
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "httpMethod": "POST",
        "path": "/mcp"
    }
    
    result = main_handler(event, None)
    
    print(f"状态码: {result['statusCode']}")
    print(f"\n响应Body:")
    
    body = json.loads(result['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    return True


def test_invalid_method():
    """测试无效的method"""
    print("\n" + "=" * 60)
    print("测试3: 无效的method")
    print("=" * 60)
    
    event = {
        "body": json.dumps({
            "method": "invalid_method"
        }),
        "headers": {
            "Content-Type": "application/json"
        },
        "httpMethod": "POST",
        "path": "/mcp"
    }
    
    result = main_handler(event, None)
    
    print(f"状态码: {result['statusCode']}")
    print(f"\n响应Body:")
    
    body = json.loads(result['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    return result['statusCode'] == 400


def test_malformed_json():
    """测试格式错误的JSON"""
    print("\n" + "=" * 60)
    print("测试4: 格式错误的JSON")
    print("=" * 60)
    
    event = {
        "body": "{invalid json}",
        "headers": {
            "Content-Type": "application/json"
        },
        "httpMethod": "POST",
        "path": "/mcp"
    }
    
    result = main_handler(event, None)
    
    print(f"状态码: {result['statusCode']}")
    print(f"\n响应Body:")
    
    body = json.loads(result['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    
    return result['statusCode'] == 500


if __name__ == "__main__":
    print("\n🧪 开始本地测试...\n")
    
    tests = [
        ("tools/list接口", test_tools_list),
        ("tools/call接口（缺少参数）", test_tools_call_without_appkey),
        ("无效的method", test_invalid_method),
        ("格式错误的JSON", test_malformed_json),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} - 通过")
            else:
                failed += 1
                print(f"\n❌ {test_name} - 失败")
        except Exception as e:
            failed += 1
            print(f"\n❌ {test_name} - 异常: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"测试总结: 通过 {passed}/{len(tests)}, 失败 {failed}/{len(tests)}")
    print("=" * 60)
