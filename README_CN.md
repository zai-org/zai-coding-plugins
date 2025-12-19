# Z.ai 编程插件市场

[English](./README.md)

Claude Code 插件集合，旨在提升编程效率和提供 GLM Coding Plan 相关功能插件。

## 可用插件

| 插件 | 描述 | 命令 |
|------|------|------|
| **glm-plan-usage** | 查询 GLM Coding Plan 的配额和使用统计 | `/glm-plan-usage:usage-query` |
| **glm-plan-bug** | 提交 GLM Coding Plan 的反馈和问题报告 | `/glm-plan-bug:case-feedback` |

## 前置要求

- Node.js 18 或更高版本
- 安装 Claude Code CLI

## 快速开始

> 在 Claude Code 中安装插件市场以访问这些插件。

### 方式一

1. 安装插件市场

```shell
claude plugin marketplace add zai-org/zai-cc
```

2. 从插件市场安装插件

```shell
claude plugin install glm-plan-usage@zai-coding-plugins
```

```shell
claude plugin install glm-plan-bug@zai-coding-plugins
```

### 方式二

运行 `npx @z_ai/coding-helper` 工具直接管理和安装插件。

`开始` -> `编码工具` -> `Claude Code` -> `插件市场`

### 使用插件

1. 进入项目目录并启动 Claude Code：

```bash
claude
```

2. 在 Claude Code 中运行以下命令：

```bash
/glm-plan-usage:usage-query
```

```bash
/glm-plan-bug:case-feedback 在此输入你的反馈
```

## 使用示例

### 查询 GLM Coding Plan 使用统计

查看当前配额和使用情况：

```bash
/glm-plan-usage:usage-query
```

### 提交 GLM Coding Plan 反馈

报告问题或提供反馈：

```bash
/glm-plan-bug:case-feedback 我的套餐遇到了一个问题
```

## 贡献

欢迎贡献代码！请随时提交 Issue 或 Pull Request。

## 许可证

Apache License 2.0
