#!/bin/bash
set -e

# 检查并初始化配置文件
if [ ! -d "/app/config" ]; then
    mkdir -p /app/config
fi

if [ ! -f "/app/config/config.yaml" ]; then
    echo "⚠️ config.yaml 不存在，使用默认配置..."
    if [ -f "/app/defaults/config.yaml" ]; then
        cp /app/defaults/config.yaml /app/config/config.yaml
    else
        echo "❌ 默认配置文件缺失"
        exit 1
    fi
fi

if [ ! -f "/app/config/frequency_words.txt" ]; then
    echo "⚠️ frequency_words.txt 不存在，使用默认配置..."
    if [ -f "/app/defaults/frequency_words.txt" ]; then
        cp /app/defaults/frequency_words.txt /app/config/frequency_words.txt
    else
        touch /app/config/frequency_words.txt
    fi
fi

# 保存环境变量
env >> /etc/environment

case "${RUN_MODE:-cron}" in
"once")
    echo "🔄 单次执行"
    exec /usr/local/bin/python main.py
    ;;
"cron")
    # 生成 crontab
    # 优先使用持久化的配置文件，如果不存在则从环境变量生成
    if [ -f "/app/config/crontab" ]; then
        echo "📅 加载持久化 crontab 配置 (/app/config/crontab)..."
        cp /app/config/crontab /tmp/crontab
    else
        echo "📅 初始化 crontab (从环境变量)..."
        echo "${CRON_SCHEDULE:-*/30 * * * *} cd /app && /usr/local/bin/python main.py" > /tmp/crontab
        # 备份一份到 config 目录，供 manage.py 管理使用
        cp /tmp/crontab /app/config/crontab
    fi
    
    echo "📋 当前生效的 crontab 内容:"
    cat /tmp/crontab

    if ! /usr/local/bin/supercronic -test /tmp/crontab; then
        echo "❌ crontab格式验证失败"
        exit 1
    fi

    # 立即执行一次（如果配置了）
    if [ "${IMMEDIATE_RUN:-false}" = "true" ]; then
        echo "▶️ 立即执行一次"
        /usr/local/bin/python main.py
    fi

    echo "⏰ 启动supercronic: ${CRON_SCHEDULE:-*/30 * * * *}"
    echo "🎯 supercronic 将作为 PID 1 运行"
    
    exec /usr/local/bin/supercronic -passthrough-logs /tmp/crontab
    ;;
*)
    exec "$@"
    ;;
esac