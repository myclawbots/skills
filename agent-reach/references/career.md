# Careers and recruiting

LinkedIn and BOSS Zhipin.

## LinkedIn

```bash
# Get a person's profile
mcporter call linkedin.get_person_profile linkedin_username="username" sections="experience,education"

# Search for people
mcporter call linkedin.search_people keywords="AI engineer" location="Shanghai"

# Get a company's profile
mcporter call linkedin.get_company_profile company_name="openai" sections="posts,jobs"

# Search for jobs
mcporter call linkedin.search_jobs keywords="software engineer" location="Remote" max_pages=2
```

> **Login required**: Before first use, run `uvx mcp-server-linkedin@latest --login` to save a valid session.

### Fallback

If MCP is unavailable, use Jina Reader:

```bash
curl -s "https://r.jina.ai/https://linkedin.com/in/username"
```

## BOSS Zhipin

When the user says “help me set up BOSS Zhipin,” follow this section to install it,
launch a dedicated Chrome session, wait for the user to log in manually, and verify
setup. Do not make the user figure out implementation details such as port 9222.
Do not enter their credentials, scan login codes, or solve slider challenges for them.

> **Important distinction: login requirements are separate from anti-bot security checks.**
> Opening zhipin.com may land on one of three pages: the logged-in `web/geek/job`,
> the logged-out `web/user/` (QR-code/phone login), or an **anti-bot security-check page**
> (a URL containing `security-check` / `zhipin-security` / `_security_check`).
> Security-check pages are unrelated to login: **they also appear when logged in**
> (almost always with a CDP-enabled Chrome session). Never infer login state from
> the current page URL.

> **Two credential stores (the browser is authoritative in strict `existing-browser` CDP mode).**
> There are two stores, and **neither should be deleted**, but they authenticate different paths:
>
> | Store | Role |
> |---|---|
> | `~/.boss-agent/auth/session.enc` | ① Required prerequisite: `_get_browser()` unconditionally calls `get_token()`. If it cannot read the token, it raises `AuthRequired` and CDP search fails before connecting to the browser. ② **Not** the search credentials: when CDP reuses a real Chrome `contexts[0]`, these cookies are injected only in the “no context” branch and are never used in practice. ③ The httpx path (low-risk operations: `status`/`detail`/`cities`/`job_card_httpx`) really uses its cookies + stoken; `force_refresh()` for code 37 also writes back to this store. |
> | Browser cookies in the dedicated Chrome profile | Credentials actually sent by high-risk operations such as search/greet in CDP mode. |
>
> **`boss status` / `status --live` only validate session.enc.** Even if they report
> `logged_in: true`, the CDP browser may be logged out. Therefore:
> 1. Immediately after launching dedicated Chrome, **pause and have the user visually
>    confirm** it is logged in (avatar in the top-right). Search is allowed only after
>    this confirmation.
> 2. The boss row in doctor directly probes the browser for a wt2 cookie. Use that result.
> 3. **`AUTH_EXPIRED` is the ground truth**: if search returns it, go straight to the
>    login runbook (user logs in to the dedicated window → `login --cdp`). Do not
>    reinterpret it as a “security check.” Treat an `_security_check` page as a
>    slider challenge only when `AUTH_EXPIRED` is absent.
> 4. Do not delete session.enc to “clean up old credentials.” Refresh it with `login --cdp`.

> **Dependency status**: The required public strict-CDP APIs came from successor
> boss-agent-cli PRs #403–#407 (#402/#382 were split at the maintainer's request),
> all merged into upstream master. The Agent Reach installer pins the upstream commit
> `4c991b77086a203173bf08a4cb64a23af6514fe6` rather than a moving branch. Once upstream
> publishes a formal release, the installer should return to a version constraint.

Health check (no side effects or searches):

```bash
agent-reach doctor          # boss row: off = not installed or CDP unreachable; warn = connection ready
                            # The message reports whether the browser has a wt2 login cookie (browser is authoritative).
```

Search and job descriptions use the public APIs (`browser_source` / `job_card_browser` /
`JobItem.lid`). Because pipx/uv tools use isolated environments, ordinary `python` may
not be able to import an installed tool. Use `uv run --with` to put the script and
pinned dependency in the same interpreter environment:

```bash
uv run --isolated --no-project \
  --with 'git+https://github.com/can4hou6joeng4/boss-agent-cli.git@4c991b77086a203173bf08a4cb64a23af6514fe6' \
  python - <<'PY'
from pathlib import Path

from boss_agent_cli.api.client import AccountRiskError, BossClient, EnvironmentRiskError
from boss_agent_cli.auth.manager import AuthManager
from boss_agent_cli.platforms.zhipin import BossPlatform

auth = AuthManager(Path.home() / ".boss-agent")

# Strict CDP mode: reuse the logged-in browser, fail immediately on CDP errors, never use headless mode.
with BossClient(
    auth,
    cdp_url="http://localhost:9222",
    browser_source="existing-browser",
) as boss:
    raw = boss.search_jobs("LLM", city="深圳", page=1)  # Shenzhen; retain the platform's city name.
    if raw.get("code") != 0:
        code, message = BossPlatform(boss).parse_error(raw)
        raise RuntimeError(f"{code}: {message}")
    items = raw.get("zpData", {}).get("jobList", [])
    for item in items:
        card = boss.job_card_browser(item["securityId"], item["lid"])
        post_desc = card.get("zpData", {}).get("jobCard", {}).get(
            "postDescription", ""
        )
        print(item.get("jobName"), post_desc)

# AccountRiskError / EnvironmentRiskError → stop immediately; do not retry automatically.
# For code 37 that explicitly indicates an expired token/stoken, BossClient refreshes and retries at most once.
PY
```

### Environment health checks and recovery (required before fetching)

If `agent-reach doctor` reports boss as `off` or `warn` before a search, follow this
runbook. Do not guess by reading source code:

1. **Check whether the CDP port is reachable**:
   ```bash
   curl -s http://localhost:9222/json/version   # A Browser field means the port is reachable.
   ```

2. **Debugging Chrome is not running or has closed**: Launch dedicated Chrome for
   the operating system (its login state is separate from the everyday browser):
   ```bash
   # macOS
   open -na "Google Chrome" --args --remote-debugging-address=127.0.0.1 \
     --remote-debugging-port=9222 --user-data-dir="$HOME/.boss-chrome-profile" \
     "https://www.zhipin.com/web/geek/job"

   # Linux
   google-chrome --remote-debugging-address=127.0.0.1 \
     --remote-debugging-port=9222 --user-data-dir="$HOME/.boss-chrome-profile" \
     "https://www.zhipin.com/web/geek/job"
   ```

   Windows PowerShell:
   ```powershell
   Start-Process chrome.exe -ArgumentList '--remote-debugging-address=127.0.0.1','--remote-debugging-port=9222',"--user-data-dir=$env:USERPROFILE\.boss-chrome-profile",'https://www.zhipin.com/web/geek/job'
   ```

   Bind only to loopback. Any process that can access port 9222 can fully control this
   Chrome session; never expose it publicly. Reuse this dedicated profile long-term
   to preserve a stable session. Do not delete or recreate it on every run, or switch
   to the user's everyday Chrome profile by default. Close the dedicated window when
   it is not in use.

   **First step after launch: pause and have the user visually confirm the window is
   logged in (avatar in the top-right).** Do not substitute `boss status` for this
   check; it only validates the local session.enc, not the browser.

3. **User logs in manually (if the browser is logged out)**: Use doctor's browser-cookie
   probe as the primary check (no wt2 = browser logged out), followed by the user's
   visual confirmation. `boss status` is only a secondary reference. Ask the user to
   log in or scan the login code in this dedicated window. Once they confirm completion,
   save the CDP session:
   ```bash
   boss --cdp-url http://localhost:9222 login --cdp
   ```

   If the window is on a security-check page (`security-check` / `zhipin-security`),
   this is an anti-bot challenge rather than a login page. Wait for it to clear or ask
   the user to solve the slider manually. Do not treat it as a logged-out session and
   ask them to scan a login code again.

4. **Check session validity** (browser-cookie probe + stoken expiration):
   ```bash
   agent-reach doctor     # Check the browser wt2 cookie probe in the boss row's message.
   boss status            # Reflects only local session.enc; secondary reference only.
   ```

5. **Handle error codes** (during search/job-description retrieval):
   - `AUTH_EXPIRED` (user not logged in) → **ground truth**: the CDP browser is logged
     out, regardless of `boss status`. Go straight to step 3 and `login --cdp`. Do not
     reinterpret it as a “security check.”
   - code 36 (`ACCOUNT_RISK`) → stop immediately; handle it manually on the BOSS page.
     Do not retry automatically.
   - code 9 (`RATE_LIMITED`) → retry after a cooldown.
   - code 37 + `环境存在异常` (“abnormal environment detected”) → `ENVIRONMENT_RISK`.
     Stop immediately; do not refresh tokens, log in again, or retry automatically.
   - Only code 37 explicitly indicating an expired token/stoken is `TOKEN_REFRESH_FAILED`.
     The client automatically refreshes and retries at most once; log in again if it still fails.

When the user asks to start a search, the agent must specify strict CDP mode
(global options precede the subcommand). The city argument below is Guangzhou;
retain its Chinese spelling for the platform's city lookup:

```bash
boss --browser-source existing-browser --cdp-url http://localhost:9222 search "LLM" --city 广州 --page 1
```

Do not silently paginate continuously. boss-agent-cli PR #383 adds a persistent
5–10-second list-request budget across CLI processes for ordinary searches. Until
that PR is merged and released, the agent should still serialize and throttle calls.

> **Waiting is expected, not a hang**: When consecutive searches trigger throttling,
> boss-agent-cli silently waits 5–10 seconds. In a TTY it displays `节流等待 Ns…`
> (“throttling: waiting N seconds…”), but Agent Reach calls it with `--json`, which
> hides that message. During this waiting period, do not retry, launch another browser,
> or switch profiles.
