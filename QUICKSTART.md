# 极速部署指南 (Quick Start)

想要立刻使用？请直接复制对应系统的命令，在终端中粘贴并运行即可。

## 🐧 Linux / Mac / 玩客云 (Arm32)

**一键安装命令**（复制整段）：

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

运行后，程序会自动在当前目录创建 `trendradar` 文件夹，并在其中生成默认配置文件。

---

## 🪟 Windows (PowerShell)

**一键安装命令**（复制整段）：

```powershell
New-Item -ItemType Directory -Force -Path trendradar; docker run -d `
  --name trend-radar `
  --restart unless-stopped `
  -e TZ=Asia/Shanghai `
  -e RUN_MODE=cron `
  -e CRON_SCHEDULE="*/30 * * * *" `
  -e IMMEDIATE_RUN=true `
  -v ${PWD}/trendradar/config:/app/config `
  -v ${PWD}/trendradar/output:/app/output `
  ghcr.io/1williamaoayers/trendradar-arm32:latest
```

---

## 🛠 如何修改配置？（推荐）

我们提供了**交互式管理工具**，无需手动编辑文件！

**运行管理命令：**
```bash
docker exec -it trend-radar python manage.py
```

你可以：
1.  修改抓取频率（每小时/每天...）
2.  管理关键词（支持**分组管理**、批量增删）
3.  **管理监控平台**（一键启用/禁用微博、抖音等）
4.  立即手动运行一次

---

## 📂 手动修改配置（备选）

如果你喜欢手动操作，也可以直接编辑文件：
1.  进入 `trendradar/config` 文件夹。
2.  修改 `config.yaml` 或 `frequency_words.txt`。
3.  重启容器生效：`docker restart trend-radar`
