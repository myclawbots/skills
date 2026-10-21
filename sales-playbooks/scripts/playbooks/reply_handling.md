# Reply Handling

Every reply is an opportunity; some replies are a stop sign. Know the difference before writing a
word. Classify the intent, record it, then act.

```
pipeline.py reply --contact <email> --intent <intent> --text "<their reply>"
```

## Intents

| Intent | What you do |
|---|---|
| `interested` | Answer anything they asked, then move toward a meeting in 1 or 2 messages. Don't oversell. |
| `question` | Answer clearly, tie it to their situation, one next step. |
| `objection` | `objection_handling.md`: acknowledge, one proof point, one question. |
| `wrong_person` | Thank them warmly, ask for a name or an intro. Make it easy. |
| `not_interested` | **No reply.** `stage --to closed_lost`. One no is enough; never "circle back". |
| `opt_out` | **No reply beyond a one-line confirmation if one is natural.** `suppress --reason opt_out`. Never try to save it, never ask why. |
| `angry_legal` | **Never reply yourself.** Suppress, and hand the thread to the owner with the facts. Mentions of lawyers, spam reports, harassment, GDPR, CAN-SPAM all count. |
| `bounce` | `suppress --reason bounce`, cancel the rest of the sequence, count it toward the bounce threshold. |
| `auto_reply` | Out of office: note the return date, push the next touch past it. No reply. |

## Conversation stages

`initial_outreach → engaged → qualifying → presenting → negotiating → closing → closed_won / closed_lost`

- **engaged**: build rapport, don't pitch, ask about their challenges.
- **qualifying**: understand need and authority through natural questions, not a checklist.
- **presenting**: how we help, with specifics from `sales/product_knowledge.md`.
- **negotiating**: concerns directly, transparent about what the owner has set as pricing and terms.
- **closing**: propose specific times (or the booking link). Make yes easy.

Advance with `pipeline.py stage --contact <email> --to <stage>` the moment it's true.

## Writing the reply

1. Match their energy and formality.
2. Short. They know who you are.
3. Answer first; never dodge.
4. No desperation: no "just checking in", "just following up", "I'd love to".
5. Specific: two or three times with the timezone, or the booking link.
6. Know when to stop.
7. Never fabricate; never promise what isn't in the product file (custom pricing, legal terms, delivery dates). "I'll find out" is a fine answer.
8. No AI tells: no em dashes, no "great question", no bullets, no exclamation marks, no "I completely understand your concern". Write like a busy person on their phone.
9. One question or next step per reply.

Reply body only, plain text; the owner's signature is added by the sending step. Show it to the owner
and send only after their yes; run `gate.py --kind reply` first (replies may go to any address that
wrote to us).

## Threads that need the owner, not you

Legal or compliance language; anger; a pricing or contract question outside the product file; anyone
asking for a commitment you can't make. Summarise the thread in chat with what you recommend, and wait.
