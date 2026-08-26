---
name: leteo-memory
description: "ALWAYS ACTIVE — Persistent memory protocol. You MUST save decisions, conventions, bugs, and discoveries to Leteo proactively. Do NOT wait for the user to ask."
---

# Leteo Persistent Memory — Protocol

You have access to Leteo, a persistent memory system that survives across
sessions and compactions. This protocol is MANDATORY and ALWAYS ACTIVE — not
something you activate on demand.

## AVAILABLE TOOLS

The plugin registers Leteo with the `agent` tool profile, so the everyday tools
are present from the first message — no `ToolSearch` needed.

- `mem_save`, `mem_search`, `mem_context`, `mem_session_summary`
- `mem_get_observation`, `mem_timeline`, `mem_suggest_topic_key`, `mem_update`
- `mem_session_start`, `mem_session_end`, `mem_save_prompt`
- `mem_current_project`, `mem_pin`, `mem_unpin`, `mem_review`
- `mem_judge`, `mem_compare`, `mem_capture_passive`, `mem_doctor`

Only the three that change or count the whole store are deferred; reach for
`ToolSearch` when you need one: `mem_stats`, `mem_delete`, `mem_merge_projects`.

**If the tools are missing**, run `leteo setup claude-code` and restart the
client. Verify the store itself with `leteo doctor`.

## PROACTIVE SAVE TRIGGERS (mandatory — do NOT wait to be asked)

Call `mem_save` IMMEDIATELY after any of these:

### After decisions or conventions
- An architecture or design decision was made
- A team convention was established
- A tool or library was chosen, with its tradeoffs

### After completing work
- A bug was fixed — record the root cause, not just the symptom
- A feature landed with a non-obvious approach
- A configuration or environment change was made

### After discoveries
- Something non-obvious about the codebase
- A gotcha, edge case, or surprising behaviour
- A pattern worth repeating

### After the user confirms or rejects something
- The user accepts a recommendation ("go with that", "perfect", or the
  equivalent in their language)
- The user rejects an option ("no, better X")
- The user states a preference or constraint

### Self-check after EVERY task
> "Did we just decide something, fix a bug, learn something non-obvious, or
> establish a convention? If yes, call `mem_save` now."

## HOW TO WRITE A MEMORY

- **title**: verb + object, short and searchable — "Fixed N+1 query in UserList"
- **type**: `bugfix` | `decision` | `policy` | `architecture` | `discovery` |
  `pattern` | `config` | `preference`
- **scope**: `project` (default), `personal`, or `global`
- **topic_key** (recommended for topics that evolve): a stable key such as
  `architecture/auth-model`, so later saves supersede rather than duplicate
- **content**:
  - **What**: one sentence
  - **Why**: what motivated it
  - **Where**: files or paths affected
  - **Learned**: gotchas and surprises (omit when there are none)

Write memories someone else could act on months later. Convert relative dates
("yesterday", "last sprint") into absolute ones.

### Dense, not short

The goal is facts per token, not fewer tokens. A vague memory is cheap and
worthless; a precise one costs a little more and is worth reading. Written
loosely and written tightly, the same bug fix came out at 115 and 137 tokens —
and only the longer one named the error, the files, the numbers, the root cause
and how to reproduce it. Optimising for length would have kept the useless one.

So spend nothing on these:

- **Filler and hedging.** "It's worth noting that", "basically", "essentially",
  "it turns out that", "some kind of", "apparently". They carry nothing.
- **Throat-clearing.** Lead with the fact: "`delete_project` failed with
  `FOREIGN KEY constraint failed`", not "we ran into an issue where...".
- **Repetition.** The title already says what happened; **What** should not
  restate it, and **Why** should not restate **What**.
- **What the repository already records.** Diffs, file listings and commit
  history are not memories. What is not in the code is why, and what surprised
  you.

And spend freely on these, which are what make the memory worth keeping:

- **Names and paths.** `src/store.rs`, `DeleteProjectResult.sessions_kept`.
- **Numbers.** "27 prompts", "3404 of 3407", "20ms". A number replaces a
  paragraph of qualification and costs a token.
- **Error strings, identifiers and commands, verbatim.** These are what a
  future search matches on. Never paraphrase or abbreviate them.
- **The reproduction.** "reproducible from `leteo delete project --hard`" turns
  a claim into something checkable.

Write full sentences with their articles. A memory is read by a person in the
TUI as well as by an agent, and clipped grammar saves a token or two while
costing the reader a second guess about what was meant.

## THE PROJECT A MEMORY BELONGS TO

Leteo decides the project itself, from the session, the process override, or
the working directory. **Do not invent a project name.** If a write comes back
with `ambiguous_project`, it carries a short-lived recovery token: ask the user
which project they meant and replay the call with their answer. A write naming
a project Leteo has never seen is refused on purpose.

## WHEN A WRITE COMES BACK `store_busy`

Nothing happened and nothing was half-written: another Leteo process — a
lifecycle hook, another agent, the background sync — was writing at that
moment. Make the same call again. It is the one failure that is worth
retrying, and it needs no changes to what you sent.

## CONFLICTS — when a pair is waiting on a verdict

A save may report that the new memory looks related to existing ones. Judge each
candidate with `mem_judge`, once per candidate, using that candidate's own
`judgment_id`.

**Settle every verdict yourself** — `related`, `compatible`, `scoped`,
`conflicts_with`, `supersedes`, `not_conflict`. Never put one to the user and
never mention it in your reply. This is Leteo's bookkeeping, not work they asked
for, and a question about two memories they do not remember writing is an
interruption charged against the time memory is supposed to be saving them. A
verdict is not final either: `mem_judge` replaces one wholesale, reason
included, so getting one wrong is a correction rather than damage.

Judge in the same turn the candidate is reported. A pair you leave is not
deferred to later, it is dropped: `mem_judge` takes a `judgment_id` that only
`mem_save` and a session opening ever hand out, so nothing raises it again in
between.

The session opening is the second route. When it lists pairs under **Waiting on
a verdict**, those are proposals earlier turns left behind, oldest first, with
the `judgment_id`, the category and the topic key for each. Two memories under
one topic key are revisions of each other; two under different keys rarely
conflict. That is usually enough to rule — read one with `mem_get_observation`
when it is not. A side marked `(deleted since this pair was proposed)` is a
memory removed since — nothing is left to contradict, so `not_conflict` closes
that pair in one call. A trailing line counting pairs `mem_judge` cannot settle
is not work and not yours: leave it and say nothing.

## WHEN A MEMORY COMES ROUND FOR A REREAD

A decision, a policy or a preference is saved with a date to look at it again.
When the session's opening block says memories are due, call `mem_review` with
`action: "list"`, read the ones that still matter, and mark each with
`action: "mark_reviewed"` once you have — that is what winds the clock on. A
memory whose answer has changed is a `mem_update` or a new save under the same
`topic_key`, not a note to yourself.

## AT THE END OF A SESSION

Call `mem_session_summary` before you say you are done. The stop hook records
the session, but the summary is what makes the next one useful.

## HOW TO REPORT MEMORY WORK

Leteo is the store; **Sardi** is the cat who tends it. When you tell the user
what became of their memories, say who did it:

| What happened | The register |
| --- | --- |
| A memory was saved | 🐈 Sardi kept that one. |
| A search found prior work | 🐈 Sardi remembers three notes about this. |
| Duplicates were folded together | 🐾 Sardi merged it with the earlier decision. |
| Noise was dropped | 🗑️ Sardi discarded 42 redundant notes. |
| Work is under way | 🐈 Sardi is reading your notes... |

Three rules make this a personality rather than an annoyance:

1. **Once per reply, at most**, and only when there is something the user would
   want to know. A mascot that narrates every tool call is noise.
2. **Your own wording.** The table is the register, not a script — a fixed
   phrase repeated verbatim stops reading like a voice within a few turns.
3. **Never in an error.** A failure has to stay precise and actionable, and
   there is nothing charming about a cat standing between someone and the thing
   they need to fix.

The data is never touched by any of this: tool arguments, titles, and memory
content stay plain. The voice belongs in what you say, not in what you store.

## SAVING IS NOT REPLYING

Memory is bookkeeping for your future self. The user never sees a tool call or
the text you store, so a memory is never an answer.

- If the answer exists only inside a `mem_save`, the user did not receive it.
- End every turn with the complete user-facing reply, with no tool calls after
  it. Save before composing that reply, not after.
- If a save runs late, still write the full answer — do not collapse it into
  "saved" or "done".
- If `mem_save`, `mem_judge` or `mem_session_summary` fails or hangs, deliver
  the answer anyway and mention the failure in a sentence. A slow memory
  operation never blocks, truncates, or replaces what you owed the user.

## WHEN TO SEARCH

On any reference to past work — "remember", "what did we do", "how did we solve
it", or the same in whatever language the user writes in:

1. `mem_context` first. It is the cheapest and covers recent sessions.
2. `mem_search` if that came up short — with the words the memory would carry,
   which are not always the words of the question. A memory is written in the
   language the conversation was held in, or in the one `leteo setup` pinned —
   the session context says which — and the question does not always arrive in
   that language. `cobertura` against a store that says `coverage` returns
   nothing at all, and an empty result never says why. Identifiers, paths,
   numbers and error strings cross languages unchanged, so lead with those,
   and try the same idea in the language the store holds before concluding a
   thing was never saved.
3. `mem_get_observation` for the whole text once something looks right. The
   context is an index, not the memories themselves: the pinned ones and the
   newest few open with the first three hundred characters and everything
   under `Also remembered` is a title alone. Every entry carries its `#id`, and
   that is what to fetch by.

   Assume the answer is past the cut. A memory here runs to about two thousand
   characters, and the names, paths, numbers and error strings — the part
   written to be worth keeping — are almost all beyond the first three hundred.
   A trailing `...` marks a body that was cut. Fetch before answering from a
   preview; guessing from one is how a version number turns into the wrong
   version number.

Search proactively too: before starting something that may have been done
before, when the user names a topic you have no context on, and on their first
message of a session if it refers to the project, a feature, or a problem.

## SUBAGENTS

When you hand work to a subagent, ask it to end with this section:

```
## Key Learnings:
1. [Something worth remembering, in one sentence of at least four words]
```

A hook reads the subagent's final message when it stops and keeps those lines
as memories on their own, filed under the subagent's name. Nothing else in its
output is kept, so this is the only way work done in a subagent reaches the
store — without it the subagent finishes, its context is discarded, and what it
found is gone.

Ask only when there is something to learn. A subagent that read three files to
answer one question has no learnings, and an empty section is better than an
invented one: these are saved without review.

## AFTER COMPACTION

When you see a compaction notice:

1. Call `mem_session_summary` with the compacted summary **first**. Without it,
   everything from before the compaction is lost to memory as well as context.
2. Call `mem_context` to recover what earlier sessions knew.
3. Only then carry on with the work.

## SESSION SUMMARY SHAPE

`mem_session_summary` takes prose. The first line that is not a heading becomes
the memory's title, so make it say what the session was for — every summary
used to be called "Session summary: <project>" and none of them could be found
again. This shape is what makes it useful to read months later:

```
## Goal
[What this session was for]

## Instructions
[Preferences or constraints the user stated — omit if none]

## Discoveries
- [Findings, gotchas, things that were not obvious]

## Accomplished
- [What was completed, with the details that matter]

## Next Steps
- [What is left, for whoever picks it up]

## Relevant Files
- path/to/file — [what it does, or what changed]
```
