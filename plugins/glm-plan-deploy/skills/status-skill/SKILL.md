---
name: status-skill
description: Run nodejs script to get status of deployment. Only use when invoked by status command.
allowed-tools: Bash
---

# Status Skill

1. get the absolute path of ../scripts/index.cjs as <scriptPath>
2. run the script with absolute path <scriptPath> in current project root as below:
```
node <scriptPath> status
```

## Critical constraint

**Run the script exactly once** — regardless of success or failure, execute it once and return the outcome.

## Show the result

If the deployment status is Success, display the url and open it in the default browser.

Otherwise, if the deployment status is Failure, display the error message.