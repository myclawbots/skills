# Offer Strategy and Booking

## Earn the right to ask

Never lead with an offer. Never pitch in a cold email. Email 1 starts a conversation. Offers come
only after genuine interest: a positive reply, a question about the product, a stated pain, a question
about pricing or next steps. Before that, you are still earning attention.

## The offer ladder

| Engagement | Signal | Offer |
|---|---|---|
| Curious | asked a question | answer it + soft next step ("happy to walk you through it if useful") |
| Interested | stated a pain, asked about features | a relevant resource from product_knowledge.md + suggest a short call |
| Ready | asked about pricing, timeline, next steps | the specific offer and a clear next step |
| Urgent | deadline, lost their vendor, hiring | move fast: the offer now, plainly |

## Offers come from `sales/config.yaml`

`offer.primary` (what we sell), `offer.entry` (trial, audit, pilot, sample), `offer.goal`
(book_call, start_trial, get_reply), `offer.booking_method`, `offer.booking_url`,
`offer.meeting_duration`, `offer.meeting_owner`. If any is empty, ask the owner before the first
interested reply needs it.

For any offer, be able to say: what they get, what it costs (money, time, or free), what they risk
(nothing, month-to-month, guarantee), and what happens next (the exact mechanic).

## Booking mechanics

- **Calendar link** (`booking_method: calendar_link`): "Here's my calendar if you want to grab 15 minutes: {{booking_url}}". Always state the duration. Never "book a demo"; say "grab time" or "jump on a call".
- **Suggest times** (`suggest_times`): "Would Thursday at 2pm or Friday morning work for a quick call?" Two or three options, day and time, timezone, same week.
- **Ask their preference** (`ask_preference`): senior prospects. "What does your calendar look like this week for a quick 15 minutes?"
- **No call** (self-serve products): "Want me to set up a trial account? Takes 2 minutes."

Booked? Put it in the owner's calendar (Google Calendar via `gws calendar events`, or Outlook) with
the prospect's context, and `pipeline.py stage --to closing`.

## Timing in the sequence

Email 1: no offer. Email 2: a soft mention at most ("we help teams like yours do X, worth a
conversation?"). Email 3: breakup, no pitch. First interested reply: acknowledge, answer, then the entry
offer or a call. Went quiet after interest: one gentle nudge, never more.

## Language

Say: "Worth a quick conversation?", "Happy to walk you through it", "Want me to send over {{specific thing}}?"
Never: "Book a demo", "Schedule a call with our team", "I'd love to show you", "Let me know if you're interested", "When are you free?"

## "What's the price?"

Answer it. Never dodge. Frame it: "Plans start at {{price}}, depending on {{variable}}. Most teams your
size are on {{tier}}." Then one qualifying question for an exact number. If there is a free entry
offer, lead with it. Only numbers from `sales/product_knowledge.md`; never a custom price, legal term or
delivery date the owner hasn't given you.
