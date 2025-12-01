#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能验证器 Hook (Feature Validator)
用于Stop事件，验证功能完成度
- 检查main_feature_list.md和所有子功能列表
- 验证功能执行规则是否被遵守
- 如果功能未完成，返回block决策和原因
- 支持继续执行机制
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime

# 配置
TASK_LIST_DIR = ".claude/task"
MAIN_LIST_FILE = "main_feature_list.md"
PROGRESS_LOG_FILE = ".claude/claude-progress.txt"

# 功能状态定义
STATUS_NOT_STARTED = '[ ]'          # 未开始
STATUS_IN_PROGRESS = '[→]'          # 进行中
STATUS_COMPLETED = '[✓]'            # 已完成

def read_task_list(filepath):
    """读取任务列表文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return ""

def parse_tasks(content):
    """
    解析功能列表内容
    返回: (原始请求, 功能列表)
    """
    lines = content.split('\n')
    original_request = ""
    tasks = []

    # 提取原始请求（假设在第一个标题行）
    for line in lines:
        if line.startswith('# 用户原始需求：') or line.startswith('# 用户原始请求：'):
            original_request = line.split('：', 1)[-1].strip()
            break
        elif line.startswith('# '):
            original_request = line.replace('# ', '').strip()
            break

    # 提取功能（以 [ ] 开头的行）
    for line in lines:
        line = line.strip()
        # 匹配功能行：[ ] 或 [✓] 或 [→] 等
        match = re.match(r'^(\[[^\]]*\])\s*(.*)$', line)
        if match:
            status = match.group(1).strip()
            task = match.group(2).strip()
            # 跳过空的功能描述
            if task:
                tasks.append({
                    'status': status,
                    'task': task
                })

    return original_request, tasks

def check_subfile(filepath, parent_request, all_subfiles):
    """
    递归检查子文件中的功能
    返回: (完成数, 总数, 未完成功能列表)
    """
    content = read_task_list(filepath)
    if not content:
        return 0, 0, []

    original_request, tasks = parse_tasks(content)

    completed = 0
    total = len(tasks)
    incomplete_tasks = []
    in_progress_tasks = []

    for task in tasks:
        # 检查是否是子文件引用
        if task['task'].endswith('.md'):
            # 这是一个子文件引用，需要递归检查
            subfile_path = os.path.join(TASK_LIST_DIR, task['task'])
            if os.path.exists(subfile_path):
                sub_completed, sub_total, sub_incomplete = check_subfile(subfile_path, original_request, all_subfiles)
                completed += sub_completed
                total += sub_total
                incomplete_tasks.extend(sub_incomplete)
        else:
            # 普通功能
            status = task['status']
            if status == STATUS_COMPLETED:
                completed += 1
            elif status == STATUS_IN_PROGRESS:
                in_progress_tasks.append(task['task'])
            elif status == STATUS_NOT_STARTED:
                incomplete_tasks.append(task['task'])

    return completed, total, incomplete_tasks, in_progress_tasks

def validate_all_tasks():
    """验证所有功能是否完成"""
    main_list_path = os.path.join(TASK_LIST_DIR, MAIN_LIST_FILE)

    if not os.path.exists(main_list_path):
        print(f"Main feature list not found: {main_list_path}", file=sys.stderr)
        return None, None, None, [], []

    # 读取主列表
    content = read_task_list(main_list_path)
    original_request, tasks = parse_tasks(content)

    completed = 0
    total = 0
    incomplete_tasks = []
    in_progress_tasks = []

    # 首先处理主列表中的功能
    for task in tasks:
        # 检查是否是子文件引用
        if task['task'].endswith('.md'):
            subfile_path = os.path.join(TASK_LIST_DIR, task['task'])
            if os.path.exists(subfile_path):
                sub_completed, sub_total, sub_incomplete, sub_in_progress = check_subfile(subfile_path, original_request, tasks)
                completed += sub_completed
                total += sub_total
                incomplete_tasks.extend(sub_incomplete)
                in_progress_tasks.extend(sub_in_progress)
        else:
            # 普通功能
            status = task['status']
            if status == STATUS_COMPLETED:
                completed += 1
            elif status == STATUS_IN_PROGRESS:
                in_progress_tasks.append(task['task'])
            elif status == STATUS_NOT_STARTED:
                incomplete_tasks.append(task['task'])
            total += 1

    return original_request, completed, total, incomplete_tasks, in_progress_tasks

def generate_validation_message(original_request, completed, total, incomplete_tasks, in_progress_tasks):
    """生成验证消息（模块化验证）"""
    if total == 0:
        return "没有找到任何功能。"

    message_parts = []
    message_parts.append("功能验证结果（按模块验证）:")
    message_parts.append(f"  总功能数: {total}")
    message_parts.append(f"  已完成: {completed}")
    message_parts.append(f"  进行中: {len(in_progress_tasks)}")
    message_parts.append(f"  未开始: {len(incomplete_tasks)}")
    message_parts.append("")

    # 按模块分组显示
    modules = {}

    # 收集进行中的模块
    for task in in_progress_tasks:
        module = extract_module_name(task)
        if module:
            if module not in modules:
                modules[module] = {'in_progress': [], 'incomplete': []}
            modules[module]['in_progress'].append(task)

    # 收集未开始的模块
    for task in incomplete_tasks:
        module = extract_module_name(task)
        if module:
            if module not in modules:
                modules[module] = {'in_progress': [], 'incomplete': []}
            modules[module]['incomplete'].append(task)

    # 按模块显示
    if modules:
        message_parts.append("按模块状态:")
        for module_name in sorted(modules.keys()):
            module_info = modules[module_name]
            in_progress_count = len(module_info['in_progress'])
            incomplete_count = len(module_info['incomplete'])

            if in_progress_count > 0 or incomplete_count > 0:
                message_parts.append(f"  模块: {module_name}")
                if in_progress_count > 0:
                    message_parts.append(f"    进行中: {in_progress_count} 个功能")
                if incomplete_count > 0:
                    message_parts.append(f"    未开始: {incomplete_count} 个功能")
                    for i, task in enumerate(module_info['incomplete'][:3], 1):
                        message_parts.append(f"      {i}. {task}")
                    if len(module_info['incomplete']) > 3:
                        message_parts.append(f"      ... 还有 {len(module_info['incomplete']) - 3} 个")
        message_parts.append("")

    # 显示多级嵌套信息
    message_parts.append("多级嵌套信息:")
    level_stats = {}
    for task in incomplete_tasks + in_progress_tasks:
        level = get_nesting_level(task)
        if level not in level_stats:
            level_stats[level] = {'incomplete': 0, 'in_progress': 0}
        if task in incomplete_tasks:
            level_stats[level]['incomplete'] += 1
        else:
            level_stats[level]['in_progress'] += 1

    if level_stats:
        for level in sorted(level_stats.keys()):
            level_name = ['主文件', 'Level 1', 'Level 2', 'Level 3', 'Level 4'][level] if level < 5 else f'Level {level}'
            stats = level_stats[level]
            if stats['incomplete'] > 0 or stats['in_progress'] > 0:
                message_parts.append(f"  {level_name}: {stats['in_progress']} 进行中, {stats['incomplete']} 未开始")

    message_parts.append("")

    # 显示未开始的功能（前5个）
    if incomplete_tasks:
        message_parts.append("未开始的功能:")
        for i, task in enumerate(incomplete_tasks[:5], 1):
            message_parts.append(f"  {i}. {task}")
        if len(incomplete_tasks) > 5:
            message_parts.append(f"  ... 还有 {len(incomplete_tasks) - 5} 个功能未开始")
        message_parts.append("")

    # 显示进行中的功能（前5个）
    if in_progress_tasks:
        message_parts.append("正在进行的功能:")
        for i, task in enumerate(in_progress_tasks[:5], 1):
            message_parts.append(f"  {i}. {task}")
        if len(in_progress_tasks) > 5:
            message_parts.append(f"  ... 还有 {len(in_progress_tasks) - 5} 个功能正在进行")
        message_parts.append("")

    return "\n".join(message_parts)

def extract_module_name(task):
    """从功能描述中动态提取模块名称"""
    if '.md' not in task:
        return None

    # 方法1: 从描述中提取模块名称（动态）
    # 格式: "sub_xxx.md - 模块名称"
    if ' - ' in task:
        parts = task.split(' - ')
        if len(parts) >= 2:
            # 返回用户定义的模块名称
            module_name = parts[1].strip()
            if module_name:
                return module_name

    # 方法2: 从文件名中智能提取（动态）
    # 格式: "sub_module_name.md" -> "模块名称"
    filename = task.split(' - ')[0].strip() if ' - ' in task else task.strip()

    # 移除.md后缀
    filename = filename.replace('.md', '')

    # 提取模块名（去掉sub_前缀）
    if filename.startswith('sub_'):
        # sub_user_management -> user_management
        module_name = filename[4:]  # 去掉'sub_'
        # 转换为友好格式
        module_name = module_name.replace('_', ' ').title()
        return module_name

    # 方法3: 如果没有前缀，直接返回
    return filename.replace('_', ' ').title()

def get_nesting_level(task):
    """获取任务的嵌套级别"""
    if '.md' in task:
        # main_feature_list.md -> Level 0
        # sub_xxx.md -> Level 1
        # sub_xxx_yyy.md -> Level 2
        # sub_xxx_yyy_zzz.md -> Level 3
        if task.startswith('sub_'):
            parts = task.replace('.md', '').split('_')
            return len(parts) - 1
    return 0

def get_nesting_path(task):
    """获取任务的嵌套路径"""
    if '.md' in task:
        parts = task.replace('.md', '').split('_')
        path = []
        for i, part in enumerate(parts):
            if i > 0:  # 跳过'sub'
                path.append(part)
        return ' > '.join(path)
    return 'main'

def main():
    """主函数"""
    try:
        # 验证所有功能
        original_request, completed, total, incomplete_tasks, in_progress_tasks = validate_all_tasks()

        # 如果没有功能列表，不阻塞
        if original_request is None:
            print("No feature list found, continuing execution")
            sys.exit(0)

        # 如果还有未完成的功能，返回block决策
        if completed < total or in_progress_tasks or incomplete_tasks:
            # 生成详细的原因说明
            validation_msg = generate_validation_message(
                original_request, completed, total, incomplete_tasks, in_progress_tasks
            )

            # 构建输出（包含详细的执行规则）
            execution_rules = """
========================================
功能执行规则（必须遵守！）
========================================

1. 模块化执行（核心原则！）
   ✅ 按业务功能模块执行，不要跨模块
   ✅ 完成一个模块的所有功能，才能开始下一个模块
   ✅ 模块内部的功能也要按顺序执行
   ✅ 状态同步：子文件功能状态 ↔ 主文件模块状态

2. 主文件和子文件处理
   - 必须先读取 main_feature_list.md
   - 找到所有子功能文件（sub_user_management.md, sub_product_management.md等）
   - 确保所有功能都被完整执行

3. 模块执行顺序
   严格按照主文件中的模块顺序执行：
   用户管理模块 → 商品管理模块 → 订单管理模块 → 支付系统模块 →
   通知系统模块 → 管理后台模块 → 部署运维模块
   - 不要跳过模块
   - 按顺序执行每个模块

4. 代码实现规则
   ❌ 不要省略任何逻辑
   ❌ 不要使用批量脚本复制类（cp, copy等命令）
   ❌ 不要因篇幅有限就省略方法实现
   ❌ 不要使用省略标记（// TODO, # ...）

   每个类都要逐个分析和修改
   每个方法都要完整实现

5. 功能状态管理
   状态转换规则：
   [ ]  →  [→]  →  [✓]
   (未开始) (进行中) (已完成)

   开始执行时: [ ] → [→]
   完成时: [→] → [✓]
   不要跳过任何状态转换

6. 状态更新责任（必须执行！）
   模型必须在执行过程中主动更新功能列表中的状态：

   **状态转换规则**：
   [ ]  →  [→]  →  [✓]
   (未开始) (进行中) (已完成)

   **何时更新状态**：
   - 开始执行一个功能时 → 立即改为 [→]
   - 完成一个功能时 → 立即改为 [✓]
   - 开始执行一个子模块时 → 立即改为 [→]
   - 完成一个子模块的所有功能时 → 立即改为 [✓]

   **如何更新状态**：
   使用 Edit 工具更新 .claude/task/ 目录下的所有 .md 文件

   **示例流程**：
   1. 读取 sub_xxx.md
   2. 找到 [ ] 某个任务
   3. 使用 Edit 改为 [→] 某个任务
   4. 执行该任务
   5. 读取上级文件
   6. 找到对应的引用状态
   7. 使用 Edit 更新上级状态

   **状态更新的重要性**：
   - ✅ 记录进度：让用户清楚知道哪些已完成
   - ✅ 避免重复：防止重复执行已完成的任务
   - ✅ 保持同步：确保子文件和父文件状态一致
   - ✅ 提供反馈：Stop hook会验证完成情况

7. 子文件处理
   - 如果功能超过20项，会自动创建子文件
   - 必须逐个处理子文件中的功能
   - 保持主文件和子文件的状态同步
   - 按模块完整执行，不要跨模块执行
"""

            # 构建输出
            output = {
                "decision": "block",
                "reason": f"""
========================================
{validation_msg}
原始请求: {original_request}

{execution_rules}

请继续执行未完成的功能，确保遵守以上所有规则！
========================================
"""
            }

            # 输出JSON并退出
            print(json.dumps(output, ensure_ascii=False, indent=2))
            sys.exit(0)
        else:
            # 所有功能已完成，不阻塞
            print(f"✓ All features completed: {completed}/{total}")
            sys.exit(0)

    except Exception as e:
        print(f"Error in task_validator: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(0)  # 出错时不阻塞

if __name__ == "__main__":
    main()
