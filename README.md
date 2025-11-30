<div align="center" id="trendradar">

<a href="https://github.com/sansan0/TrendRadar" title="TrendRadar">
  <img src="/_image/banner.webp" alt="TrendRadar Banner" width="80%">
</a>

🚀 最快<strong>30秒</strong>部署的热点助手 —— 告别无效刷屏，只看真正关心的新闻资讯

[![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg?style=flat-square)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-部署-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/r/wantcat/trendradar)

</div>

## 📖 关于本项目 (增强版)

这是一个基于 [TrendRadar](https://github.com/sansan0/TrendRadar) 的二次开发增强版本。

我们保留了原版强大的全网热点聚合与推送功能，并针对**非技术用户**（小白用户）进行了深度优化，致力于打造**最易用、最省心**的 Docker 部署体验。

### 🌟 本版独家特性

1.  **🛠️ 交互式管理工具**：内置 `manage.py` 脚本，提供全中文的可视化菜单。
    *   无需手动编辑 YAML 配置文件。
    *   无需记忆复杂的 Linux/Docker 命令。
    *   像点菜一样配置推送通道、关键词和监控平台。
2.  **⏱️ 定时任务持久化**：彻底解决了 Docker 重启后 Crontab 丢失的问题，在管理界面设置的定时任务永久有效。
3.  **🛡️ 智能防呆设计**：平台增删、配置修改均有实时预览和确认机制，防止误操作。

---

## 🚀 极速开始 (Docker)

### 1. 启动容器

无需复杂的配置，直接运行以下命令即可启动：

```bash
# 创建配置目录
mkdir -p config output

# 下载默认配置文件 (可选，不下载也会自动生成)
wget https://raw.githubusercontent.com/sansan0/TrendRadar/master/config/config.yaml -P config/
wget https://raw.githubusercontent.com/sansan0/TrendRadar/master/config/frequency_words.txt -P config/

# 启动容器
docker run -d --name trend-radar \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/output:/app/output \
  ghcr.io/1williamaoayers/trendradar-arm32:latest
```

### 2. ✨ 进入管理工具 (核心功能)

容器启动后，只需运行这一条命令，即可开始所有配置：

```bash
docker exec -it trend-radar python manage.py
```

🎉 **你将看到如下交互式界面：**

```text
==================================================
       TrendRadar 管理工具 (TrendRadar Manager)      
==================================================
1. ⏱️  修改抓取频率 (定时任务)
2. 📝 管理关键词 (按组管理)
3. 📺 管理监控平台 (增删)
4. 🔔 修改配置文件 (通知/Webhook)
5. ▶️  立即手动运行一次
0. 🚪 退出

请输入选项 [0-5]: 
```

**💡 通过这个菜单，你可以轻松完成：**
*   **修改抓取频率**：支持 30分钟、1小时、6小时、8小时、12小时 或 每天固定时间。
*   **管理关键词**：分组添加/删除你关心的热点关键词（如：`AI`, `华为`, `!广告`）。
*   **管理监控平台**：输入 `weibo` 自动联想为 `微博`，轻松增删监控源。
*   **配置推送通知**：向导式配置 飞书、钉钉、企业微信、邮件 等推送通道。

---

## ✨ 核心功能概览

### **1. 全网热点聚合**
默认支持 11+ 主流平台，包括：
- 知乎、抖音、B站热搜、微博
- 华尔街见闻、财联社、雪球
- 澎湃新闻、凤凰网、今日头条
- 百度热搜、贴吧等

### **2. 智能推送策略**
*   **当日汇总 (daily)**：适合普通用户，每天按时汇总当日热点。
*   **当前榜单 (current)**：适合自媒体，实时追踪当前榜单变化。
*   **增量监控 (incremental)**：适合交易员，只推送最新出现的消息，零重复。

### **3. 多渠道推送**
支持 **企业微信**、**飞书**、**钉钉**、**Telegram**、**邮件**、**Ntfy** 等多种推送方式。

---

## 🙏 致谢

本项目基于 [TrendRadar](https://github.com/sansan0/TrendRadar) 开发，感谢原作者 [sansan0](https://github.com/sansan0) 的开源贡献。

如有使用问题或建议，欢迎提交 Issue 反馈。
