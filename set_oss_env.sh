#!/bin/bash
# 阿里云 OSS 环境变量设置脚本
# 使用方式: source set_oss_env.sh  或  . set_oss_env.sh
#
# 如何获取阿里云 OSS 配置：
# 1. 登录阿里云控制台 https://ram.console.aliyun.com/users
# 2. 创建 AccessKey 或使用已有 AccessKey
# 3. 在 OSS 控制台创建 Bucket：https://oss.console.aliyun.com
# 4. 获取 Endpoint（如 oss-cn-hangzhou.aliyuncs.com）

# ↓↓↓ 请将下面的值替换为你自己的阿里云 OSS 配置 ↓↓↓
export OSS_ACCESS_KEY_ID="your-access-key-id"
export OSS_ACCESS_KEY_SECRET="your-access-key-secret"
export OSS_BUCKET_NAME="your-bucket-name"
export OSS_ENDPOINT="oss-cn-hangzhou.aliyuncs.com"
export OSS_USE_HTTPS="true"
# ↑↑↑ 请替换上面的值为你自己的配置 ↑↑↑

echo ""
echo "==================================="
echo "  阿里云 OSS 环境变量设置"
echo "==================================="
echo ""
echo "  Bucket:   $OSS_BUCKET_NAME"
echo "  Endpoint: $OSS_ENDPOINT"
echo "  HTTPS:    $OSS_USE_HTTPS"
echo ""
echo " ✅ 环境变量已设置！请运行: python3 run.py"
echo ""
