# Agent Superpowers Kit

自定义 AI coding 研发 skill 库，组合 gstack + Compound Engineering + Superpowers。

## 直接开发模式

最高频的工作流：已有功能改进或新功能添加。

完整流程: `/dev` (编排器)
独立调用: `/dev-eval` → `/dev-plan` → `/dev-review-plan` → `/dev-code` → `/dev-qa` → `/dev-accept` → `/dev-ship`

## Skill routing

当用户的请求匹配以下场景时，调用对应 skill：

- 评估想法、分析需求、这个值不值得做 → invoke dev-eval
- 制定计划、做个方案、plan this → invoke dev-plan
- 审查计划、review plan → invoke dev-review-plan
- 开始编码、写代码、implement → invoke dev-code
- 测试、QA、全面测试 → invoke dev-qa
- 验收、创建 PR → invoke dev-accept
- 合并、发布、收尾、ship → invoke dev-ship
- 完整开发流程、从头做这个功能 → invoke dev
