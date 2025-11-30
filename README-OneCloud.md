# 玩客云/Arm32 设备一键部署指南

本项目完美支持 **玩客云 (OneCloud)** 等 32 位 ARM 设备 (armv7l)，以及树莓派等 64 位 ARM 设备。

## 🚀 极速开始（一行命令）

请直接复制下面的命令到终端运行即可：

```bash
mkdir -p trendradar && docker run -d \
  --name trend-radar \
  --restart unless-stopped \
  -e TZ=Asia/Shanghai \
  -e RUN_MODE=cron \
  -e CRON_SCHEDULE="*/30 * * * *" \
  -e IMMEDIATE_RUN=true \
  -v $(pwd)/trendradar/config:/app/config \
  -v $(pwd)/trendradar/output:/app/output \
  ghcr.io/1williamaoayers/trendradar-arm32:latest
```

## 🛠️ 如何管理与配置？（新功能）

我们内置了一个强大的**交互式管理工具**，你不需要再记忆复杂的命令了！

**只需运行：**

```bash
docker exec -it trend-radar python manage.py
```

你会看到一个图形化的菜单：

```text
==================================================
       TrendRadar 管理工具 (TrendRadar Manager)      
==================================================
1. ⏱️  修改抓取频率 (定时任务)
2. 📝 管理关键词 (按组管理)
3. 📺 管理监控平台 (启用/禁用)
4. 🔔 修改配置文件 (通知/Webhook)
5. ▶️  立即手动运行一次
0. 🚪 退出

请输入选项 [0-5]: 
```

### ✨ 核心功能亮点：

*   **⏱️ 傻瓜式定时设置**：选 1，直接选"每小时"或"每天"，不用算复杂的 cron 表达式。
*   **📝 强大的关键词分组管理**：选 2，支持**按组管理**关键词！
    *   你可以把关键词按类别分组（比如：科技组、娱乐组、股票组）。
    *   支持**批量添加/删除**。
    *   支持**新建/删除**整个分组。
*   **📺 可视化平台管理**：选 3，列出所有支持的平台（微博、抖音、知乎等），直接输入序号就能**启用/禁用**，再也不用去改复杂的配置文件了！
*   **▶️ 立即运行**：选 5，马上抓取一次热搜，看看效果。

**⚠️ 注意：** 如果你修改了抓取频率，记得退出工具后重启一下容器：`docker restart trend-radar`
