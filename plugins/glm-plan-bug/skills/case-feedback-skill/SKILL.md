---
name: case-feedback-skill
description: Run the case feedback script to submit feedback for the current conversation. Only use when invoked by case-feedback-agent.
allowed-tools: Bash, Read
---

# Case Feedback Skill

Execute the feedback submission script and return the result.

## Critical constraint

**Run the script exactly once** — regardless of success or failure, execute it once and return the outcome.

## Execution

### Gather information

**feedback**:

- If the user explicitly provided feedback text, use that directly
- If the user describes a problem or issue, summarize it concisely as the feedback
- Ask the user for clarification only if no feedback intent can be inferred

**context**:

The context contains a summary of the conversation, and **must append** the original, complete conversation history data.

Summarize the current conversation context, including:
- What task the user was trying to accomplish
- What operations were performed
- Any errors or unexpected behaviors encountered
- Relevant code snippets or file paths (keep it concise)

**code_type**:

Identify the programming language or code type involved (e.g., JavaScript, Python, Java). If not relevant, leave it blank.

**request_id**:

Extract the unique request ID or the session ID associated with this conversation or case. If not available, leave it blank.

**happened_time**:

Extract the timestamp when the issue occurred. If not mentioned, leave it blank.


### Run the submission

Use Node.js to execute the bundled script, pay attention to the path changes in the Windows:

```bash
node scripts/submit-feedback.mjs --feedback "user feedback content" --context "conversation context summary" --code_type "the current code type, eg: javascript, typescript, python, java, etc. Not required." --happened_time "the time when the issue happened, eg: 2025-12-10 11:15:00. Not required." --request_id "the unique request id if available. Not required."
```

> If your working directory is elsewhere, `cd` into the plugin root first or use an absolute path:
> `node /absolute/path/to/glm-plan-bug/skills/case-feedback-skill/scripts/submit-feedback.mjs --feedback "..." --context "..."`

### Return the result

After execution, return the result to the caller:
- **Success**: display the submission confirmation
- **Failure**: show the error details and likely cause
