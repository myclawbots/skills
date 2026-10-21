# MyClawBots skills

Skills for [MyClawBots](https://myclawbots.ai) agents: a `SKILL.md` an agent reads, plus the
scripts it needs. Every folder here is also usable as-is in Claude Code, Codex, Cursor or any agent
that loads skills from a folder.

Browse them with descriptions, install counts and a copy button at **https://myclawbots.ai/skills**.

## Use a skill

On a MyClawBots agent (in chat): `claw install <slug>`

In Claude Code, Codex or Cursor:

```
npx -y @myclawbots/cli skill add <slug>     # writes ~/.claude/skills/<slug> and every other agent home it finds
```

or copy the folder: `npx degit myclawbots/skills/<slug> ~/.claude/skills/<slug>`

## What is here

This repository mirrors every skill in the MyClawBots skills registry (all MIT-licensed); it is updated
automatically on every production release. Each skill's `SKILL.md` frontmatter names its author,
license, category and tags.

## Contribute

Open an issue or a pull request against a skill's folder. Keep `SKILL.md` body text plain
(no secrets, no credentials, nothing machine-specific), keep scripts text-only, and say in the PR
which agent and task you tested it with. Changes land here after review through the registry.

## License

MIT, see `LICENSE`. Where a skill was adapted from someone else's MIT work, its `NOTICE` file says so.
