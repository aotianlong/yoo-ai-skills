---
name: commit
description: Use this skill when the user types `git commit`, `/commit`, or asks to commit changes.
---

# commit

Use this skill when the user types `git commit`, `/commit`, or asks to commit changes.

## Steps

1. Run `git status` and `git diff` (staged + unstaged) and `git log --oneline -5` in parallel to understand the current state.
2. Analyze the changes:
   - Identify the type: feat / fix / refactor / chore / docs / test / style
   - Identify the scope (module/component name)
   - Write a concise subject line in the same language as the surrounding commit messages (Chinese or English)
3. Stage the changed files with `git add <specific files>` (never use `git add -A` or `git add .` to avoid accidentally including sensitive files).
4. Create the commit using a HEREDOC:
   ```
   git commit -m "$(cat <<'EOF'
   <type>(<scope>): <subject>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```
5. Run `git status` to confirm success.

## Rules

- Follow Conventional Commits format: `type(scope): subject`
- Subject must be in the same language as recent commit messages
- Never use `--no-verify` or skip hooks
- Never amend existing commits unless explicitly asked
- Do not push unless explicitly asked
