#!/usr/bin/env python3
"""The SDR pipeline: one SQLite file the agent and the owner can both read.

Every fact about a company or a person is a row in `observations` (signal code, value, confidence,
evidence URL, time), never a column, so new signals need no migration, history is free, and a cohort
is a query. Outgoing email waits in `outbox` until the owner approves it. Suppressions are forever.
Standard library only. Default file: /root/.openclaw/workspace/sales/pipeline.db (override with
SALES_PIPELINE_DB).

Run `pipeline.py --help` or `pipeline.py <command> --help`.
"""
import argparse
import csv
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone

DB = os.environ.get("SALES_PIPELINE_DB", "/root/.openclaw/workspace/sales/pipeline.db")

STAGES = ["initial_outreach", "engaged", "qualifying", "presenting", "negotiating", "closing", "closed_won", "closed_lost"]
INTENTS = ["interested", "question", "objection", "wrong_person", "not_interested", "opt_out", "angry_legal", "bounce", "auto_reply"]
STOP_INTENTS = {"opt_out": "opt_out", "angry_legal": "angry", "bounce": "bounce"}
SUPPRESS_REASONS = ["opt_out", "bounce", "angry", "legal", "not_fit", "owner"]
EMAIL_STATUSES = ["verified", "risky", "guess", "invalid"]

# The signal catalog: what may be recorded about a company or a person, and why it matters.
# Nothing is collected by default; the owner confirms which ones during onboarding.
SIGNALS = {
    "FOUND_IN_SERP": "appeared in a target-market search",
    "SERP_RANK": "search rank position for a target query (value_num)",
    "NO_WEBSITE": "no website found",
    "UNCLAIMED_LISTING": "business listing not claimed by the owner",
    "REVIEW_RATING": "public review rating (value_num)",
    "REVIEW_COUNT": "number of public reviews (value_num)",
    "INCUMBENT_AGENCY": "a footer credit names who built or runs the site (value_text)",
    "RUNNING_GOOGLE_ADS": "Google Ads tag on the site: spending on acquisition today",
    "RUNNING_META_ADS": "Meta pixel on the site: spending on paid social",
    "TECH_STACK": "platform and tools the site runs (value_text)",
    "NO_SCHEMA_MARKUP": "no JSON-LD structured data: a nameable SEO gap",
    "NO_ONLINE_BOOKING": "no booking or scheduling widget: after-hours demand is lost",
    "SITE_PAGE_COUNT": "pages in sitemap.xml (value_num)",
    "BLOG_STALE": "newest content older than a year (value_text = date)",
    "BLOCKS_AI_CRAWLERS": "robots.txt blocks AI crawlers",
    "HIRING_ROLE": "an open role that implies buying in your category (value_text = role)",
    "FUNDING": "a recent raise with a public source (value_text = round)",
    "CONTACT_FOUND": "a named person on the team/about page (value_text = title)",
    "DECISION_MAKER_TITLE": "title matches an owner or decision-maker pattern",
    "REGISTRY_VERIFIED": "public registry confirms the person's role",
    "LIKELY_OWNER": "indicators suggest this person owns the business",
    "EMAIL_PATTERN": "the domain's address format, e.g. first.last (value_text)",
    "EMAIL_STATUS": "verified / risky / guess / invalid (value_text)",
    "CONTACT_FORM_URL": "a contact form when no address is deliverable (value_text = URL)",
    "COMPETITOR_CUSTOMER": "publicly uses a competitor (value_text)",
    "LEADERSHIP_CHANGE": "a new leader in a relevant function (value_text)",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
  id TEXT PRIMARY KEY, name TEXT NOT NULL, domain TEXT UNIQUE, website TEXT, description TEXT, industry TEXT,
  size TEXT, location TEXT, source TEXT, source_url TEXT, notes TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS contacts (
  id TEXT PRIMARY KEY, company_id TEXT NOT NULL REFERENCES companies(id), first_name TEXT NOT NULL, last_name TEXT NOT NULL,
  title TEXT NOT NULL, email TEXT UNIQUE, email_status TEXT DEFAULT 'guess', linkedin_url TEXT, seniority TEXT, department TEXT,
  score INTEGER, score_note TEXT, stage TEXT NOT NULL DEFAULT 'initial_outreach', channel TEXT, source_url TEXT, notes TEXT,
  created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS observations (
  id TEXT PRIMARY KEY, company_id TEXT, contact_id TEXT, signal_code TEXT NOT NULL, value_num REAL, value_text TEXT,
  confidence REAL NOT NULL DEFAULT 1.0, evidence_url TEXT, observed_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS obs_company ON observations(company_id, signal_code);
CREATE INDEX IF NOT EXISTS obs_contact ON observations(contact_id, signal_code);
CREATE TABLE IF NOT EXISTS outbox (
  id TEXT PRIMARY KEY, contact_id TEXT NOT NULL REFERENCES contacts(id), step INTEGER NOT NULL, channel TEXT NOT NULL DEFAULT 'email',
  subject TEXT, body TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', send_after TEXT, approved_at TEXT, sent_at TEXT,
  message_id TEXT, rejected_reason TEXT, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY, contact_id TEXT NOT NULL REFERENCES contacts(id), direction TEXT NOT NULL, intent TEXT, text TEXT,
  at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS suppressions (
  email TEXT PRIMARY KEY, reason TEXT NOT NULL, note TEXT, at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, kind TEXT NOT NULL, detail TEXT);
"""


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def connect():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    return db


def log(db, kind, detail=""):
    db.execute("INSERT INTO events (at, kind, detail) VALUES (?, ?, ?)", (now(), kind, detail))


def out(obj):
    print(json.dumps(obj, indent=2, default=str))


def company_by_ref(db, ref):
    """A company by domain or id."""
    row = db.execute("SELECT * FROM companies WHERE domain = ? OR id = ?", (ref.lower(), ref)).fetchone()
    if not row:
        sys.exit(f"no company for '{ref}' (add-company first)")
    return row


def contact_by_ref(db, ref):
    """A contact by email or id."""
    row = db.execute("SELECT * FROM contacts WHERE email = ? OR id = ?", (ref.lower(), ref)).fetchone()
    if not row:
        sys.exit(f"no contact for '{ref}'")
    return row


def suppressed(db, email):
    return bool(email) and db.execute("SELECT 1 FROM suppressions WHERE email = ?", (email.lower(),)).fetchone() is not None


# ── commands ─────────────────────────────────────────────────────────────────

def cmd_init(db, a):
    out({"ok": True, "db": DB, "signals": len(SIGNALS)})


def cmd_signals(db, a):
    for code, why in SIGNALS.items():
        print(f"{code:22} {why}")


def cmd_add_company(db, a):
    t = now()
    domain = (a.domain or "").lower().strip() or None
    existing = db.execute("SELECT * FROM companies WHERE domain = ?", (domain,)).fetchone() if domain else None
    if existing:
        db.execute("UPDATE companies SET name=?, website=COALESCE(?,website), description=COALESCE(?,description), industry=COALESCE(?,industry), size=COALESCE(?,size), location=COALESCE(?,location), source=COALESCE(?,source), source_url=COALESCE(?,source_url), updated_at=? WHERE id=?",
                   (a.name, a.website, a.description, a.industry, a.size, a.location, a.source, a.source_url, t, existing["id"]))
        db.commit()
        return out({"id": existing["id"], "updated": True})
    cid = new_id("co")
    db.execute("INSERT INTO companies VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
               (cid, a.name, domain, a.website, a.description, a.industry, a.size, a.location, a.source, a.source_url, None, t, t))
    log(db, "company.added", cid)
    db.commit()
    out({"id": cid, "created": True})


def cmd_add_contact(db, a):
    co = company_by_ref(db, a.company)
    email = (a.email or "").lower().strip() or None
    if email and suppressed(db, email):
        sys.exit(f"{email} is suppressed; do not add")
    t = now()
    existing = db.execute("SELECT * FROM contacts WHERE email = ?", (email,)).fetchone() if email else None
    if existing:
        db.execute("UPDATE contacts SET title=?, email_status=?, linkedin_url=COALESCE(?,linkedin_url), updated_at=? WHERE id=?",
                   (a.title, a.email_status, a.linkedin, t, existing["id"]))
        db.commit()
        return out({"id": existing["id"], "updated": True})
    cid = new_id("ct")
    db.execute("INSERT INTO contacts (id, company_id, first_name, last_name, title, email, email_status, linkedin_url, seniority, department, source_url, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
               (cid, co["id"], a.first, a.last, a.title, email, a.email_status, a.linkedin, a.seniority, a.department, a.source_url, t, t))
    log(db, "contact.added", cid)
    db.commit()
    out({"id": cid, "company_id": co["id"], "created": True})


def cmd_observe(db, a):
    if a.signal not in SIGNALS:
        sys.exit(f"unknown signal '{a.signal}'; see `pipeline.py signals`")
    co = company_by_ref(db, a.company) if a.company else None
    ct = contact_by_ref(db, a.contact) if a.contact else None
    if not co and not ct:
        sys.exit("observe needs --company or --contact")
    oid = new_id("ob")
    db.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?)",
               (oid, co["id"] if co else (ct["company_id"] if ct else None), ct["id"] if ct else None, a.signal, a.num, a.text, a.confidence, a.url, now()))
    if a.signal == "EMAIL_STATUS" and ct and a.text in EMAIL_STATUSES:
        db.execute("UPDATE contacts SET email_status=?, updated_at=? WHERE id=?", (a.text, now(), ct["id"]))
    db.commit()
    out({"id": oid})


def cmd_cohort(db, a):
    must = [s for s in (a.must or "").split(",") if s]
    nots = [s for s in (a.exclude or "").split(",") if s]
    for s in must + nots:
        if s not in SIGNALS:
            sys.exit(f"unknown signal '{s}'")
    sql = "SELECT c.id, c.name, c.domain, c.industry, c.size FROM companies c WHERE 1=1"
    params = []
    for s in must:
        sql += " AND EXISTS (SELECT 1 FROM observations o WHERE o.company_id = c.id AND o.signal_code = ?)"
        params.append(s)
    for s in nots:
        sql += " AND NOT EXISTS (SELECT 1 FROM observations o WHERE o.company_id = c.id AND o.signal_code = ?)"
        params.append(s)
    rows = db.execute(sql + " ORDER BY c.name", params).fetchall()
    out({"count": len(rows), "must": must, "not": nots, "companies": [dict(r) for r in rows]})


def cmd_score(db, a):
    ct = contact_by_ref(db, a.contact)
    if not 1 <= a.points <= 10:
        sys.exit("score is 1 to 10")
    db.execute("UPDATE contacts SET score=?, score_note=?, updated_at=? WHERE id=?", (a.points, a.note, now(), ct["id"]))
    db.commit()
    tier = "high" if a.points >= 8 else "medium" if a.points >= 5 else "low" if a.points >= 3 else "skip"
    out({"id": ct["id"], "score": a.points, "tier": tier})


def cmd_queue(db, a):
    ct = contact_by_ref(db, a.contact)
    if a.channel == "email" and not ct["email"]:
        sys.exit("contact has no email")
    if ct["email"] and suppressed(db, ct["email"]):
        sys.exit(f"{ct['email']} is suppressed; nothing may be queued")
    with open(a.body_file, encoding="utf-8") as f:
        body = f.read().strip()
    oid = new_id("ob" if False else "msg")
    db.execute("INSERT INTO outbox (id, contact_id, step, channel, subject, body, status, send_after, created_at) VALUES (?,?,?,?,?,?,'pending',?,?)",
               (oid, ct["id"], a.step, a.channel, a.subject, body, a.send_after, now()))
    db.commit()
    out({"id": oid, "status": "pending", "words": len(body.split()), "next": "show it to the owner; `approve <id>` only after their yes"})


def cmd_outbox(db, a):
    rows = db.execute("""SELECT o.id, o.step, o.channel, o.status, o.subject, o.send_after, c.first_name, c.last_name, c.email, c.email_status, co.name AS company
                         FROM outbox o JOIN contacts c ON c.id = o.contact_id JOIN companies co ON co.id = c.company_id
                         WHERE o.status IN ('pending','approved') ORDER BY o.status DESC, o.created_at""").fetchall()
    out({"count": len(rows), "messages": [dict(r) for r in rows]})


def cmd_show(db, a):
    row = db.execute("SELECT o.*, c.email, c.first_name, c.last_name FROM outbox o JOIN contacts c ON c.id = o.contact_id WHERE o.id = ?", (a.id,)).fetchone()
    if not row:
        sys.exit("no such message")
    out(dict(row))


def cmd_approve(db, a):
    row = db.execute("SELECT * FROM outbox WHERE id = ? AND status = 'pending'", (a.id,)).fetchone()
    if not row:
        sys.exit("no pending message with that id")
    db.execute("UPDATE outbox SET status='approved', approved_at=? WHERE id=?", (now(), a.id))
    log(db, "outbox.approved", a.id)
    db.commit()
    out({"id": a.id, "status": "approved", "next": "run gate.py on the exact text, then send through the connector, then `sent <id>`"})


def cmd_reject(db, a):
    db.execute("UPDATE outbox SET status='rejected', rejected_reason=? WHERE id=? AND status IN ('pending','approved')", (a.reason, a.id))
    db.commit()
    out({"id": a.id, "status": "rejected"})


def cmd_sent(db, a):
    row = db.execute("SELECT * FROM outbox WHERE id = ? AND status = 'approved'", (a.id,)).fetchone()
    if not row:
        sys.exit("message is not approved (approve first) or already sent")
    t = now()
    db.execute("UPDATE outbox SET status='sent', sent_at=?, message_id=? WHERE id=?", (t, a.message_id, a.id))
    db.execute("INSERT INTO conversations VALUES (?,?,?,?,?,?)", (new_id("cv"), row["contact_id"], "out", None, row["body"], t))
    log(db, "outbox.sent", a.id)
    db.commit()
    out({"id": a.id, "status": "sent"})


def cmd_reply(db, a):
    ct = contact_by_ref(db, a.contact)
    t = now()
    db.execute("INSERT INTO conversations VALUES (?,?,?,?,?,?)", (new_id("cv"), ct["id"], "in", a.intent, a.text, t))
    result = {"contact": ct["id"], "intent": a.intent}
    if a.intent in STOP_INTENTS and ct["email"]:
        db.execute("INSERT OR IGNORE INTO suppressions VALUES (?,?,?,?)", (ct["email"].lower(), STOP_INTENTS[a.intent], a.text[:200] if a.text else None, t))
        db.execute("UPDATE outbox SET status='cancelled', rejected_reason=? WHERE contact_id=? AND status IN ('pending','approved')", (a.intent, ct["id"]))
        db.execute("UPDATE contacts SET stage='closed_lost', updated_at=? WHERE id=?", (t, ct["id"]))
        result["suppressed"] = True
        result["note"] = "no reply; the sequence is cancelled" if a.intent != "opt_out" else "a one-line confirmation at most; never again"
    elif a.intent == "not_interested":
        db.execute("UPDATE outbox SET status='cancelled', rejected_reason='not_interested' WHERE contact_id=? AND status IN ('pending','approved')", (ct["id"],))
        db.execute("UPDATE contacts SET stage='closed_lost', updated_at=? WHERE id=?", (t, ct["id"]))
        result["note"] = "no reply; one no is enough"
    elif a.intent in ("interested", "question", "objection"):
        db.execute("UPDATE outbox SET status='cancelled', rejected_reason='replied' WHERE contact_id=? AND status IN ('pending','approved')", (ct["id"],))
        if ct["stage"] == "initial_outreach":
            db.execute("UPDATE contacts SET stage='engaged', updated_at=? WHERE id=?", (t, ct["id"]))
        result["note"] = "remaining sequence cancelled; answer first, then the next step"
    if a.intent == "bounce":
        bounces = db.execute("SELECT count(*) FROM suppressions WHERE reason='bounce' AND at > datetime('now','-1 day')").fetchone()[0]
        result["bounces_24h"] = bounces
    db.commit()
    out(result)


def cmd_stage(db, a):
    ct = contact_by_ref(db, a.contact)
    db.execute("UPDATE contacts SET stage=?, updated_at=? WHERE id=?", (a.to, now(), ct["id"]))
    log(db, "stage", f"{ct['id']} -> {a.to}")
    db.commit()
    out({"id": ct["id"], "stage": a.to})


def cmd_suppress(db, a):
    t = now()
    db.execute("INSERT OR REPLACE INTO suppressions VALUES (?,?,?,?)", (a.email.lower(), a.reason, a.note, t))
    db.execute("UPDATE outbox SET status='cancelled', rejected_reason=? WHERE contact_id IN (SELECT id FROM contacts WHERE email=?) AND status IN ('pending','approved')", (a.reason, a.email.lower()))
    log(db, "suppressed", f"{a.email} {a.reason}")
    db.commit()
    out({"email": a.email.lower(), "reason": a.reason, "forever": True})


def cmd_is_suppressed(db, a):
    row = db.execute("SELECT * FROM suppressions WHERE email = ?", (a.email.lower(),)).fetchone()
    if row:
        out(dict(row))
        return 0
    print("not suppressed")
    return 1


def cmd_stats(db, a):
    q = lambda sql, *p: db.execute(sql, p).fetchone()[0]
    today = now()[:10]
    stats = {
        "companies": q("SELECT count(*) FROM companies"),
        "contacts": q("SELECT count(*) FROM contacts"),
        "qualified_without_sequence": q("SELECT count(*) FROM contacts c WHERE c.score >= 5 AND c.stage='initial_outreach' AND c.email IS NOT NULL AND c.email_status IN ('verified','risky') AND NOT EXISTS (SELECT 1 FROM outbox o WHERE o.contact_id=c.id) AND NOT EXISTS (SELECT 1 FROM suppressions s WHERE s.email=c.email)"),
        "outbox_pending_approval": q("SELECT count(*) FROM outbox WHERE status='pending'"),
        "outbox_approved_due": q("SELECT count(*) FROM outbox WHERE status='approved' AND (send_after IS NULL OR send_after <= ?)", now()),
        "sent_today": q("SELECT count(*) FROM outbox WHERE status='sent' AND sent_at LIKE ?", today + "%"),
        "replies_unanswered": q("SELECT count(*) FROM contacts c WHERE (SELECT direction FROM conversations v WHERE v.contact_id=c.id ORDER BY at DESC LIMIT 1)='in' AND c.stage NOT IN ('closed_won','closed_lost')"),
        "bounces_24h": q("SELECT count(*) FROM suppressions WHERE reason='bounce' AND at > datetime('now','-1 day')"),
        "suppressed": q("SELECT count(*) FROM suppressions"),
        "by_stage": {r["stage"]: r["n"] for r in db.execute("SELECT stage, count(*) AS n FROM contacts GROUP BY stage")},
        "reply_rate": None,
    }
    sent = q("SELECT count(DISTINCT contact_id) FROM outbox WHERE status='sent'")
    replied = q("SELECT count(DISTINCT contact_id) FROM conversations WHERE direction='in' AND intent NOT IN ('bounce','auto_reply')")
    positive = q("SELECT count(DISTINCT contact_id) FROM conversations WHERE direction='in' AND intent IN ('interested','question','objection')")
    if sent:
        stats["reply_rate"] = round(100.0 * replied / sent, 1)
        stats["positive_reply_rate"] = round(100.0 * positive / sent, 1)
    out(stats)


def cmd_export(db, a):
    table = {"contacts": "SELECT c.*, co.name AS company, co.domain FROM contacts c JOIN companies co ON co.id=c.company_id",
             "companies": "SELECT * FROM companies",
             "outbox": "SELECT o.*, c.email FROM outbox o JOIN contacts c ON c.id=o.contact_id",
             "conversations": "SELECT v.*, c.email FROM conversations v JOIN contacts c ON c.id=v.contact_id"}[a.what]
    rows = db.execute(table).fetchall()
    w = csv.writer(sys.stdout)
    if rows:
        w.writerow(rows[0].keys())
        for r in rows:
            w.writerow([r[k] for k in r.keys()])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init").set_defaults(fn=cmd_init)
    sub.add_parser("signals").set_defaults(fn=cmd_signals)
    s = sub.add_parser("add-company"); s.add_argument("--name", required=True); s.add_argument("--domain"); s.add_argument("--website"); s.add_argument("--description"); s.add_argument("--industry"); s.add_argument("--size"); s.add_argument("--location"); s.add_argument("--source"); s.add_argument("--source-url"); s.set_defaults(fn=cmd_add_company)
    s = sub.add_parser("add-contact"); s.add_argument("--company", required=True); s.add_argument("--first", required=True); s.add_argument("--last", required=True); s.add_argument("--title", required=True); s.add_argument("--email"); s.add_argument("--email-status", default="guess", choices=EMAIL_STATUSES); s.add_argument("--linkedin"); s.add_argument("--seniority"); s.add_argument("--department"); s.add_argument("--source-url"); s.set_defaults(fn=cmd_add_contact)
    s = sub.add_parser("observe"); s.add_argument("--company"); s.add_argument("--contact"); s.add_argument("--signal", required=True); s.add_argument("--num", type=float); s.add_argument("--text"); s.add_argument("--url"); s.add_argument("--confidence", type=float, default=1.0); s.set_defaults(fn=cmd_observe)
    s = sub.add_parser("cohort"); s.add_argument("--must"); s.add_argument("--not", dest="exclude"); s.set_defaults(fn=cmd_cohort)
    s = sub.add_parser("score"); s.add_argument("--contact", required=True); s.add_argument("--points", type=int, required=True); s.add_argument("--note"); s.set_defaults(fn=cmd_score)
    s = sub.add_parser("queue"); s.add_argument("--contact", required=True); s.add_argument("--step", type=int, required=True); s.add_argument("--channel", default="email", choices=["email", "linkedin"]); s.add_argument("--subject"); s.add_argument("--body-file", required=True); s.add_argument("--send-after"); s.set_defaults(fn=cmd_queue)
    sub.add_parser("outbox").set_defaults(fn=cmd_outbox)
    s = sub.add_parser("show"); s.add_argument("id"); s.set_defaults(fn=cmd_show)
    s = sub.add_parser("approve"); s.add_argument("id"); s.set_defaults(fn=cmd_approve)
    s = sub.add_parser("reject"); s.add_argument("id"); s.add_argument("--reason", required=True); s.set_defaults(fn=cmd_reject)
    s = sub.add_parser("sent"); s.add_argument("id"); s.add_argument("--message-id"); s.set_defaults(fn=cmd_sent)
    s = sub.add_parser("reply"); s.add_argument("--contact", required=True); s.add_argument("--intent", required=True, choices=INTENTS); s.add_argument("--text"); s.set_defaults(fn=cmd_reply)
    s = sub.add_parser("stage"); s.add_argument("--contact", required=True); s.add_argument("--to", required=True, choices=STAGES); s.set_defaults(fn=cmd_stage)
    s = sub.add_parser("suppress"); s.add_argument("email"); s.add_argument("--reason", required=True, choices=SUPPRESS_REASONS); s.add_argument("--note"); s.set_defaults(fn=cmd_suppress)
    s = sub.add_parser("is-suppressed"); s.add_argument("email"); s.set_defaults(fn=cmd_is_suppressed)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    s = sub.add_parser("export"); s.add_argument("--what", required=True, choices=["contacts", "companies", "outbox", "conversations"]); s.set_defaults(fn=cmd_export)
    a = p.parse_args(argv)
    db = connect()
    try:
        rc = a.fn(db, a)
    finally:
        db.close()
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())
