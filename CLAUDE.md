# CLAUDE.md

Guidance for Claude Code (claude.ai/code) when working in this repository.

@AGENTS.md

`AGENTS.md` (imported above) is the authoritative entry point: what this repo is, where each kind
of content lives, how publications are generated, and the failure modes that produce no error
message. Read it first. Everything below is supplementary.

## Editing content

Most requests are content edits, and the pattern is the same each time: find the file in the table
in `AGENTS.md`, edit it, and keep the front matter intact. Prose lives in markdown; structure lives
in front matter.

- **Non-ASCII characters** (en dashes, accented names) must be written with the Write/Edit tools.
  Piping content through a bash heredoc on this Windows machine mangles them.
- **Images** go in `assets/img/`: headshots in `people/`, sponsor logos in `logos/`, lab and
  facility photos in `lab/`. Reference them from front matter as a path relative to `assets/img/`
  (people) or as an absolute `/assets/img/...` path (everything else).
- **Never invent facts about people.** Names, titles, degrees, and roles come from the PI or from
  a published source. If a role is unconfirmed, leave the entry commented out in
  `_pages/people.md` rather than guessing.

## Verifying a change

There is no Ruby toolchain on this machine, so a full `jekyll build` is not available locally.
Before finishing, sanity-check by hand:

- Front matter parses as YAML, and every `image:`/`content:` path in `_pages/people.md` exists.
- Every `{% include %}` target exists in `_includes/`.
- Every `assets/img/...` reference resolves to a file on disk.

A short Python script covering all four checks is the fastest way to do this.
