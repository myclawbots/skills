# Cold Email Copywriting

## The only rule that matters

Write like a real person sending a real email. Not a marketer. Not an AI. A person who noticed
something, has a thought, and is reaching out. Read the draft out loud: if it sounds like a sales
pitch, delete it and start over.

## Compliance and deliverability (override everything below)

- **Subject lines are truthful.** No "re:" on a thread that doesn't exist, no "fwd:", no implied prior relationship.
- **Identity is real.** From-name, company and signature are the owner's configured persona. Never pose as a consumer, a customer or a mutual contact.
- **Every email can be stopped.** A plain line such as "Reply stop and I won't write again" and the owner's physical mailing address in the signature. "Stop", "remove me", "not interested, don't email again" are all opt-outs: honour them immediately and permanently, even mid-conversation.
- **Hygiene:** plain text, at most one link (zero in email 1), no attachments, no tracking pixels, no ALL CAPS, no spam-trigger phrasing.
- **EU/UK:** B2B cold email needs a defensible legitimate interest: the pitch must fit the person's professional role, and email 1 must make objecting easy.

## Banned patterns (never)

- Em dashes. Use periods, commas or line breaks.
- "Picture this", "Here's what I keep seeing", "In today's …", "Imagine if", "What if I told you".
- Before/after lists. Feature dumps (3+ features). Bullet points. Bold, italics, headers.
- "Worth a quick look/chat/call?", "I hope this finds you well", "Just following up", "I'd love to", "Reaching out because", "Wanted to", "Let me know if you're interested", "Are you the right person?", "No pressure", "No obligation".
- "Game-changer", "revolutionary", "cutting-edge", any hype word.
- Multiple questions in one email. Starting with "I" or "We". Parenthetical asides. More than one exclamation mark per sequence (zero is better).
- The prospect's name in the subject line. "Quick question" in the subject.

## What makes a good cold email

- **Short.** Under 75 words for email 1, under 60 for emails 2 and 3. Count.
- **Sounds like a person.** Out loud test.
- **One point.** One observation, one idea, one question.
- **About them.** Their name, company or situation appears before the product does. Ideally the product is not named in email 1.
- **Earns a reply, not a sale.** You are opening a door, not closing.

## What the data says

Median cold reply is about 3 %; the top decile gets 10 %+. The gap is relevance and deliverability,
not clever copy. Order of impact: **deliverability > list quality and relevance > copy**.

- Replies peak at 50 to 125 words. 200+ words halves the rate.
- An ask that gives them something whether or not they buy (a teardown, a relevant number) beats "do you have 30 minutes?" by about a quarter.
- Easy-yes asks ("is this on your radar at all?") beat big asks.
- About 6 touches over 14 to 28 days, then stop.
- A one-line bump nearly doubles replies versus re-pitching at length.
- No open or click tracking: pixels cost 8 to 12 % inbox placement.
- Segments of 50 or fewer reply about 3× better than blasts of 1,000+.

## The 3-email sequence

### Email 1: the observation

Something you noticed about them or their business. Not a compliment. Connect it to a problem or
opportunity. Don't name the product. End with a question they would actually want to answer.

Structure: one line specific to them (2 sentences max) → one line connecting it to a gap (1 sentence)
→ one question.

Good:
```
Subject: {{company}} website

{{first_name}}, looked at {{company}}'s site. You're clearly doing good work but the site probably isn't converting the way it should given how strong your reviews are.

Curious how you're currently getting leads beyond word of mouth?
```

Bad: a compliment ("you've clearly built something real"), a "here's what I keep seeing", a "picture
this", a "worth a quick look?". That reads as generated.

### Email 2: the angle

A completely different angle. Don't reference email 1, don't say "following up". New subject, new
idea. One specific pain, one number if you have a real one, one line on how you solve that exact
thing, one direct question.

```
Subject: monday reports

{{first_name}}, most ops teams your size rebuild the same inventory report by hand every Monday morning. That's half a day a week nobody has.

We generate it straight out of the systems {{company}} already runs, so it's sitting there when you log in.

Worth a look, or is this already handled?
```

### Email 3: the breakup

Under 40 words. Respectful, no pitch, no summary, no guilt trip ("you're probably losing 5-10 leads a
month"), no fake warmth ("hope storm season treats you well").

```
Subject: closing the loop

{{first_name}}, sounds like the timing isn't right. Totally get it.

If this ever becomes a priority, I'm around.
```

### The bump (only if config allows a 4th touch)

One or two sentences, 2 to 3 weeks later: "Still worth a look, or should I close the file?"

## Why replies happen

Every email is built around exactly one trigger:

1. **Recognition.** You named a problem they live with, in their words. Needs real specificity: "your pricing page has four tiers but no annual option" beats "companies struggle with pricing".
2. **Curiosity gap.** You know something they'd want to know. Only if you deliver the payoff when they reply. Never a fake gap.
3. **Easy yes.** Replying is cheaper than deleting. "Is this on your radar at all?"
4. **Peer proof.** A named, real, public peer did something relevant. Only if true.

No trigger, no reply, however clean the copy.

## Subject lines

Lowercase. 2 to 5 words. Looks like an internal email. New subject for emails 2 and 3. Good:
`{{company}} website`, `missed calls`, `one thing`, `your lead flow`, `closing the loop`. Bad:
anything with the prospect's name, "transform", "exclusive", "3 ways to", "I'd love to connect".

## Personalization that works

Their specific product, service or market; something visible on their site (not "I looked at your
site"); their city or region; a challenge their industry faces right now. Not "you've clearly built
something real", not "companies like yours", not "as a {{title}}".

## Tone by prospect

C-suite: even shorter, get to the point. Technical: specific about the problem, no emotional language.
Small business owners: warm but never salesy, they get pitched all day. Enterprise: professional, still
human. Default: conversational, direct, 7th-grade reading level.

## Campaign variety

Different campaigns must feel different: tone, length, angle, structure. If three campaigns read like one
template with variables swapped, rewrite them.

## The test (before every draft goes to the owner)

1. Could a real person have written this?
2. Exactly one idea?
3. Under 75 words (email 1)?
4. Would I reply to it?
5. Any em dashes?
6. Any banned pattern?
7. Is every factual claim true and from `sales/product_knowledge.md` or the prospect's own pages?
8. Honest subject, real identity, a way to stop?

Yes to 5 or 6, or no to 7 or 8: rewrite. Then `scripts/gate.py` checks the same things in code before
it goes out.
