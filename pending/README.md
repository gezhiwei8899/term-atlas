# Proposals / 待审核数据

Use the same five-file layout and schemas as `data/`, with `review.status = "pending"`.
Sources are required; `rights.basis = "unresolved"` is allowed while permissions are
being checked. Validation checks this directory; builds never read it.

Submit new records here. A maintainer verifies evidence and rights, moves the record
to `data/` preserving its ID, and records the review in the PR. Do not keep duplicate
copies. To reconsider an existing entry, move it back here using the same ID, or
request a correction without creating a shadow record.

本目录沿用正式数据的五文件布局和 Schema，仅允许 `pending` 状态。必须填写
来源；权利未核实时可用 `unresolved`。校验包含本目录，构建始终排除本目录。
审核通过后保留原 ID 移入 `data/` 并记录审核依据，不保留重复副本。已有词条
重审应移回本目录或提交纠错申请，不得新建相同 ID 的影子记录。
