#!/usr/bin/env python3
"""
Sub-Agent 执行验证和检查器
在 Sub-agent 完成时验证执行总结和功能状态

主要功能：
1. 监听 SubagentStop 事件
2. 读取 sub-agent 的对话历史和总结
3. 读取功能列表文件
4. 验证执行总结的完整性
5. 检查功能状态更新是否正确
6. 检查是否有功能遗漏或错误
7. 生成验证报告

AskUserQuestion 使用约束（重要！）：
============================

何时需要使用 AskUserQuestion 工具：
1. ✅ 检测到Sub-Agent产生幻觉时，需要用户确认如何处理
2. ✅ 发现功能状态不一致时，需要用户确认修正方案
3. ✅ 验证过程中发现Sub-Agent总结不完整时，需要用户补充信息
4. ✅ 检测到Sub-Agent声称创建的文件不存在时，需要用户确认
5. ✅ 验证规则需要用户确认或调整时
6. ✅ 任何需要用户输入或决策的场景

何时不使用 AskUserQuestion：
1. ❌ 文件存在性可以自动验证时
2. ❌ 功能完成度可以自动计算时
3. ❌ 幻觉检测可以自动完成时
4. ❌ 状态不一致可以自动识别时
5. ❌ 不需要用户输入就能完成验证时

优先级原则：
- 幻觉检测优先级最高：如果发现Sub-Agent声称创建不存在的文件或完成不在列表中的功能，
  必须立即阻止并报告，必要时使用AskUserQuestion确认如何处理
- 功能完整性次之：确保所有声称的功能都在功能列表中
- 状态一致性再次：确保功能状态标记与实际情况一致

注意：此Hook是自动执行的，如需与用户交互，请通过MCP工具调用AskUserQuestion
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Set

# 配置
SUMMARY_DIR = ".claude/feature-execution-summaries"
SUMMARY_INDEX_FILE = ".claude/feature-execution-summaries/index.md"
FEATURE_LIST_DIR = ".claude/task"

def ensure_summary_dir():
    """确保总结目录存在"""
    Path(SUMMARY_DIR).mkdir(parents=True, exist_ok=True)

def parse_feature_status(line: str) -> Tuple[str, str]:
    """
    解析功能状态行
    返回: (状态, 功能描述)
    """
    # 匹配格式: [ ] 功能描述 或 [✓] 功能描述 或 [→] 功能描述
    match = re.match(r'^(\[([✓→ ])\])\s*(.+)$', line.strip())
    if match:
        status = match.group(2)
        description = match.group(3).strip()
        return status, description
    return None, None

def read_feature_list_file(filepath: str) -> List[Dict]:
    """
    读取功能列表文件
    返回: [{'status': '✓', 'description': '...', 'file': '...', 'line': ...}]
    """
    features = []

    if not os.path.exists(filepath):
        return features

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        line = line.rstrip('\n')

        # 跳过空行和注释
        if not line.strip() or line.strip().startswith('#'):
            continue

        # 检查是否是功能行（包含 [ ] 或 [✓] 或 [→]）
        if '[' in line and ']' in line and (' [' in line or line.startswith('[')):
            status, description = parse_feature_status(line)
            if status and description:
                features.append({
                    'status': status,
                    'description': description,
                    'file': filepath,
                    'line': line_num
                })

    return features

def read_all_feature_lists() -> List[Dict]:
    """
    读取所有功能列表文件（主文件和子文件）
    返回: 所有功能的列表
    """
    all_features = []

    # 读取主文件
    main_file = os.path.join(FEATURE_LIST_DIR, 'main_feature_list.md')
    main_features = read_feature_list_file(main_file)

    # 处理主文件中的子文件引用
    for feature in main_features:
        # 如果是子文件引用（如 [ ] sub_user_auth.md - 用户认证子模块）
        if feature['description'].endswith('.md'):
            sub_file = os.path.join(FEATURE_LIST_DIR, feature['description'].split(' - ')[0])
            if os.path.exists(sub_file):
                sub_features = read_feature_list_file(sub_file)
                all_features.extend(sub_features)
            else:
                # 如果子文件不存在，记录为引用
                all_features.append({
                    'status': feature['status'],
                    'description': feature['description'],
                    'file': feature['file'],
                    'line': feature['line'],
                    'is_subfile_reference': True
                })
        else:
            all_features.append(feature)

    return all_features

def verify_file_exists(file_path: str) -> bool:
    """
    验证文件是否真实存在
    """
    if not file_path:
        return False
    # 转换为绝对路径（相对于项目根目录）
    abs_path = os.path.join(os.getcwd(), file_path)
    return os.path.exists(abs_path)

def detect_hallucination(summary: Dict, all_features: List[Dict]) -> Dict:
    """
    检测 Sub-Agent 是否产生幻觉（声称完成但实际没完成的工作）

    返回: {
        'hallucinated_files': [...],  # 声称存在但实际不存在的文件
        'hallucinated_features': [...],  # 声称完成但实际没完成的功能
        'real_files': [...],  # 真实存在的文件
        'real_features': [...]  # 真实完成的功能
    }
    """
    hallucinated_files = []
    real_files = []
    hallucinated_features = []

    # 验证声称的文件是否真实存在
    for file_path in summary['modified_files']:
        if verify_file_exists(file_path):
            real_files.append(file_path)
        else:
            hallucinated_files.append(file_path)

    # 验证声称的功能是否在功能列表中
    summary_features = set(summary['completed_features'])
    real_features_in_list = []
    for feature in all_features:
        if feature['status'] == '✓' and not feature.get('is_subfile_reference'):
            real_features_in_list.append(feature['description'])

    # 检测声称完成但实际不在功能列表中的功能
    for feature in summary['completed_features']:
        if feature not in real_features_in_list:
            hallucinated_features.append(feature)

    return {
        'hallucinated_files': hallucinated_files,
        'real_files': real_files,
        'hallucinated_features': hallucinated_features,
        'real_features': real_features_in_list
    }

def extract_summary_from_transcript(messages: List[Dict]) -> Dict:
    """
    从对话历史中提取 Sub-Agent 的执行总结
    返回: {'task': '...', 'completed_features': [...], 'modified_files': [...]}
    """
    task_description = ""
    completed_features = set()
    modified_files = set()
    key_decisions = []
    errors = []

    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')

        if role == 'user':
            # 提取任务描述
            if 'Execute feature:' in content or '执行功能:' in content:
                task_description = content.replace('Execute feature:', '').replace('执行功能:', '').strip()
            elif not task_description:
                task_description = content[:200]

        elif role == 'assistant':
            # 提取已完成的功能
            patterns = [
                r'已完成[：:\s]*(.+?)(?:\n|$)',
                r'完成[了]?[:：]\s*(.+?)(?:\n|$)',
                r'✓\s*(.+?)(?:\n|$)',
                r'已实现[：:]\s*(.+?)(?:\n|$)',
                r'已创建[：:]\s*(.+?)(?:\n|$)',
                r'已添加[：:]\s*(.+?)(?:\n|$)',
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    completed_features.add(match.strip())

            # 提取修改的文件
            file_patterns = [
                r'修改的文件[：:\s]*(.+?)(?:\n|$)',
                r'创建的文件[：:\s]*(.+?)(?:\n|$)',
                r'编辑的文件[：:\s]*(.+?)(?:\n|$)',
                r'文件路径[：:\s]*(.+?)(?:\n|$)',
            ]
            for pattern in file_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    files = re.split(r'[,\s]+', match)
                    for file_path in files:
                        file_path = file_path.strip()
                        if file_path and ('.py' in file_path or '.js' in file_path or
                                         '.ts' in file_path or '.java' in file_path or
                                         '.md' in file_path or '.html' in file_path or
                                         '.css' in file_path or '.json' in file_path):
                            modified_files.add(file_path)

            # 提取关键决策和错误
            if '决策' in content or '注意' in content or '重要' in content:
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if '决策' in para or '注意' in para or '重要' in para:
                        key_decisions.append(para.strip())

            if '错误' in content or '失败' in content or 'Error' in content or 'Failed' in content:
                errors.append(content.strip())

    return {
        'task': task_description,
        'completed_features': list(completed_features),
        'modified_files': list(modified_files),
        'key_decisions': key_decisions,
        'errors': errors
    }

def verify_feature_completion(summary: Dict, all_features: List[Dict]) -> Dict:
    """
    验证功能完成情况
    返回: 验证结果
    """
    summary_features = set(summary['completed_features'])
    feature_descriptions = {f['description'] for f in all_features if not f.get('is_subfile_reference')}

    # 检查总结中提到的功能是否在功能列表中
    not_in_list = summary_features - feature_descriptions
    in_list = feature_descriptions

    # 检查功能列表中是否有未完成的
    completed_in_list = {f['description'] for f in all_features if f['status'] == '✓'}
    not_completed = in_list - completed_in_list

    # 检查状态更新
    status_issues = []
    for feature in all_features:
        if feature['status'] == '✓' and feature['description'] not in summary_features:
            status_issues.append({
                'type': 'status_mismatch',
                'feature': feature['description'],
                'issue': '功能状态标记为已完成，但总结中未提及'
            })
        elif feature['status'] == ' ' and feature['description'] in summary_features:
            status_issues.append({
                'type': 'status_mismatch',
                'feature': feature['description'],
                'issue': '总结中提及功能已完成，但状态未更新'
            })

    return {
        'not_in_list': list(not_in_list),
        'completed_features': list(completed_in_list),
        'not_completed': list(not_completed),
        'status_issues': status_issues
    }

def collect_subagent_summary():
    """收集并验证 Sub-Agent 的执行总结"""
    try:
        # 从 stdin 读取 hook 数据
        input_data = json.load(sys.stdin)

        # 提取 sub-agent 信息
        agent_id = input_data.get('agentId', 'unknown')
        agent_type = input_data.get('agent_type', 'unknown')
        agent_description = input_data.get('description', '')

        # 获取 sub-agent 的对话历史
        agent_transcript_file = f".claude/agent-{agent_id}.jsonl"

        if not os.path.exists(agent_transcript_file):
            print(f"No transcript found for agent {agent_id}", file=sys.stderr)
            return

        # 读取对话历史
        messages = []
        with open(agent_transcript_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    message = json.loads(line)
                    messages.append(message)
                except:
                    continue

        # 提取 Sub-Agent 的总结
        summary = extract_summary_from_transcript(messages)

        # 读取所有功能列表
        all_features = read_all_feature_lists()

        # 验证功能完成情况
        verification = verify_feature_completion(summary, all_features)

        # 检测幻觉（声称但实际不存在的工作）
        hallucination = detect_hallucination(summary, all_features)

        # 统计功能状态
        completed_count = sum(1 for f in all_features if f['status'] == '✓')
        in_progress_count = sum(1 for f in all_features if f['status'] == '→')
        pending_count = sum(1 for f in all_features if f['status'] == ' ')
        total_count = len(all_features)

        # 生成验证报告文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"verification-{agent_id}-{timestamp}.md"
        report_filepath = os.path.join(SUMMARY_DIR, report_filename)

        # 生成验证报告
        with open(report_filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Sub-Agent 执行验证报告\n\n")
            f.write(f"**Agent ID**: `{agent_id}`\n")
            f.write(f"**Agent Type**: `{agent_type}`\n")
            f.write(f"**Agent Description**: {agent_description}\n")
            f.write(f"**验证时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if summary['task']:
                f.write(f"## 执行任务\n\n{summary['task']}\n\n")

            # 验证结果概览
            f.write("## 验证结果概览\n\n")
            f.write(f"✅ **验证状态**: ")

            has_issues = (verification['not_in_list'] or
                         verification['status_issues'] or
                         verification['not_completed'] or
                         hallucination['hallucinated_files'] or
                         hallucination['hallucinated_features'])

            # 如果有幻觉，标记为严重问题
            if hallucination['hallucinated_files'] or hallucination['hallucinated_features']:
                f.write("❌ 发现幻觉（严重问题）\n\n")
            elif has_issues:
                f.write("⚠️ 发现问题\n\n")
            else:
                f.write("✅ 验证通过\n\n")

            # 功能状态统计
            f.write("### 功能状态统计\n\n")
            f.write(f"- ✅ **已完成**: {completed_count} 个\n")
            f.write(f"- 🔄 **进行中**: {in_progress_count} 个\n")
            f.write(f"- ⏳ **待执行**: {pending_count} 个\n")
            f.write(f"- 📊 **总功能数**: {total_count} 个\n\n")

            if total_count > 0:
                completion_rate = (completed_count / total_count) * 100
                f.write(f"**完成率**: {completion_rate:.1f}%\n\n")

            # 【重点】幻觉检测（防止Sub-Agent胡说八道）
            if hallucination['hallucinated_files'] or hallucination['hallucinated_features']:
                f.write("### ❌ 问题 0: 检测到幻觉（严重问题！）\n\n")
                f.write("⚠️ **严重问题**：Sub-Agent 声称完成了不存在的工作！这是幻觉。\n\n")

                if hallucination['hallucinated_files']:
                    f.write(f"**幻觉文件**（声称创建但实际不存在）：**{len(hallucination['hallucinated_files'])}** 个\n")
                    for file_path in hallucination['hallucinated_files']:
                        f.write(f"  - ❌ `{file_path}` (不存在)\n")
                    f.write("\n")

                if hallucination['hallucinated_features']:
                    f.write(f"**幻觉功能**（声称完成但实际不在功能列表中）：**{len(hallucination['hallucinated_features'])}** 个\n")
                    for feature in hallucination['hallucinated_features']:
                        f.write(f"  - ❌ {feature} (不在功能列表)\n")
                    f.write("\n")

                f.write("⚠️ **警告**：这些是 Sub-Agent 的幻觉（声称但实际没做的工作）。\n")
                f.write("请让 Sub-Agent 重新检查工作，删除所有幻觉内容。\n\n")

            # 【重点】文件真实性验证
            f.write("### ✅ 文件真实性验证\n\n")
            if hallucination['real_files']:
                f.write(f"✅ **真实存在的文件**：{len(hallucination['real_files'])} 个\n")
                for file_path in hallucination['real_files'][:5]:  # 只显示前5个
                    f.write(f"  - ✅ `{file_path}` (存在)\n")
                if len(hallucination['real_files']) > 5:
                    f.write(f"  - ... 还有 {len(hallucination['real_files']) - 5} 个文件\n")
                f.write("\n")
            else:
                f.write("⚠️ 未检测到任何文件（可能 Sub-Agent 没有创建或修改文件）\n\n")

            if hallucination['hallucinated_files']:
                f.write(f"❌ **幻觉文件**：{len(hallucination['hallucinated_files'])} 个\n")
                for file_path in hallucination['hallucinated_files']:
                    f.write(f"  - ❌ `{file_path}` (不存在)\n")
                f.write("\n")

            # Sub-Agent 提到的功能
            if summary['completed_features']:
                f.write("### Sub-Agent 声称完成的功能\n\n")
                for feature in summary['completed_features']:
                    f.write(f"- {feature}\n")
                f.write("\n")

            # 验证问题
            if verification['not_in_list']:
                f.write("### ⚠️ 问题 1: 总结中的功能不在功能列表中\n\n")
                f.write("以下功能在 Sub-Agent 总结中提到，但不在功能列表中：\n\n")
                for feature in verification['not_in_list']:
                    f.write(f"- {feature}\n")
                f.write("\n")

            if verification['not_completed']:
                f.write("### ⚠️ 问题 2: 功能列表中有未完成的功能\n\n")
                f.write("以下功能仍在功能列表中标记为未完成：\n\n")
                for feature in verification['not_completed']:
                    f.write(f"- {feature}\n")
                f.write("\n")

            if verification['status_issues']:
                f.write("### ⚠️ 问题 3: 功能状态不一致\n\n")
                for issue in verification['status_issues']:
                    f.write(f"- **{issue['feature']}**: {issue['issue']}\n")
                f.write("\n")

            # 修改的文件
            if summary['modified_files']:
                f.write("### 📝 修改的文件\n\n")
                for file_path in sorted(summary['modified_files']):
                    f.write(f"- `{file_path}`\n")
                f.write("\n")

            # 关键决策
            if summary['key_decisions']:
                f.write("### 📌 关键决策\n\n")
                for decision in summary['key_decisions']:
                    f.write(f"{decision}\n\n")

            # 错误和警告
            if summary['errors']:
                f.write("### ❌ 错误和警告\n\n")
                for error in summary['errors']:
                    f.write(f"{error}\n\n")

            # 验证结论
            f.write("### 验证结论\n\n")
            if not has_issues:
                f.write("✅ **验证通过**：所有功能状态正确，无发现问题。\n\n")
            else:
                f.write("⚠️ **发现问题**：请检查上述问题并修正。\n\n")

        # 更新索引文件
        update_index(report_filename, agent_id, agent_type, summary['task'],
                    has_issues, completed_count, total_count)

        print(f"✓ Verification report saved: {report_filepath}")

        # 输出验证结果到 stderr（供日志记录）
        if has_issues:
            print(f"⚠️ 验证发现问题", file=sys.stderr)
            if verification['not_in_list']:
                print(f"  - {len(verification['not_in_list'])} 个功能不在列表中", file=sys.stderr)
            if verification['status_issues']:
                print(f"  - {len(verification['status_issues'])} 个状态不一致", file=sys.stderr)
            if verification['not_completed']:
                print(f"  - {len(verification['not_completed'])} 个功能未完成", file=sys.stderr)
        else:
            print(f"✅ 验证通过", file=sys.stderr)

        # 输出 JSON 决策（必需）
        # 【重点】幻觉检测优先级最高
        if hallucination['hallucinated_files'] or hallucination['hallucinated_features']:
            # 检测到幻觉 - 严重问题，必须阻止
            output = {
                "decision": "block",
                "reason": f"❌ 严重问题：检测到幻觉！Sub-Agent 声称创建了 {len(hallucination['hallucinated_files'])} 个不存在的文件，声称完成了 {len(hallucination['hallucinated_features'])} 个不在功能列表中的功能。这是幻觉，必须删除所有虚假内容。"
            }
        elif has_issues:
            # 其他问题 - 允许继续但记录
            output = {
                "decision": "allow",
                "reason": f"验证发现问题：已完成 {completed_count}/{total_count} 个功能"
            }
        else:
            # 全部通过
            output = {
                "decision": "allow",
                "reason": "✅ 验证通过：所有功能完成且无幻觉"
            }

        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        print(f"Error in verification: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

def update_index(report_filename: str, agent_id: str, agent_type: str,
                task_description: str, has_issues: bool, completed: int, total: int):
    """更新验证报告索引"""
    ensure_summary_dir()

    index_entries = []
    if os.path.exists(SUMMARY_INDEX_FILE):
        with open(SUMMARY_INDEX_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # 提取现有的条目
            if '\n' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('- ['):
                        # 找到下一个验证块
                        j = i
                        while j < len(lines) and (lines[j].startswith('- [') or
                                                 lines[j].startswith('  →') or
                                                 lines[j].startswith('  ⚠') or
                                                 lines[j].startswith('  ✅')):
                            j += 1
                        index_entries.append('\n'.join(lines[i:j]))

    # 添加新条目
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    short_task = task_description[:50] + "..." if len(task_description) > 50 else task_description
    completion_rate = (completed / total * 100) if total > 0 else 0
    status = "⚠️ 有问题" if has_issues else "✅ 验证通过"

    new_entry = f"- [{timestamp}] `{agent_type}` ({agent_id[:8]}...) - {short_task}\n"
    new_entry += f"  → {status}: {completed}/{total} ({completion_rate:.0f}%)\n"
    new_entry += f"  → [{report_filename}]()\n"

    # 重新生成索引文件
    with open(SUMMARY_INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write("# Sub-Agent 执行验证报告索引\n\n")
        f.write("**说明**: 所有验证报告按时间倒序排列\n\n")
        f.write("## 验证记录\n\n")
        f.write(new_entry)
        f.writelines(index_entries)
        f.write("\n---\n")
        f.write(f"*最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

if __name__ == "__main__":
    collect_subagent_summary()
