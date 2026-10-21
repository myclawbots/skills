#!/usr/bin/env python3
"""Deterministic pre-send gate: the last check before an email leaves.

Prompt rules are a floor, not a guarantee. Every outgoing email passes these non-model checks after
the owner approved it and before the connector sends it. A failure blocks the send and says why, so a
bad draft can never reach a prospect. Adapted from Harvey's gate.py (MIT, Ethan Rogers).

Usage:
  gate.py --to EMAIL --subject TEXT --body-file PATH [--status verified|risky|guess|invalid]
          [--allow-risky] [--kind sequence|reply] [--max-words N] [--json]
Exit 0: may send. Exit 1: blocked (reasons on stdout). Exit 2: usage error.

  --status      the address's deliverability as recorded in the pipeline (default: guess)
  --kind reply  the person wrote to us first, so deliverability is proven and --status is ignored
"""
import argparse
import json
import re
import sys

# Spam-filter and AI-tell phrases that must never appear in outgoing mail. Mirrors
# playbooks/email_frameworks.md; enforced here because a playbook can be ignored.
BANNED_PHRASES = (
    "act now", "buy now", "click here", "click below", "limited time", "limited offer",
    "exclusive deal", "special offer", "risk-free", "no obligation", "100% free", "make money",
    "double your", "guaranteed results", "winner", "congratulations",
    "i hope this finds you well", "hope this email finds you well", "i hope this email finds you",
    "picture this", "what if i told you", "in today's fast-paced world", "game-changer",
    "game changer", "cutting-edge", "revolutionize your", "unlock your", "supercharge your",
    "just following up", "just checking in", "i'd love to", "reaching out because",
    "quick question", "worth a quick look", "worth a quick chat", "worth a quick call",
    "as an ai", "i'm an ai", "i am an ai", "as a language model",
)

MAX_SUBJECT_LEN = 90
DEFAULT_MAX_BODY_WORDS = 220   # hard ceiling; the playbook aims far lower (75 for email 1)
MAX_LINKS = 1

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
MERGE_TAG_RE = re.compile(r"\{\{\s*\w+\s*\}\}|\{\s*\w+\s*\}(?!\})")
URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)
HTML_RE = re.compile(r"<\s*(html|body|div|table|img|a|p|br|span)\b", re.IGNORECASE)
DELIVERABLE = {"verified", "risky"}


def pre_send_check(to_email, subject, body, *, status="guess", allow_risky=False, kind="sequence",
                   max_words=DEFAULT_MAX_BODY_WORDS):
    """Every deterministic check. Returns a list of reasons; empty means the email may go."""
    reasons = []
    subject = (subject or "").strip()
    body = (body or "").strip()
    to_email = (to_email or "").strip().lower()

    if not EMAIL_RE.match(to_email):
        reasons.append(f"invalid recipient address '{to_email}'")
    if kind == "sequence":
        allowed = DELIVERABLE if allow_risky else {"verified"}
        if (status or "guess") not in allowed:
            reasons.append(f"email status '{status or 'guess'}' is not deliverable (need {', '.join(sorted(allowed))})")

    if not subject:
        reasons.append("empty subject")
    if not body:
        reasons.append("empty body")
    if len(subject) > MAX_SUBJECT_LEN:
        reasons.append(f"subject too long ({len(subject)} > {MAX_SUBJECT_LEN})")
    if re.match(r"^\s*(re|fwd?)\s*:", subject, re.IGNORECASE) and kind == "sequence":
        reasons.append("fake reply/forward subject on a fresh thread")
    words = len(body.split())
    if words > max_words:
        reasons.append(f"body too long ({words} words > {max_words})")

    leftover = MERGE_TAG_RE.findall(subject + " " + body)
    if leftover:
        reasons.append(f"unrendered merge tags: {sorted(set(leftover))[:3]}")

    lowered = (subject + " " + body).lower()
    hits = [p for p in BANNED_PHRASES if p in lowered]
    if hits:
        reasons.append(f"banned phrases: {hits[:3]}")
    if "—" in body or "—" in subject:
        reasons.append("em dash in text (an AI tell; use a period or comma)")

    links = URL_RE.findall(body)
    if len(links) > MAX_LINKS:
        reasons.append(f"too many links ({len(links)} > {MAX_LINKS})")
    if HTML_RE.search(body):
        reasons.append("HTML markup in body (plain text only)")
    if body.count("!") > 1:
        reasons.append("more than one exclamation mark")
    return reasons


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--to", required=True)
    p.add_argument("--subject", required=True)
    p.add_argument("--body-file", required=True)
    p.add_argument("--status", default="guess", choices=["verified", "risky", "guess", "invalid"])
    p.add_argument("--allow-risky", action="store_true")
    p.add_argument("--kind", default="sequence", choices=["sequence", "reply"])
    p.add_argument("--max-words", type=int, default=DEFAULT_MAX_BODY_WORDS)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        with open(a.body_file, encoding="utf-8") as f:
            body = f.read()
    except OSError as e:
        print(f"cannot read body file: {e}", file=sys.stderr)
        return 2
    reasons = pre_send_check(a.to, a.subject, body, status=a.status, allow_risky=a.allow_risky, kind=a.kind, max_words=a.max_words)
    if a.json:
        print(json.dumps({"ok": not reasons, "reasons": reasons, "words": len(body.split())}))
    elif reasons:
        print("BLOCKED:")
        for r in reasons:
            print(f"  - {r}")
    else:
        print(f"OK ({len(body.split())} words)")
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
