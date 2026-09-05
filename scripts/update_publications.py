#!/usr/bin/env python3
"""Generate _bibliography/papers.bib from scratch using OpenAlex.

Fetches all works for ORCID 0000-0002-8108-2591 and writes a clean papers.bib.
The existing file is completely replaced on every run — no merging, no patching.

Filters applied:
  - Excluded types: dataset, paratext, peer-review, grant, editorial,
    erratum, dissertation (theses), report (technical reports)
  - Machine-translated duplicates removed (NICT source, or non-Latin title)
  - Preprints (arXiv, SSRN, etc.) removed when a published version exists
  - Manual exclusions read from scripts/publications_exclusions.txt

Run from the repo root:
    python scripts/update_publications.py

Requirements: pip install requests
"""

import re
import sys
import time
from datetime import datetime, timezone
from typing import Optional
import requests
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ORCID = "0000-0002-8108-2591"
BIB_PATH = Path("_bibliography/papers.bib")
EXCLUSIONS_PATH = Path("scripts/publications_exclusions.txt")
API_BASE = "https://api.openalex.org"
CONTACT_EMAIL = "koutsakis@unm.edu"

# OpenAlex sometimes fails to link new papers to the canonical ORCID author
# record, creating orphaned author IDs instead. List any known extras here —
# works from all of them are merged and deduplicated with the main ORCID query.
# To find new ones: https://openalex.org/authors?filter=display_name:Georgios+Koutsakis
EXTRA_AUTHOR_IDS = []

# Work types to keep (everything else is silently dropped).
# Note: 'dissertation' (theses) and 'report' (technical reports) are
# intentionally excluded — the group does not list either on the page.
ALLOWED_TYPES = frozenset({
    'article', 'preprint', 'proceedings-article', 'book-chapter',
    'book', 'review', 'letter',
})

# Source names that identify a preprint server (case-insensitive substring match)
PREPRINT_SOURCE_NAMES = frozenset({'arxiv', 'ssrn', 'biorxiv', 'medrxiv', 'chemrxiv', 'techrxiv'})

# DOI prefixes that identify a preprint (arXiv = 10.48550, SSRN = 10.2139)
PREPRINT_DOI_PREFIXES = ('10.48550/', '10.2139/')

# ---------------------------------------------------------------------------
# LaTeX / Unicode helpers
# ---------------------------------------------------------------------------

_LATEX_MAP = {
    'á': "{\\'a}", 'à': '{\\`a}', 'â': '{\\^a}', 'ä': '{\\"a}', 'ã': '{\\~a}', 'å': '{\\aa}',
    'é': "{\\'e}", 'è': '{\\`e}', 'ê': '{\\^e}', 'ë': '{\\"e}',
    'í': "{\\'i}", 'ì': '{\\`i}', 'î': '{\\^i}', 'ï': '{\\"i}',
    'ó': "{\\'o}", 'ò': '{\\`o}', 'ô': '{\\^o}', 'ö': '{\\"o}', 'õ': '{\\~o}', 'ø': '{\\o}',
    'ú': "{\\'u}", 'ù': '{\\`u}', 'û': '{\\^u}', 'ü': '{\\"u}',
    'ý': "{\\'y}", 'ÿ': '{\\"y}',
    'ñ': '{\\~n}', 'ç': '{\\c{c}}', 'ß': '{\\ss}', 'æ': '{\\ae}', 'œ': '{\\oe}',
    'Á': "{\\'A}", 'À': '{\\`A}', 'Â': '{\\^A}', 'Ä': '{\\"A}', 'Å': '{\\AA}',
    'É': "{\\'E}", 'È': '{\\`E}', 'Ê': '{\\^E}', 'Ë': '{\\"E}',
    'Í': "{\\'I}", 'Î': '{\\^I}', 'Ï': '{\\"I}',
    'Ó': "{\\'O}", 'Ö': '{\\"O}', 'Ô': '{\\^O}', 'Ø': '{\\O}',
    'Ú': "{\\'U}", 'Ü': '{\\"U}', 'Û': '{\\^U}',
    'Ñ': '{\\~N}', 'Ç': '{\\c{C}}', 'Æ': '{\\AE}', 'Œ': '{\\OE}',
    'ł': '{\\l}',  'Ł': '{\\L}',
    'ş': '{\\c{s}}', 'Ş': '{\\c{S}}',
    'ğ': '{\\u{g}}', 'Ğ': '{\\u{G}}',
    'ő': '{\\H{o}}', 'Ő': '{\\H{O}}',
    'ű': '{\\H{u}}', 'Ű': '{\\H{U}}',
    'ž': '{\\v{z}}', 'Ž': '{\\v{Z}}',
    'š': '{\\v{s}}', 'Š': '{\\v{S}}',
    'č': '{\\v{c}}', 'Č': '{\\v{C}}',
    'ř': '{\\v{r}}', 'Ř': '{\\v{R}}',
    'ě': '{\\v{e}}', 'Ě': '{\\v{E}}',
    'ď': '{\\v{d}}', 'Ď': '{\\v{D}}',
    'ť': '{\\v{t}}', 'Ť': '{\\v{T}}',
    'ň': '{\\v{n}}', 'Ň': '{\\v{N}}',
    '&': '\\&',
}

_SUBSCRIPT   = str.maketrans('0123456789+-=()aehijklmnoprstuvx',
                              '₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ')
_SUPERSCRIPT = str.maketrans('0123456789+-=()nid',
                              '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱᵈ')


def _apply_sub(m: re.Match) -> str:
    return m.group(1).translate(_SUBSCRIPT)

def _apply_sup(m: re.Match) -> str:
    return m.group(1).translate(_SUPERSCRIPT)


def clean_title(title: str) -> str:
    """Normalise math/HTML notation in titles to plain Unicode.

    OpenAlex titles may contain:
      - LaTeX display-math  $$\\text{CO}_2$$  → CO₂
      - LaTeX inline-math   $\\text{CO}_2$    → CO₂
      - HTML subscripts     CO<sub>2</sub>     → CO₂
      - HTML superscripts   x<sup>2</sup>      → x²

    jekyll-scholar's LaTeX filter strips $ delimiters but leaves bare commands,
    causing visible artefacts like "\\text CO_2".  We convert everything to
    plain Unicode here so the title is clean before entering the BibTeX file.
    """
    # 0. HTML sub/superscripts first (some OpenAlex titles use these instead of LaTeX)
    title = re.sub(r'<sub>(.*?)</sub>', lambda m: m.group(1).translate(_SUBSCRIPT),   title)
    title = re.sub(r'<sup>(.*?)</sup>', lambda m: m.group(1).translate(_SUPERSCRIPT), title)
    # Strip any other HTML tags that might appear
    title = re.sub(r'<[^>]+>', '', title)

    # 1. Collapse display-math markers $$...$$ → $...$
    title = re.sub(r'\$\$(.*?)\$\$', r'$\1$', title, flags=re.DOTALL)

    # 2. Inside any $...$ block, do math-to-Unicode conversion, then strip $
    def fix_math_block(m: re.Match) -> str:
        s = m.group(1)
        # Strip text/formatting commands — just keep their content
        s = re.sub(r'\\(?:text|mathrm|mathit|mathbf|operatorname)\{([^}]*)\}', r'\1', s)
        # Convert sub/superscripts to Unicode
        s = re.sub(r'_\{([^}]+)\}', _apply_sub, s)
        s = re.sub(r'_([0-9])', lambda x: x.group(1).translate(_SUBSCRIPT), s)
        s = re.sub(r'\^\{([^}]+)\}', _apply_sup, s)
        s = re.sub(r'\^([0-9])', lambda x: x.group(1).translate(_SUPERSCRIPT), s)
        # Strip any remaining LaTeX commands and bare braces
        s = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', s)
        s = re.sub(r'\\[a-zA-Z]+', '', s)
        s = s.replace('{', '').replace('}', '')
        return s.strip()

    title = re.sub(r'\$([^$]+)\$', fix_math_block, title)

    # 3. Handle any stray subscript/superscript notation outside math delimiters
    title = re.sub(r'_\{([^}]+)\}', _apply_sub, title)
    title = re.sub(r'\^\{([^}]+)\}', _apply_sup, title)

    return title


def latex_encode(text: str) -> str:
    """Replace Unicode characters with their LaTeX equivalents."""
    if not text:
        return ''
    for char, enc in _LATEX_MAP.items():
        text = text.replace(char, enc)
    return text


# ---------------------------------------------------------------------------
# OpenAlex API
# ---------------------------------------------------------------------------

_WORK_FIELDS = ('id,title,authorships,publication_year,primary_location,'
                'biblio,doi,abstract_inverted_index,type,open_access')


def _fetch_works_by_filter(filter_str: str, label: str = '') -> list:
    """Paginate through OpenAlex works matching filter_str and return all results."""
    results = []
    cursor = '*'
    headers = {'User-Agent': f'koutsakis-lab-website/1.0 (mailto:{CONTACT_EMAIL})'}

    while cursor:
        params = {
            'filter': filter_str,
            'per_page': 200,
            'cursor': cursor,
            'select': _WORK_FIELDS,
        }
        resp = requests.get(f'{API_BASE}/works', params=params,
                            headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        batch = data.get('results', [])
        results.extend(batch)
        if label:
            print(f'  [{label}] {len(results)} works...', end='\r', flush=True)
        meta = data.get('meta', {})
        cursor = meta.get('next_cursor') if len(batch) == 200 else None
        time.sleep(0.05)

    return results


def fetch_all_works(orcid: str, extra_author_ids: list) -> list:
    """Fetch works via ORCID filter plus any extra OpenAlex author IDs.

    OpenAlex occasionally fails to link new papers to the canonical ORCID
    record, creating orphaned author IDs. Works from all sources are merged
    and deduplicated by OpenAlex work ID before returning.
    """
    # Primary: fetch by ORCID
    print('  Fetching by ORCID...', end='\r', flush=True)
    works = _fetch_works_by_filter(
        f'authorships.author.orcid:{orcid}', label='ORCID'
    )
    print(f'  ORCID query: {len(works)} works.          ')

    # Supplemental: fetch each extra author ID using OpenAlex pipe-OR syntax
    if extra_author_ids:
        pipe_ids = '|'.join(extra_author_ids)
        print(f'  Fetching {len(extra_author_ids)} extra author ID(s)...', end='\r', flush=True)
        extra = _fetch_works_by_filter(
            f'authorships.author.id:{pipe_ids}', label='extra IDs'
        )
        print(f'  Extra IDs query: {len(extra)} works.          ')

        # Merge, deduplicating by OpenAlex work ID
        seen_ids = {w['id'] for w in works}
        new_works = [w for w in extra if w['id'] not in seen_ids]
        print(f'  Added {len(new_works)} new work(s) from extra author IDs.')
        works.extend(new_works)

    print(f'  Total before filtering: {len(works)} works.')
    return works


def reconstruct_abstract(inv_index: Optional[dict]) -> Optional[str]:
    """Reconstruct an abstract string from OpenAlex's inverted-index format."""
    if not inv_index:
        return None
    word_at = {}
    for word, positions in inv_index.items():
        for pos in positions:
            word_at[pos] = word
    return ' '.join(word_at[i] for i in sorted(word_at)) if word_at else None


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def _norm(s: str) -> str:
    """Normalise a string for fuzzy matching (lowercase, alphanumeric only)."""
    return re.sub(r'[^a-z0-9]', '', s.lower()) if s else ''


def load_exclusions() -> set:
    """Load the manual exclusion list (DOIs and OpenAlex IDs)."""
    if not EXCLUSIONS_PATH.exists():
        return set()
    result = set()
    for line in EXCLUSIONS_PATH.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            line = (line.replace('https://doi.org/', '')
                       .replace('https://openalex.org/', '')
                       .lower().strip())
            result.add(line)
    return result


def is_excluded(work: dict, exclusions: set) -> bool:
    doi     = (work.get('doi') or '').replace('https://doi.org/', '').strip().lower()
    work_id = (work.get('id') or '').replace('https://openalex.org/', '').strip().lower()
    return doi in exclusions or work_id in exclusions


# Non-Latin script ranges (CJK ideographs, hiragana, katakana, fullwidth forms,
# and the 【 】 brackets used by translation services). The group publishes in
# English, so any title containing these is an OpenAlex machine-translation
# duplicate — e.g. 【Powered by NICT】 or 【JST・京大機械翻訳】 — of an English work.
_NONLATIN_TITLE_RE = re.compile(
    r'[　-〿぀-ヿ㐀-䶿一-鿿＀-￯]'
)


def is_machine_translation(work: dict) -> bool:
    """Return True for non-English, machine-translated duplicate entries.

    Two signals: (1) the source is a known translation service (NICT), or
    (2) the title carries non-Latin script, which for this group only ever
    appears on auto-translated copies of an English original.
    """
    loc = work.get('primary_location') or {}
    src = loc.get('source') or {}
    name = (src.get('display_name') or loc.get('raw_source_name') or '').lower()
    if 'nict' in name:
        return True
    return bool(_NONLATIN_TITLE_RE.search(work.get('title') or ''))


def is_preprint(work: dict) -> bool:
    """Return True if the work is a preprint (arXiv, SSRN, or type=preprint)."""
    if (work.get('type') or '').lower() == 'preprint':
        return True
    loc = work.get('primary_location') or {}
    src = loc.get('source') or {}
    name = (src.get('display_name') or loc.get('raw_source_name') or '').lower()
    if any(ps in name for ps in PREPRINT_SOURCE_NAMES):
        return True
    doi = (work.get('doi') or '').replace('https://doi.org/', '')
    return doi.startswith(PREPRINT_DOI_PREFIXES)


def deduplicate(works: list) -> list:
    """Remove preprints when a published version of the same work exists.

    Groups works by normalised title. Within each group, if any non-preprint
    version exists, all preprints are dropped. If the group is all preprints,
    the most recent is kept.
    """
    groups: dict[str, list] = {}
    for w in works:
        key = _norm(w.get('title') or '')
        if len(key) < 10:        # too short to reliably match on title
            key = f'__unique_{id(w)}'
        groups.setdefault(key, []).append(w)

    result = []
    removed = 0
    for group in groups.values():
        if len(group) == 1:
            result.append(group[0])
            continue
        published = [w for w in group if not is_preprint(w)]
        preprints  = [w for w in group if is_preprint(w)]
        if published:
            result.extend(published)
            removed += len(preprints)
        else:
            # All are preprints — keep the most recent
            result.append(max(group, key=lambda w: w.get('publication_year') or 0))
            removed += len(group) - 1

    if removed:
        print(f'  Deduplication removed {removed} preprint(s) with published equivalents.')
    return result


# ---------------------------------------------------------------------------
# BibTeX formatting
# ---------------------------------------------------------------------------

_STOPWORDS = frozenset({
    'a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for',
    'and', 'or', 'with', 'by', 'from', 'via', 'using', 'into',
    'is', 'are', 'was', 'be', 'as', 'its',
})

_TYPE_MAP = {
    'article': 'article',
    'preprint': 'article',
    'proceedings-article': 'inproceedings',
    'book-chapter': 'incollection',
    'book': 'book',
    'review': 'article',
    'letter': 'article',
}

# Lower-case particles that belong to the last name, not the first
_NAME_PARTICLES = frozenset({
    'von', 'van', 'de', 'del', 'della', 'di', 'du', 'la', 'le', 'les',
    'el', 'al', 'ter', 'zur', 'zum', 'af', 'av', 'den', 'der', 'ten',
    'op', 'het', 'bin', 'binti', 'das', 'dos', 'do', 'da',
})


def _abbreviate_token(token: str) -> str:
    """Abbreviate one name token to its initial(s).

    "Georgios" → "G."   |   "Jean-Marc" → "J.-M."   |   "M." → "M."
    """
    if not token:
        return token
    # Already a bare initial or initial-with-period
    core = token.rstrip('.')
    if len(core) == 1 and core.isalpha():
        return core + '.'
    # Hyphenated first name: "Jean-Marc" → "J.-M."
    if '-' in token:
        parts = token.split('-')
        return '-'.join(
            (p[0].upper() + '.' if p and p[0].isalpha() else p)
            for p in parts
        )
    # Normal token
    return (token[0].upper() + '.') if token[0].isalpha() else token


def _split_name(display_name: str) -> tuple:
    """Split 'First [Middle] [particle] Last' → (last_str, [first_tokens]).

    Name particles (van, von, de, …) are kept with the last name:
      "Adri van Duin"    → ("van Duin", ["Adri"])
      "Mei Ling Tan"     → ("Tan",      ["Mei", "Ling"])
      "Jean-Marc Rinard" → ("Rinard",   ["Jean-Marc"])
    """
    tokens = display_name.split()
    if len(tokens) <= 1:
        return display_name, []

    # Collect the last-name block: the final token, plus any preceding particles
    last_start = len(tokens) - 1
    while last_start > 0 and tokens[last_start - 1].lower() in _NAME_PARTICLES:
        last_start -= 1

    last        = ' '.join(tokens[last_start:])
    first_toks  = tokens[:last_start]
    return last, first_toks


def _name_to_bibtex(display_name: str) -> str:
    """Convert a full display name to abbreviated BibTeX 'Last, F. M.' format.

    Uses display_name (OpenAlex's normalised full name) as input so that
    abbreviation is always applied to a complete, unambiguous spelling.
    """
    if not display_name:
        return ''

    # Input may already be "Last, First Middle" (e.g. from some raw_author_name values)
    if ',' in display_name:
        last, rest = display_name.split(',', 1)
        first_toks = rest.strip().split()
    else:
        last, first_toks = _split_name(display_name)

    abbreviated = ' '.join(_abbreviate_token(t) for t in first_toks if t)
    last_enc    = latex_encode(last.strip())
    abbr_enc    = latex_encode(abbreviated)

    return f'{last_enc}, {abbr_enc}' if abbr_enc else last_enc


def format_authors(authorships: list) -> str:
    """Format author list as 'Last, F. M. and Last, F. M. ...' with LaTeX encoding.

    Always uses display_name (OpenAlex's fully resolved spelling) as the base
    so that abbreviation is applied consistently regardless of how individual
    papers cited the author.
    """
    parts = []
    for a in authorships:
        name = (((a.get('author') or {}).get('display_name') or '')
                or (a.get('raw_author_name') or '')).strip()
        if not name:
            continue
        parts.append(_name_to_bibtex(name))
    return ' and '.join(parts)


def make_key(work: dict, used_keys: set) -> str:
    """Generate a unique BibTeX key: firstauthorlastyearfirstword."""
    auths = work.get('authorships') or []
    year  = str(work.get('publication_year') or '0000')
    title = work.get('title') or ''

    if auths:
        tokens = ((auths[0].get('author') or {}).get('display_name') or '').split()
        last = re.sub(r'[^a-zA-Z]', '', tokens[-1]).lower() if tokens else 'unknown'
    else:
        last = 'unknown'

    words = re.sub(r'[^a-zA-Z\s]', ' ', title).lower().split()
    first_word = next(
        (w for w in words if w not in _STOPWORDS and len(w) > 1),
        words[0] if words else 'work',
    )

    base = f'{last}{year}{first_word}'
    key, suffix = base, ord('b')
    while key in used_keys:
        key = base + chr(suffix)
        suffix += 1
    return key


def work_to_bibtex(work: dict, key: str) -> str:
    """Convert an OpenAlex work dict to a BibTeX entry string."""
    entry_type = _TYPE_MAP.get((work.get('type') or 'article').lower(), 'article')

    title   = latex_encode(clean_title(work.get('title') or ''))
    authors = format_authors(work.get('authorships') or [])
    year    = str(work.get('publication_year') or '')
    doi     = (work.get('doi') or '').replace('https://doi.org/', '').strip()

    loc    = work.get('primary_location') or {}
    source = loc.get('source') or {}
    venue  = latex_encode(source.get('display_name') or loc.get('raw_source_name') or '')

    bib    = work.get('biblio') or {}
    volume = bib.get('volume') or ''
    number = bib.get('issue') or ''
    fp, lp = bib.get('first_page') or '', bib.get('last_page') or ''
    pages  = f'{fp}--{lp}' if fp and lp else fp

    abstract_raw = reconstruct_abstract(work.get('abstract_inverted_index'))
    abstract     = latex_encode(abstract_raw) if abstract_raw else ''

    oa     = work.get('open_access') or {}
    oa_url = (oa.get('oa_url') or '') if oa.get('is_oa') else ''

    venue_field = 'journal' if entry_type == 'article' else 'booktitle'

    lines = [f'@{entry_type}{{{key},']
    lines.append(f'  title={{{title}}},')
    lines.append(f'  author={{{authors}}},')
    if venue:
        lines.append(f'  {venue_field}={{{venue}}},')
    if volume:
        lines.append(f'  volume={{{volume}}},')
    if number:
        lines.append(f'  number={{{number}}},')
    if pages:
        lines.append(f'  pages={{{pages}}},')
    if year:
        lines.append(f'  year={{{year}}},')
    if doi:
        lines.append(f'  doi={{{doi}}},')
    if oa_url:
        lines.append(f'  open_access_url={{{oa_url}}},')
    if abstract:
        lines.append(f'  abstract={{{abstract}}},')
    lines.append('}')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    exclusions = load_exclusions()
    if exclusions:
        print(f'Loaded {len(exclusions)} manual exclusion(s) from {EXCLUSIONS_PATH}')

    print('Fetching works from OpenAlex...')
    works = fetch_all_works(ORCID, EXTRA_AUTHOR_IDS)

    # --- Filter ---
    before = len(works)
    works = [w for w in works if (work_type := (w.get('type') or '').lower())
             in ALLOWED_TYPES]
    print(f'  Dropped {before - len(works)} entries with excluded types '
          f'(dataset, paratext, etc.).')

    before = len(works)
    works = [w for w in works if not is_machine_translation(w)]
    print(f'  Dropped {before - len(works)} machine-translated/non-English entry/entries.')

    before = len(works)
    works = [w for w in works if not is_excluded(w, exclusions)]
    print(f'  Dropped {before - len(works)} manually excluded entry/entries.')

    # --- Deduplicate preprints ---
    works = deduplicate(works)

    # --- Sort newest-first ---
    works.sort(key=lambda w: w.get('publication_year') or 0, reverse=True)

    # --- Generate BibTeX ---
    used_keys: set = set()
    entries = []
    for work in works:
        if not work.get('title'):
            continue
        key = make_key(work, used_keys)
        used_keys.add(key)
        entries.append(work_to_bibtex(work, key))

    print(f'\nGenerating {len(entries)} BibTeX entries...')

    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    header = (
        f'% Auto-generated from OpenAlex on {timestamp}\n'
        f'% ORCID: {ORCID}\n'
        f'% Do not edit by hand — run scripts/update_publications.py to regenerate\n'
        f'% To permanently exclude an entry, add its DOI or OpenAlex ID\n'
        f'% to scripts/publications_exclusions.txt\n\n'
    )

    BIB_PATH.write_text(header + '\n\n'.join(entries) + '\n', encoding='utf-8')
    print(f'Written to {BIB_PATH}')


if __name__ == '__main__':
    main()
