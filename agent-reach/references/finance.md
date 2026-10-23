# Financial market data

Xueqiu stock quotes, search, and trending content. Quotes may be delayed and are not investment advice.

## Check status first

```bash
agent-reach doctor --json
```

Use the backend in `xueqiu.active_backend` when populated; `null` only means Doctor
did not complete a live content check. Xueqiu needs a logged-in session or the minimum
required cookie. Do not interpret HTTP 400 as evidence that a stock does not exist.

## OpenCLI (preferred on desktops with an existing logged-in Chrome session)

```bash
# Verify the current login session
opencli xueqiu whoami -f yaml

# Stock search and live quotes
opencli xueqiu search "NVIDIA" -f yaml
opencli xueqiu stock NVDA -f yaml

# Trending content and stocks
opencli xueqiu hot -f yaml
opencli xueqiu hot-stock -f yaml

# View all read-only commands
opencli xueqiu --help
```

OpenCLI only reuses an existing browser session explicitly controlled by the user.
Do not automatically run `opencli xueqiu login`. If no logged-in session exists,
ask the user to log in to Chrome first, or explicitly import the minimum cookie
required by Xueqiu:

```bash
agent-reach configure --from-browser chrome --platform xueqiu
```

This configuration reads and saves only `xq_a_token`; it does not collect cookies
from other platforms.

## Verification and failure handling

- Success means receiving a stock name, ticker, price, or nonempty content list. Exit code 0 with empty fields does not count.
- HTTP 400 usually indicates a session/cookie problem, not a nonexistent ticker.
- If `whoami` succeeds but `stock`/`hot` fails, report an adapter parsing or platform API issue. Do not misdiagnose it as a logged-out session.
