#!/bin/bash
# vault-curl — curl for calls that use a key saved in MyClawBots → Secrets.
#
# The agent only ever holds surrogates (mcb_sec_…). This wrapper rewrites every
# https:// URL to the api-proxy's /vault/fwd/<host>/<path> route, where the
# proxy swaps each surrogate for the real key (only toward that key's allowed
# hosts and injection points) and scrubs it from the response. Spec:
# docs/secrets-vault.md §10.1.
#
# Options are an ALLOWLIST: anything that could send the request (or the
# platform key) somewhere other than the vault — proxies, --connect-to,
# --resolve, config files, --next — is refused with exit 2.
#
# Must stay bash 3.2 compatible (the tests run it with macOS /bin/bash): no
# ${x,,}, no associative arrays, no mapfile. Never use `set -x` here, and never
# print the key. A copy ships in the gemini-image skill; keep them identical.
set -euo pipefail

VAULT_CURL_BIN="${VAULT_CURL_BIN:-/usr/bin/curl}"
VAULT_OPENCLAW_CONFIG="${VAULT_OPENCLAW_CONFIG:-/root/.openclaw/openclaw.json}"
VAULT_APPLY_ENV="${VAULT_APPLY_ENV:-/root/.openclaw/apply-env.sh}"

usage() {
    cat <<'USAGE'
vault-curl — call an API with a key saved in MyClawBots → Secrets.

Use it exactly like curl, with https:// URLs only:

    vault-curl -sS https://api.example.com/v1/things -H "Authorization: Bearer $MY_KEY"

Put $NAME only where the key's "Put it in" says (a header, a query parameter,
or -u for Basic auth). Your saved keys and where each one goes are listed in
AGENTS.md ("Saved API keys"). A key added after you started is not in your env
yet: run `vault-curl --secrets` (or call the myclawbots list_secrets tool) and
use its surrogate string in place of $NAME. OpenClaw's own secrets tool does
not see these keys.

    vault-curl --secrets     # JSON: every saved key, its surrogate, hosts, where it goes
USAGE
}

die() { echo "vault-curl: $2" >&2; exit "$1"; }

lower() { printf '%s' "$1" | tr '[:upper:]' '[:lower:]'; }

# ── --help / no arguments ─────────────────────────────────────
if [ "$#" -eq 0 ]; then
    usage >&2
    exit 2
fi
for a in "$@"; do
    [ "$a" = "--" ] && break
    if [ "$a" = "--help" ]; then usage; exit 0; fi
done

# ── Vault base URL ────────────────────────────────────────────
# VAULT_API_PROXY_URL, not VAULT_PROXY_URL: that name is the vault-proxy
# (:3128 HTTPS proxy) in control-plane env and must never be taken for the
# api-proxy base.
VAULT_BASE="${VAULT_API_PROXY_URL:-${API_PROXY_URL:-${SOCIAL_POST_PROXY_URL:-}}}"
while [ -n "$VAULT_BASE" ] && [ "${VAULT_BASE%/}" != "$VAULT_BASE" ]; do
    VAULT_BASE="${VAULT_BASE%/}"
done
[ -n "$VAULT_BASE" ] || die 1 "API_PROXY_URL is not configured"

# ── Proxy key (D17): openclaw.json MCP header → apply-env.sh → env ──
# Read at run time, so a settings save that mints a new key takes effect
# without restarting the gateway. apply-env.sh is parsed, never sourced.
# Sets KEY.
is_key() { [[ "$1" =~ ^[0-9a-f]{64}$ ]]; }
resolve_key() {
    local cand
    KEY=""
    if command -v jq >/dev/null 2>&1; then
        cand=$(jq -r '.mcp.servers.myclawbots.headers["x-api-key"] // empty' "$VAULT_OPENCLAW_CONFIG" 2>/dev/null || true)
        if is_key "$cand"; then KEY="$cand"; fi
    fi
    if [ -z "$KEY" ]; then
        cand=$(sed -n 's/^export PROXY_API_KEY="\([0-9a-f]\{64\}\)"$/\1/p' "$VAULT_APPLY_ENV" 2>/dev/null | tail -n 1 || true)
        if is_key "$cand"; then KEY="$cand"; fi
    fi
    if [ -z "$KEY" ] && is_key "${PROXY_API_KEY:-}"; then
        KEY="$PROXY_API_KEY"
    fi
    [ -n "$KEY" ] || die 1 "no MyClawBots proxy key found"
}

run_curl() {
    exec env -u http_proxy -u HTTP_PROXY -u https_proxy -u HTTPS_PROXY -u all_proxy -u ALL_PROXY \
        -u no_proxy -u NO_PROXY -u CURL_HOME \
        "$VAULT_CURL_BIN" -q --noproxy '*' --proto =http --proto-redir =http --max-redirs 10 --path-as-is \
        -H "x-mcb-proxy-key: ${KEY}" "$@"
}

# ── --secrets: the live listing (surrogates only, never values) ──
# The same GET start.sh makes at boot, so a key added after boot can be found
# without a restart or an MCP client.
if [ "$#" -eq 1 ] && [ "$1" = "--secrets" ]; then
    resolve_key
    run_curl -sS --fail-with-body --max-time 20 "${VAULT_BASE}/vault/secrets"
fi

# ── Option tables ─────────────────────────────────────────────
SHORT_FLAGS='sSfiIvLGgNOJ#'
SHORT_VALUE='AbcdDeFHmorTuwXyYzC'
LONG_FLAGS=' --silent --show-error --fail --fail-with-body --fail-early --include --head --verbose --location --get --globoff --no-buffer --compressed --no-progress-meter --progress-bar --remote-name --remote-header-name --create-dirs --http1.1 --http2 --raw --retry-all-errors --retry-connrefused --no-keepalive '
LONG_VALUE=' --data --data-ascii --data-binary --data-raw --data-urlencode --json --form --form-string --header --user --user-agent --referer --cookie --cookie-jar --output --output-dir --dump-header --write-out --request --max-time --connect-timeout --upload-file --range --retry --retry-delay --retry-max-time --limit-rate --max-filesize --oauth2-bearer --url-query --speed-limit --speed-time --time-cond --continue-at '

# in_list " --a --b " --a   (exact word match, no globbing)
in_list() {
    case "$1" in
        *" $2 "*) return 0 ;;
    esac
    return 1
}

refuse() {
    die 2 "$1 is not allowed: it could send the request somewhere the vault can't check"
}

# Named explicitly so the agent gets a clear reason (the allowlist would
# refuse them anyway).
is_refused_long() {
    case "$1" in
        --proxy|--proxy-*|--preproxy|--socks*|--connect-to|--resolve|--unix-socket|\
        --abstract-unix-socket|--config|--next|--doh-url|--interface|--haproxy-protocol|\
        --expand-*|--variable|--location-trusted|--proto|--proto-redir|--path-as-is|\
        --max-redirs|--insecure|--cert|--key|--cacert|--capath|--trace|--trace-ascii|\
        --stderr|--netrc*|--aws-sigv4|--libcurl) return 0 ;;
    esac
    return 1
}

is_refused_short() {
    case "$1" in
        x|U|K|:|n|k) return 0 ;;
    esac
    return 1
}

# ── URL candidate → vault URL ─────────────────────────────────
# Sets REWRITTEN. Path and query bytes are kept exactly (no re-encoding).
rewrite_url() {
    local url="$1" scheme rest authority tail path seg lseg
    scheme=$(lower "${url:0:8}")
    if [ "$scheme" != "https://" ]; then
        if [ "$(lower "${url:0:7}")" = "http://" ]; then
            die 2 "only https:// URLs can use saved secrets"
        fi
        die 2 "$url is not an https:// URL"
    fi
    rest="${url:8}"

    # Authority ends at the first / ? or #.
    authority="${rest%%[/?#]*}"
    tail="${rest:${#authority}}"

    case "$authority" in
        *@*) die 2 "credentials in the URL are not supported; put credentials in -u or a header" ;;
    esac
    authority=$(lower "$authority")
    authority="${authority%:443}"
    case "$authority" in
        '') die 2 "$url has no host" ;;
        *:*) die 2 "only the default https port (443) is supported" ;;
    esac

    # Drop any #fragment.
    tail="${tail%%#*}"

    # No . or .. path segments (curl runs with --path-as-is, and the proxy
    # refuses them too). Percent-encoded dots count: URL parsers decode them.
    path="${tail%%\?*}"
    while [ -n "$path" ]; do
        path="${path#/}"
        seg="${path%%/*}"
        path="${path:${#seg}}"
        lseg=$(lower "$seg")
        case "$lseg" in
            .|..|%2e|.%2e|%2e.|%2e%2e) die 2 "./.. path segments are not supported" ;;
        esac
    done

    [ -n "$tail" ] || tail="/"
    REWRITTEN="${VAULT_BASE}/vault/fwd/${authority}${tail}"
}

# ── Argument walk ─────────────────────────────────────────────
OUT=()
URLS=0
positional=0
while [ "$#" -gt 0 ]; do
    arg="$1"
    shift

    if [ "$positional" -eq 1 ]; then
        rewrite_url "$arg"; OUT+=("$REWRITTEN"); URLS=$((URLS + 1))
        continue
    fi

    case "$arg" in
        --)
            positional=1
            ;;
        --*)
            name="${arg%%=*}"
            if [ "$name" != "$arg" ]; then has_eq=1; value="${arg#*=}"; else has_eq=0; value=""; fi
            if is_refused_long "$name"; then refuse "$name"; fi
            if [ "$name" = "--url" ]; then
                if [ "$has_eq" -eq 0 ]; then
                    [ "$#" -gt 0 ] || die 2 "--url needs a value"
                    value="$1"; shift
                fi
                rewrite_url "$value"; OUT+=("--url" "$REWRITTEN"); URLS=$((URLS + 1))
            elif in_list "$LONG_FLAGS" "$name"; then
                [ "$has_eq" -eq 0 ] || die 2 "$name does not take a value"
                OUT+=("$arg")
            elif in_list "$LONG_VALUE" "$name"; then
                if [ "$has_eq" -eq 1 ]; then
                    OUT+=("$arg")
                else
                    [ "$#" -gt 0 ] || die 2 "$name needs a value"
                    OUT+=("$arg" "$1"); shift
                fi
            else
                die 2 "$name is not supported"
            fi
            ;;
        -?*)
            # Short bundle, one letter at a time. The first value letter takes
            # the rest of the bundle (or the next argument) as its value.
            i=1
            took_next=0
            while [ "$i" -lt "${#arg}" ]; do
                c="${arg:$i:1}"
                if is_refused_short "$c"; then refuse "-$c"; fi
                case "$SHORT_FLAGS" in
                    *"$c"*) i=$((i + 1)); continue ;;
                esac
                case "$SHORT_VALUE" in
                    *"$c"*)
                        if [ $((i + 1)) -ge "${#arg}" ]; then
                            [ "$#" -gt 0 ] || die 2 "-$c needs a value"
                            took_next=1
                        fi
                        break
                        ;;
                esac
                die 2 "-$c is not supported"
            done
            if [ "$took_next" -eq 1 ]; then
                OUT+=("$arg" "$1"); shift
            else
                OUT+=("$arg")
            fi
            ;;
        *)
            rewrite_url "$arg"; OUT+=("$REWRITTEN"); URLS=$((URLS + 1))
            ;;
    esac
done

[ "$URLS" -gt 0 ] || die 2 "no https:// URL given"

resolve_key

# -q must be curl's first argument (it disables ~/.curlrc). --proto =http is
# right: every URL curl fetches is a rewritten plain-http vault URL on 6PN.
run_curl ${OUT[@]+"${OUT[@]}"}
