#!/bin/bash

# 部署脚本 - ADP 多Agent协同 MCP 服务

set -e

echo "🚀 开始部署 ADP 多Agent协同 MCP 服务..."

# 检查是否在正确的目录
if [ ! -f "index.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 步骤1：检查配置
echo ""
echo "📋 步骤1：检查配置..."

if grep -q "your-finance-app-id" agents_config.py; then
    echo "⚠️  警告：检测到默认的 Agent 配置"
    echo "   请先修改 agents_config.py 中的 app_id"
    read -p "   是否继续部署？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 步骤2：创建部署包
echo ""
echo "📦 步骤2：创建部署包..."

# 清理旧的部署包
rm -f function.zip

# 打包代码
zip -r function.zip . -x "*.git*" "*.md" "deploy.sh" "function.zip" "__pycache__/*" "*.pyc"

echo "✅ 部署包创建完成：function.zip"

# 步骤3：显示下一步操作
echo ""
echo "🎯 步骤3：部署到腾讯云"
echo ""
echo "方式一：通过控制台部署"
echo "  1. 访问 https://console.cloud.tencent.com/scf"
echo "  2. 创建函数，选择 Python 3.9 运行环境"
echo "  3. 上传 function.zip"
echo "  4. 设置执行方法为：index.main_handler"
echo "  5. 配置 API 网关触发器"
echo ""
echo "方式二：通过 Serverless Framework 部署"
echo "  1. 安装：npm install -g serverless"
echo "  2. 配置密钥：serverless credentials set --provider tencent --key YOUR_KEY --secret YOUR_SECRET"
echo "  3. 部署：serverless deploy"
echo ""

# 步骤4：测试建议
echo "🧪 部署后测试"
echo ""
echo "获取部署 URL 后，运行："
echo '  curl -X POST https://YOUR_URL/mcp \'
echo '    -H "Content-Type: application/json" \'
echo '    -d '"'"'{"method": "tools/list"}'"'"
echo ""

echo "✅ 准备完成！请按照上述步骤完成部署。"
