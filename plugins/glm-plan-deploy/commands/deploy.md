---
allowed-tools: Skill, Bash
description: Deploy current project for current account
---

# deploy command

trigger @glm-plan-deploy:deploy-skill to deploy current folder

## Critical constraint

**Run the skill exactly once** — regardless of success or failure, execute a single deploy and return the result.
