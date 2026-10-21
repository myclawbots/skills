# Prospecting Without Paid Tools

Find companies, find the person, find a signal, verify the address. Web search, the company's own
site, LinkedIn through Linkedroid, and public registries are enough for a small, sharp list.

## 1. Search operators

LinkedIn profiles: `site:linkedin.com/in "VP Marketing" "SaaS" "Austin"` ·
team pages: `site:{{domain}} team OR about OR leadership` ·
companies in a segment: `"{{industry}}" "{{location}}" site:linkedin.com/company` ·
email pattern: `"@{{domain}}"`.

## 2. LinkedIn through Linkedroid

`linkedin_search_profiles` / `linkedin_run_search` by title, company, location. Second-degree
connections accept more. Company page → people. Never browser automation; Linkedroid's own limits
apply (see `linkedin_outreach.md`).

## 3. The company's own site (free, no model needed)

- `/team`, `/about`, `/leadership`, `/people`: names and titles, sometimes emails or LinkedIn links.
- `/careers`, `/jobs`: a relevant open role is the strongest signal (`HIRING_ROLE`).
- The footer: "site by {{agency}}" (`INCUMBENT_AGENCY`).
- Page source: ad tags and pixels (`RUNNING_GOOGLE_ADS`, `RUNNING_META_ADS`), platform and tools (`TECH_STACK`), JSON-LD or none (`NO_SCHEMA_MARKUP`), a booking widget or none (`NO_ONLINE_BOOKING`).
- `sitemap.xml`: page count (`SITE_PAGE_COUNT`); the newest blog date (`BLOG_STALE`).
- `robots.txt`: AI crawlers blocked (`BLOCKS_AI_CRAWLERS`).

Use `curl -sL` and read; record each finding with `pipeline.py observe --signal CODE --url <page>`.
Only signals the owner confirmed during onboarding are collected; `pipeline.py signals` lists the
catalog.

## 4. Email patterns

In order of prevalence: `first.last@`, `first@`, `firstlast@`, `flast@`, `firstl@`, `f.last@`,
`last.first@`, `first_last@`, `first-last@`. One real address on the company site reveals the pattern
for everyone (`EMAIL_PATTERN`). Verify: MX record exists; address found on the site = `verified`;
catch-all domain = `risky`; pattern only = `guess`. The gate refuses `guess` for sequences; `risky`
only when the owner allows it in config.

## 5. Trigger events

New hire in a relevant role · recent funding · product launch · job post in your domain ·
a competitor using you (public) · expansion · leadership change · tech change. Sources: news search,
company blog and press page, careers page, Crunchbase free tier, LinkedIn company updates.

## 6. Referral mining

"Not the right person" → ask who is, and whether they'd intro. Deal closed → ask for peers with the
same problem. Only use a name as social proof when it was actually given.

## Daily quotas (sustainable, not heroic)

Research 20 to 30 companies · identify 10 to 15 prospects · verify 10 to 15 addresses · score every
one before it enters the outbox. Small lists of 50 or fewer per segment reply best.
