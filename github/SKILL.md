---
name: github
description: Manage GitHub repositories, issues, pull requests, and code reviews. Search code, create branches, and track CI/CD status.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: integrations
tags: [github, pull-requests, issues, ci]
suggested_template: devops_bot
---

# GitHub Skill

Manage GitHub repositories, create and respond to issues, handle pull requests, run code reviews, and track CI/CD pipeline status. Search code and manage branches for seamless development workflow integration.

> **Dashboard Connection Required**
> This skill needs GitHub connected in the MyClawBots dashboard:
> **https://myclawbots.ai/settings/social** → GitHub → **Connect**.
>
> That is a one-time OAuth sign-in on the account, and every agent you own
> inherits it — there is nothing to connect per agent, and nothing to paste.

## Your GitHub token

You never see the real token. MyClawBots keeps it and gives you `$GITHUB_PAT`, a
stand-in (`mcb_sec_…`) that only works through **`vault-curl`**: it swaps in the
real token on the way to `https://api.github.com`, and only there. There is no
`gh` CLI on this machine.

- Put `$GITHUB_PAT` **only** in the `Authorization: Bearer` header, exactly as in
  the commands below. Anywhere else (URL, body, another header) is refused.
  The one exception is git over HTTPS to `github.com` through the vault proxy
  (section 14), where it is the Basic-auth password.
- Never print, echo or save the stand-in or any token, and never try to recover
  the real one. Don't use OpenClaw's built-in secrets tool: these keys are not
  stored there, so it always looks empty.

## Prerequisites

- GitHub account with repository access
- GitHub connected at https://myclawbots.ai/settings/social (one-time, account-wide)
- Repository permissions for the actions you plan to take
- Appropriate branch protection settings understood

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| GitHub connected in Settings → Connectors | Yes | Provides `$GITHUB_PAT` (a stand-in) to this agent |
| `vault-curl` | Yes | Sends the calls; swaps the stand-in for the real token |
| `slack` skill | No | Optional: for PR and issue notifications |

**Pre-flight checks:**
- Check the stand-in is present: `[ -n "$GITHUB_PAT" ] && echo present || echo missing`
- If it is missing (GitHub was connected after you started), look it up live:
  `vault-curl --secrets`. If an entry is named `GITHUB_PAT`, use its `surrogate`
  string in place of `$GITHUB_PAT` in every command. No restart is needed.
- If `vault-curl` is not found (`command -v vault-curl` prints nothing), run
  `bash /root/.openclaw/skills/github/scripts/vault-curl.sh` in its place.
- If none of that finds a token, do NOT reach for `gh`, `git config`, or any
  local credential store — none of them are configured here. Say exactly this
  instead:

  > I don't have access to GitHub yet. Connect GitHub at
  > https://myclawbots.ai/settings/social, then ask me again.
- If integrating with Slack: ensure `slack` skill is connected

## How It Works

This skill provides agent-friendly access to GitHub's core development operations via the official GitHub REST API. Every call is `vault-curl` against `https://api.github.com` with `-H "Authorization: Bearer $GITHUB_PAT"`.

The skill supports:
- **Repository Management**: List repos and view details
- **Issue Tracking**: Create, search, update, and discuss issues
- **Pull Requests**: Create, view, and review PRs with full diff analysis
- **Code Review**: Create reviews with approval, changes requested, or comments
- **CI/CD Integration**: Monitor GitHub Actions workflow runs and status
- **Code Search**: Find specific code patterns across repositories
- **Branch Management**: List, create, and switch branches

## Available Tools

### 1. List Repositories
Get all repositories you have access to.

```bash
vault-curl -sS -X GET "https://api.github.com/user/repos?per_page=30&sort=updated" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Returns:** Array of repository objects with names, URLs, descriptions, languages, stars, and fork status.

---

### 2. Get Repository Details
Retrieve comprehensive information about a specific repository.

```bash
vault-curl -sS -X GET "https://api.github.com/repos/owner/repo" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Parameters:**
- `owner`: Repository owner username (required)
- `repo`: Repository name (required)

**Returns:** Repository metadata including description, URL, visibility, default branch, language, topics, and activity stats.

---

### 3. List Issues
Retrieve issues from a repository with filtering by state and limits.

```bash
vault-curl -sS -X GET "https://api.github.com/repos/owner/repo/issues?state=open&per_page=30" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Query Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)
- `state`: Filter by "open", "closed", "all" (optional, default: open)
- `labels`: Comma-separated labels to filter (optional)
- `assignee`: Filter by assignee username (optional)
- `limit`: Max results, default 30 (optional)

**Returns:** Array of issue objects with numbers, titles, bodies, labels, assignees, and status.

---

### 4. Create Issue
Create a new GitHub issue with title, description, labels, and assignees.

```bash
vault-curl -sS -X POST "https://api.github.com/repos/owner/repo/issues" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix authentication flow on mobile",
    "body": "Users on iOS are unable to complete OAuth flow. Session expires after redirect.\n\n## Steps to Reproduce\n1. Open app on iOS\n2. Tap Login\n3. Complete OAuth\n\n## Expected\nUser logged in and redirected to dashboard\n\n## Actual\nSession error, redirect fails",
    "labels": ["bug", "authentication", "mobile"],
    "assignees": ["username1", "username2"]
  }'
```

**Request Body:**
- `title`: Issue title (required)
- `body`: Issue description in Markdown (required for clarity)
- `labels`: Array of label strings (optional)
- `assignees`: Array of GitHub usernames (optional)

**Returns:** Created issue number and full issue object.

---

### 5. Update Issue
Modify issue title, body, labels, assignees, or state.

```bash
vault-curl -sS -X PATCH "https://api.github.com/repos/owner/repo/issues/42" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix authentication flow on mobile (IN PROGRESS)",
    "state": "open",
    "labels": ["bug", "authentication", "mobile", "high-priority"],
    "assignees": ["username1"]
  }'
```

**Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)
- `number`: Issue number (required)

**Request Body:**
- Any of: `title`, `body`, `state` (open/closed), `labels`, `assignees`

**Returns:** Updated issue object.

---

### 6. Comment on Issue
Add a comment to an issue for discussion and updates.

```bash
vault-curl -sS -X POST "https://api.github.com/repos/owner/repo/issues/42/comments" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Started investigating. The issue appears to be in the OAuth redirect handler. Found that the session timeout is set to 5 minutes, but the OAuth flow takes longer on slow networks."
  }'
```

**Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)
- `number`: Issue number (required)

**Request Body:**
- `body`: Comment text in Markdown (required)

**Returns:** Created comment with ID, author, and timestamp.

---

### 7. List Pull Requests
Retrieve pull requests from a repository filtered by state.

```bash
vault-curl -sS -X GET "https://api.github.com/repos/owner/repo/pulls?state=open&per_page=20" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Query Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)
- `state`: Filter by "open", "closed", "merged", "all" (optional, default: open)
- `head`: Filter by head branch (optional)
- `base`: Filter by base branch (optional)
- `limit`: Max results, default 20 (optional)

**Returns:** Array of PR objects with numbers, titles, branches, and status.

---

### 8. Get Pull Request Details
Retrieve full details about a specific PR including diff statistics and reviews.

```bash
vault-curl -sS -X GET "https://api.github.com/repos/owner/repo/pulls/128" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)
- `number`: PR number (required)

**Returns:** PR object with title, description, base/head branches, author, state, diff stats (additions, deletions, changed files), reviewers, and approval status.

---

### 9. Create Pull Request Review
Submit a code review on a PR with approval, requested changes, or comments.

```bash
vault-curl -sS -X POST "https://api.github.com/repos/owner/repo/pulls/128/reviews" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "body": "Implementation looks solid. The OAuth redirect handler properly manages session timeout and the retry logic is robust. A few suggestions for improvement:\n\n1. Consider adding exponential backoff for network failures\n2. Add more comprehensive error logging\n\nOtherwise approved.",
    "event": "APPROVE"
  }'
```

**Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)
- `number`: PR number (required)

**Request Body:**
- `body`: Review comments in Markdown (optional)
- `event`: "APPROVE", "REQUEST_CHANGES", or "COMMENT" (required)

**Returns:** Created review ID and object.

---

### 10. List Recent CI Runs
Get recent GitHub Actions workflow runs for a repository.

```bash
vault-curl -sS -X GET "https://api.github.com/repos/owner/repo/actions/runs?per_page=10" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Query Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)
- `limit`: Max runs to return, default 10 (optional)

**Returns:** Array of workflow run objects with names, status (success, failure, pending), conclusion, branch, and timestamp.

---

### 11. Search Code
Search for specific code patterns, functions, or strings across a repository.

```bash
vault-curl -sS -X GET "https://api.github.com/search/code?q=function%20authenticate%20repo:owner/repo&per_page=20" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Query Parameters:**
- `q`: Search query (required)
- `repo`: Repository in "owner/repo" format (optional, omit to search all)
- `limit`: Max results, default 20 (optional)

**Returns:** Array of code search results with file paths, line numbers, and context snippets.

---

### 12. List Branches
Get all branches in a repository.

```bash
vault-curl -sS -X GET "https://api.github.com/repos/owner/repo/branches" \
  -H "Authorization: Bearer $GITHUB_PAT"
```

**Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)

**Returns:** Array of branch objects with names, commit SHAs, and protected status.

---

### 13. Create Branch
Create a new branch from an existing branch for feature development.

```bash
# First, get the SHA of the branch you are branching from:
vault-curl -sS -X GET "https://api.github.com/repos/owner/repo/git/ref/heads/main" \
  -H "Authorization: Bearer $GITHUB_PAT"

# Then create the new branch ref using that SHA:
vault-curl -sS -X POST "https://api.github.com/repos/owner/repo/git/refs" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "refs/heads/feature/oauth-mobile-fix",
    "sha": "<sha-from-previous-call>"
  }'
```

**Parameters:**
- `owner`: Repository owner (required)
- `repo`: Repository name (required)

**Request Body:**
- `ref`: Fully qualified ref of the new branch, e.g. `refs/heads/<name>` (required)
- `sha`: Commit SHA to branch from (required — fetch it with the `git/ref/heads/<base>` call above)

**Returns:** Created ref object with the new branch name and commit SHA.

---

### 14. Clone and Push with git (needs the vault proxy)

`$GITHUB_PAT` is also accepted by `github.com` itself, as the password of git's
HTTPS Basic auth. This works **only when the vault proxy is on** for this
agent: git honours `HTTPS_PROXY`, the proxy sees the Basic header git sends to
`github.com`, and swaps the stand-in (the password) for the real token there.
`vault-curl` cannot do this for you: git talks to GitHub itself.

```bash
# Check the proxy first. Empty output = no proxy: use section 15 instead.
printenv HTTPS_PROXY

# Clone (the stand-in is only the Basic-auth password; the user name is literal):
git clone https://x-access-token:$GITHUB_PAT@github.com/owner/repo.git /root/.openclaw/workspace/repo
cd /root/.openclaw/workspace/repo
# Don't keep the stand-in in .git/config:
git remote set-url origin https://github.com/owner/repo.git

# Push a branch (name the URL again, same form):
git push https://x-access-token:$GITHUB_PAT@github.com/owner/repo.git feature/oauth-mobile-fix
```

- Only `github.com`, only in that `https://x-access-token:$GITHUB_PAT@github.com/…`
  form. Never put the stand-in anywhere else in a URL, and never in `git config`,
  a credential helper or a file.
- A push is one request per pack: packs over 10 MB are refused by the proxy.
  Push smaller commits, or use section 15 for single files.
- If git fails with an authentication or certificate error, the proxy is not
  serving this command: fall back to section 15. Don't retry with other tricks.

---

### 15. Read and Write Repository Files (API fallback)
Always available (plain `vault-curl`, no proxy needed). Use it when
`HTTPS_PROXY` is empty or git fails as described above.

```bash
# Read one file (raw content) from a branch:
vault-curl -sS "https://api.github.com/repos/owner/repo/contents/src/app.py?ref=main" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "Accept: application/vnd.github.raw"

# Create or update a file on a branch (content is base64; "sha" is required
# when updating, from a GET of the same path without the raw Accept header):
vault-curl -sS -X PUT "https://api.github.com/repos/owner/repo/contents/docs/notes.md" \
  -H "Authorization: Bearer $GITHUB_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "docs: add notes",
    "content": "<base64 of the new file>",
    "branch": "feature/oauth-mobile-fix",
    "sha": "<current file sha, when updating>"
  }'
```

A public repository can always be cloned without a token for local reading:
`git clone https://github.com/owner/repo.git /root/.openclaw/workspace/repo`.

---

## Workflow Statuses

Common GitHub Actions workflow statuses:

| Status | Meaning |
|--------|---------|
| `pending` | Workflow queued but not started |
| `in_progress` | Workflow currently running |
| `success` | All jobs passed |
| `failure` | One or more jobs failed |
| `cancelled` | Workflow manually cancelled |
| `skipped` | Workflow skipped (no changes) |

---

## Review Events

When creating a PR review, use one of these events:

| Event | Meaning |
|-------|---------|
| `APPROVE` | Approve the PR for merge |
| `REQUEST_CHANGES` | Request changes before merging |
| `COMMENT` | Comment without approval or rejection |

---

## Important Rules

1. **Always Search for Issues First**: Before creating a new issue, search for existing ones using keywords. Many issues are duplicates.

2. **Confirm Before Creating Issues/PRs**: When creating issues or PRs, verify they don't already exist. Double-check the repository.

3. **Include Clear Descriptions**: Provide comprehensive descriptions with context, steps to reproduce (for bugs), expected vs actual behavior, and relevant error messages.

4. **Check CI Status Before Approving**: Never approve a PR without verifying that all CI checks pass. Use the CI runs endpoint to validate.

5. **Review Diff Statistics**: Always check the diff stats before reviewing. Large PRs (100+ files) may need different review strategies.

6. **Use Appropriate Review Events**: Use "REQUEST_CHANGES" only when blocking issues exist. Use "COMMENT" for suggestions. Use "APPROVE" when ready.

7. **Reference Issues in PRs**: When creating a PR that fixes an issue, reference it in the description (e.g., "Fixes #42") to auto-link them.

8. **Add Meaningful Labels**: Use labels consistently (bug, feature, documentation, high-priority, etc.) for organization and filtering.

9. **Keep Branch Names Descriptive**: Use branch names like "feature/oauth-mobile-fix" or "bugfix/session-timeout" that explain the work.

10. **Avoid Merging Failing Builds**: Never merge a PR when CI is failing or incomplete. Wait for green status.

11. **Use Code Search Strategically**: Before refactoring, search for all usages of a function or pattern to understand impact.

12. **Request Reviews Proactively**: When creating PRs, ensure appropriate reviewers are assigned. Don't leave PRs in limbo.
