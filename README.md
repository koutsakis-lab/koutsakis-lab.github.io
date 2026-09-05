# Koutsakis Lab Website

This repository holds the source for the Koutsakis Lab website (Propulsion, Heat Transfer and
Materials, University of New Mexico), built with [Jekyll](https://jekyllrb.com) and deployed via
GitHub Pages.

The site is built on the [al-folio Jekyll theme](https://github.com/alshedivat/al-folio), used
under the MIT license; most unused al-folio features have been removed, and layouts/includes/Sass
are edited directly in this repo (see [`_layouts/`](_layouts/), [`_includes/`](_includes/),
[`_sass/`](_sass/)).

## Table of Contents

- [Getting started](#getting-started)
- [Building the site](#building-the-site)
- [Pushing to production](#pushing-to-production)
- [Repository layout](#repository-layout)
- [Editing content](#editing-content)
  - [Homepage](#homepage---_pagesaboutmd)
  - [Research page](#research-page---_pagesresearchhtml)
  - [People page](#people-page---_pagespeoplemd)
  - [Publications page](#publications-page---_pagespublicationsmd)
  - [Teaching page](#teaching-page---_pagesteachinghtml)
  - [News / announcements](#news--announcements---_news)
  - [Sponsors](#sponsors---_datasponsorsyml)
  - [Contact page](#contact-page---_pagescontactmd)
  - [Adding more pages](#adding-more-pages)
- [License](#license)

---

## Getting started

Building the site locally requires [Ruby](https://www.ruby-lang.org/en/) and
[Bundler](https://bundler.io/).

### macOS

```bash
brew install chruby ruby-install
ruby-install ruby 3.4.1
echo "source $(brew --prefix)/opt/chruby/share/chruby/chruby.sh" >> ~/.zshrc
echo "source $(brew --prefix)/opt/chruby/share/chruby/auto.sh" >> ~/.zshrc
echo "chruby ruby-3.4.1" >> ~/.zshrc # run 'chruby' to see the actual version
```
Quit and relaunch the terminal, then verify (`ruby -v`) and install Bundler:
```bash
gem install bundler
```

### Linux (Debian, Ubuntu, Mint)

```bash
sudo apt-get install ruby-full build-essential zlib1g-dev
gem install bundler
```

### Windows

Install [RubyInstaller for Windows](https://rubyinstaller.org/downloads/), ticking the option to
run `ridk install` (MSYS2 + development tools) at the end. In a new terminal:
```powershell
ruby -v
gem install bundler
```

---

## Building the site

```bash
git clone https://github.com/koutsakis-lab/koutsakis-lab.git
cd koutsakis-lab
bundle install
bundle exec jekyll build
```

To preview locally:
```bash
bundle exec jekyll serve
```
which serves the site at `http://localhost:4000`. Pass `--livereload` to auto-refresh the browser
on file changes, or `--port 4001` if the default port is in use.

Make sure `_config.yml`'s `url` is `https://koutsakis-lab.github.io` and `baseurl` is left blank
(do not delete the key) before building.

---

## Pushing to production

Pushes to `main` trigger [`.github/workflows/jekyll.yml`](.github/workflows/jekyll.yml), which
builds the site with Jekyll and deploys it to GitHub Pages automatically — there is no manual
build/deploy step. Make substantial changes on a branch and open a pull request before merging to
`main`.

`.github/workflows/update-publications.yml` runs weekly and regenerates
[`_bibliography/papers.bib`](_bibliography/papers.bib) from OpenAlex via
[`scripts/update_publications.py`](scripts/update_publications.py) — see that script's header and
[`scripts/publications_exclusions.txt`](scripts/publications_exclusions.txt) before hand-editing
the bibliography.

---

## Repository layout

```txt
.
├── assets/
│   └── img/
│       ├── logos/   — sponsor/collaborator logos (see _data/sponsors.yml)
│       └── people/  — profile photos for the people page
├── _bibliography/
│   ├── papers.bib          — generated from OpenAlex; do not hand-edit
│   └── accepted.bib        — hand-maintained "accepted / in press" entries
├── _config.yml             — site configuration
├── _data/
│   ├── sponsors.yml        — homepage sponsor grid
│   └── coauthors.yml       — co-author name disambiguation for publications
├── _includes/, _layouts/, _sass/ — theme templates and styles
├── _news/                  — dated announcement files shown on the homepage
├── _pages/                 — site pages (about, research, people, contact, ...)
│   └── people/
│       ├── faculty (about_koutsakis.md), grad/, undergrad/, affiliates/
├── _research/               — research-area tiles shown on the /research/ page
├── _teaching/               — courses shown on the /teaching/ page
└── scripts/                 — publication-fetch script and its exclusion list
```

---

## Editing content

### Homepage — `_pages/about.md`

Front matter toggles what's shown:
```yaml
news: true # includes a list of news items
selected_papers: false # includes a list of papers marked as "selected={true}"
social: true # includes social icons at the bottom of the page
sponsors: true # Includes sponsors
```
`hero_image` sets the homepage banner; set `hero_video` alongside it to autoplay a video with
`hero_image` as the poster frame. The body of the file is the homepage introduction text and
supports LaTeX via MathJax.

### Research page — `_pages/research.html`

Loops over the `research` collection (`_research/*.md`), rendering each as an expandable tile.
Front matter per file:
```yaml
layout: default
title: Propulsion
img: /assets/img/some_image.jpg
align: left
background: "#0f1c50"
text: "#ffffff"
mode: dark
```
`background`/`text` set the tile's accent color; `align` controls how the tile image is cropped;
`mode` (`dark`/`light`) sets the overlay/text contrast. The body markdown is the tile's expanded
content — figures, videos, and prose describing that research area.

### People page — `_pages/people.md`

Lists faculty, graduate students, undergraduates, and research affiliates. Each entry pairs a
photo with a bio file:
```yaml
- align: left
  image: people/lastname.jpg
  content: people/grad/about_lastname.md
```
To add someone: drop a photo in `assets/img/people/`, add a bio markdown file under the matching
`_pages/people/{grad,undergrad,affiliates}/` folder (existing files show the format — name, title,
degrees, a short research/interests blurb, and an email/Scholar link line), then add one entry to
the array above. To remove someone, delete their entry, bio file, and photo.

### Publications page — `_pages/publications.md`

Automatically generated from `_bibliography/papers.bib` (see [Pushing to
production](#pushing-to-production) for how that file is kept current) plus a hand-maintained
`_bibliography/accepted.bib` for accepted/in-press work not yet indexed by OpenAlex — remove an
entry from `accepted.bib` once it appears in the generated bibliography, to avoid it listing twice.
Sorting and display options are configured under `scholar:` in `_config.yml`.

### Teaching page — `_pages/teaching.html`

Generated from `_teaching/*.md`. Front matter fields:
```yaml
title: "ME 320L: Heat Transfer"       # required
catalog: "https://catalog.unm.edu/..." # optional — link to the UNM Catalog entry
syllabus: "ME320.pdf"                  # optional — file name under assets/pdf/
```
The course description is the body of the file.

### News / announcements — `_news/`

One file per item, named `YYYY-MM-DD-slug.md`, with `layout: post` and `inline: true` front
matter. Up to 3 show on the homepage at once (configurable via `announcements.limit` in
`_config.yml`), even if more exist in the folder.

### Sponsors — `_data/sponsors.yml`

Each entry is a `name`, a `logo` filename (under `assets/img/logos/`), an optional `url`, and a
`current` flag. Rendered by [`_includes/sponsors.liquid`](_includes/sponsors.liquid) in the
homepage sponsor grid.

### Contact page — `_pages/contact.md`

Plain markdown — edit directly.

### Adding more pages

Create a markdown/HTML file under `_pages/` with front matter like:
```yaml
---
layout: page
permalink: /url-here/
title: Page Title
description: optional
nav: true
nav_order: 99
---
```
`nav`/`nav_order` control whether and where the page appears in the top navigation (lower number
= further left). `layout: page` is the default for any page that doesn't need the specialized
`about` or `research` layouts.

---

## License

The al-folio theme is available as open source under the terms of the [MIT
License](https://github.com/alshedivat/al-folio/blob/master/LICENSE). It was originally based on
the [\*folio theme](https://github.com/bogoli/-folio) by [Lia Bogoev](https://liabogoev.com),
also under the MIT license. See [`LICENSE`](LICENSE) for the full attribution.
