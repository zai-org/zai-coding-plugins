# GLM Plan Usage Plugin

Query quota and usage statistics for GLM Coding Plan.

Attention:

- This plugin is designed to work specifically with the GLM Coding Plan in Claude Code.
- This plugin requires Node.js to be installed in your environment.

## How to use

In Claude Code, run:
```
/glm-plan-usage:usage-query
```

## Command overview

### /usage-query

Retrieve the usage information for the current account.

**Execution flow:**
1. Command `/usage-query` triggers `@usage-query-agent`
2. The agent invokes `@usage-query-skill`
3. The skill checks the Node.js environment and executes the query script with the appropriate method
4. The skill returns either the successful response or the failure reason

**Important constraint:** Run the query exactly once and return immediately whether it succeeds or fails.
