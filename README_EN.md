# TermAtlas

**An open bilingual lexicon of sensitive terms and notable named entities.**

[中文](README.md) · [Contributing](CONTRIBUTING.md) · [Data model](docs/data-model.md) · [Governance and licensing](docs/governance.md)

TermAtlas is a community-driven data repository for developers who need traceable,
reviewable, machine-readable lexicons. Its source format is UTF-8 JSONL, with lightweight
Python 3.11+ tools. This initial release establishes the infrastructure: **the production
dataset is empty**. Three synthetic records in `examples/data/` are excluded from exports.

Sensitivity depends on region, context and use. TermAtlas is not a universal blocklist.
**Named entities and sensitive terms are separate. Listing a person, company or organization
does not imply sensitivity, illegality, danger or any other negative attribute.**

## Features and collections

- **Sensitive terms:** Chinese and English terms, explicit aliases and variants; multiple
  regional assessments and categories per meaning, with risk labels and usage boundaries.
- **Named entities:** notable public people, companies and organizations; Chinese and
  English names, abbreviations, aliases, disambiguation and public references.
- **Traceability:** random UUIDs, source and reuse metadata, review states, dates and Git history.
- **Validation:** JSON Schema, cross-record duplicate checks, Unicode conflict warnings,
  pytest and GitHub Actions.
- **Reproducibility:** stable ordering, complete JSON records, separate exports and SHA-256
  manifests, without a database or service.

The entity collection excludes private-person profiling, private phone numbers, home
addresses and unsupported characterizations.

## Repository layout

```text
data/                       # Reviewed data; initially empty
  sensitive/{zh,en}.jsonl
  entities/{people,companies,organizations}.jsonl
pending/                    # Same layout, isolated proposals
schemas/                    # Common, sensitive-term and entity schemas
scripts/                    # Validation, lossless formatting and builds
tests/                      # Unit and CLI tests; examples or temporary fixtures only
examples/                   # Synthetic records and an export reader
docs/                       # Data dictionary, governance and licensing
.github/                    # CI, Issue / PR templates and dependency updates
dist/                       # Generated output, excluded from Git
README.md / README_EN.md
CONTRIBUTING.md
LICENSE / LICENSE-DATA / LICENSES/
pyproject.toml / requirements-dev.txt
```

## Quick start

```bash
git clone git@github.com:gezhiwei8899/term-atlas.git
cd term-atlas
python -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.txt

python scripts/validate.py
python scripts/validate.py --examples
python scripts/build.py
python examples/read_exports.py
```

On Windows, activate with `.venv\Scripts\activate`. For runtime dependencies alone,
use `python -m pip install -e .`. Tools currently require a source checkout;
this project does not yet ship a public Python SDK or a self-contained data wheel.

`validate.py` checks `data/` and `pending/` by default. Errors identify the file, line
and reason, and return a nonzero exit status. Add `--examples` to check examples,
or `--strict` to fail on potential alias, homonym or compatibility-character conflicts.
Regular CI reports these warnings for human review instead of requiring distinct
entities to be merged.

## Data format

Each line contains one JSON object. Blank lines, comments, BOMs and duplicate object
keys are rejected; empty files are valid. This is a **complete synthetic proposal**,
expanded for readability. In a JSONL file it occupies a single line.
The reserved `example.invalid` URL intentionally does not resolve and is not a real source.

```json
{
  "schema_version": "1.0",
  "id": "st_b26dd26b-5edb-4964-bfc0-758ed7b2ccf8",
  "term": "example-placeholder",
  "language": "en",
  "sense": "synthetic-example",
  "aliases": [],
  "assessments": [{
    "regions": ["001"],
    "categories": ["context_dependent"],
    "risk": "low",
    "context": "Synthetic placeholder only; no real sensitivity assessment."
  }],
  "sources": [{
    "url": "https://example.invalid/term-atlas/synthetic",
    "title": "Synthetic example, not a real source",
    "accessed_at": "2026-10-20",
    "rights": {"basis": "unresolved", "note": "For documentation only."}
  }],
  "review": {"status": "pending"},
  "created_at": "2026-10-20",
  "updated_at": "2026-10-20"
}
```

The separate [Entity Schema](schemas/entity.schema.json) uses `entity_type`, `names`,
`disambiguation` and `regions` for identity and name-usage scope. It has no sensitivity
categories or risk fields. See the [complete synthetic entity](examples/data/entities/companies.jsonl)
and [Chinese term example](examples/data/sensitive/zh.jsonl).
At least one Chinese or English name is required. Add the other only when verified;
do not invent translations.

IDs consist of `st_` or `ne_` followed by a UUID v4. They remain unchanged when a name
or category changes. Supported language tags are `zh`, `zh-Hans`, `zh-Hant` and `en`;
regions are recorded separately. See the [data dictionary](docs/data-model.md) for
field definitions and controlled values.

## Normalization and duplicates

- Original strings are preserved. NFC is used only to compare canonically equivalent spellings.
- There is no automatic NFKC rewriting, case folding, simplified/traditional conversion,
  punctuation removal or whitespace removal.
- NFKC + casefold discovers review candidates only: `ABC`, `ＡＢＣ` and `abc` are never
  automatically merged.
- The same spelling, base language and `sense` belong in one record with regional
  assessments and category arrays. Different meanings need distinct senses and context.
  Homonymous entities need distinct evidence and `disambiguation`.
- The two collections are never cross-compared to infer sensitivity. Known Chinese script
  variants must be recorded as explicit aliases.

```bash
python scripts/format.py --check  # Read-only check
python scripts/format.py          # Sort records and keys; preserve strings, IDs and arrays
```

## Using exports

```text
dist/
  sensitive/zh.txt               # Chinese terms and explicit Chinese aliases
  sensitive/en.txt               # English terms and explicit English aliases
  sensitive/terms.json           # Complete records, including context and provenance
  entities/entities.json         # Complete entity records
  entities/people.json
  entities/companies.json
  entities/organizations.json
  manifest.json                 # Counts, license and per-file SHA-256 hashes
```

Only `approved` records from `data/` are exported. Pending records, deprecated records
and examples are excluded. JSON arrays are ordered by ID. TXT removes **exact duplicate
strings only**, sorts by Unicode code point and preserves original spellings.
The same data and tool version produce the same bytes; no build timestamp is added.

**TXT loses region, meaning, risk and provenance. Treat it only as a candidate vocabulary.**
Read complete JSON when context matters. Never add entity names to sensitive-term TXT,
or treat a match alone as grounds to block someone or infer wrongdoing.

```python
import json
from pathlib import Path

terms = json.loads(Path("dist/sensitive/terms.json").read_text(encoding="utf-8"))
entities = json.loads(Path("dist/entities/entities.json").read_text(encoding="utf-8"))
# Consult each term's assessments for context; entities support entity recognition only.
```

## Contributing and checks

Fork → propose records in `pending/` or update an existing record → provide sources,
context and reuse evidence → open a PR → pass CI → human review → move approved
records into production while retaining IDs. See [CONTRIBUTING.md](CONTRIBUTING.md).
Templates cover new terms, entities, edits, corrections and removals.
Disputed records follow the [governance process](docs/governance.md).
Do not repeat private information in public issues.

```bash
python -m ruff check .
python -m ruff format --check .
python scripts/validate.py --examples
python scripts/format.py --check
python -m pytest -q
python scripts/build.py
```

CI runs on PRs and pushes to `main`, tests Python 3.11 / 3.14, and compares two builds.
The repository administrator must make both `Quality (Python …)` checks required
in branch protection or a ruleset and require human PR review. A failed workflow
alone does not prevent an administrator from merging directly.

## Sources, licensing and limitations

Code, schemas and documentation use [MIT](LICENSE). Data contributions and database
arrangements owned by contributors use [CC0 1.0](LICENSE-DATA), with the
[full legal text](LICENSES/CC0-1.0.txt) included. CC0 applies only to rights the contributor
can grant; it does not grant third-party privacy, publicity or trademark rights.
See [Creative Commons' CC0 explanation](https://creativecommons.org/publicdomain/zero/1.0/).

A source citation is evidence, **not permission to copy**. Every source records
`rights.basis` and a note: independently written factual reference, CC0, explicit
compatible permission, or unresolved rights. Do not bulk-copy datasets with unclear
permissions. Material requiring attribution or other additional conditions cannot
simply be relabeled CC0; propose a compatible licensing arrangement for maintainer
review first. No third-party dataset is imported in this initialization.

The data is provided as-is and may be incomplete, ambiguous or outdated. Users must
evaluate context, sources and applicable rules. Inclusion is not an allegation,
reputation assessment or legal conclusion about any person or organization.

## Roadmap

- [x] Separate schemas, provenance, pending-data isolation, validation, formatting,
  deterministic exports and CI.
- [ ] Small batches of human-reviewed Chinese and English records; refine category guidance.
- [ ] More languages, tag searches, versioned datasets and incremental updates.
- [ ] Evaluate exact matching, Aho-Corasick, fuzzy matching, tokenization and NER as needed.
- [ ] Evaluate a REST API and Python / Java / Go / JavaScript SDKs as needed.

These extensions are not implemented yet. The data remains independent of a matching
engine or service framework.
