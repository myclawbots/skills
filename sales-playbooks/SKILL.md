---
name: sales_playbooks
description: Outbound sales playbooks, a deterministic pre-send gate and a local pipeline store for an SDR agent — prospect with signals, write short human cold email, handle replies, qualify, and never send without the owner's approval.
author:
  name: Ethan Rogers
  url: https://github.com/ethanplusai/harvey
license: MIT
category: productivity
tags: [sales, cold-email, prospecting, pipeline, objections]
suggested_template: sales_sdr
---

# Sales Playbooks

This skill turns an agent into a disciplined SDR: it finds prospects for a reason (a signal), writes
short human email, handles replies, qualifies, books, and keeps a pipeline the owner can read. Nothing
leaves without the owner's yes, and nothing leaves that fails the pre-send gate.

Adapted from Harvey (MIT, © 2026 Ethan Rogers); see `NOTICE`.

## What is in here

```
scripts/playbooks/          (shipped under scripts/ because that is what the registry delivers)
  sales_methodology.md    the loop, channel rules, decision priorities, metrics, hard ethical rules
  prospecting_tactics.md  finding companies and people without paid tools; signals; daily quotas
  lead_qualification.md   BANT screen, ICP score 1-10, MEDDIC, disqualifiers
  account_navigation.md   companies vs contacts, who to email first, multi-threading, sample review
  signal_playbook.md      turning one signal into the first line; which signal wins
  email_frameworks.md     the 3-email sequence, banned phrases, subject lines, the test
  offer_strategy.md       earn the right to ask; offer ladder; booking mechanics; pricing questions
  objection_handling.md   LAARC, the 4 categories, diagnose first, hard guardrails
  reply_handling.md       intents, conversation stages, what never gets a reply
  linkedin_outreach.md    LinkedIn via Linkedroid: connect, message, limits
scripts/
  gate.py                 deterministic pre-send check, exit 0 = may send
  pipeline.py             SQLite pipeline: companies, contacts, observations (signals), outbox, conversations, suppressions
```

Read `scripts/playbooks/sales_methodology.md` first. Then the playbook for the task at hand: write a sequence
→ `email_frameworks.md` + `signal_playbook.md`; a reply came in → `reply_handling.md` +
`objection_handling.md`; building a list → `prospecting_tactics.md` + `lead_qualification.md`.

## The rules that are not negotiable

1. **Nothing sends without the owner.** Every outgoing email or LinkedIn message is shown in chat,
   one at a time, and sent only after an explicit yes for that message (or for a batch the owner
   asked to approve as a batch). Never approve for them. Never "send the rest like this".
2. **The gate runs before every send**, after approval, on the exact text going out:
   `python3 scripts/gate.py --to <email> --subject <s> --body-file <f> [--status verified|risky|guess] [--kind sequence|reply]`.
   Exit 0 means send. Anything else: fix the email, re-show it, re-approve. Never bypass the gate.
3. **Opt-outs are absolute.** "Stop", "unsubscribe", "remove me", "not interested, don't email again"
   in any wording and on any channel: `pipeline.py suppress <email> --reason opt_out`, confirm once if
   a reply is appropriate, never contact again, never try to save it.
4. **Never fabricate.** No invented customers, numbers, case studies, scarcity, referrals, or prior
   conversations. Every claim traces to `sales/product_knowledge.md` or the prospect's own public pages.
5. **Say you are automated if asked.** Immediately and truthfully.
6. **When in doubt, don't send.** Flag it to the owner instead.

## Where things live

- `sales/config.yaml` — persona, product, offer, ICP, channels, caps, quiet hours (written during onboarding, see the template's BOOTSTRAP.md).
- `sales/product_knowledge.md`, `sales/competitive_intel.md` — learned from the owner's website and answers; the only sources for product claims.
- `sales/pipeline.db` — the SQLite store managed by `scripts/pipeline.py` (never edit by hand).
- `sales/drafts/` — email text files the gate reads.

All paths are under the workspace: `/root/.openclaw/workspace/sales/`.

## pipeline.py in one screen

```
pipeline.py init
pipeline.py add-company --name "Acme" --domain acme.com [--industry ...] [--size ...] [--location ...] [--source ...]
pipeline.py add-contact --company acme.com --first Sarah --last Lee --title "VP Marketing" [--email s@acme.com --email-status verified|risky|guess] [--linkedin URL]
pipeline.py observe --company acme.com [--contact s@acme.com] --signal HIRING_ROLE --text "Head of Growth" [--url ...] [--confidence 0.9]
pipeline.py signals                       # the catalog you may record (nothing is collected by default)
pipeline.py cohort --must HIRING_ROLE,DECISION_MAKER_TITLE --not INCUMBENT_AGENCY   # companies matching a signal query
pipeline.py score --contact s@acme.com --points 8 --note "exact title, verified email"
pipeline.py queue --contact s@acme.com --step 1 --subject "acme website" --body-file sales/drafts/acme-1.txt [--send-after 2026-10-22T14:00:00Z]
pipeline.py outbox                        # what waits for approval, in order
pipeline.py approve <id> | reject <id> --reason ...
pipeline.py sent <id> --message-id ...    # after the connector confirms
pipeline.py reply --contact s@acme.com --intent interested|objection|question|wrong_person|not_interested|opt_out|angry_legal|bounce --text "..."
pipeline.py stage --contact s@acme.com --to engaged|qualifying|presenting|negotiating|closing|closed_won|closed_lost
pipeline.py suppress <email> --reason opt_out|bounce|angry|legal|not_fit
pipeline.py is-suppressed <email>         # exit 0 = suppressed, do not contact
pipeline.py stats                         # counts the heartbeat decides from
pipeline.py export --what contacts|companies|outbox|conversations > file.csv
```

Every fact is a row in `observations` with a signal code, value, confidence, evidence URL and time,
so a company can be re-profiled later and the history kept.

## Sending

- **Gmail**: `gws gmail users messages send` with a plain-text body (the `google-workspace` skill has the exact command). Create a draft first when the owner wants to send from their own client: `gws gmail users drafts create`.
- **Outlook / Microsoft 365**: the `mail` command from the `outlook` skill.
- **LinkedIn**: the Linkedroid tools (`linkedin_send_connection`, `linkedin_send_message`), within the limits in `scripts/playbooks/linkedin_outreach.md`. Never browser automation.
- Plain text only. At most one link, none in email 1. No tracking pixels. The owner's real name, company and physical mailing address in the signature; a working way to say stop.

## The heartbeat

The template's HEARTBEAT.md runs the loop. Priority each pass: **replies → send approved → write
sequences for queued prospects → prospect → report**. Respect `quiet_hours` and `max_daily_sends`
from `sales/config.yaml`; stop all sending when bounces exceed the threshold and tell the owner.
