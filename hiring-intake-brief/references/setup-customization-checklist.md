---
title: Setup and customization checklist
description: Trigger setup, placeholders, policy decisions and the behaviour that must never be removed.
---

# Setup and customization checklist

## 1. Trigger setup

Two triggers. A new role fires a full intake. A stalled search fires rewrite mode. Reference triggers:

```
A new role needs briefing: [role].

Load and follow the <Hiring intake brief> skill.

Context for this run:
- Role: [ATS link or ID, or "new"]
- Hiring manager: [name]
- Intake notes or recording: [link, if the call has happened]
```

```
The search for [role] has stalled.

Load and follow the <Hiring intake brief> skill in Rewrite mode.

Context for this run:
- Current brief: [version and link]
- What has happened so far: [candidates, drop-off reasons, feedback]
```

- [ ] `{{ATS}}` or `{{DOCS}}` holds past job descriptions and briefs for similar seats.
- [ ] `{{REVIEW_CHANNEL}}` exists and every sign-off holder reads it.

## 2. Placeholders

- [ ] `{{ATS}}`, `{{CRM}}`, `{{DOCS}}`, `{{NOTES_TOOL}}`, `{{REVIEW_CHANNEL}}`, `{{HIRING_MANAGER}}`, `{{PAY_BENCHMARK}}`, `{{CURRENCY}}` all filled, or the optional ones deleted.
- [ ] `{{PAY_BENCHMARK}}` names its source and the date it was checked, for every seat you hire. See `hireability-check.md` for what it should cover.

## 3. Policy decisions

- [ ] **Start in trial mode** for the first two roles.
- [ ] **Feedback limits.** Adopt the tiers in `process-contract.md` or set your own, and name who chases them.
- [ ] **Sign-off.** Decide who must sign every brief, by seat level.
- [ ] **Must-have cap.** Three by default. Change it deliberately, not by drift.
- [ ] **Requirement language.** Review for proxies of protected attributes before the first brief.

## 4. Behaviour that must never be removed

- The twelve-month outcomes question opens every intake.
- The five skipped questions are asked on every intake.
- Must-haves are capped and each one passes the substitution test.
- Every pay figure names its source. Missing data is named, never estimated.
- The hireability check runs before approval.
- Any blocking flag the hiring manager overrules gets a dated tripwire and an agreed fallback brief.
- Signed briefs are versioned, never edited in place, and candidates in process are re-checked on every change.
- Nothing is advertised, sourced or sent before a human approves the brief.
- When a rival is at final stage, candidate generation starts the same day.
- Every write is read back, and failures are reported on the brief.
