---
allowed-tools: Skill, Bash
description: Get status of last deployment
---

# status command

trigger @glm-plan-deploy:status-skill to get the status of last deployment

## Critical constraint

**Run the skill exactly once** — regardless of success or failure, execute a single status and return the result.
