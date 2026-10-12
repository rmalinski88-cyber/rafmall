#!/bin/sh
# SessionStart hook for the task-observer skill (.claude/skills/task-observer).
# Based on references/environments.md, "A session-start hook". It computes the
# activation and review state and injects it as additionalContext. It never
# blocks: on any problem it prints nothing and exits 0.
#
# Workspace: $TASK_OBSERVER_WORKSPACE if set, else <repo>/.claude/task-observer-workspace,
# where <repo> is $CLAUDE_PROJECT_DIR or the parent of this script's .claude folder.

if [ -n "${TASK_OBSERVER_WORKSPACE:-}" ]; then
  ws="$TASK_OBSERVER_WORKSPACE"
elif [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then
  ws="$CLAUDE_PROJECT_DIR/.claude/task-observer-workspace"
else
  here=$(cd "$(dirname "$0")" 2>/dev/null && pwd) || exit 0
  ws="${here%/.claude/hooks}/.claude/task-observer-workspace"
fi
d="$ws/skill-observations"
[ -d "$d" ] || exit 0

open=$(find "$d/observation-log" -maxdepth 1 -name '*.md' -exec grep -l '^status: open$' {} + 2>/dev/null | wc -l | tr -d ' ')
last=$(cat "$d/last-review-date.txt" 2>/dev/null || echo never)
msg="Invoke the task-observer skill before the first tool call. The task-observer workspace is $ws (TASK_OBSERVER_WORKSPACE). Observation files are created only by scripts/new-observation.sh in the skill directory, never by copying a header."
if [ "${open:-0}" -gt 0 ]; then
  msg="$msg $open open observations; last review: $last."
  cutoff=$(date -d '7 days ago' +%F 2>/dev/null || date -v-7d +%F)
  case "$last" in
    (never) msg="$msg Offer the review." ;;
    (*) [ "$(printf '%s\n%s\n' "$last" "$cutoff" | sort | head -1)" = "$last" ] && msg="$msg Offer the review." ;;
  esac
fi
# Escape for JSON: backslashes and double quotes only; the message contains no newlines.
esc=$(printf '%s' "$msg" | sed 's/\\/\\\\/g; s/"/\\"/g')
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$esc"
exit 0
