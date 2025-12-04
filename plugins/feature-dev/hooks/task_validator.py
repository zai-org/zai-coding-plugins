#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能验证器 Hook (Feature Validator)
用于Stop事件，验证功能完成度

核心功能：
1. 递归检查所有层级的功能文件（主文件 + 子文件 + 子子文件...）
2. 完整检测所有功能状态（未开始、进行中、已完成）
3. 不遗漏任何未完成的功能
4. 提供详细的验证报告

AskUserQuestion 使用约束（重要！）：
============================

何时需要使用 AskUserQuestion 工具：
1. ✅ 验证过程中发现功能描述不清晰，需要用户确认
2. ✅ 检测到功能状态冲突，需要用户决定如何处理
3. ✅ 发现子文件缺失，需要用户确认是否创建
4. ✅ 验证规则需要用户确认或调整
5. ✅ 任何需要用户输入或决策的场景

何时不使用 AskUserQuestion：
1. ❌ 功能状态可以自动判断时
2. ❌ 文件存在性可以自动验证时
3. ❌ 功能完成度可以自动计算时
4. ❌ 不需要用户输入就能完成验证时

注意：此Hook是自动执行的，如需与用户交互，请通过MCP工具调用AskUserQuestion
"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Optional

# 配置
TASK_LIST_DIR = ".claude/task"
MAIN_LIST_FILE = "main_feature_list.md"
PROGRESS_LOG_FILE = ".claude/claude-progress.txt"

# 功能状态定义
STATUS_NOT_STARTED = '[ ]'          # 未开始
STATUS_IN_PROGRESS = '[→]'          # 进行中
STATUS_COMPLETED = '[✓]'            # 已完成

# 支持的状态模式
STATUS_PATTERNS = [
    r'^\[\s*\]',          # [ ] 未开始
    r'^\[\s*→\s*\]',      # [→] 进行中
    r'^\[\s*✓\s*\]',      # [✓] 已完成
    r'^\[\w+\]',          # [任何字符] 通用匹配
]

class FeatureItem:
    """功能项类"""
    def __init__(self, status: str, feature: str, level: int = 0, parent: Optional[str] = None):
        self.status = status
        self.feature = feature
        self.level = level  # 嵌套层级
        self.parent = parent  # 父功能
        self.is_subfile = feature.endswith('.md')

    def __repr__(self):
        return f"Feature(level={self.level}, status={self.status}, feature={self.feature[:30]}...)"

class FeatureValidator:
    """功能验证器"""

    def __init__(self):
        self.all_features: List[FeatureItem] = []
        self.subfiles_found: List[str] = []
        self.incomplete_features: List[FeatureItem] = []
        self.in_progress_features: List[FeatureItem] = []
        self.completed_features: List[FeatureItem] = []

    def read_file(self, filepath: str) -> str:
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            return ""

    def parse_features_from_content(self, content: str, level: int = 0, parent: Optional[str] = None) -> List[FeatureItem]:
        """
        从文件内容解析功能
        返回: FeatureItem列表
        """
        features = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith('#'):
                continue

            # 匹配功能状态
            for pattern in STATUS_PATTERNS:
                match = re.match(pattern, line)
                if match:
                    status = match.group(0)

                    # 提取功能描述（去除状态标记）
                    feature_desc = line[len(status):].strip()

                    # 如果是子文件引用，特殊处理
                    if feature_desc.endswith('.md'):
                        feature = feature_desc
                    else:
                        feature = feature_desc

                    # 创建功能项
                    feature_item = FeatureItem(status, feature, level, parent)
                    features.append(feature_item)

                    # 如果是子文件，记录
                    if feature_item.is_subfile:
                        self.subfiles_found.append(feature)

                    break

        return features

    def validate_all_features(self) -> Tuple[Optional[str], int, int, List[FeatureItem], List[FeatureItem], List[FeatureItem]]:
        """
        验证所有功能
        返回: (原始请求, 已完成数, 总数, 未完成功能, 进行中功能, 已完成功能)
        """
        main_list_path = os.path.join(TASK_LIST_DIR, MAIN_LIST_FILE)

        # 检查主文件是否存在
        if not os.path.exists(main_list_path):
            print(f"Main feature list not found: {main_list_path}", file=sys.stderr)
            return None, 0, 0, [], [], []

        # 读取主文件
        content = self.read_file(main_list_path)
        if not content:
            print("Main feature list is empty", file=sys.stderr)
            return None, 0, 0, [], [], []

        # 解析主文件
        main_features = self.parse_features_from_content(content, level=0)

        # 提取原始请求
        original_request = self.extract_original_request(content)

        # 递归检查所有文件
        self.check_recursive(main_features, level=0)

        # 统计结果
        completed = len(self.completed_features)
        total = len(self.all_features)

        return original_request, completed, total, self.incomplete_features, self.in_progress_features, self.completed_features

    def extract_original_request(self, content: str) -> str:
        """提取原始请求"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# 用户原始需求：') or line.startswith('# 用户原始请求：'):
                return line.split('：', 1)[-1].strip()
            elif line.startswith('# '):
                return line.replace('# ', '').strip()
        return "Unknown request"

    def check_recursive(self, features: List[FeatureItem], level: int = 0) -> None:
        """
        递归检查功能列表
        level: 当前嵌套层级（0=主文件，1=第一级子文件，2=第二级子文件...）
        """
        for feature_item in features:
            # 添加到总功能列表
            self.all_features.append(feature_item)

            # 根据状态分类
            if feature_item.status == STATUS_COMPLETED:
                self.completed_features.append(feature_item)
            elif feature_item.status == STATUS_IN_PROGRESS:
                self.in_progress_features.append(feature_item)
            elif feature_item.status == STATUS_NOT_STARTED:
                self.incomplete_features.append(feature_item)

            # 如果是子文件，递归检查
            if feature_item.is_subfile:
                subfile_path = os.path.join(TASK_LIST_DIR, feature_item.feature)

                # 检查文件是否存在
                if not os.path.exists(subfile_path):
                    print(f"Warning: Subfile not found: {subfile_path}", file=sys.stderr)
                    # 将缺失的子文件标记为未完成
                    missing_feature = FeatureItem(STATUS_NOT_STARTED, f"子文件缺失: {feature_item.feature}", level + 1, feature_item.feature)
                    self.incomplete_features.append(missing_feature)
                    self.all_features.append(missing_feature)
                    continue

                # 读取子文件
                subfile_content = self.read_file(subfile_path)
                if not subfile_content:
                    print(f"Warning: Subfile is empty: {subfile_path}", file=sys.stderr)
                    empty_feature = FeatureItem(STATUS_NOT_STARTED, f"子文件为空: {feature_item.feature}", level + 1, feature_item.feature)
                    self.incomplete_features.append(empty_feature)
                    self.all_features.append(empty_feature)
                    continue

                # 解析子文件功能
                sub_features = self.parse_features_from_content(subfile_content, level + 1, feature_item.feature)

                # 递归检查子文件
                self.check_recursive(sub_features, level + 1)

    def get_module_statistics(self) -> Dict[str, Dict]:
        """获取模块级别的统计信息"""
        modules = {}

        for feature in self.incomplete_features + self.in_progress_features:
            module = self.extract_module_name(feature)
            if module not in modules:
                modules[module] = {
                    'incomplete': [],
                    'in_progress': [],
                    'total': 0
                }

            if feature in self.incomplete_features:
                modules[module]['incomplete'].append(feature)
            elif feature in self.in_progress_features:
                modules[module]['in_progress'].append(feature)

            modules[module]['total'] = len(modules[module]['incomplete']) + len(modules[module]['in_progress'])

        return modules

    def extract_module_name(self, feature: FeatureItem) -> str:
        """从功能中提取模块名称"""
        feature_str = feature.feature

        # 如果是子文件引用
        if feature_str.endswith('.md'):
            # 格式: "sub_xxx.md - 模块名称"
            if ' - ' in feature_str:
                parts = feature_str.split(' - ')
                if len(parts) >= 2:
                    module_name = parts[1].strip()
                    if module_name:
                        return module_name

            # 从文件名提取
            filename = feature_str.split(' - ')[0].strip() if ' - ' in feature_str else feature_str
            filename = filename.replace('.md', '')

            if filename.startswith('sub_'):
                module_name = filename[4:]  # 去掉'sub_'
                return module_name.replace('_', ' ').title()

            return filename.replace('_', ' ').title()

        # 普通功能
        return "其他"

    def generate_validation_report(self, original_request: str, completed: int, total: int) -> str:
        """生成验证报告"""
        if total == 0:
            return "没有找到任何功能。"

        report_parts = []

        # 总体统计
        report_parts.append("=" * 80)
        report_parts.append("功能验证报告（完整性检查）")
        report_parts.append("=" * 80)
        report_parts.append(f"原始请求: {original_request}")
        report_parts.append(f"总功能数: {total}")
        report_parts.append(f"已完成: {completed}")
        report_parts.append(f"进行中: {len(self.in_progress_features)}")
        report_parts.append(f"未开始: {len(self.incomplete_features)}")
        report_parts.append(f"完成率: {(completed/total*100):.1f}%" if total > 0 else "0%")
        report_parts.append("")

        # 按模块统计
        modules = self.get_module_statistics()
        if modules:
            report_parts.append("按模块统计（未完成/进行中）:")
            for module_name in sorted(modules.keys()):
                module_info = modules[module_name]
                if module_info['total'] > 0:
                    report_parts.append(f"  {module_name}:")
                    if module_info['incomplete']:
                        report_parts.append(f"    未开始: {len(module_info['incomplete'])} 个")
                        for i, feature in enumerate(module_info['incomplete'][:3], 1):
                            report_parts.append(f"      {i}. {feature.feature}")
                        if len(module_info['incomplete']) > 3:
                            report_parts.append(f"      ... 还有 {len(module_info['incomplete']) - 3} 个")
                    if module_info['in_progress']:
                        report_parts.append(f"    进行中: {len(module_info['in_progress'])} 个")
                        for i, feature in enumerate(module_info['in_progress'][:3], 1):
                            report_parts.append(f"      {i}. {feature.feature}")
                        if len(module_info['in_progress']) > 3:
                            report_parts.append(f"      ... 还有 {len(module_info['in_progress']) - 3} 个")
                    report_parts.append("")

        # 按层级统计
        level_stats = {}
        for feature in self.all_features:
            level = feature.level
            if level not in level_stats:
                level_stats[level] = {'total': 0, 'completed': 0, 'in_progress': 0, 'incomplete': 0}

            level_stats[level]['total'] += 1

            if feature.status == STATUS_COMPLETED:
                level_stats[level]['completed'] += 1
            elif feature.status == STATUS_IN_PROGRESS:
                level_stats[level]['in_progress'] += 1
            elif feature.status == STATUS_NOT_STARTED:
                level_stats[level]['incomplete'] += 1

        report_parts.append("按层级统计:")
        for level in sorted(level_stats.keys()):
            level_name = ['主文件', 'Level 1', 'Level 2', 'Level 3', 'Level 4+'][level] if level < 5 else f'Level {level}'
            stats = level_stats[level]
            if stats['total'] > 0:
                report_parts.append(f"  {level_name}: {stats['completed']}/{stats['total']} 已完成 "
                                  f"({stats['in_progress']} 进行中, {stats['incomplete']} 未开始)")
        report_parts.append("")

        # 详细未完成功能列表（所有）
        if self.incomplete_features:
            report_parts.append("未完成的功能详情:")
            for i, feature in enumerate(self.incomplete_features, 1):
                level_indicator = "  " * feature.level
                report_parts.append(f"{i}. [{level_indicator}]{feature.feature}")
            report_parts.append("")

        # 详细进行中功能列表
        if self.in_progress_features:
            report_parts.append("进行中的功能详情:")
            for i, feature in enumerate(self.in_progress_features, 1):
                level_indicator = "  " * feature.level
                report_parts.append(f"{i}. [{level_indicator}]{feature.feature}")
            report_parts.append("")

        # 完整性检查
        report_parts.append("=" * 80)
        report_parts.append("完整性检查:")
        report_parts.append("=" * 80)

        # 检查是否有子文件
        subfiles = [f for f in self.all_features if f.is_subfile]
        if subfiles:
            report_parts.append(f"✓ 发现 {len(subfiles)} 个子文件")
            missing_subfiles = []
            for subfile_feature in subfiles:
                subfile_path = os.path.join(TASK_LIST_DIR, subfile_feature.feature)
                if not os.path.exists(subfile_path):
                    missing_subfiles.append(subfile_feature.feature)

            if missing_subfiles:
                report_parts.append(f"✗ 缺失 {len(missing_subfiles)} 个子文件:")
                for subfile in missing_subfiles:
                    report_parts.append(f"  - {subfile}")
            else:
                report_parts.append("✓ 所有子文件都存在")

        # 检查功能状态
        if len(self.incomplete_features) == 0 and len(self.in_progress_features) == 0:
            report_parts.append("✓ 所有功能已完成")
        else:
            if len(self.incomplete_features) > 0:
                report_parts.append(f"✗ 有 {len(self.incomplete_features)} 个功能未开始")
            if len(self.in_progress_features) > 0:
                report_parts.append(f"! 有 {len(self.in_progress_features)} 个功能正在进行")

        report_parts.append("=" * 80)

        return "\n".join(report_parts)

    def generate_execution_rules(self) -> str:
        """生成执行规则"""
        rules = """
========================================
功能执行规则（必须遵守！）
========================================

1. 完整性检查（最高优先级！）
   ✅ 必须检查所有层级的文件（主文件 + 所有子文件 + 子子文件...）
   ✅ 必须检测所有功能状态（未开始、进行中、已完成）
   ✅ 不遗漏任何未完成的功能
   ✅ 确保所有子文件都存在

2. 模块化执行（核心原则！）
   ✅ 按业务功能模块执行，不要跨模块
   ✅ 完成一个模块的所有功能，才能开始下一个模块
   ✅ 模块内部的功能也要按顺序执行
   ✅ 状态同步：子文件功能状态 ↔ 主文件模块状态

3. 主文件和子文件处理
   - 必须先读取 main_feature_list.md
   - 找到所有子功能文件（sub_user_management.md, sub_product_management.md等）
   - 递归检查所有层级的子文件（子文件的子文件也要检查）
   - 确保所有功能都被完整执行
   - 如果发现缺失的子文件，必须立即报告

4. 模块执行顺序
   严格按照主文件中的模块顺序执行：
   用户管理模块 → 商品管理模块 → 订单管理模块 → 支付系统模块 →
   通知系统模块 → 管理后台模块 → 部署运维模块
   - 不要跳过模块
   - 按顺序执行每个模块

5. 代码实现规则
   ❌ 不要省略任何逻辑
   ❌ 不要使用批量脚本复制类（cp, copy等命令）
   ❌ 不要因篇幅有限就省略方法实现
   ❌ 不要使用省略标记（// TODO, # ...）

   每个类都要逐个分析和修改
   每个方法都要完整实现

6. 功能状态管理（严格！）
   状态转换规则：
   [ ]  →  [→]  →  [✓]
   (未开始) (进行中) (已完成)

   何时更新状态：
   - 开始执行一个功能时 → 立即改为 [→]
   - 完成一个功能时 → 立即改为 [✓]
   - 开始执行一个子模块时 → 立即改为 [→]
   - 完成一个子模块的所有功能时 → 立即改为 [✓]

   如何更新状态：
   使用 Edit 工具更新 .claude/task/ 目录下的所有 .md 文件

7. 状态更新责任（必须执行！）
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

   **状态更新的重要性**：
   - ✅ 记录进度：让用户清楚知道哪些已完成
   - ✅ 避免重复：防止重复执行已完成的任务
   - ✅ 保持同步：确保子文件和父文件状态一致
   - ✅ 提供反馈：Stop hook会验证完成情况

8. 子文件处理（递归！）
   - 如果功能超过20项，会自动创建子文件
   - 必须逐个处理子文件中的功能
   - 如果子文件中还有子文件，也要递归处理
   - 保持主文件和所有层级子文件的状态同步
   - 按模块完整执行，不要跨模块执行
"""
        return rules

def main():
    """主函数"""
    try:
        # 创建验证器
        validator = FeatureValidator()

        # 验证所有功能
        original_request, completed, total, incomplete, in_progress, completed_features = validator.validate_all_features()

        # 如果没有功能列表，不阻塞
        if original_request is None:
            print("No feature list found, continuing execution")
            sys.exit(0)

        # 生成验证报告
        validation_report = validator.generate_validation_report(original_request, completed, total)

        # 如果还有未完成的功能，返回block决策
        if completed < total or in_progress or incomplete:
            # 生成执行规则
            execution_rules = validator.generate_execution_rules()

            # 构建输出
            output = {
                "decision": "block",
                "reason": f"""
{validation_report}

{execution_rules}

请继续执行未完成的功能，确保遵守以上所有规则！
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
