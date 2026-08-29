---
name: control-browser
description: "Drive the user's real, signed-in browser through Ghostlight's governed tools. Use to open, navigate, inspect, find, click, type, fill forms, screenshot, upload, record, or verify web pages from an agent session, including web-UI testing, rendered-page reading, and form journeys. Prefer these tools over guessing at page structure or replaying raw browser commands."
---

# Controlling the browser with Ghostlight

These tools drive the user's visible Chromium browser through one governed path. Every call
returns one envelope: `status`, `effect`, `readiness`, `repeat_safe`, a Ghostlight-authored
`summary`, tool-specific `facts`, and up to two safe `next_steps`. Read the summary and
`next_steps` before deciding what to do next; they are written to be followed.

## Observe, then act

Perception handles are cheap and deliberate. Do not guess at page structure.

- `browser_inspect` lists semantic controls (role, accessible name, state) and returns
  `target_` handles. `scope: "document"` returns a bounded structure tree under a `snapshot_`
  handle and diffs it against the prior snapshot, so one extra inspect proves whether your
  edit landed.
- `browser_find` ranks controls by visible or accessible text. Use it when you know the label:
  the fastest route to a control is its name.
- Acting on a stale `target_` handle is refused on purpose: a navigation made the page unseen,
  so observe again. `tab_` handles are different -- they are durable slots, and navigating
  through a closed one recreates the tab under the same handle and says so.
- Typed selectors (`name`, optional `role`, optional `exact`) are accepted wherever target
  handles are, including waits. Prefer a selector when stashing a handle adds nothing.

## Coordinates come from a view

Never invent pixel coordinates. `browser_screenshot` returns a `view_` handle that binds
coordinates to one tab, document generation, viewport, scale, and zoom. Click, hover, drag,
and wheel-scroll at `view_` pixels from the returned image; a bounded region capture returns a
new, magnified view for precision. Coordinate input on a stale view is rejected -- take a
fresh screenshot.

## Acting

- `browser_fill_form` fills 1 to 30 fields in one call and proves a contained submit before
  clicking `submit_target`; it never submits without one. Use it over repeated typing.
- `browser_type_text` sends real per-character events, with `focused: true` to type into
  whatever is focused and `clear_first` to replace. Use it when keystroke events matter.
- `browser_click` takes a target or a view point; `click_count` covers double and triple.
  `browser_press_key` takes one key or a stroke sequence with repeat and modifiers.
- Credential-class fields (passwords, card numbers) stop before dispatch and ask for visible
  user handoff. That refusal is a feature; do not route around it.
- `browser_upload` attaches local paths, inline base64 files (1 to 5, each and combined under
  5,000,000 bytes), or a captured image, to a file input or dropped at a view point.
- `browser_execute` runs page JavaScript and can mutate or navigate anything. Use a semantic
  tool whenever one fits; reach for execute only for what no other tool expresses.

## Composing steps

- `browser_sequence` runs 2 to 8 fixed steps (click, fill, type_text, press_key, scroll,
  hover, wait) on one tab, stopping at the first failure. Use it for a known, stable journey.
- `browser_flow` runs 1 to 20 steps of any non-composite tool and lets later steps reference
  earlier envelopes with `{"flow_ref": {"step": "id", "pointer": "/facts/..."}}`. Use
  `dry_run: true` to decode and classify the whole plan before anything dispatches.
  Compose journeys here when step outputs feed later inputs (open, then reuse the found
  handle, then wait for its text).
- Every step is classified and audited independently under the invocation's authority;
  composite wrappers add no power of their own.

## Waiting and dialogs

- `browser_wait` on `load_ready`, `url_contains`, `text_present` or `text_absent`,
  `target_present` or `target_absent`, or `selector_present`. Bounded executor-side sleeps use
  `duration` (0 to 10000 ms). A false condition is a decisive failed answer, not "unknown" --
  do not retry blindly; observe instead.
- Per-call `timeout_ms` runs 100 to 30000, defaulting to 8000.
- A JavaScript dialog blocks its tab until handled. Check and resolve it with `browser_dialog`
  (`status`, `accept`, `dismiss`, `respond`); deal with it before other work on that tab.

## Telling the truth about effects

- `repeat_safe: false` means the same call is known unsafe or of unknown safety to repeat.
  Do not replay it; observe and decide.
- `effect` of `partial` or `unknown` means some work may have happened. Say so in anything you
  report; never claim completion the envelope does not claim.
- Refusals name the deciding reason and the remedy. When a refusal surprises you, ask
  `policy_explain` first: it compiles the authority in force, one line per capability, and is
  always available.

## Recording evidence

`browser_record` makes a short, memory-only GIF: `start`, ordinary work, then `save` (to a
file input, a download, or back to you) or `discard`. Frames never leave the browser except
by your explicit save. A replay is a human-scale artifact: report what it shows and how long
it plays, and let the facts carry the byte counts.
