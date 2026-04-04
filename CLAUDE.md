# Agent Superpowers Kit

自定义 AI coding 研发 skill 库，组合 gstack + Compound Engineering + Superpowers。

## 四种开发模式

| 模式 | 入口 | 场景 |
|------|------|------|
| 直接开发 | `/dev` | 已有功能改进或新功能，最高频 |
| 像素级还原 | `/dev` 或 `/dev-pixel` | 按 HTML 原型像素级实现 |
| 自主设计 | `/dev` 或 `/dev-design` | 从反馈到设计到开发 (0→1) |
| 排查修复 | `/dev` 或 `/dev-fix` | Bug 复现→根因分析→修复 |

统一入口 `/dev` 会自动识别模式。也可以直接调用各模式专属 skill 或阶段 skill。

## Skill routing

路由优先级：如果输入同时匹配 `/dev` 和子 skill，优先走 `/dev` 编排器。

- 完整开发流程、从头做这个功能、开始开发 → invoke dev
- 像素级还原、按原型开发、HTML 原型 → invoke dev-pixel
- 客户反馈、需要设计、从零开始、0到1 → invoke dev-design
- 修复 bug、排查问题、报错了、异常 → invoke dev-fix
- 评估想法、分析需求、这个值不值得做 → invoke dev-eval
- 制定计划、做个方案、plan this → invoke dev-plan
- 审查计划、review plan → invoke dev-review-plan
- 开始编码、写代码、implement → invoke dev-code
- 测试、QA、全面测试 → invoke dev-qa
- 准备验收、验收通过了 → invoke dev-accept
- 合并、发布、收尾、ship → invoke dev-ship
