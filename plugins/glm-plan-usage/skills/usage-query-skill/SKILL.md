---
name: usage-query-skill
description: Run the usage query script to retrieve account usage information for GLM Coding Plan. Only use when invoked by usage-query-agent.
allowed-tools: Bash, Read
---

# Usage Query Skill

Execute the usage query script and return the result.

## Critical constraint

**Run the script exactly once** — regardless of success or failure, execute it once and return the outcome.

## Execution


### Run the query

Use Node.js to execute the bundled script, pay attention to the path changes in the Windows:

```bash
node scripts/query-usage.mjs
```

> If your working directory is elsewhere, `cd` into the plugin root first or use an absolute path:
> `node /absolute/path/to/glm-plan-usage/skills/usage-query-skill/scripts/query-usage.mjs`

### Return the result

After execution, return the result to the caller:
- **Success**: display the usage payload (JSON)
- **Failure**: show the error details and likely cause
