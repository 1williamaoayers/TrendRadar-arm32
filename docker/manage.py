#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TrendRadar 管理工具 - 交互式配置
"""

import os
import sys
import subprocess

CONFIG_PATH = "/app/config/config.yaml"
KEYWORDS_PATH = "/app/config/frequency_words.txt"
CRONTAB_PATH = "/app/config/crontab"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    clear_screen()
    print("==================================================")
    print("       TrendRadar 管理工具 (TrendRadar Manager)      ")
    print("==================================================")

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_keyword_groups():
    """
    读取关键词，保留分组结构 (空行分隔)
    返回: list of lists, e.g., [['word1', 'word2'], ['word3']]
    """
    content = read_file(KEYWORDS_PATH)
    if not content:
        return []
    
    groups = []
    current_group = []
    
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if line:
            current_group.append(line)
        else:
            if current_group:
                groups.append(current_group)
                current_group = []
    
    # Append the last group if it exists
    if current_group:
        groups.append(current_group)
        
    return groups

def save_keyword_groups(groups):
    """
    保存关键词组，组之间用空行分隔
    """
    lines = []
    for i, group in enumerate(groups):
        if group:
            lines.extend(group)
            # 如果不是最后一组，添加空行分隔
            if i < len(groups) - 1:
                lines.append("")
    
    # 确保文件末尾有换行
    content = '\n'.join(lines) + '\n'
    write_file(KEYWORDS_PATH, content)

def get_current_cron():
    try:
        with open(CRONTAB_PATH, 'r') as f:
            line = f.readline().strip()
            parts = line.split(' cd /app')[0]
            return parts
    except:
        return "未知"

def update_cron(schedule):
    cron_content = f"{schedule} cd /app && /usr/local/bin/python main.py\n"
    write_file(CRONTAB_PATH, cron_content)
    print("\n⚠️  注意：修改定时任务需要重启容器才能生效。")
    return True

def manage_cron():
    print_header()
    current = get_current_cron()
    print(f"当前抓取频率: {current}")
    print("\n请选择新的频率:")
    print("1. 每 30 分钟 (*/30 * * * *)")
    print("2. 每 1 小时 (0 * * * *)")
    print("3. 每 2 小时 (0 */2 * * *)")
    print("4. 每 4 小时 (0 */4 * * *)")
    print("5. 每 6 小时 (0 */6 * * *)")
    print("6. 每 8 小时 (0 */8 * * *)")
    print("7. 每 12 小时 (0 */12 * * *)")
    print("8. 每天一次 (固定时间)")
    print("9. 自定义 cron 表达式")
    print("0. 返回主菜单")
    
    choice = input("\n请输入选项 [0-9]: ")
    
    schedule = ""
    if choice == '1': schedule = "*/30 * * * *"
    elif choice == '2': schedule = "0 * * * *"
    elif choice == '3': schedule = "0 */2 * * *"
    elif choice == '4': schedule = "0 */4 * * *"
    elif choice == '5': schedule = "0 */6 * * *"
    elif choice == '6': schedule = "0 */8 * * *"
    elif choice == '7': schedule = "0 */12 * * *"
    elif choice == '8':
        print("\n请输入每天运行的时间 (24小时制):")
        print("例如: 08:00 (早上8点)")
        print("例如: 23:30 (晚上11点半)")
        time_str = input("请输入时间: ").strip()
        try:
            # 简单验证格式
            if ':' in time_str:
                h, m = time_str.split(':')
                schedule = f"{int(m)} {int(h)} * * *"
            else:
                # 假设只输入了小时
                schedule = f"0 {int(time_str)} * * *"
        except:
            print("⚠️ 时间格式错误")
            input("按回车继续...")
            return
            
    elif choice == '9': schedule = input("请输入 cron 表达式 (如 0 * * * *): ")
    elif choice == '0': return

    if schedule:
        update_cron(schedule)
        print(f"\n✅ 定时任务已更新为: {schedule}")
        print("ℹ️  请在退出管理工具后，手动重启容器以应用更改: docker restart trend-radar")
        input("\n按回车键继续...")

def manage_keywords():
    while True:
        print_header()
        groups = get_keyword_groups()
        
        print("📋 当前关键词列表 (按组显示):")
        print("-" * 40)
        
        # 生成全局索引映射
        # map_idx_to_pos = { global_idx: (group_idx, word_idx) }
        map_idx_to_pos = {}
        global_counter = 1
        
        if not groups:
            print("   (空 - 监控全网热点)")
        else:
            for g_idx, group in enumerate(groups):
                print(f" [组 {g_idx + 1}]:")
                for w_idx, word in enumerate(group):
                    print(f"   {global_counter}. {word}")
                    map_idx_to_pos[global_counter] = (g_idx, w_idx)
                    global_counter += 1
                if g_idx < len(groups) - 1:
                    print("") # 组间空行
        print("-" * 40)
        
        print("\n操作选项:")
        print("1. ➕ 添加关键词 (支持单/多词)")
        print("2. ➖ 删除关键词 (按序号)")
        print("3. 📦 添加新关键词组 (独立分组)")
        print("4. ❌ 删除整组关键词")
        print("5. 🗑️ 清空所有 (恢复监控全网)")
        print("6. 📝 手动编辑文件 (nano)")
        print("0. 🔙 返回主菜单")
        
        choice = input("\n请输入选项 [0-6]: ")
        
        if choice == '1': # 添加关键词
            print("\n提示：支持简单词(如:AI)、必须词(如:手机+华为)、排除词(如:手机!苹果)")
            new_words_input = input("请输入关键词 (多个词用逗号隔开): ")
            if new_words_input:
                new_words_list = [w.strip() for w in new_words_input.replace('，', ',').split(',') if w.strip()]
                
                if not new_words_list:
                    continue

                if not groups:
                    # 如果当前没有组，直接创建新组
                    groups.append(new_words_list)
                    save_keyword_groups(groups)
                    print(f"✅ 已创建新组并添加 {len(new_words_list)} 个关键词")
                else:
                    # 选择要加入的组
                    print("\n请选择要加入的组:")
                    for i in range(len(groups)):
                        # 显示组的前3个词作为标识
                        preview = ", ".join(groups[i][:3])
                        if len(groups[i]) > 3: preview += "..."
                        print(f"{i + 1}. 组 {i + 1} ({preview})")
                    print(f"{len(groups) + 1}. 新建组")
                    
                    g_choice = input(f"请输入组序号 [1-{len(groups) + 1}]: ")
                    if g_choice.isdigit():
                        g_idx = int(g_choice) - 1
                        if 0 <= g_idx < len(groups):
                            # 加入现有组
                            added_count = 0
                            for w in new_words_list:
                                if w not in groups[g_idx]:
                                    groups[g_idx].append(w)
                                    added_count += 1
                            if added_count > 0:
                                save_keyword_groups(groups)
                                print(f"✅ 已向组 {g_idx + 1} 添加 {added_count} 个关键词")
                            else:
                                print("⚠️ 关键词已存在于该组")
                        elif g_idx == len(groups):
                            # 新建组
                            groups.append(new_words_list)
                            save_keyword_groups(groups)
                            print(f"✅ 已新建组并添加 {len(new_words_list)} 个关键词")
                        else:
                            print("❌ 无效的组序号")
                input("按回车继续...")
                        
        elif choice == '2': # 删除关键词
            if not map_idx_to_pos:
                print("\n⚠️ 列表为空，无法删除")
                input("按回车继续...")
                continue
                
            del_idx_input = input("\n请输入要删除的序号 (多个用逗号隔开): ")
            if del_idx_input:
                try:
                    # 获取要删除的全局索引列表
                    target_global_idxs = sorted([int(i.strip()) for i in del_idx_input.replace('，', ',').split(',') if i.strip().isdigit()], reverse=True)
                    
                    deleted_count = 0
                    # 需要反向操作以避免索引偏移问题，但这里涉及两层结构，直接修改有点麻烦
                    # 策略：标记要删除的位置，然后重构 groups
                    
                    # 构建待删除集合 (group_idx, word_idx)
                    to_delete = set()
                    for g_idx in target_global_idxs:
                        if g_idx in map_idx_to_pos:
                            to_delete.add(map_idx_to_pos[g_idx])
                    
                    if not to_delete:
                        print("⚠️ 无效的序号")
                    else:
                        new_groups = []
                        for g_i, group in enumerate(groups):
                            new_group = []
                            for w_i, word in enumerate(group):
                                if (g_i, w_i) not in to_delete:
                                    new_group.append(word)
                                else:
                                    deleted_count += 1
                            if new_group: # 只保留非空组
                                new_groups.append(new_group)
                        
                        groups = new_groups
                        save_keyword_groups(groups)
                        print(f"✅ 已删除 {deleted_count} 个关键词")
                        
                except Exception as e:
                    print(f"❌ 操作失败: {e}")
                input("按回车继续...")

        elif choice == '3': # 添加新组
            print("\n提示：输入一组相关的关键词，将作为一个独立的分组保存")
            new_words_input = input("请输入关键词 (多个词用逗号隔开): ")
            if new_words_input:
                new_words_list = [w.strip() for w in new_words_input.replace('，', ',').split(',') if w.strip()]
                if new_words_list:
                    groups.append(new_words_list)
                    save_keyword_groups(groups)
                    print(f"✅ 已添加新组，包含 {len(new_words_list)} 个关键词")
                else:
                    print("⚠️ 未输入有效关键词")
            input("按回车继续...")

        elif choice == '4': # 删除整组
            if not groups:
                print("\n⚠️ 列表为空")
                input("按回车继续...")
                continue
            
            print("\n现有分组:")
            for i in range(len(groups)):
                preview = ", ".join(groups[i][:3])
                if len(groups[i]) > 3: preview += "..."
                print(f"{i + 1}. 组 {i + 1} ({len(groups[i])} 词): {preview}")
            
            del_g_idx = input("\n请输入要删除的组序号 (多个用逗号隔开): ")
            if del_g_idx:
                try:
                    indexes = sorted([int(i.strip()) - 1 for i in del_g_idx.replace('，', ',').split(',') if i.strip().isdigit()], reverse=True)
                    deleted_count = 0
                    for idx in indexes:
                        if 0 <= idx < len(groups):
                            groups.pop(idx)
                            deleted_count += 1
                    
                    if deleted_count > 0:
                        save_keyword_groups(groups)
                        print(f"✅ 已删除 {deleted_count} 个分组")
                    else:
                        print("⚠️ 未删除任何组")
                except Exception as e:
                    print(f"❌ 操作失败: {e}")
            input("按回车继续...")

        elif choice == '5': # 清空
            confirm = input("\n⚠️ 确定要清空所有关键词吗？(y/n): ")
            if confirm.lower() == 'y':
                save_keyword_groups([])
                print("✅ 已清空")
                input("按回车继续...")
                
        elif choice == '6': # Nano
            try:
                subprocess.run(["nano", KEYWORDS_PATH])
            except FileNotFoundError:
                print("❌ 系统未安装 nano 编辑器")
            input("按回车继续...")
            
        elif choice == '0':
            break

def get_config_val(key, lines):
    """获取配置值"""
    for line in lines:
        s = line.strip()
        # 简单匹配 key: value，排除注释行
        if s.startswith(key + ":") and not s.startswith("#"):
            try:
                val = s.split(":", 1)[1].strip()
                # 去除行尾注释
                if " #" in val: val = val.split(" #")[0].strip()
                # 去除引号
                val = val.strip('"').strip("'")
                return val
            except:
                return ""
    return ""

def update_config_val(key, new_val, lines):
    """更新配置值，保留缩进和注释"""
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith(key + ":") and not s.startswith("#"):
            # 保留缩进
            indent = line[:line.find(key)]
            # 保留注释
            comment = ""
            # 简单的注释保留逻辑
            if "#" in line:
                # 尝试找到最后一个 #，但这可能误伤 url 中的 # (虽然 url 通常在引号里)
                # 这里假设注释是以 " #" 开头
                parts = line.split(" #", 1)
                if len(parts) > 1:
                    comment = " #" + parts[1]
            
            # 格式化新值
            if isinstance(new_val, bool):
                v_str = "true" if new_val else "false"
            else:
                # 字符串加引号
                v_str = f'"{new_val}"'
                
            lines[i] = f"{indent}{key}: {v_str}{comment}"
            return True
    return False

def manage_notification():
    while True:
        print_header()
        content = read_file(CONFIG_PATH)
        lines = content.split('\n')
        
        # 获取当前状态
        enable_notify = get_config_val("enable_notification", lines) == "true"
        
        # 获取各通道配置 (仅用于显示状态)
        feishu = get_config_val("feishu_url", lines)
        ding = get_config_val("dingtalk_url", lines)
        wework = get_config_val("wework_url", lines)
        tg_token = get_config_val("telegram_bot_token", lines)
        email = get_config_val("email_to", lines)
        ntfy = get_config_val("ntfy_topic", lines)
        
        def show_status(val):
            return "✅ 已配置" if val else "⬜ 未配置"

        print("🔔 通知配置管理:")
        print("-" * 40)
        print(f"   全局通知开关: {'✅ [开启]' if enable_notify else '❌ [关闭]'} (控制是否发送通知)")
        print("-" * 40)
        print(f"   1. 飞书 (Feishu)      {show_status(feishu)}")
        print(f"   2. 钉钉 (DingTalk)    {show_status(ding)}")
        print(f"   3. 企业微信 (WeWork)  {show_status(wework)}")
        print(f"   4. Telegram           {show_status(tg_token)}")
        print(f"   5. 邮件 (Email)       {show_status(email)}")
        print(f"   6. Ntfy               {show_status(ntfy)}")
        print("-" * 40)
        print(f"   7. 📧 邮件高级配置    (发件人/SMTP等)")
        print(f"   8. 🕐 推送时间窗口    (设置免打扰时段)")
        print("-" * 40)
        print("请选择要配置的推送通道:")
        print(" [1] 飞书 (Feishu)")
        print(" [2] 钉钉 (DingTalk)")
        print(" [3] 企业微信 (WeWork)")
        print(" [4] Telegram")
        print(" [5] 邮件 (Email)")
        print(" [6] Ntfy")
        print("-" * 40)
        print(" [7] 📧 邮件高级配置    (发件人/SMTP等)")
        print(" [8] 🕐 推送时间窗口    (设置免打扰时段)")
        print("-" * 40)
        print("其他操作:")
        print(" [t] 切换全局通知开关 (On/Off)")
        print(" [e] 手动编辑配置文件 (nano)")
        print(" [0] 返回主菜单")
        
        choice = input("\n请输入选项: ").strip().lower()
        
        if choice == '0':
            break
            
        elif choice == 't':
            new_state = not enable_notify
            if update_config_val("enable_notification", new_state, lines):
                write_file(CONFIG_PATH, '\n'.join(lines))
                print(f"\n✅ 全局通知已{'开启' if new_state else '关闭'}")
            else:
                print("\n❌ 更新失败，未找到配置项")
            input("按回车继续...")
            
        elif choice in ['1', '2', '3', '4', '5', '6']:
            key_map = {
                '1': ('feishu_url', '飞书 Webhook URL'),
                '2': ('dingtalk_url', '钉钉 Webhook URL'),
                '3': ('wework_url', '企业微信 Webhook URL'),
                '4': ('telegram_bot_token', 'Telegram Bot Token'), # TG 还需要 chat_id，这里简化处理
                '5': ('email_to', '收件人邮箱 (多个用逗号分隔)'),
                '6': ('ntfy_topic', 'Ntfy Topic')
            }
            
            key, name = key_map[choice]
            current_val = get_config_val(key, lines)
            
            print(f"\n🔧 正在配置通道: 【{name}】")
            print("-" * 40)
            print(f"当前配置值: {current_val if current_val else '(暂未配置)'}")
            print("-" * 40)
            print("提示: 直接输入新值可覆盖修改")
            print("提示: 输入 'clear' 可清空该配置")
            print("提示: 直接回车可保持不变")
            
            new_val = input(f"\n请输入新的 {name}: ").strip()
            
            if new_val:
                if new_val.lower() == 'clear':
                    new_val = ""
                
                # 特殊处理 Telegram，如果配置 Token，可能也需要 Chat ID
                if choice == '4' and new_val:
                    tg_chat_id = get_config_val("telegram_chat_id", lines)
                    print(f"\n🔧 正在配置: 【Telegram Chat ID】")
                    print("-" * 40)
                    print(f"当前 Chat ID: {tg_chat_id if tg_chat_id else '(暂未配置)'}")
                    print("-" * 40)
                    new_chat_id = input("请输入新的 Chat ID (回车保持不变): ").strip()
                    if new_chat_id:
                        update_config_val("telegram_chat_id", new_chat_id, lines)
                
                if update_config_val(key, new_val, lines):
                    write_file(CONFIG_PATH, '\n'.join(lines))
                    print(f"\n✅ {name} 已更新成功！")
                else:
                    print("\n❌ 更新失败，未找到对应配置项")
            else:
                print("\n🚫 未输入任何内容，配置保持不变")
            input("按回车继续...")

        elif choice == '7':
            manage_email_config(lines)
            write_file(CONFIG_PATH, '\n'.join(lines)) # 保存子菜单的修改
            
        elif choice == '8':
            manage_push_window(lines)
            write_file(CONFIG_PATH, '\n'.join(lines)) # 保存子菜单的修改

        elif choice == 'e':
            try:
                subprocess.run(["nano", CONFIG_PATH])
            except FileNotFoundError:
                print("❌ 系统未安装 nano 编辑器")
            input("按回车继续...")

def manage_email_config(lines):
    while True:
        print_header()
        email_to = get_config_val("email_to", lines)
        email_from = get_config_val("email_from", lines)
        email_pass = get_config_val("email_password", lines)
        smtp_server = get_config_val("email_smtp_server", lines)
        
        mask_pass = "******" if email_pass else "(空)"
        
        print("📧 邮件高级配置:")
        print("-" * 40)
        print(f"   1. 收件人 (To)      : {email_to}")
        print(f"   2. 发件人 (From)    : {email_from}")
        print(f"   3. 密码/授权码      : {mask_pass}")
        print(f"   4. SMTP 服务器      : {smtp_server if smtp_server else '(自动识别)'}")
        print("-" * 40)
        print(" [0] 返回上一级")
        
        choice = input("\n请输入选项: ").strip()
        
        if choice == '0': break
        
        key_map = {
            '1': ('email_to', '收件人'),
            '2': ('email_from', '发件人'),
            '3': ('email_password', '密码/授权码'),
            '4': ('email_smtp_server', 'SMTP 服务器')
        }
        
        if choice in key_map:
            key, name = key_map[choice]
            new_val = input(f"\n请输入新的{name} (输入 clear 清空): ").strip()
            if new_val:
                if new_val.lower() == 'clear': new_val = ""
                update_config_val(key, new_val, lines)
                print(f"✅ {name} 已更新")
            input("按回车继续...")

def manage_push_window(lines):
    while True:
        print_header()
        # 解析 yaml 结构比较麻烦，这里用简单文本匹配
        # 假设格式是标准的
        # push_window:
        #   enabled: false
        #   time_range:
        #     start: "20:00"
        
        # 辅助函数：查找嵌套 key 的值
        def get_nested_val(parent, key, lines):
            in_parent = False
            for line in lines:
                if line.strip().startswith(parent + ":"): in_parent = True
                if in_parent and line.strip().startswith(key + ":"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
                if in_parent and line.strip() and not line.startswith(" ") and not line.strip().startswith(parent):
                    # 缩进结束，跳出
                    if not line.strip().startswith("#"): return "" 
            return ""

        # 辅助函数：更新嵌套 key
        def update_nested_val(parent, key, new_val, lines):
            in_parent = False
            for i, line in enumerate(lines):
                if line.strip().startswith(parent + ":"): in_parent = True
                if in_parent and line.strip().startswith(key + ":"):
                    indent = line[:line.find(key)]
                    if isinstance(new_val, bool): v = "true" if new_val else "false"
                    else: v = f'"{new_val}"'
                    lines[i] = f"{indent}{key}: {v}"
                    return True
            return False

        enabled = get_nested_val("push_window", "enabled", lines) == "true"
        start_time = get_nested_val("push_window", "start", lines) # time_range 下的 start
        end_time = get_nested_val("push_window", "end", lines)
        
        # 由于 start/end 在 time_range 下，上面的简单查找可能找不到，需要更精确的定位
        # 这里为了稳健，我们针对 config.yaml 的特定结构做个简单处理
        # 我们直接遍历查找 "start:" 和 "end:"，因为全文件只有这里有
        start_time = get_config_val("start", lines)
        end_time = get_config_val("end", lines)

        print("🕐 推送时间窗口 (免打扰设置):")
        print("-" * 40)
        print(f"   状态: {'✅ [已启用]' if enabled else '❌ [未启用]'} (启用后仅在指定时间段推送)")
        print(f"   1. 开始时间: {start_time}")
        print(f"   2. 结束时间: {end_time}")
        print("-" * 40)
        print(" [t] 切换启用状态")
        print(" [1] 修改开始时间")
        print(" [2] 修改结束时间")
        print(" [0] 返回上一级")
        
        choice = input("\n请输入选项: ").strip().lower()
        
        if choice == '0': break
        elif choice == 't':
            update_nested_val("push_window", "enabled", not enabled, lines)
        elif choice == '1':
            val = input("请输入开始时间 (如 09:00): ").strip()
            if val: update_config_val("start", val, lines)
        elif choice == '2':
            val = input("请输入结束时间 (如 22:00): ").strip()
            if val: update_config_val("end", val, lines)

def get_platforms_info():
    """
    解析配置文件中的 platforms 部分
    返回: (platforms_list, start_line_index, end_line_index, all_lines)
    platforms_list items: {'id': '...', 'name': '...', 'enabled': bool, 'lines': [str]}
    """
    content = read_file(CONFIG_PATH)
    if not content:
        return [], -1, -1, []
        
    lines = content.split('\n')
    start_idx = -1
    
    # 找到 platforms: 的位置
    for i, line in enumerate(lines):
        if line.strip().startswith('platforms:'):
            start_idx = i
            break
            
    if start_idx == -1:
        return [], -1, -1, lines
        
    platforms = []
    current_platform = {}
    
    # 从 platforms: 下一行开始解析
    i = start_idx + 1
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 如果遇到新的顶级key (不缩进且不以-开头/注释)，则结束
        # 注意：这里假设 platforms 是最后一个或者后面有明确的顶级key
        # 简单的判断：如果行不为空，且缩进比 platforms 大，或者是列表项
        # 但 yaml 格式比较灵活，这里针对该项目的 config.yaml 格式进行特化处理
        
        if not stripped: # 空行保留，归属到上一个或者忽略
            i += 1
            continue
            
        # 如果缩进没有了，说明退出了 platforms 块
        if line and not line.startswith(' ') and not line.startswith('#'):
             # 这是一个新的顶级 key，结束
             break

        # 检测列表项开始
        # 启用状态: "  - id: ..."
        # 禁用状态: "  # - id: ..." 或 "#   - id: ..."
        is_new_item = False
        is_enabled = True
        
        if stripped.startswith('- id:'):
            is_new_item = True
            is_enabled = True
        elif stripped.startswith('#') and '- id:' in stripped:
            # 可能是注释掉的列表项
            # 简单判断：去掉 # 后是否符合格式
            uncommented = stripped.lstrip('#').strip()
            if uncommented.startswith('- id:'):
                is_new_item = True
                is_enabled = False
        
        if is_new_item:
            # 保存上一个
            if current_platform:
                platforms.append(current_platform)
            
            # 解析 ID 和 Name
            # 提取 id
            temp_line = stripped.lstrip('#').strip()
            # "- id: "weibo"" -> weibo
            # 使用简单的字符串处理
            try:
                id_part = temp_line.split('id:', 1)[1].split('name:', 1)[0].strip().strip('"').strip("'")
                current_platform = {
                    'id': id_part,
                    'name': '未知', # 稍后解析
                    'enabled': is_enabled,
                    'raw_lines': [line] # 保存原始行
                }
            except:
                # 解析失败，跳过
                current_platform = {}
        else:
            # 如果是当前 platform 的后续行 (比如 name: ...)
            if current_platform:
                current_platform['raw_lines'].append(line)
                # 尝试提取 name
                temp_line = stripped.lstrip('#').strip()
                if temp_line.startswith('name:'):
                    try:
                        name_part = temp_line.split('name:', 1)[1].strip().strip('"').strip("'")
                        current_platform['name'] = name_part
                    except:
                        pass
        
        i += 1
        
    if current_platform:
        platforms.append(current_platform)
        
    return platforms, start_idx, i, lines

def save_platforms(platforms, start_idx, end_idx, all_lines):
    """
    保存 platforms 修改到文件
    """
    new_lines = []
    
    # 保持缩进风格
    indent = "  "
    
    for p in platforms:
        # 重建该 platform 的行
        # 简单起见，我们重新生成标准格式，而不是尝试修改 raw_lines
        # 这样可以规避很多注释处理的麻烦，但也丢失了行内注释
        
        prefix = indent if p['enabled'] else indent + "# "
        
        # 第一行: - id: "xxx"
        line1 = f'{prefix}- id: "{p["id"]}"'
        new_lines.append(line1)
        
        # 第二行:   name: "xxx"
        # 注意对齐: 如果 prefix 是 "  ", name 前面是 "    "
        # 如果 prefix 是 "  # ", name 前面是 "  #   "
        name_indent = indent + "  " if p['enabled'] else indent + "#   "
        line2 = f'{name_indent}name: "{p["name"]}"'
        new_lines.append(line2)

    # 替换原有的行
    final_lines = all_lines[:start_idx+1] + new_lines + all_lines[end_idx:]
    
    write_file(CONFIG_PATH, '\n'.join(final_lines))

def manage_platforms():
    while True:
        print_header()
        platforms, start_idx, end_idx, all_lines = get_platforms_info()
        
        if not platforms:
            print("⚠️  无法解析配置文件中的 platforms 部分")
            input("按回车返回...")
            return

        print("📺 监控平台管理:")
        print("-" * 40)
        
        # 分页显示，每页显示 10 个，避免刷屏
        # 这里简化处理，直接全部显示，支持滚动吧，毕竟也就20-30个
        
        for i, p in enumerate(platforms):
            status = "✅" if p['enabled'] else "❌"
            print(f"   {i + 1}. [{status}] {p['name']} ({p['id']})")
            
        print("-" * 40)
        print("操作选项:")
        print(" [a]    ➕ 添加新平台")
        print(" [d]    ➖ 删除平台")
        print(" [0]    🔙 返回主菜单")
        
        choice = input("\n请输入选项: ").strip().lower()
        
        if choice == '0':
            break
            
        elif choice == 'a':
            # 定义常见平台字典，用于提示和自动补全名称
            common_platforms = {
                "weibo": "微博", "zhihu": "知乎", "baidu": "百度热搜", 
                "toutiao": "今日头条", "tencent": "腾讯新闻", "douyin": "抖音",
                "bilibili-hot-search": "B站热搜", "tieba": "百度贴吧", "ithome": "IT之家",
                "thepaper": "澎湃新闻", "ifeng": "凤凰网", "wallstreetcn-hot": "华尔街见闻",
                "36kr": "36氪", "sspai": "少数派", "juejin": "掘金", "csdn": "CSDN"
            }

            print("\n--- 添加新平台 ---")
            print("📚 常见支持的平台参考:")
            # 简单的格式化输出
            items = [f"{k}({v})" for k, v in common_platforms.items()]
            for i in range(0, len(items), 3):
                print("  " + ", ".join(items[i:i+3]))
            print("-" * 40)
            
            print("➡️  添加平台 (支持分步输入 或 一行输入)")
            print("方式 1: 仅输入 ID (如 weibo) -> 回车后补全名称")
            print("方式 2: 同时输入 ID 和名称 (如 weibo 微博)")
            
            user_input_str = input("\n请输入: ").strip()
            if not user_input_str:
                print("⚠️ 输入不能为空")
                input("按回车继续...")
                continue

            # 解析输入
            parts = user_input_str.split(None, 1)
            new_id = parts[0]
            new_name = ""
            
            if len(parts) > 1:
                new_name = parts[1].strip()
                
            # 检查重复
            if any(p['id'] == new_id for p in platforms):
                print(f"⚠️ ID '{new_id}' 已存在")
                input("按回车继续...")
                continue
                
            # 如果没有输入名称，或者名称为空，则进入第二步
            if not new_name:
                print("\n➡️  步骤 2: 输入平台名称")
                # 尝试自动匹配名称
                default_name = common_platforms.get(new_id, new_id)
                new_name = input(f"请输入名称 [直接回车使用默认: {default_name}]: ").strip()
                if not new_name: new_name = default_name
            
            # 显示预览
            print("\n📝 即将写入配置文件:")
            print("  - id: \"{}\"".format(new_id))
            print("    name: \"{}\"".format(new_name))
            
            confirm = input("\n确认添加吗？(y/n): ").strip().lower()
            if confirm == 'y':
                platforms.append({
                    'id': new_id,
                    'name': new_name,
                    'enabled': True
                })
                save_platforms(platforms, start_idx, end_idx, all_lines)
                print(f"✅ 已添加: {new_name} ({new_id})")
            else:
                print("🚫 已取消")
            input("按回车继续...")
            
        elif choice == 'd':
            print("\n--- 删除平台 ---")
            print("提示: 请输入要删除的序号，支持删除多个")
            print("例子: 输入 1    (删除第1个)")
            print("例子: 输入 1,3  (删除第1个和第3个)")
            del_idx = input("\n请输入要删除的序号: ")
            try:
                indexes = sorted([int(x.strip()) - 1 for x in del_idx.replace('，', ',').split(',') if x.strip().isdigit()], reverse=True)
                if not indexes:
                    print("⚠️ 无效的序号")
                    input("按回车继续...")
                    continue
                    
                to_delete = []
                for idx in indexes:
                    if 0 <= idx < len(platforms):
                        to_delete.append(platforms[idx])
                
                if not to_delete:
                    print("⚠️ 未找到要删除的平台")
                else:
                    print("\n📝 即将删除以下平台 (ID和名称都将删除):")
                    for p in to_delete:
                        print(f"  ❌ [ID: {p['id']}] Name: {p['name']}")
                    
                    confirm = input("\n确认删除吗？(y/n): ").strip().lower()
                    if confirm == 'y':
                        for idx in indexes:
                             if 0 <= idx < len(platforms):
                                platforms.pop(idx)
                        save_platforms(platforms, start_idx, end_idx, all_lines)
                        print(f"✅ 已删除 {len(to_delete)} 个平台")
                    else:
                        print("🚫 已取消")
            except Exception as e:
                print(f"❌ 错误: {e}")
            input("按回车继续...")
            
        else:
            print("⚠️ 无效的输入")
            input("按回车继续...")

def manual_run_now():
    print_header()
    print("🚀 正在立即运行一次抓取任务...")
    print("-" * 40)
    try:
        # 切换到 /app 目录运行，确保相对路径正确
        subprocess.run("cd /app && /usr/local/bin/python main.py", shell=True)
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
    
    print("-" * 40)
    input("\n按回车键返回主菜单...")

def main():
    while True:
        print_header()
        print("1. ⏱️  修改抓取频率 (定时任务)")
        print("2. 📝 管理关键词 (按组管理)")
        print("3. 📺 管理监控平台 (增删)")
        print("4. 🔔 修改配置文件 (通知/Webhook)")
        print("5. ▶️  立即手动运行一次")
        print("0. 🚪 退出")
        
        choice = input("\n请输入选项 [0-5]: ")
        
        if choice == '1': manage_cron()
        elif choice == '2': manage_keywords()
        elif choice == '3': manage_platforms()
        elif choice == '4': manage_notification()
        elif choice == '5': manual_run_now()
        elif choice == '0': sys.exit(0)

if __name__ == "__main__":
    main()
