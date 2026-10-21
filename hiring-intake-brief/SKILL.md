---
name: hiring-intake-brief
title: Hiring intake brief
description: |
  Use this skill when a founder, hiring manager or recruiter opens a sales, marketing, customer success or other GTM role and needs to brief it before anyone advertises, sources or contacts a candidate. Runs a structured intake, asks the five questions most intakes skip, tests the brief against the market for pay, profile, seniority, location and process speed, and returns a one-page role brief with hireability flags, the candidate pitch and a signed process contract. Ends with one Yes/No: approve the brief as written, or fix the top flag first. Triggers on "we need to hire a", "brief this role", "intake call", "role kickoff", "write the job spec", "first sales hire", "first marketer", "why can't we fill this role", "the search has stalled", "is this salary enough".
author:
  name: Justin Blij
  url: https://www.linkedin.com/in/jusblij
license: MIT
category: general
tags: [hiring, sales, leadership]
suggested_template: hr_recruiter
source:
  name: GTM Skills by Swan
  url: https://www.gtmskills.com/skill/hiring-intake-brief
  repo: https://github.com/swan-gtm/gtm-skills
  path: skills/justin-blij/hiring-intake-brief
  creator: https://www.gtmskills.com/justin-blij
  commit: 5d786aad0c7b2ca59b1abf1f601f9407ca261996
---
# Hiring intake brief

Runs once per role, before the job is advertised or anyone is approached, and again whenever the brief changes. It produces the document every later step of the hire works from: the brief, the flags, the pitch and the rules of the process.

**The prime rule: brief a role the market can fill.** Most failed searches were lost before the first candidate was found. The pay sat below what the profile earns, the must-haves described three people, nobody agreed why the role existed, or the process moved slower than good candidates stay on the market. Any good operator can define the outcomes. A recruiter's job is to know whether the people who can deliver them will say yes to this pay, this title, this location and this process. Fix the brief while it costs a day. Fixed later, it costs three weeks and usually a candidate.

The skill is built from searches that went both ways. In one, the hiring manager rewrote the brief three weeks in, swapping an activity target for a revenue number and lifting the pay, and the hire was made from the re-scored pool. Every change had been available at intake. In another, the seat was re-scoped after the lead candidate reached a partner interview, three different pay figures followed, and the search was lost. Nobody had asked for one signed version.

## Template placeholders

Replace every `{{...}}` before enabling. The setup checklist in `references/setup-customization-checklist.md` covers each one.

- `{{ATS}}`: where roles, past hires and job descriptions live
- `{{CRM}}`: company stage and growth context, if kept separately
- `{{DOCS}}`: where the signed brief is stored, if not in `{{ATS}}`
- `{{NOTES_TOOL}}`: intake call recordings or notes
- `{{REVIEW_CHANNEL}}`: where the brief and flags are posted for sign-off
- `{{HIRING_MANAGER}}`: who owns the role and signs the brief
- `{{PAY_BENCHMARK}}`: your sourced pay data for the segment and location
- `{{CURRENCY}}`: currency for pay and deal sizes

## Trial mode (recommended for the first two roles)

Run the intake and the hireability check, but write nothing to `{{ATS}}`. Post the brief to `{{REVIEW_CHANNEL}}` marked TRIAL next to whatever brief the team would have written anyway. When each search closes, compare which brief predicted the problems the search actually hit. Switch writes on once the team trusts it.

## Diagnostic questions (before the first intake)

Ask these once per team.

1. Of your last three searches that stalled or failed, at what point did you first know? What did the brief say at the start?
2. Who signs off a hire here, and were they in the room when the last role was briefed?
3. How do you set pay for a new role today: market data, the last person's salary, or the budget line?
4. How long does a candidate typically wait for feedback after an interview?
5. Has a role here ever been re-scoped after candidates were already in process? What did it cost?

## Fast path (twenty minutes)

For a founder with one call and no patience for a form, run only this, then fill the rest of the brief from the systems and a follow-up note:

1. The anchor question in Step 2, pushed until it has numbers.
2. "Walk me through your last five deals", for any sales hire.
3. The five skipped questions in Step 4.
4. Three must-haves, each through the substitution test.
5. Pay, with the source, against `{{PAY_BENCHMARK}}`.

## The play

### Step 1. Pull before asking

- From `{{ATS}}` or `{{DOCS}}`: any existing job description, the last hire into this seat and how it went, past intake notes for similar roles.
- From `{{CRM}}`: company stage, funding, headcount and recent growth, if available.
- From `{{NOTES_TOOL}}`: the intake call recording or notes, if the call has already happened.

Ask only what the systems cannot answer. A hiring manager who is asked for what is already on file stops trusting the process.

### Step 2. Open with the anchor question

Before the full intake, ask: **"What does this person have to deliver in the first twelve months for you to call it a great hire?"** Push for numbers: pipeline, revenue, retention, a team built, a launch shipped. If the answer is a list of skills or "I'll know them when I see them", the brief is not ready, and the rest of the intake exists to get it ready.

For a first or early sales hire, ask next: **"Walk me through how your last five deals got done."** If nobody can, the company is hiring someone to invent the motion, not to run it. Flag that before writing a word of the brief.

### Step 3. Run the intake in seven sections

Use `references/intake-question-bank.md`. Every question carries its reason, so the asker can explain it if challenged.

1. **Business context.** Why hire now, new or backfill, and if backfill, why the last person left.
2. **The role.** Where 80% of the first ninety days goes, hands-on versus strategic, what candidates usually misunderstand about it.
3. **Reporting and stakeholders.** Who they report to, how that person manages, who else has to say yes.
4. **The person.** Non-negotiable behaviours, who has not worked out here and why, early proof they can deliver.
5. **Success.** The twelve-month outcomes, what a strong hire looks like at day ninety.
6. **The process.** Stages, owners, feedback times, start date.
7. **Risk and culture.** Politics, past friction hiring this role, anything not yet asked.

### Step 4. Ask the questions most intakes skip

These five are mandatory on every intake. Each one has decided a search.

- **Who else is in this process?** Other recruiters, internal referrals, candidates already at final stage.
- **Has anyone on the hiring side worked with a likely candidate before?** Prior history with one manager can outweigh any shortlist.
- **Who runs any work sample, and on whose clock?** A sample nobody chases is where good candidates go quiet.
- **How will candidates be submitted, and how fast will you respond?** Agree the channel and the reply time in the room.
- **If a rival candidate is already at final stage, what is the deadline?** Then candidate generation starts the same day. Intake paperwork never outranks the clock.

### Step 5. Cut the must-haves to three

Write the twelve-month outcomes first, then the must-haves that follow from them. Cap at three. Run the substitution test on every line: could something else stand in for this? If yes, it is a nice-to-have. Then name the weaknesses the team will accept. Hiring for no weaknesses produces the pleasant candidate, not the strong one. Three is a house discipline. Nobody has proved it is the right number, but every extra must-have shrinks the pool, and it shrinks it unevenly.

### Step 6. Run the hireability check

Use `references/hireability-check.md`. Test the brief against the market and flag each conflict: pay versus market, the unicorn combination, seniority versus scope, price point, location and work model, process speed, and the pitch. Every flag gets a severity (blocks the hire, slows the search, note) and a fix. When pay or profile is short, offer the trade-off instead of a warning: "If we need X, we give up Y."

When the hiring manager hears a blocking flag and keeps the brief anyway, do not argue a second time. Write the flag down as a known risk, with what it predicts and a tripwire: "If we have fewer than [n] interested candidates who meet all three must-haves by [date], we switch to [the fallback brief]." Agree the fallback now, while nobody is attached to a candidate. Hiring managers who would never accept the original challenge will usually accept a tripwire, and the date settles the argument without anyone losing face.

### Step 7. Build the pitch and the process contract

- The pitch, from `references/pitch-builder.md`: two sentences, in the hiring manager's own words, that answer why someone good would leave a job they like for this one.
- The process contract, from `references/process-contract.md`: stages and owners, the feedback limits, who runs the work sample, how candidates are submitted, and the deadline if a rival process is live.

### Step 8. Post the brief and stop

```
[Company] / [Role] / Role brief v[n] / [date]
Why now: [driver] | New or backfill: [ ] | If backfill, why they left: [ ]
Twelve-month outcomes: 1. [ ] 2. [ ] 3. [ ]
First 90 days, 80% of time on: [ ]
Must-haves (max 3): [ ] | Weaknesses we accept: [ ] | Deal-breakers: [ ]
Profile line: [price point sold at, stage worked at, self-sourced share or equivalent]
Pay: base [ ] OTE [ ] mix [ ] equity [value, vesting] | Market: [ ] (source) | Gap: [ ]
Pitch: [two sentences, hiring manager's words]
Candidates misunderstand: [ ] | Did not work out before because: [ ]
Who signs off: [names, all agreed to this version: yes/no]
Process: [stages, owner each] | CV reply [n]h | Scorecards [n]h | Final decision [n]h
Work sample run by [ ] | Submit via [ ] | Competing processes: [ ] | Deadline: [ ]
Hireability flags: [flag, severity, fix] or none
Tripwire: if [signal] by [date], switch to [fallback brief] or none
Decision: Approve this brief as written? Yes / No
          Fix [top flag] first? Yes / No
```

### Step 9. Write back, after the decision

Only after a human answers:

- Save the brief to `{{ATS}}` or `{{DOCS}}` as a numbered version. Read it back. Not found means retry once, then post a visible warning: "Brief write failed, manual save needed".
- Any later change to scope, pay, location or seniority creates a new version with a one-line change log, and names who and what it affects. Never edit a signed version in place.

Write failures never block the brief.

### Step 10. The first twenty-four hours

The day after approval sets the pace of the search. Run the five actions in `references/process-contract.md`: signed brief to every stakeholder, three calibration profiles, scorecard locked, diaries held, sourcing live from the signed brief. If two of the three calibration profiles are rejected for reasons the brief never mentioned, the brief is wrong, so fix it before sourcing goes wide.

## Rewrite mode

When a search stalls, run the intake again against the current brief. Compare the two versions, name what changed and what did not, and re-test the hireability flags. A brief changed mid-search means every candidate already in process is re-checked against the new version within days, not weeks.

## Handoffs

The skill works on its own. When other parts of the hiring process exist, it feeds them:

- **After:** the twelve-month outcomes and the profile line become the seat a scorecard measures against. The must-haves become its must-have criteria.
- **After:** the pitch and the pay become the opening of any job ad or outreach.
- **At offer:** the market pay line and the competing processes are the first facts an offer plan needs.

## What good looks like

- The brief starts with outcomes and numbers. Skills and years come later, if at all.
- Three must-haves, each one surviving the substitution test, and a named list of weaknesses the team accepts.
- Every pay figure carries its source. A gap is named in money, not adjectives.
- Everyone who can say no to the hire signed the same version before the first candidate was contacted.
- The pitch would make a good candidate at a good company pick up the phone.
- Feedback limits are in the brief with a named owner, not left to goodwill.
- When the brief changes, the version number changes, and the candidates in process are re-checked.
- The hiring manager accepts most calibration profiles on the first pass. Rejections cite the brief, not taste.
- Any flag the hiring manager overruled has a tripwire with a date on it.

## Anti-patterns

- **The recycled job description.** An old ad, reused for a seat that has changed.
- **The logo brief.** "Someone from a famous company" in place of the selling motion the seat actually runs.
- **The wish list.** Enterprise and SMB, hunter and farmer, our industry, five years, all mandatory.
- **The silent stakeholder.** The person with a veto meets the first shortlist and rewrites the role.
- **Pay set by the budget line.** The number came from what was left in the plan, not what the profile earns.
- **The unlocked brief.** Scope, pay or location moves while candidates are in process and nobody writes it down.

## Why the hard rules exist

- **Outcomes before requirements.** Without agreed outcomes, every interviewer scores against their own picture of the role, and good shortlists get rejected for reasons nobody can explain.
- **Three must-haves.** Each extra filter removes good candidates the team never sees, and it removes some groups faster than others.
- **The five skipped questions.** Parallel processes, prior relationships, unowned work samples, unanswered submissions and missed deadlines have each ended searches that looked healthy.
- **A signed, versioned brief.** A brief that moves without a record moves the goalposts for every candidate already running, and the search pays for it in trust and time.
- **Speed written in.** Strong candidates are usually in more than one process. Feedback that takes a week loses them to the company that took a day.

## Rules

- MUST open with the twelve-month outcomes question and record the answer with numbers.
- MUST ask the five skipped questions in Step 4 on every intake.
- MUST cap must-haves at three and run the substitution test on each.
- MUST run the hireability check before the brief is approved.
- MUST name the source of every pay figure. Missing data is named, never estimated.
- MUST put the pitch in the hiring manager's own words.
- MUST version every change to a signed brief and re-check candidates in process against it.
- MUST set a dated tripwire and an agreed fallback brief for any blocking flag the hiring manager overrules.
- NEVER include requirements that act as proxies for protected attributes: years of experience as a stand-in for age, "culture fit" without a definition, "energy" or "presence" without a behaviour attached.
- NEVER advertise, source or contact a candidate before a human approves the brief.
- NEVER let intake paperwork delay candidate generation when a rival process is already live.
