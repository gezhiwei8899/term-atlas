# TermAtlas contributor guide

- Keep sensitive terms and named entities separate in models, directories and exports.
  Entity inclusion never implies sensitivity or wrongdoing.
- Use Python 3.11+ and JSON Schema Draft 2020-12. Keep dependencies small.
- Read the relevant schema, implementation and tests before editing. Preserve existing
  data and IDs; never derive IDs from names or regenerate IDs during formatting.
- Only reviewed, source-backed records with verified reuse rights belong in `data/`.
  Put proposals in `pending/` and synthetic records in `examples/` or `tests/fixtures/`.
- Do not automatically merge Unicode compatibility forms, case variants, simplified
  and traditional Chinese, homonyms or aliases. Explain ambiguity and review it.
- For changes, run the commands in CONTRIBUTING.md, including Ruff, validation,
  formatting checks, pytest and reproducible builds. Do not commit `dist/` or environments.
- Code, schemas and documentation use MIT; project-owned data contributions use CC0.
  A source link does not establish permission to copy that source.
- Default branch: `main`. Do not force-push or overwrite unrelated work.
