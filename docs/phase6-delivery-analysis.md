# Phase 6: 交付 — 最佳技能组合分析

## Phase 6 的关键洞察：这是一条完整的交付流水线，不是单个技能选择

Phase 6 的技能按时间顺序排列，形成从"代码完成"到"生产验证"的完整链路：

```
代码完成
    |
    v
[resolve-pr-feedback]   处理 PR 评审反馈
    |
    v
[git-commit-push-pr]    提交 + 推送 + PR        <-- CE 轻量路径
[gstack/ship]           完整发布流程              <-- gstack 重量路径
    |
    +-- [feature-video]  录屏嵌入 PR（可选，并行）
    |
    v
[document-release]       文档同步
    |
    v
[land-and-deploy]        合并 + 部署 + 金丝雀验证
    |
    v
生产环境已验证
```

---

## 技能对比

### 提交与 PR 创建（两条路径）

| 维度 | `git-commit-push-pr` (CE) | `gstack/ship` (gstack) | `finishing-a-development-branch` (SP) |
|---|---|---|---|
| **定位** | 一步到位：代码 -> PR | 完整发布流程：测试->审查->版本->PR | 分支收尾：测试 -> 4 选项 |
| **测试** | 不运行测试 | **并行测试 + 失败分诊 + 覆盖审计** | 运行测试（通过才继续） |
| **代码审查** | 不做审查 | **内置预着陆审查 + 对抗审查** | 不做审查 |
| **版本管理** | 无 | **自动版本号 + CHANGELOG** | 无 |
| **提交策略** | 按文件分组逻辑提交 | **可二分提交（按依赖排序）** | 单次提交 |
| **PR 描述** | **自适应深度**（小改动简短，大改动完整） | 完整（覆盖图 + 审查发现 + 测试结果） | 基础模板 |
| **计划合规** | 无 | **计划完成度审计 + 范围漂移检测** | 无 |
| **适用场景** | 日常提交、小功能、快速 PR | 重要功能发布、需要质量门的交付 | SP 流程收尾 |

### 关键差异：`git-commit-push-pr` vs `gstack/ship`

```
git-commit-push-pr:
  代码变更 -> 提交 -> 推送 -> PR
  (假设 ce:review 已经在 ce:work Phase 3 完成)

gstack/ship:
  代码变更 -> 合并基线 -> 测试 -> 覆盖审计 -> 计划审计 ->
  预着陆审查 -> 对抗审查 -> 版本号 -> CHANGELOG ->
  可二分提交 -> 验证门 -> 推送 -> PR
  (自带完整的质量门，不依赖上游审查)
```

**两者不冲突 — 取决于上游是否已有质量保障：**
- 如果上游走的是 `ce:work`（内置 ce:review），用 `git-commit-push-pr` 就够
- 如果上游没有审查机制，`gstack/ship` 提供完整的质量门

---

## 最佳组合：两条路径

### 路径 A：CE 流水线（推荐，已有上游质量保障）

```
ce:work (Phase 4, 内置 ce:review)
    |
    v  代码已审查、测试已通过
    |
    +-- resolve-pr-feedback (如果 PR 已存在且有评论)
    |
    v
git-commit-push-pr
    |  自适应 PR 描述
    |  逻辑分组提交
    |  自动检测已有 PR 并更新
    |
    +-- feature-video (可选，并行)
    |
    v
land-and-deploy
    |  合并 -> 部署 -> 金丝雀验证
    |
    v
document-release (可选)
```

**适用于**：日常功能开发，已经走了 ce:brainstorm -> ce:plan -> ce:work -> ce:review 全流程。

### 路径 B：gstack 全流程（独立质量保障）

```
代码完成（可能没走 ce:review）
    |
    v
gstack/ship
    |  Step 1:   预飞检查 + Review Readiness Dashboard
    |  Step 2:   合并基线分支
    |  Step 3:   测试 + 覆盖审计（目标 80%，最低 60%）
    |  Step 3.45: 计划完成度审计
    |  Step 3.5: 预着陆代码审查（自动修复 + 人工判断）
    |  Step 3.8: 对抗审查（Claude + Codex）
    |  Step 4:   版本号（MICRO/PATCH 自动，MINOR/MAJOR 询问）
    |  Step 4.5: CHANGELOG（从 diff 自动生成）
    |  Step 6:   可二分提交
    |  Step 7-8: 推送 + 创建 PR
    |
    +-- feature-video (可选)
    |
    v
document-release
    |  全文档审计 + 自动更新 + 语气润色
    |
    v
land-and-deploy
    |  CI -> 合并前就绪报告 -> 合并 -> 部署 -> 金丝雀
    |
    v
生产环境已验证
```

**适用于**：重要发布、没有走 CE 流水线的代码、需要版本号和 CHANGELOG 的项目。

---

## `gstack/ship` 的独特价值（CE 流水线没有的）

| 能力 | CE 流水线 | gstack/ship |
|---|---|---|
| 版本号管理 | 无 | MICRO/PATCH 自动，MINOR/MAJOR 询问 |
| CHANGELOG | 无 | 从 diff + commits 自动生成，"卖点"风格 |
| 测试覆盖审计 | ce:work 有 Test Discovery | **ASCII 覆盖图 + 60%/80% 门 + 自动生成缺失测试** |
| 计划完成度审计 | ce:review 有 R-ID 追溯 | 逐条对比 diff vs 计划项（DONE/PARTIAL/NOT DONE） |
| 可二分提交 | git-commit-push-pr 按文件分组 | **按依赖排序的可二分提交**（每个可独立回滚） |
| 对抗审查 | ce:review 有 adversarial-reviewer | Claude 对抗 + **Codex 对抗**（独立 AI 二审） |
| Review Readiness Dashboard | 无 | 检查所有评审状态，7 天过期 |

---

## `land-and-deploy` 的关键设计

```
Step 3.5: 合并前就绪报告（最后的人工关卡）

  +-----------------------------------------------------+
  | PRE-MERGE READINESS REPORT                           |
  +-----------------------------------------------------+
  | Reviews:  Eng ✅ CLEARED (2h ago)                    |
  |           CEO ✅ DONE (1d ago)                       |
  | Tests:    ✅ 47/47 pass                              |
  | E2E:      ✅ 3/3 pass (today)                        |
  | Docs:     ⚠️ CHANGELOG not updated                   |
  | PR Body:  ✅ Matches commits                         |
  +-----------------------------------------------------+
  | BLOCKERS: None                                       |
  | WARNINGS: Document-release not run                   |
  +-----------------------------------------------------+

  Proceed with merge? [Yes / No / Run document-release first]
```

**金丝雀验证按 diff 范围分级：**

| diff 类型 | 验证深度 |
|---|---|
| Docs only | 跳过 |
| Config only | Smoke（200 状态码） |
| Backend only | 控制台错误 + 性能检查 |
| Frontend（任何） | 全量：URL + 控制台 + 性能 + 文本 + 截图 |

**每个失败点都提供回滚选项。**

---

## PR 反馈处理：`resolve-pr-feedback`

```
PR 有未解决的评审评论
    |
    v
resolve-pr-feedback
    |
    +-- 获取所有未解决线程（GraphQL）
    |
    +-- 分诊：new vs already-handled
    |
    +-- 聚类分析（>=3 项时）: 按主题/文件分组
    |
    +-- 并行派发 pr-comment-resolver Agent（每批 4 个）
    |     每个 Agent 返回: fixed / fixed-differently / replied / not-addressing / needs-human
    |
    +-- 提交代码修复 + 回复并解决线程（GraphQL）
    |
    +-- 验证：重新获取线程，确认已清空
    |     最多循环 3 次
    |
    v
  "Resolved N of M new items on PR #NUMBER"
  needs-human 项留给用户决定
```

---

## `feature-video` 的独特价值

```
feature-video:
  1. 从 PR 变更文件推断受影响路由
  2. 规划镜头列表（开场 -> 导航 -> 功能演示 -> 边界情况 -> 成功状态）
  3. 用 agent-browser 逐帧截图
  4. ffmpeg 拼接为 MP4（H.264, 0.5fps）
  5. 上传到 GitHub（通过浏览器自动化操作 PR 页面）
  6. 嵌入 PR 描述的 ## Demo 部分
```

**在 lfg/slfg 流水线中是最后一步**，让 PR 审查者不用本地运行就能看到功能效果。

---

## 按场景选择

| 场景 | 推荐路径 | 原因 |
|---|---|---|
| 日常功能（已走 CE 流程） | `git-commit-push-pr` -> `land-and-deploy` | ce:review 已做审查，不需要重复 |
| 重要发布（需要版本号） | `gstack/ship` -> `document-release` -> `land-and-deploy` | 完整质量门 + 版本管理 |
| 有 UI 变更 | 任一路径 + `feature-video` | PR 中嵌入录屏 |
| PR 有评审反馈 | `resolve-pr-feedback` -> 继续交付 | 先处理反馈再发布 |
| 开源项目发布 | `gstack/ship` + `document-release` | CHANGELOG + 文档对用户重要 |
| 快速修复 | `git-commit-push-pr` -> `land-and-deploy` | 最短路径 |
| 首次部署 | `land-and-deploy`（自动 dry-run） | 自动检测平台 + 验证命令 |

---

## 六阶段文档/产出链路

```
Phase 1        Phase 2        Phase 3        Phase 4        Phase 5        Phase 6
需求文档       DESIGN.md      实施计划        代码实现       审查裁决       交付产出
R1,R2,R3  --> Token/色值 --> Req Trace --> ce:work    --> ce:review --> git-commit-push-pr
                                           增量提交       safe_auto      或 gstack/ship
                                                          修复            |
                                                                         +-> PR (GitHub)
                                                                         +-> VERSION
                                                                         +-> CHANGELOG
                                                                         +-> 文档更新
                                                                         +-> 金丝雀验证
                                                                         |
                                                                         v
                                                                     生产环境
```

---

## 一句话结论

**Phase 6 有两条互补路径：CE 路径（`git-commit-push-pr` -> `land-and-deploy`）适合已有上游质量保障的日常交付；gstack 路径（`ship` -> `document-release` -> `land-and-deploy`）适合需要完整质量门的重要发布。两者共享 `land-and-deploy` 作为最终交付器（合并->部署->金丝雀），以及 `resolve-pr-feedback` 处理 PR 评审反馈。`gstack/ship` 的独特价值是版本管理、CHANGELOG、覆盖审计和可二分提交 — 这些 CE 流水线不提供。**
