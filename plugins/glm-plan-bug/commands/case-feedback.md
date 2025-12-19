---
allowed-tools: all
description: Submit case feedback to report issues or suggestions for the current conversation
---

# Case Feedback

Invoke @glm-plan-bug:case-feedback-agent to submit feedback for the current case/conversation.

## Critical constraint

**Run the submission exactly once** — regardless of success or failure, execute a single submission and return the result immediately.

## Usage

The user may provide feedback content directly, or you can help summarize the issue. The context will be automatically extracted from the current conversation.
