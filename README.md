# TermAtlas

**开放的中英文敏感词与知名实体词库。**

[English](README_EN.md) · [贡献指南](CONTRIBUTING.md) · [数据模型](docs/data-model.md) · [治理与许可](docs/governance.md)

TermAtlas 是社区驱动的结构化数据仓库，面向需要可追溯、可审核、可直接读取词库的开发者。
主要数据源为 UTF-8 JSONL，工具使用 Python 3.11+。当前交付数据基础设施，**正式数据为空**；
3 条虚构记录仅位于 `examples/data/`，不参与正式导出。

敏感性依赖地区、语境和用途。TermAtlas 不是普遍适用的绝对封禁清单。
**知名实体与敏感词完全分离：收录人物、企业或机构不表示其敏感、违法、危险或存在其他负面属性。**

## 特点与分类

- **敏感词**：中文、英文、别名及变体；每种语义可有多个地区评估和分类，记录风险提示与适用／不适用语境。
- **知名实体**：公众人物、企业、组织；中英文标准名称、简称、别名、同名区分和公开来源。
- **可追溯**：随机 UUID 标识、来源与再利用依据、审核状态、日期及 Git 更新历史。
- **可验证**：JSON Schema、跨记录重复检查、Unicode 冲突提示、pytest 和 GitHub Actions。
- **可复现**：稳定排序、完整 JSON 和分类型导出、SHA-256 清单；不依赖数据库或服务。

实体库不接收私人个体画像、私人电话、家庭住址或无依据的主观定性。

## 目录

```text
data/                       # 正式数据；初始化为空
  sensitive/{zh,en}.jsonl
  entities/{people,companies,organizations}.jsonl
pending/                    # 同样布局，隔离待审核提案
schemas/                    # common、sensitive、entity Schema
scripts/                    # 校验、无损格式化、构建
tests/                      # 单元与 CLI 测试；测试数据取自 examples 或临时目录
examples/                   # 虚构样例与读取示例
docs/                       # 数据字典、治理及许可说明
.github/                    # CI、Issue / PR 模板、依赖更新
dist/                       # 构建生成，不纳入 Git
README.md / README_EN.md
CONTRIBUTING.md
LICENSE / LICENSE-DATA / LICENSES/
pyproject.toml / requirements-dev.txt
```

## 快速开始

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

Windows 可使用 `.venv\Scripts\activate` 激活环境。只运行校验／构建时，也可以用
`python -m pip install -e .` 安装运行时依赖。源码检出是工具运行的前提；
当前没有发布 Python SDK 或可独立携带数据的 wheel。

`validate.py` 默认检查 `data/` 和 `pending/`，错误包含文件、行号和原因，失败返回非零。
`--examples` 加查示例；`--strict` 将可疑别名、同名或兼容字符警告也视为失败。
普通 CI 保留警告供人工审核，不会为了通过检查而强迫合并不同实体。

## 数据格式

每行一个 JSON 对象，无空行、注释、BOM 或重复对象键；文件可为空。下面是**完整虚构提案**，
为便于阅读展示为多行 JSON；JSONL 中需压成一行。`example.invalid` 是有意不可访问的占位域名，
不能作为真实词条来源。

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

实体使用独立的 [Entity Schema](schemas/entity.schema.json)，用 `entity_type`、`names`、
`disambiguation` 和 `regions` 表示身份与名称使用范围，不包含敏感分类或风险字段。
查看 [完整虚构实体](examples/data/entities/companies.jsonl) 和
[中文敏感词格式示例](examples/data/sensitive/zh.jsonl)。中文与英文标准名称至少提供一种；
只有有据可查时才补充另一种，避免编造译名。

ID 为 `st_` 或 `ne_` 加 UUID v4，首次分配后永久保留，与名称、分类无关。
语言支持 `zh`、`zh-Hans`、`zh-Hant`、`en`；地区单独记录。详细字段和枚举见
[数据模型](docs/data-model.md)。

## 标准化与重复检查

- 原始文本保持原样；规范等价的 NFC 形式只用作确定重复的比较键。
- 不自动进行 NFKC、大小写折叠、繁简转换、标点或空格删除。
- NFKC + casefold 只发现可疑冲突；例如 `ABC`、`ＡＢＣ`、`abc` 不会被自动合并。
- 同一词形、基础语言和 `sense` 的记录必须合并地区评估，分类使用数组。
  不同语义使用不同 `sense` 和上下文说明；同名实体通过来源和 `disambiguation` 区分。
- 敏感词与实体从不交叉进行敏感属性推断。已记录的繁简变体使用显式别名。

```bash
python scripts/format.py --check  # 仅检查
python scripts/format.py          # 稳定排序对象键和记录；不改字符串、ID 或数组
```

## 使用构建产物

```text
dist/
  sensitive/zh.txt               # 中文标准词及显式中文别名
  sensitive/en.txt               # 英文标准词及显式英文别名
  sensitive/terms.json           # 完整敏感词记录，保留所有语境及来源
  entities/entities.json         # 完整实体记录
  entities/people.json
  entities/companies.json
  entities/organizations.json
  manifest.json                 # 记录数、许可、各文件 SHA-256
```

仅 `data/` 中的 `approved` 记录参与导出，`pending`、`deprecated` 和示例均不导出。
JSON 按 ID 排序；TXT 仅按**完全相同字符串**去重，按 Unicode 码点排序，不改变原始拼写。
相同数据和工具版本产生相同字节，不添加构建时间。

**TXT 会丢失地区、语义、风险与来源，只能作为候选词表。** 需要语境判断时读取完整 JSON；
不可把实体加入敏感词 TXT，也不应仅凭命中就封禁用户或判断其违法性。

```python
import json
from pathlib import Path

terms = json.loads(Path("dist/sensitive/terms.json").read_text(encoding="utf-8"))
entities = json.loads(Path("dist/entities/entities.json").read_text(encoding="utf-8"))
# 使用 terms 中的 assessments 决定适用语境；entities 仅用于实体识别。
```

## 贡献与验证

Fork → 在 `pending/` 提交提案或修改已有条目 → 填写来源、语境及权利依据 →
提交 PR → CI → 人工审核 → 保留 ID 移入正式库。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。
支持新增敏感词、实体、修改、纠错和删除申请；有争议内容按
[治理流程](docs/governance.md) 重审。不要在公开 Issue 中重复披露隐私。

```bash
python -m ruff check .
python -m ruff format --check .
python scripts/validate.py --examples
python scripts/format.py --check
python -m pytest -q
python scripts/build.py
```

CI 在 PR 和 `main` 推送时测试 Python 3.11 / 3.14，并比较两次构建结果。
仓库管理员需在分支保护或 ruleset 中将两个 `Quality (Python …)` 检查设为必需，
并要求人工 PR 审核；工作流失败本身并不会禁止管理员直接合并。

## 来源、许可与使用边界

代码、Schema 和文档使用 [MIT](LICENSE)。贡献者拥有权利的原创数据及数据库编排使用
[CC0 1.0](LICENSE-DATA)，完整条款见 [法律文本](LICENSES/CC0-1.0.txt)。
CC0 仅适用于贡献者可处分的权利，不授予第三方隐私、肖像或商标权利。
参阅 [Creative Commons 的 CC0 说明](https://creativecommons.org/publicdomain/zero/1.0/)。

来源链接用于验证事实，**不等于复制许可**。每个来源记录 `rights.basis` 和说明：
原创事实摘录、CC0、明确兼容授权或待核验。禁止整体复制授权不明的数据集。
需署名等额外条件的内容不能直接归入本库的 CC0 数据；应先提出可兼容的许可方案，
获得维护者审核。本次初始化没有导入第三方数据集。

词库按现状提供，可能存在遗漏、歧义或过期信息。使用者需结合具体语境、来源和适用规则
评估结果；任何收录都不构成对个人或机构的指控、信誉判断或法律结论。

## 路线图

- [x] 独立数据模型、溯源、待审隔离、校验、格式化、确定性导出和 CI。
- [ ] 经人工审核的小批量中英文数据与分类规则迭代。
- [ ] 多语言、标签检索、版本化数据集和增量更新。
- [ ] 按真实需求评估精确匹配、Aho-Corasick、模糊匹配、分词与 NER。
- [ ] 按真实需求评估 REST API 和 Python / Java / Go / JavaScript SDK。

这些扩展不属于当前实现；数据不绑定某个匹配引擎或服务框架。
