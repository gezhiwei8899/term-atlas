# Synthetic examples / 虚构示例

Every record in `data/` **under this examples directory** is synthetic. The reserved
`example.invalid` URLs intentionally do not resolve and are not evidence about real
people, companies or words. These examples have `pending` status and unresolved
source rights to demonstrate a proposal, not a reviewed production entry.

Run `python scripts/validate.py --examples` from the repository root. Examples are
never included by `scripts/build.py`. Do not move these examples into the production
`data/` directory. Generate a new UUID when preparing a real proposal.

本目录中的数据全为虚构，`example.invalid` 是有意不可访问的示例域名，不是
真实资料来源。示例演示待审提案；请勿将它们移入正式数据或用于实际敏感判断。
`read_exports.py` 演示读取构建产物，不实现匹配或封禁逻辑。
