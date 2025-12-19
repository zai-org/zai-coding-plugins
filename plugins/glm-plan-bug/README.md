# GLM Plan Bug Plugin

Submit case feedback and bug reports for GLM Coding Plan.

Attention: 

- This plugin is designed to work specifically with the GLM Coding Plan in Claude Code.
- This plugin requires Node.js to be installed in your environment.

## How to use

In Claude Code, run:
```
/glm-plan-bug:case-feedback i have a issue with my plan
```

## Command overview

### /case-feedback

Submit case feedback to report issues or suggestions for the current conversation.

**Execution flow:**
1. Command `/case-feedback` triggers `@case-feedback-agent`
2. The agent invokes `@case-feedback-skill`
3. The skill gathers feedback information and executes the submission script
4. The skill returns either the successful response or the failure reason

**Important constraint:** Run the submission exactly once and return immediately whether it succeeds or fails.
