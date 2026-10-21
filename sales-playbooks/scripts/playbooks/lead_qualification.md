# Lead Qualification

BANT to screen, an ICP score to prioritise, MEDDIC when a deal has several stakeholders.

## BANT

- **Budget.** Signals: company size, funding, hiring in your category, ads running. Green: recently funded, hiring in the domain. Red: tiny team with no budget signal.
- **Authority.** Decision makers: owner, founder, C-suite, VP, Director, Head of. Influencers: Manager, Lead, Senior (can champion). Not the authority? Ask for the right person instead of burning a sequence.
- **Need.** Do they have the problem you solve? Validate from their site, tech, job posts, public posts.
- **Timeline.** Active evaluation, recent vendor change, a deadline. "Not now" is fine: log a date and stop until then.

## ICP score (1 to 10, before any outreach)

| Criteria | Points |
|---|---|
| Title match: exact ICP title 3, adjacent 2, related 1 | 0-3 |
| Company fit: right industry and size 3, one of them 2, tangential 1 | 0-3 |
| Engagement signal: posts about relevant topics 2, active publicly 1 | 0-2 |
| Reachability: verified email 2, LinkedIn only 1, nothing 0 | 0-2 |

Record it: `pipeline.py score --contact <email or id> --points N --note "why"`.

- **8-10:** personalised sequence now.
- **5-7:** batch campaign.
- **3-4:** only if the pipeline needs volume.
- **1-2:** skip.

## MEDDIC (multi-stakeholder deals)

Metrics the buyer cares about · Economic buyer · Decision criteria · Decision process · Identified
pain · Champion. Capture these as notes on the company as a conversation progresses; don't interrogate
a prospect with the checklist.

## Disqualify

- Below the ICP's minimum size.
- Unrelated industry.
- No discoverable contact.
- Deeply entrenched competitor with no switching signal.
- Opted out, bounced, or hostile: suppressed, never reconsidered.
- The owner already works with them (ask during the sample review).

## Enrichment order (cheapest first)

1. Company domain and size: website, LinkedIn company page.
2. Decision-maker name and title: team/about page, LinkedIn.
3. Email: the company's pattern (`pipeline.py observe --signal EMAIL_PATTERN`), then verification; record status honestly (`verified`, `risky`, `guess`).
4. Recent news: search.
5. Tech stack: what the site runs.
6. Personalisation angles: public posts, blog, careers page.

Never fabricate a field. Blank beats guessed.
