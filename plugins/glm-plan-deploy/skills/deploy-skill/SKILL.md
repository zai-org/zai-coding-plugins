---
name: deploy-skill
description: Run nodejs script to deploy user project. Only use when invoked by deploy command.
allowed-tools: Bash
---

# Deploy Skill


1. get the absolute path of ../scripts/index.cjs as <scriptPath>
2. run the script with absolute path <scriptPath> in current project root as below:
```
node <scriptPath> deploy
```

## Critical constraint

**Run the script exactly once** — regardless of success or failure, execute it once and return the outcome.

## Show the result

If the deployment completes with Success status, display the url of the deployment, and open it in default browser.

Otherwise, if the deployment completes with Failure status, display the error message.