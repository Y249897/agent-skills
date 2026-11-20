# Agent Skills

A collection of **skill packs** for AI coding assistants (DSH, Claude Code, and others). Each skill takes one repetitive chore off your hands: install it once, then call it by name.

Most skills are written in Chinese (the material they work with is); this README and each skill's `SKILL.md` frontmatter are enough to know what a skill does and when to use it.

## Skills

| Skill | What it does | Path |
| --- | --- | --- |
| `kaoyan-phrases` | Extracts fixed collocations from English study material, accumulates them into one Excel master table, and delivers an Anki CSV plus a Word handout | [`skills/kaoyan-phrases`](skills/kaoyan-phrases) |

## Install

A skill is just a folder with a `SKILL.md` inside. Copy the folder into your assistant's skills directory — no restart needed:

```powershell
# DSH
Copy-Item skills\kaoyan-phrases "$HOME\.dsh\skills\" -Recurse

# Claude Code
Copy-Item skills\kaoyan-phrases "$HOME\.claude\skills\" -Recurse
```

Once installed, ask for the task in plain language and the skill triggers on its own, e.g. "pull the collocations out of this reading passage and make me a phrase list".

## Layout

```
skills/<skill-name>/
├── SKILL.md          Entry point: when to use it, how, hard rules (YAML frontmatter)
├── README.md         Human-facing docs: purpose, usage, outputs, install
├── references/       Step-by-step detail, referenced from SKILL.md
├── tools/            Executable scripts
├── examples/         Sample inputs and outputs
└── LICENSE
```

- A `SKILL.md`'s `description` decides **when it triggers**; state both what it does and when to reach for it.
- The body only loads when the skill is used, so details belong in `references/` and the entry file stays short.
- Scripts resolve paths relative to the working directory and write into the user's own project — no hard-coded drive letters.

## Contributing

Issues and PRs are welcome. Follow the layout above, and add one row to the table in this README.

## License

MIT, see [LICENSE](LICENSE).
