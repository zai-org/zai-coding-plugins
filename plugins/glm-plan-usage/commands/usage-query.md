---
allowed-tools: all
description: Query the usage information for the current account
---

# Usage Query

Invoke @glm-plan-usage:usage-query-agent to retrieve the usage information for the current account.

## Critical constraint

**Run the query exactly once** — regardless of success or failure, execute a single query and return the result immediately.
