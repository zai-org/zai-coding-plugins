# Z.ai Coding Plugins Marketplace

[中文文档](./README_CN.md)

A collection of plugins to enhance coding productivity and provide GLM Coding Plan relate service for Claude Code.

## Available Plugins

| Plugin               | Description                                                           | 
|----------------------|-----------------------------------------------------------------------|
| **glm-plan-usage**   | Query quota and usage statistics for GLM Coding Plan                  |
| **glm-plan-bug**     | Submit case feedback and bug reports for GLM Coding Plan              |

## Prerequisites

- Node.js 18 or higher
- Install Claude Code CLI

## Quick Start

> Install the marketplace within Claude Code to access the plugins.

### Method A

> Prerequisite: Git environment is set up.

1. Install the Marketplace

```shell
claude plugin marketplace add zai-org/zai-coding-plugins
```

2. Install Plugins from the Marketplace

```shell
claude plugin install glm-plan-usage@zai-coding-plugins
```

```shell
claude plugin install glm-plan-bug@zai-coding-plugins
```

### Method B

Run the `npx @z_ai/coding-helper` tool to manage and install the plugins directly.

`Start` -> `Coding Tool` -> `Claude Code` -> `Plugin Marketplace`

### Using the Plugins

1. Navigate to your project and start Claude Code:

```bash
claude
```

2. Use the installed plugins with the following commands:

```bash
/glm-plan-usage:usage-query
```

```bash
/glm-plan-bug:case-feedback Your feedback message here
```

## Usage Examples

### Query GLM Coding Plan Usage Statistics

Check your current quota and usage:

```bash
/glm-plan-usage:usage-query
```

### Submit GLM Coding Plan Feedback

Report issues or provide feedback:

```bash
/glm-plan-bug:case-feedback I have an issue with my plan
```

## Contributing

We welcome contributions! Please feel free to submit issues or pull requests.

## License

Apache License 2.0