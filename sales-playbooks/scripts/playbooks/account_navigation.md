# Account Navigation: Several Contacts at One Company

A company is an account; a contact is a person at it. Create the company first
(`pipeline.py add-company`), then attach contacts (`pipeline.py add-contact`).

## Company profile (fill only what you can verify)

Name, domain, website, one-line description, industry, size, location, source and source URL. From
their site, LinkedIn company page or search. Can't verify a field? Leave it blank.

## Contact profile

Required: first name, last name, current title, company. Optional, only if verifiable: email with an
honest status (`verified` after a check or found on the company site, `risky` for a catch-all domain,
`guess` for a pattern), phone only if public, LinkedIn URL, seniority and department inferred from the
title. Record where each fact came from.

Never fabricate contact details. A contact without a verified email is still useful on LinkedIn.

## Who first

| Deal size | First | Second | Not first |
|---|---|---|---|
| Small (< $500/mo) | end user / manager | their boss | C-suite |
| Mid-market ($500-5k/mo) | Director / VP | the manager who'd use it | individual contributors |
| Enterprise ($5k+/mo) | VP / C-suite | a champion manager | junior staff |

## Multi-threading

1. **One at a time.** Never email several people at the same company simultaneously.
2. **Start at the right level**: the person who feels the pain, can evaluate, and actually reads email.
3. **Move on response.** Manager silent → the VP. VP says "talk to my team" → the manager, referencing the VP. Manager interested → ask about looping in their boss.
4. **Wait 5 business days** between contacts at the same company.
5. **Share context across contacts** ("your colleague Sarah mentioned she's evaluating options") only when it's true and recorded.

Seniority from title: C-suite (Chief …, CEO/CTO/CFO/CMO/COO/CRO) · VP (VP, SVP, EVP, Head of) ·
Director · Manager (Manager, Team Lead) · Individual (Analyst, Specialist, Coordinator, Engineer).

## When to stop an account

Three contacts emailed with no response; any contact says not interested or stop; the company stops
matching the ICP on closer look. `pipeline.py suppress` the contacts with `--reason not_fit` and move on.

## Sample review (once, and whenever the ICP changes)

Before autonomous prospecting: research 5 to 10 companies with one or two contacts each and show
them to the owner. "Here are 8 companies with 1 or 2 contacts each. Are these the right targets?"
Adjust on their feedback ("too small", "wrong industry", "we already work with them"). Only after
approval does prospecting run on its own.
