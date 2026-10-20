# 治理、来源与许可 / Governance, sources and licensing

## 收录与人工审核 / Admission and review

TermAtlas 记录有依据的词汇语境和公开知名实体。不得因为人物、企业或组织的身份、
观点或立场自动将其标记为敏感，更不得由“被收录”推导违法、危险或其他负面属性。
所有公开数据应尽量依赖可核验的一手资料；必要时交叉核对多份可靠公开来源。

The collections describe evidenced linguistic contexts and notable public entities.
Identity, opinions or positions never automatically establish sensitivity. Inclusion
does not imply wrongdoing, danger or any negative attribute. Prefer verifiable primary
references and corroborate them with other reliable public sources where needed.

新数据先进入 `pending/`。审核包括名称与别名准确性、上下文、地区、歧义、私人信息、
来源的实际内容以及再利用权利。CI 只辅助发现错误；审核人需在 PR 中给出结论，
通过后才写入 `approved` 和审核元数据。CI 无法核实审核人的真实身份或自行授予许可。
作者之外的审核者有助于避免自证。

New records enter the pending stage. Review covers names, aliases, context, regions,
ambiguity, private information, actual source content and reuse rights. CI assists this
review; it cannot authenticate reviewers or grant rights. Record a human decision in the
PR before approval. Independent review is preferred over an author's self-approval.

## 纠错、删除与争议 / Corrections, removals and disputes

1. 使用纠错／删除 Issue 模板，以 ID 定位，提供可公开的理由和证据；也可直接提交修复 PR。
   / Identify the record, explain the issue and provide public evidence through an Issue or PR.
2. 维护者核对报告，对可信的事实、隐私或权利问题，先通过 PR 将记录移回待审区或移除，
   使后续构建停止导出，再调查。
   / For credible factual, privacy or rights concerns, exclude the record from future
   builds through a reviewed move or removal while investigating.
3. 根据证据修正、停用或删除，记录公开可披露的理由。停用仅适合可以合法安全保留的数据；
   无权使用或私人数据不能仅靠 `deprecated` 留在公开源文件中。
   / Correct, deprecate or remove with a public rationale where appropriate. Deprecation
   is unsuitable for retaining private or unauthorized material in public source files.
4. 允许凭新证据复审；争议未解决前不将其当作已核实数据发布。
   / New evidence can reopen review; unresolved claims do not become approved data.

不要在公开 Issue/PR 重复私人信息或上传证件。敏感报告可通过仓库的私人漏洞报告入口
**在该功能已启用时**联系维护者；否则只提交不含私人内容的记录 ID，申请私下联系渠道。
初始化不假定该功能已启用，也不虚构联系邮箱。

Do not post private details or identity documents in public issues. Use GitHub private
vulnerability reporting **if the repository has enabled it**; otherwise post only a
non-sensitive record ID and request a private contact route. This initialization does
not assume the feature is enabled or publish an invented contact address.

删除当前文件不能自动删除 Git 历史、旧导出、Fork 或第三方副本。需要清除历史时，
由仓库所有者单独评估并授权相应操作；工具不会自动重写历史或 force push。
合理记录撤回决定，通知受影响的数据使用者需另行安排。

Removing a current file cannot erase Git history, earlier exports, forks or third-party
copies. Historical removal needs a separate owner-authorized response. These tools do
not rewrite history or force-push. Record the withdrawal where appropriate; notification
of downstream consumers requires a separate operational process.

## 代码与数据许可 / Code and data licensing

- 代码、Schema、文档：MIT，见 [LICENSE](../LICENSE)。
- 原创数据及编排：贡献者在可处分权利范围内按 CC0 1.0 提供，见
  [LICENSE-DATA](../LICENSE-DATA) 与 [完整文本](../LICENSES/CC0-1.0.txt)。
- 本次没有第三方数据导入。示例为项目原创虚构记录，示例 URL 不是引用证据。

Code, schemas and documentation use MIT. Original data and database arrangement use
CC0 only to the extent contributors hold the relevant rights. No third-party dataset
is imported here. Synthetic examples are original illustrations, not factual claims.

来源核验和授权核验是两项独立工作。官方网页可能是可靠的事实来源，但不因此拥有开放许可。
`fact_reference` 只用于核对事实并原创表达；不得用于掩盖复制原文、批量抽取或绕过数据库权利。
`cc0` 和 `permission` 必须附适用该材料的授权证据，并人工检查适用范围。
授权不清楚时标记 `unresolved` 并留在待审区；不要先发布再补证据。

Evidence quality and permission are separate questions. An official website can verify
a fact without licensing its content for copying. `fact_reference` covers independently
written factual records, not copying passages, bulk extraction or ignoring database rights.
CC0 and permission claims need applicable evidence and human scope checks. Keep unclear
rights unresolved and pending rather than publishing first.

CC BY 4.0 内容有署名等条件，本项目不能把它直接改称 CC0。若未来需要兼容此类来源，
先讨论单独许可的数据分区、署名与下游要求，再修改模型与构建流程。当前不建立这种分区。
不要以来源是公开网站、搜索可见或数据量小为由推定获得再许可权。

CC BY 4.0 carries conditions such as attribution and cannot simply be relabeled CC0.
Supporting such sources would require a separately reviewed licensing arrangement,
attribution and downstream handling before changing schemas or exports. No such partition
exists yet. Public availability, search visibility or a small extraction size does not
establish relicensing rights.

CC0 不处理所有权利，不能授权第三方隐私、肖像或商标使用。官方解释见
[Creative Commons CC0](https://creativecommons.org/publicdomain/zero/1.0/)；
项目随附的标准法律文本取自
[SPDX license-list-data](https://github.com/spdx/license-list-data/blob/main/text/CC0-1.0.txt)。

CC0 does not clear every right, including third-party privacy, publicity and trademarks.
The linked Creative Commons explanation and bundled standard legal text define its scope.

## 合并门禁 / Merge controls

工作流使用 `pull_request` 与 `main` 推送事件、只读 `contents` 权限，固定 Actions 提交 SHA，
不为 Fork 执行授予写权限或注入仓库秘密。Python 3.11 / 3.14 分别运行静态检查、数据校验、
测试与双次构建比较。

CI runs on pull requests and main-branch pushes with read-only contents permission and
pinned Action commits. Forked code receives no workflow write permission or repository
secrets. Python 3.11 / 3.14 jobs run static checks, validation, tests and repeat-build comparison.

仓库所有者需要在 GitHub 分支保护／ruleset 中启用：

- PR 审核（建议至少一名非作者审核者）。
- 必需状态 `Quality (Python 3.11)` 与 `Quality (Python 3.14)`。
- 对数据、Schema、工具及许可变更的人工作业要求。

The owner must configure required PR reviews and both named quality checks in branch
protection or a ruleset. These are repository settings, not properties a workflow file
can enforce by itself. This initialization does not change repository access controls.
