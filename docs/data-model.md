# 数据模型 / Data model

Schema version: **1.0**. [Sensitive terms](../schemas/sensitive.schema.json) and
[named entities](../schemas/entity.schema.json) share only common metadata definitions
from [common.schema.json](../schemas/common.schema.json).
JSON Schema uses [Draft 2020-12](https://json-schema.org/draft/2020-12).
The Python validator explicitly enables format checks and resolves bundled schemas
offline; a standalone consumer must also enable `format` validation.

两个模型只共用元数据，不共享敏感属性。格式校验必须显式启用；仓库工具离线解析本地 Schema，
不请求来源网站。Schema 验证结构，不能证明来源内容、审核人身份或再利用权利属实。

## 共享字段 / Shared fields

所有下表字段均必填，除非标记为可选。字段不接受 `null`，无隐式默认值；
空别名使用 `[]`。未定义字段被拒绝，扩展放入可选的 `extensions`。
日期均为有效公历 `YYYY-MM-DD`，无时区或时间单位；更新历史由 Git 提交及 PR 保存。

Fields are required unless marked optional. `null` is not accepted, no defaults are
injected, and an empty alias list is `[]`. Unknown fields are rejected; use optional
namespaced extensions. Dates are calendar dates without time or timezone.
Git and PRs hold the change history rather than a growing history array in every record.

| 字段 / Field | 类型、约束与含义 / Type, constraints and meaning |
|---|---|
| `schema_version` | 字符串常量 `"1.0"` / String constant. |
| `id` | `st_`（敏感词）或 `ne_`（实体）+ 小写 UUID v4；全库唯一，改名或重分类不变 / Globally unique lowercase UUID v4 with family prefix; immutable. |
| `aliases` | 唯一对象数组，可空；别名适用于整条记录语义 / Unique objects, possibly empty; aliases share the record's meaning. |
| `aliases[].text` | 1–200 字符，非空白，无首尾空白和隐藏格式控制符 / Nonblank text; no surrounding whitespace or invisible formatting controls. |
| `aliases[].language` | `zh`, `zh-Hans`, `zh-Hant`, `en`，大小写固定 / Fixed supported language tags. |
| `aliases[].kind` | `alias`（别名）、`abbreviation`（简称／缩写）、`variant`（显式文字变体） / Alias, abbreviation or explicit spelling/script variant. |
| `sources` | 至少 1 个唯一来源对象 / At least one unique source object. |
| `sources[].url` | 最长 2048 字符的 HTTPS URI，不含账户密码，仅标准端口；应为可公开验证的精确页面 / Public evidence page; HTTPS on the default port, no credentials. |
| `sources[].title` | 1–500 非空白字符；真实页面标题或准确资料名称 / Actual source title or accurate description. |
| `sources[].accessed_at` | 实际访问日期，不能晚于 `updated_at` / Date checked, no later than `updated_at`. |
| `sources[].rights.basis` | `fact_reference`, `cc0`, `permission`, `unresolved`；定义见下文 / Reuse basis; see below. |
| `sources[].rights.note` | 1–2000 非空白字符，解释摘录方式或权利依据 / Explain extraction method or reuse rights. |
| `sources[].rights.evidence_url` | 可选 HTTPS URI；`cc0`、`permission` 时必填 / Optional, required for CC0 or explicit permission claims. |
| `review.status` | `pending`（待审）、`approved`（审核通过）、`deprecated`（保留但停用） / Review state. |
| `review.reviewed_by` | 可选，`approved` / `deprecated` 必填，1–100 字符；公开审核者标识 / Public reviewer handle required for reviewed states. |
| `review.reviewed_at` | 可选，已审核状态必填；在创建日期和更新日期之间 / Review date within the record's date interval. |
| `review.note` | 可选，已审核状态必填，1–2000 字符；审核结论及依据 / Decision and rationale. |
| `created_at` | 创建日期，不晚于更新日期 / Creation date, no later than update date. |
| `updated_at` | 最近一次记录修改日期；审核或停用也更新 / Last record modification date, including review or deprecation. |
| `extensions` | 可选对象；键为 `namespace:key`，值为有限 JSON 值；不覆盖核心字段 / Optional namespaced metadata; finite JSON values only, no core-field overrides. |

所有文本禁止 Unicode 控制字符（Cc）和代理字符（Cs）；名称另禁止 Cf 与 Unicode 行／段分隔符。
保留合法组合字符、变体选择符和 emoji。`extensions` 不允许 NaN、Infinity 或溢出数值，
顶层必填字段和内部类型不能用扩展字段绕过。

Text rejects Unicode control/surrogate characters. Names additionally reject format
controls and line/paragraph separators. Combining characters, variation selectors and
emoji are preserved. Non-finite values, including overflowing exponents, are rejected.
Extensions cannot bypass required fields or introduce core semantics.

### 来源权利 / Source rights

| `basis` | 含义 / Meaning |
|---|---|
| `fact_reference` | 独立核对事实并原创撰写；不复制来源表述，不批量提取数据库。不宣称原网页为 CC0。 / Independently verified facts and original wording; no protected-text copying or bulk extraction, no CC0 claim about the source. |
| `cc0` | 有明确 CC0 依据；证据链接须支持该材料的许可。 / Verified CC0 material with an applicable license reference. |
| `permission` | 权利人明确授权与本项目 CC0 再利用兼容；说明范围并链接证据。 / Explicit authorization compatible with CC0 contribution; document scope and evidence. |
| `unresolved` | 尚未核验，只允许待审与示例目录。 / Unverified, restricted to pending records and examples. |

验证器只核验字段与格式，不联网检测页面、许可有效性或 ISO 地区分配状态。
这些需要人工核验。代码检查通过不等于允许复制。

The validator checks fields and syntax, not page availability, licensing validity or
ISO region assignments. Human review must verify these facts.

## 敏感词字段 / Sensitive-term fields

| 字段 / Field | 约束与含义 / Constraints and meaning |
|---|---|
| `term` | 1–200 字符标准词形，规则同别名文本 / Canonical spelling, same text rules as aliases. |
| `language` | `zh`, `zh-Hans`, `zh-Hant`, `en`；中文写入 `zh.jsonl`，英文写入 `en.jsonl` / Primary language determines the file. |
| `sense` | 1–80 字符的小写英文 slug；区分同词不同义，例如 `synthetic-example` / Meaning discriminator, not an identity derived from spelling. |
| `assessments` | 至少 1 项；一个评估可以含多个分类和地区 / One or more contextual assessments. |
| `assessments[].regions` | 至少一个大写 ISO 3166-1 alpha-2 地区码，或单独 `001` 表示不限定地区；唯一值 / Region codes, or `001` for no regional restriction. |
| `assessments[].categories` | 至少 1 个唯一分类，枚举见下表 / One or more unique controlled categories. |
| `assessments[].risk` | `low`, `medium`, `high`，仅为该语境内的人工风险提示，无全局评分或封禁阈值 / Contextual reviewer label, not a global score or blocking threshold. |
| `assessments[].context` | 1–2000 非空白字符，说明语境、证据关联、适用与不适用情况 / Explain applicability, evidence and exclusions. |

| 分类 / Category | 用途 / Intended scope |
|---|---|
| `profanity` | 粗俗表达 / Profanity |
| `harassment` | 侮辱或骚扰性用法 / Harassing or abusive usage |
| `hate` | 有依据的仇恨表达语境 / Evidence-backed hateful usage |
| `sexual` | 性相关内容语境 / Sexual-content contexts |
| `violence` | 暴力相关内容语境 / Violence-related contexts |
| `self_harm` | 自伤相关内容语境 / Self-harm-related contexts |
| `regulated_goods` | 特定地区受监管物品语境；需说明地区依据 / Region-specific regulated-goods contexts |
| `context_dependent` | 需要特殊处理且证据足够的其他语境；不能代替说明 / Other evidenced contexts requiring special handling |

`low` 表示在已述语境中建议提示；`medium` 表示建议进一步检查上下文；
`high` 表示在已述语境中建议优先人工复核。它们都是数据标签，不要求自动执法或封禁。
分类不能直接赋予实体。新增分类先修改 Schema、文档、测试并经 PR 审核。

`low` suggests an advisory signal in the described context; `medium` suggests further
context checks; `high` suggests prioritizing human review. These are dataset labels,
not enforcement instructions. Never attach categories automatically to entities.
New categories require a schema, documentation and test change through review.

同一词形、基础语言（`zh-Hans` / `zh-Hant` 归入 `zh`）及 `sense` 只能有一条记录。
同义词的分类与地区差异放在同一条记录的评估数组里。每个地区在一条记录中只能出现一次；
全球 `001` 不和其他地区混用，不实现隐式地区覆盖。不同语义另建记录及 `sense`，
上下文须解释差异。别名若只适用另一语义，应放入另一记录。

One record per spelling, base language and sense. Combine categories and regional
differences in its assessment array. A region appears in at most one assessment;
global `001` cannot be combined with regional overrides. Different meanings need
separate senses and explanatory context. An alias with a different meaning belongs
to the appropriate separate record.

## 实体字段 / Entity fields

| 字段 / Field | 约束与含义 / Constraints and meaning |
|---|---|
| `entity_type` | `person` → `people.jsonl`; `company` → `companies.jsonl`; `organization` → `organizations.jsonl`. |
| `names` | 对象，允许 `zh` 和 `en`，至少一个；各名称 1–200 字符；未知译名省略，不填 `null` / At least one verified Chinese or English name. |
| `disambiguation` | 1–1000 非空白字符；简述公开身份、同名区分依据，不能带入私人数据或负面推断 / Public identity context distinguishing homonyms. |
| `regions` | 名称使用范围，至少一个地区码或 `001`；不是国籍、注册地或住所 / Name-usage scope, not nationality, incorporation or residence. |

中文主名称可采用一种已核验字形，其他简繁体字形放入显式别名。缩写也在 `aliases`
中存储，避免维护多个重复列表。实体不含 `term`、`assessments`、敏感分类或风险字段。

Choose a verified Chinese spelling as the primary name; put other verified script
forms in aliases. Abbreviations use the same alias list to avoid redundant fields.
Entity records have no term assessments, sensitivity categories or risk fields.

## 重复与 Unicode / Duplicates and Unicode

1. 相同 ID 是错误，覆盖正式库与待审区；重命名保留 ID。
   / Duplicate IDs fail validation, including across production and pending stages.
2. 确定重复：敏感词比较 `(基础语言, NFC(term), sense)`；实体比较
   `(entity_type, NFC(names), NFC(disambiguation))`。完全相同的身份描述应合并；
   有依据的同名实体必须写出区别。
   / Confirmed keys use canonical equivalence; genuinely distinct homonyms need disambiguation.
3. 每条记录中主名称和别名按基础语言与 NFC 比较，不允许重复。
   / A record cannot repeat a primary name or alias under the same base language.
4. 同一家族不同记录的名称／别名使用 NFKC + casefold 发现冲突，输出警告及两条位置，
   从不删除或合并。不同语义、同名实体和有区别的兼容字符都可能合理。
   / Lossy comparison discovers review candidates only; it never rewrites or merges data.
5. 不自动做简繁转换、拼音、同音、空白／标点清洗、模糊匹配或跨家族比较。
   / No automatic Chinese conversion, transliteration, fuzzy matching or cross-family inference.

NFC 用于规范等价比较，不修改源字符；如需区分规范等价字形的特殊研究语境，
应提出模型变更，不能靠修改 `sense` 来绕过重复检查。NFKC 的 `①` 与 `1` 等
兼容形式只提示；变体选择符保持区别。

NFC is a canonical-equivalence comparison policy, not a text rewrite. A use case that
needs distinct canonically equivalent glyph forms requires a model discussion, not an
invented sense to evade checks. Compatibility forms such as `①` and `1` only warn.
Variation selectors remain distinct.

## 生命周期与导出 / Lifecycle and exports

- `pending/`: 只允许 `pending`，不构建；同样验证 Schema 与重复。
- `data/`: 只允许 `approved`、`deprecated`，禁止未核验权利。
- `examples/data/`: 仅虚构 `pending`；单独校验，永不构建。
- `approved` 才导出；修改内容、审核或停用时更新日期，PR/Git 留存理由。

The pending stage accepts pending records only; production accepts approved or
deprecated records with resolved rights. Examples remain synthetic and pending.
Only approved production records are exported. Changes and decisions live in Git/PR history.

JSON 导出保留完整记录，按 ID 排序；TXT 包含标准词和显式别名，按别名自身语言路由，
只按原字符串去重并按码点排序。同一候选词属于多个语义时 TXT 仍只有一个词形，
因此应用必须回查 JSON。空库产生空 TXT、`[]` JSON 与零计数清单。
每次构建重写已知产物，不删除输出目录中无关文件；文件逐个原子替换，整个目录不是事务。
构建过程先完整校验，数据错误时不改动已有产物。

JSON exports retain complete records sorted by ID. TXT routes explicit aliases by
their own language, deduplicates exact strings and sorts by code point. A spelling
shared by several meanings appears once, so applications must consult JSON for context.
Empty datasets produce empty TXT, JSON arrays and zero counts. Builds replace known
artifacts and preserve unrelated files. Replacement is atomic per file, not for the
whole directory; data-validation failures leave existing output unchanged.

新增实体类型、语言、字段含义或不兼容约束需要版本说明及迁移计划；不能静默重新解释旧数据。
当前预留 `schema_version`、稳定 ID、命名空间扩展及 Git 历史，不提前实现 API、索引或 SDK。

New entity types, languages or incompatible meanings require documented versioning
and migration rather than silent reinterpretation. Stable IDs, schema versions,
namespaced extensions and Git history leave room for future tooling without implementing it now.
