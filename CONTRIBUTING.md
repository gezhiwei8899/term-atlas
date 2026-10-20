# 贡献指南 / Contributing

欢迎可验证、可复用的词条及工具改进。请先阅读 [中文说明](README.md)、
[English README](README_EN.md)、[数据字典](docs/data-model.md) 和
[治理与许可](docs/governance.md)。

We welcome verifiable records and tooling improvements. Read the linked documents
before contributing. The same standards apply to both language collections.

## 收录标准 / Inclusion criteria

- 敏感词必须有明确语义、适用地区、上下文、分类依据及误判说明。
  身份、观点、政治立场或被列入实体库都不是自动判为敏感的依据。
- 实体必须有公开知名性和可靠来源。优先官方资料、机构档案、可信公开参考资料；
  同名不等于同一实体。中文／英文名称、别名和缩写分别核实。
- 不接收私人联系方式、住址、身份凭证、私人个体画像或无依据指控。
- 不编造来源，不把搜索摘要当作完整证据，不整体复制许可不明的数据集。

Sensitive terms need a defined meaning, regional scope, contextual evidence, categories
and false-positive guidance. Identity, opinions, political positions or entity membership
do not establish sensitivity. Entities need public notability and reliable references,
preferably official or institutional records. Verify every name, alias and abbreviation.
No private contact details, addresses, identity documents, private-person profiles,
unsupported allegations, invented sources or unlicensed bulk imports.

## 标准流程 / Workflow

1. Fork 仓库并创建工作分支 / Fork the repository and create a working branch.
2. 新条目放入 `pending/` 对应 JSONL；首次生成 UUID v4：
   `python -c "import uuid; print(uuid.uuid4())"`，加 `st_` 或 `ne_` 前缀。
   不复制示例 ID，不按名称生成或重新分配已有 ID。
   / Put new records in the matching `pending/` file. Generate a fresh UUID v4 once;
   retain existing IDs for edits.
3. 填写真实来源、访问日期、权利依据、分类或身份区分；状态为 `pending`。
   只提交本人有权贡献的原创内容；复制内容须有兼容 CC0 的明确依据。
   / Provide real sources, access dates, reuse evidence and contextual or identity
   details. Use `pending`; contribute only material you have the right to contribute.
4. 运行下面的全部检查，解释警告。/ Run all checks below and explain warnings.
5. 提交 PR，列出变动 ID、依据和预期影响；保持 PR 范围集中。
   / Open a focused PR with changed IDs, evidence and expected effects.
6. CI 通过后，由维护者人工核对来源、隐私、别名、上下文及权利。
   作者填写 `approved` 不等于已获批准，CI 也不验证人物身份或版权归属。
   / A maintainer checks evidence, privacy, aliases, context and rights. A status
   field or passing CI does not establish factual or legal accuracy.
7. 审核者将记录保留 ID 移入 `data/`，填写 `reviewed_by`（公开 GitHub 用户名）、
   `reviewed_at`、`note`，更新 `updated_at`；在 PR 记录决定后合并。
   / The reviewer moves approved records into `data/`, preserving IDs and recording
   their public GitHub handle, review date and decision note before merging.

已有记录修改也通过 PR 审核。需要重审时将原记录移到 `pending/`，不要在两个目录保留同 ID。
不再推荐使用但可安全保留的记录设为 `deprecated`；隐私或无权使用的内容应按删除流程移除，
不应为保存历史而重复公开。审核过程通常要求作者以外的人参与。

Changes to existing records also require review. Move records needing reconsideration
to `pending/` rather than duplicating an ID across stages. Use `deprecated` for records
that can safely remain for reference but should no longer be exported. Remove private
or unauthorized content through the removal process instead of preserving it publicly.
Review should normally involve someone other than the author.

## 本地检查 / Local checks

Python 3.11+：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --require-hashes -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
python scripts/validate.py --examples
python scripts/format.py --check
python -m pytest -q
python scripts/build.py
python scripts/build.py --output /tmp/term-atlas-check
diff -ru dist /tmp/term-atlas-check
```

最后的 `diff` 示例适用于 POSIX；CI 自动执行相同检查。代码格式使用 `python -m ruff format .`；
数据格式使用 `python scripts/format.py`。格式化不会变更 ID、字符串或数组次序，
也不会删除重复记录。请人工修复确定重复，解释合法同名，不要无依据合并。
`python scripts/validate.py --strict` 可额外将警告视为失败。

The final `diff` example is for POSIX systems; CI performs the same comparison.
Use Ruff for Python formatting and `scripts/format.py` for JSONL formatting.
The latter preserves IDs, strings and array order and never removes duplicate records.
Resolve confirmed duplicates manually and explain legitimate homonyms.
Use `--strict` when you also want warnings to fail validation.

工具错误返回非零；格式错误含文件和行号。CI 用哈希锁定的 `requirements-dev.txt`。
维护者更新依赖时，可用以下命令重建锁定文件，并在 Python 3.11 / 3.14 上重测：

Tools return nonzero on errors and report file/line locations. CI installs from the
hash-pinned `requirements-dev.txt`. Maintainers can refresh it using the command below
and rerun checks on Python 3.11 / 3.14. `uv` is only needed to refresh this file.

```bash
uv pip compile pyproject.toml --extra dev --python-version 3.11 \
  --generate-hashes --output-file requirements-dev.txt
```

## 修改、纠错、删除和争议 / Corrections, removal and disputes

使用对应 Issue 模板，提供记录 ID、理由、可公开证据和建议处理。对来源授权不明、
事实错误或隐私风险的报告，维护者先核验并视情况移出构建集合，再作修订或删除决定。
说明审核理由，允许新证据触发复审；不因报告者身份或观点拒绝有效证据。
不要上传证件或在公开讨论复述私人数据。敏感披露渠道及历史清理边界见
[治理文档](docs/governance.md)。

Use the correction/removal template with the record ID, reason, public evidence and
requested outcome. Maintainers assess factual, licensing and privacy concerns, exclude
records from exports where warranted, and document a correction or removal decision.
New evidence can reopen review. Do not post identity documents or repeat private data;
see governance for disclosure options and historical-copy limitations.

## 许可确认 / Licensing

贡献代码、Schema 和文档表示同意按 MIT 提供；在本人拥有权利的范围内，
原创数据及编排按 CC0 贡献。第三方内容不因提交 PR 而变成 CC0。
`fact_reference` 表示以来源核对事实并独立撰写，不允许复制受保护表述或批量提取。
CC0 或明确授权导入须提供 `evidence_url`；需要署名等额外条件时先开 Issue，
不能用 `permission` 字段绕过条件。`unresolved` 只能留在待审区。

Contribute code, schemas and documentation under MIT, and your original data/arrangement
under CC0 to the extent you hold the rights. A PR does not relicense third-party material.
`fact_reference` means checking facts and independently writing the record, not copying
protected wording or extracting a database in bulk. CC0 or permission-based reuse needs
an evidence URL. Discuss additional attribution or other obligations before importing;
the `permission` field does not waive them. Unresolved rights stay in the pending area.

提交信息建议使用 `feat(data): ...`、`fix(data): ...`、`fix(tools): ...` 或 `docs: ...`。
请勿提交 `dist/`、虚拟环境、凭证或无关格式修改。

Prefer Conventional Commits and focused changes. Do not commit generated exports,
virtual environments, credentials or unrelated formatting changes.
