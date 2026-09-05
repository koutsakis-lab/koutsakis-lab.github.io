# Agent Guidelines — Koutsakis Lab website

The website of the Koutsakis Lab (Propulsion, Heat Transfer and Materials), Department of
Mechanical Engineering, University of New Mexico. Deployed to GitHub Pages from `main` by
`.github/workflows/jekyll.yml`.

## What this repo is

A **self-contained Jekyll site**, originally derived from the [al-folio](https://github.com/alshedivat/al-folio)
theme. Everything the site needs lives here — layouts, includes, Sass, plugins, content, and
assets. There is no theme gem: `_layouts/`, `_includes/`, `_sass/`, and `_plugins/` are ours to
edit directly.

## Where things live

| Change                                  | File(s)                                                     |
| --------------------------------------- | ----------------------------------------------------------- |
| Site identity, feature flags, plugins   | `_config.yml`                                                |
| Homepage text and hero image            | `_pages/about.md`                                            |
| Research tiles (the /research/ page)    | `_research/*.md` — one file per expandable tile              |
| People                                  | `_pages/people.md` + bios in `_pages/people/{grad,undergrad,affiliates}/` |
| Courses                                 | `_teaching/*.md`                                             |
| News items                              | `_news/*.md` (one file per item, `inline: true`)             |
| Sponsors                                | `_data/sponsors.yml` + logos in `assets/img/logos/`          |
| Publications                            | `_bibliography/papers.bib` — **generated, do not hand-edit** |
| Co-author links on the publications page| `_data/coauthors.yml`                                        |
| Layout / styling                        | `_layouts/*.liquid`, `_includes/*.liquid`, `_sass/*.scss`    |

## Publications are generated

`_bibliography/papers.bib` is regenerated from OpenAlex by `scripts/update_publications.py`,
which is pinned to **ORCID 0000-0002-8108-2591** and runs weekly via
`.github/workflows/update-publications.yml`. Hand edits are overwritten. To drop an entry, add
its DOI to `scripts/publications_exclusions.txt` and re-run the script.

`_bibliography/accepted.bib` is the hand-maintained companion for accepted / in-press work that
OpenAlex does not know about yet. `scripts/update_publications.py` merges its entries into the top
of the generated `papers.bib` on every run (skipping any whose title it already found via
OpenAlex), so accepted/in-press papers render as ordinary entries on the Publications page rather
than a separate section — `accepted.bib` itself is never touched by the generator.
**When one of these papers is published, delete it from `accepted.bib`** — otherwise the merge step
starts silently skipping it (title now matches OpenAlex) and there's no reason to keep it around.

## Things that fail silently

1. **A page needs `nav: true` and a unique `nav_order`** to appear in the navbar. Duplicate
   `nav_order` values or duplicate `permalink`s across pages produce a confusing build, not an error.
2. **Collections with `output: false`** (`news`, `research`, `teaching`) render only through the
   page that loops over them. Adding a file to a collection that nothing iterates over does
   nothing at all.
3. **Bios need markdown hard breaks.** Two trailing spaces at the end of a line, or the name,
   title, and degrees collapse into a single run-on line.

## Local development

Ruby is not installed on the maintainer's machine, so a local `jekyll build`/`jekyll serve` is not
available. With a Ruby + Bundler toolchain elsewhere, `bundle install && bundle exec jekyll serve`
works (`http://localhost:4000`, `baseurl` is blank for this site). Otherwise, push to a branch and
let `.github/workflows/jekyll.yml` build it — a failed Action run is the way errors surface.

## Before committing

- Only reference the University of New Mexico and the Koutsakis Lab — no other institution's name,
  branding, or people.
- Don't publish claims about people (titles, roles, affiliations) that aren't confirmed.
- Research figures are placeholders (`<div class="figure-placeholder">`) until real figures exist;
  swap them for `<img>` when they do.
