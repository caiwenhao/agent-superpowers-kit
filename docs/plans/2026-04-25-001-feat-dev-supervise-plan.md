---
title: "feat: Add dev-supervise meta-skill for skill self-evolution"
type: feat
status: active
date: 2026-04-25
origin: docs/superpowers/specs/2026-04-20-dev-supervise-design.md
---

# feat: Add dev-supervise meta-skill for skill self-evolution

## Overview

新增 `dev-supervise` 元 skill，为 `dev:*` skill 库提供三层自我监督能力：L1 实时拦截（hook 脚本）、L2 会话复盘（信号提取）、L3 历史扫描（聚合报告）。目标是让 skill 库在使用中积累改进证据，驱动自我进化。

## Problem Frame

`dev:*` skill 库缺乏运行期反馈机制。iron law 违规（如在 main 分支直接编码、Phase 4 中执行 git commit）只能靠人工发现；用户纠正（回滚、打断、重做）散落在 session transcript 中无人收集；跨 session 的 skill 质量趋势无法量化。`dev-supervise` 填补这个缺口。(see origin: docs/superpowers/specs/2026-04-20-dev-supervise-design.md §一)

## Requirements Trace

- R1. L1 实时拦截：PreToolUse/PostToolUse hook 拦截铁律 6（工作区）和铁律 7（提交触发）违规，warn 铁律 4（证据先行）
- R2. L1 事件日志：拦截/警告事件追加到 `~/.claude/state/supervise-incidents.jsonl`
- R3. L2 信号提取：从 session transcript 提取四类结构信号（回滚、打断、重做、L1 事件）
- R4. L2 输出：按 skill 分组追加到 `docs/supervise/feedback/<skill-name>.md`
- R5. L2 集成：作为 `dev-learn` 的 `skill-self-review` 子步运行
- R6. L3 历史扫描：枚举 transcript、按 repo 过滤、聚合排行、输出结构化改进建议
- R7. L3 命令入口：`/dev:supervise [--since 14d] [--scope project|global]`
- R8. Codex 退化：每个 `dev-*/SKILL.md` 顶部追加 `<SUPERVISE-CHECK>` 自检段
- R9. Phase 推断：L1 从 transcript 倒序查找最近 Skill 调用推断当前 phase；不可用时降级为仅工作区/提交规则

## Scope Boundaries

- 不进入 `dev-flow` 自动编排
- 不自动 patch SKILL.md（仅累积证据，改进由人工落地）
- 首版仅支持 Claude Code transcript 格式，Codex 留 TODO
- 不做语义/情感分析，仅提取结构信号
- L1 hook 注册为手动步骤（文档化），不自动修改 settings.json

## Context & Research

### Relevant Code and Patterns

- Hook 契约：Claude Code PreToolUse 接收 `{"tool_name":"...","tool_input":{...}}` JSON stdin，返回 `{"permissionDecision":"deny|ask","message":"..."}` 或 `{}` 放行
- Hook 注册：`.claude/settings.json` 的 `hooks.PreToolUse[].matcher` 支持 `"Bash|Write|Edit"` 管道语法
- Transcript 格式：`~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`，NDJSON，`type: "user"|"assistant"`，tool_use 在 assistant message 的 `content[].type=="tool_use"` 中
- CE transcript 解析：`compound-engineering-plugin/.../extract-metadata.py` 提供平台检测（前 10 行）、`--cwd-filter` repo 过滤、tail-seek 末尾时间戳
- Skill 结构：`dev-learn/SKILL.md` 和 `dev-doctor/SKILL.md` 是最近的 utility skill 参考
- 环境变量：hook 上下文暴露 `CLAUDE_PROJECT_DIR`、`CLAUDE_SKILL_DIR`、`CLAUDE_PLUGIN_ROOT`

### Institutional Learnings

- gstack `freeze`/`careful` 是生产级 hook 实现参考（bash），`dev-supervise` 选 Python 因为需要 JSONL 解析
- `dev-init` 明确不碰 `.claude/settings.json`，L1 hook 注册是 `dev-supervise` 自己的职责
- CE `extract-skeleton.py` 的 framework tag 剥离（`<system-reminder>` 等）对 L2 信号提取有参考价值，避免误报

## Key Technical Decisions

- **L1 用 Python 而非 bash**：需要解析 JSONL transcript 做 phase 推断，Python 的 json 模块比 bash sed/grep 可靠（see origin §三）
- **Phase 推断读 transcript 而非文件标记**：避免残留、并发、竞态问题（see origin §三 Phase 判定）
- **L2 信号为结构信号而非语义匹配**：回滚=Edit 反向、打断=用户消息插入工具序列中间、重做=同文件短时间内改≥3次。不做正则/关键词匹配，降低误报（see origin §四）
- **L3 project scope 默认，global 显式指定**：避免跨 repo 数据泄漏（see origin §五）
- **不自动 patch SKILL.md**：抬高门槛，避免 skill 自我污染（see origin §七）
- **L1 hook 手动注册**：提供文档化安装步骤，用户执行 `update-config` 或手动编辑 settings.json
- **Skill→Phase 映射表**：L1 phase 推断使用固定映射：`dev-discover`→1, `dev-design`→2, `dev-plan`→3, `dev-code`→4, `dev-verify`→5, `dev-ship`→6, `dev-learn`→7, `dev-flow`→"orchestrator"（不限制）。`ce:*`/`gstack-*`/`superpowers:*` 不直接映射 phase，取最近的 `dev-*` 调用。此映射表作为 Python dict 硬编码在 `iron_law_guard.py` 中，L3 `scan_history.py` import 复用

## Open Questions

### Resolved During Planning

- **L2 在 dev-learn 中的执行位置**：在所有 Route (A-F) 之前运行。理由：先收集本 session 信号，再执行知识捕获，信号数据可供后续 Route 参考
- **L1 hook 注册方式**：手动注册（文档化步骤）。理由：`dev-init` 不碰 settings.json 是既有边界，`dev-supervise` 遵循同样原则，避免意外修改用户配置

### Deferred to Implementation

- **Transcript 路径发现的具体降级逻辑**：hook 上下文是否暴露 session id 需要实际测试确认
- **CE extract-metadata.py 的复用程度**：是直接 import 还是提取核心逻辑重写，取决于实际依赖链

## High-Level Technical Design

> *This illustrates the intended approach and is directional guidance for review, not implementation specification. The implementing agent should treat it as context, not code to reproduce.*

```mermaid
graph TD
    subgraph "L1 实时拦截 (hook)"
        A[PreToolUse: Bash|Write|Edit] --> B{规则匹配}
        B -->|铁律6: main+非worktree| C[DENY: 创建 worktree]
        B -->|铁律7: commit+非ship| D[DENY: 用 /dev:ship]
        B -->|无匹配| E[ALLOW]
        F[PostToolUse: Bash] --> G{铁律4: 断言无证据?}
        G -->|是| H[WARN + 记录 incidents]
        G -->|否| E
    end

    subgraph "L2 会话复盘 (dev-learn 子步)"
        I[Session transcript] --> J[extract_signals.py]
        J --> K[四类信号: 回滚/打断/重做/L1事件]
        K --> L[docs/supervise/feedback/skill.md]
    end

    subgraph "L3 历史扫描 (/dev:supervise)"
        M[枚举 sessions] --> N[按 repo 过滤]
        N --> O[批量 L2 信号提取]
        O --> P[按 skill+信号 聚合排行]
        P --> Q[结构化改进建议报告]
    end
```

## Implementation Units

- [x] **Unit 1: L1 iron_law_guard.py + hook 注册文档**

**Goal:** 实现 PreToolUse/PostToolUse hook 脚本，拦截铁律 6（工作区）和铁律 7（提交触发），warn 铁律 4（证据先行），并记录事件日志。

**Requirements:** R1, R2, R9

**Dependencies:** None

**Files:**
- Create: `scripts/supervise/iron_law_guard.py`
- Create: `scripts/supervise/__init__.py`
- Create: `docs/supervise/README.md`
- Test: 无独立测试文件（hook 脚本通过手动 echo JSON | python 验证）

**Approach:**
- 单一 Python 脚本同时处理 PreToolUse 和 PostToolUse，通过环境变量或 stdin JSON 的 `tool_name` 区分
- PreToolUse 路径：解析 stdin JSON，提取 `tool_input.command`（Bash）或文件路径（Write/Edit），匹配规则表
- PostToolUse 路径：检查最近 assistant 文本是否含断言关键词，且最近 N=10 步无测试命令
- Phase 推断：读 `CLAUDE_PROJECT_DIR` 定位 transcript，倒序查找最近 `Skill` tool_use，提取 skill 名映射到 phase；不可用时跳过 phase 相关检查
- 事件日志追加到 `~/.claude/state/supervise-incidents.jsonl`，确保目录存在
- `docs/supervise/README.md` 包含 hook 注册步骤（settings.json 配置示例）

**Patterns to follow:**
- gstack `check-careful.sh` 的 stdin JSON 契约和 permissionDecision 输出格式（Python 等价）
- CE `extract-metadata.py` 的 transcript 读取模式

**Test scenarios:**
- Happy path: echo `{"tool_name":"Bash","tool_input":{"command":"git commit -m test"}}` | python iron_law_guard.py → 输出 deny JSON（铁律 7，非 dev-ship phase）
- Happy path: echo `{"tool_name":"Bash","tool_input":{"command":"ls -la"}}` | python iron_law_guard.py → 输出 `{}`（放行）
- Happy path: 在 main 分支 + 非 worktree 路径下，Write/Edit 工具 → deny（铁律 6）
- Happy path: Phase 推断命中 `dev-ship` 时，`git commit` 命令 → 输出 `{}`（铁律 7 豁免）
- Happy path: Phase 推断命中 `dev-code` 时，`git push` 命令 → 输出 deny JSON（铁律 7 拦截）
- Edge case: `CLAUDE_PROJECT_DIR` 未设置 → 跳过 phase 推断，仅执行工作区/提交规则（铁律 7 默认拦截 commit/push）
- Edge case: transcript 文件不存在或为空 → 降级为无 phase 信息
- Edge case: `git commit --amend` 和 `git push --force` 也应匹配铁律 7
- Edge case: transcript 中最近 Skill 调用为 `ce:work`（非 dev-* 前缀）→ 向上查找最近的 `dev-*` 调用
- Error path: stdin 非 JSON → 静默放行（`{}`），不阻断用户工作

**Verification:**
- 手动 echo 各规则触发场景的 JSON，确认输出正确的 permissionDecision
- 在 worktree 中和 main 分支分别测试铁律 6
- 确认 incidents.jsonl 正确追加事件记录

- [x] **Unit 2: L2 extract_signals.py 信号提取核心**

**Goal:** 实现从单个 session transcript 提取四类结构信号（回滚、打断、重做、L1 事件）的 Python 脚本，供 L2 和 L3 复用。

**Requirements:** R3

**Dependencies:** Unit 1（读取 L1 事件日志格式）

**Files:**
- Create: `scripts/supervise/extract_signals.py`
- Test: 无独立测试文件（通过构造 mock transcript JSONL 验证）

**Approach:**
- 输入：单个 transcript JSONL 文件路径
- 输出：结构化信号列表（JSON stdout），每条含 `{signal_type, evidence, skill, timestamp}`
- 核心函数 `extract_signals(transcript_path: str, session_id: str | None = None) -> list[dict]` 供 L3 直接 import；CLI 入口 `if __name__ == "__main__"` 接受文件路径参数，输出 JSON 到 stdout
- 回滚检测：遍历 assistant 消息，找到 Edit tool_use 后紧跟用户消息再紧跟 assistant Edit（diff 反向或重写同一文件关键段）
- 打断检测：用户消息插入在 assistant 连续 tool_use 序列中间（非自然轮次结束）
- 重做检测：同一文件在 10 分钟窗口内被 assistant Edit/Write ≥3 次
- L1 事件：读 `~/.claude/state/supervise-incidents.jsonl`，按 session id 过滤
- Skill 归属：每个信号关联最近的 Skill tool_use 调用名
- 剥离 framework tags（`<system-reminder>` 等）避免误报

**Patterns to follow:**
- CE `extract-metadata.py` 的 JSONL 逐行解析和平台检测
- CE `extract-skeleton.py` 的 framework tag 剥离正则

**Test scenarios:**
- Happy path: 构造含 Edit→用户纠正→反向 Edit 的 transcript → 检测到回滚信号
- Happy path: 构造含用户消息插入连续 tool_use 中间的 transcript → 检测到打断信号
- Happy path: 构造同文件 10 分钟内 4 次 Edit 的 transcript → 检测到重做信号
- Edge case: 空 transcript → 输出空信号列表
- Edge case: 无 Skill tool_use 的 session → 信号的 skill 字段为 "unknown"
- Edge case: L1 incidents 文件不存在 → 跳过 L1 事件类型，不报错

**Verification:**
- 用构造的 mock transcript 运行脚本，确认四类信号均可正确提取
- 确认输出 JSON 格式可被 L3 scan_history.py 直接消费

- [x] **Unit 3: dev-learn 追加 skill-self-review 子步**

**Goal:** 在 `dev-learn/SKILL.md` 中追加 L2 `skill-self-review` 子步，使 Phase 7 结束时自动收集本 session 的 skill 执行信号。

**Requirements:** R4, R5

**Dependencies:** Unit 2（extract_signals.py 必须存在）

**Files:**
- Modify: `claude-skills/dev-learn/SKILL.md`
- Create: `docs/supervise/feedback/.gitkeep`

**Approach:**
- 在 dev-learn Workflow 步骤 1（Detect scene）之前插入新步骤 0：`skill-self-review`
- 时机说明：dev-learn 本身就是 Phase 7，"Phase 7 结束时运行"等价于"dev-learn 工作流开始时先收集信号"。放在 Route 检测之前是因为信号数据可供后续 Route 参考（如 Route E skill 改进）
- 该子步调用 `scripts/supervise/extract_signals.py` 处理当前 session transcript
- 将输出按 skill 分组追加到 `docs/supervise/feedback/<skill-name>.md`
- 每条格式：`- YYYY-MM-DD / sess: <path> / 信号: <type> / 证据: <evidence> / phase: <phase>`
- 若无信号则静默跳过，不打断 dev-learn 正常流程
- 宣告（中文）："正在收集本 session 的 skill 执行信号..."

**Patterns to follow:**
- dev-learn 现有的 Signal 检测和 Route 宣告模式
- dev-learn 的中文状态报告风格

**Test scenarios:**
- Happy path: Phase 7 执行时，skill-self-review 子步运行并追加信号到 feedback 文件
- Edge case: 本 session 无信号 → 子步静默完成，不创建空 feedback 文件
- Edge case: feedback 目录不存在 → 自动创建
- Integration: skill-self-review 完成后，dev-learn 正常继续 Route A-F 检测

**Verification:**
- 确认 dev-learn SKILL.md 中新子步的位置和格式与现有风格一致
- 确认 feedback 文件追加格式符合设计文档 §四

- [x] **Unit 4: L3 scan_history.py + dev-supervise SKILL.md 主入口**

**Goal:** 实现跨 session 历史扫描脚本和 `/dev:supervise` skill 主入口，支持 project/global scope 和时间窗口过滤。

**Requirements:** R6, R7

**Dependencies:** Unit 2（复用 extract_signals.py）

**Files:**
- Create: `scripts/supervise/scan_history.py`
- Create: `claude-skills/dev-supervise/SKILL.md`
- Create: `.agents/skills/dev-supervise/SKILL.md` (symlink → `../../../claude-skills/dev-supervise/SKILL.md`)

**Approach:**
- `scan_history.py`：
  - 枚举 `~/.claude/projects/*/conversations/*.jsonl`
  - project scope：解析每个 session 的 cwd，过滤命中当前 repo（参考 CE `--cwd-filter` 模式）
  - global scope：扫所有 session，输出到 `~/.claude/skill-feedback/aggregated-<date>.md`
  - 对每个 session 调用 `extract_signals.py` 的核心函数（import，非子进程）
  - 按 `(skill, signal_type)` 聚合计数，排序输出
  - 生成 Markdown 报告：排行榜表格 + 每个 top 问题的证据引用和建议方向
  - `--since` 参数过滤时间窗口（默认 14d）
- `SKILL.md`：
  - 不进入 dev-flow 编排，独立入口
  - 解析参数（--since, --scope），调用 scan_history.py
  - 输出报告路径，宣告结果摘要（中文）
  - 不修改任何 SKILL.md（仅报告）

**Patterns to follow:**
- CE `extract-metadata.py` 的 session 枚举和 cwd 过滤
- dev-doctor 的独立 utility skill 结构
- 设计文档 §五 的报告格式

**Test scenarios:**
- Happy path: 在有多个 session 的环境中运行 → 输出按 skill 聚合的排行榜报告
- Happy path: `--scope project` → 仅包含当前 repo 的 session
- Happy path: `--since 7d` → 仅包含最近 7 天的 session
- Edge case: 无 session 文件 → 输出空报告，不报错
- Edge case: `--scope global` → 输出到 `~/.claude/skill-feedback/`，不入 repo
- Edge case: session transcript 格式异常（非 JSONL）→ 跳过该 session，记录 warning

**Verification:**
- 确认 project scope 报告写入 `docs/supervise/aggregated/<date>.md`
- 确认 global scope 报告写入 `~/.claude/skill-feedback/aggregated-<date>.md`
- 确认 symlink 正确指向 claude-skills 中的真实文件

- [x] **Unit 5: Codex 退化 — dev-* SKILL.md 追加 SUPERVISE-CHECK 自检段**

**Goal:** 在每个 `dev-*/SKILL.md` 顶部追加 `<SUPERVISE-CHECK>` 自检段，使 Codex 环境下 Claude 在执行前自报工作区和提交状态。

**Requirements:** R8

**Dependencies:** Unit 1（自检段内容与 L1 规则表对齐）

**Files:**
- Modify: `claude-skills/dev-discover/SKILL.md`
- Modify: `claude-skills/dev-design/SKILL.md`
- Modify: `claude-skills/dev-plan/SKILL.md`
- Modify: `claude-skills/dev-code/SKILL.md`
- Modify: `claude-skills/dev-verify/SKILL.md`
- Modify: `claude-skills/dev-ship/SKILL.md`
- Modify: `claude-skills/dev-learn/SKILL.md`
- Modify: `claude-skills/dev-flow/SKILL.md`

**Approach:**
- 在每个 SKILL.md 的 YAML frontmatter 之后、第一个 `#` 标题之前插入 `<SUPERVISE-CHECK>` 块
- 内容为 3 条自检指令（中文），对应铁律 6/7/4
- 不分叉文件，Claude Code 环境下该段被 L1 hook 覆盖（冗余但无害）
- `dev-ship` 的自检段中铁律 7 检查标记为"本 phase 豁免"

**Patterns to follow:**
- 设计文档 §四 Codex 端退化描述

**Test scenarios:**
- Happy path: 每个 dev-* SKILL.md 包含 SUPERVISE-CHECK 段
- Edge case: dev-ship 的铁律 7 检查标记为豁免
- Integration: SUPERVISE-CHECK 段不影响 Claude Code 环境下 skill 的正常路由

**Test expectation:** none — 纯文本插入，无行为变化，通过目视检查确认格式一致

**Verification:**
- grep 确认所有 8 个 dev-* SKILL.md 包含 `<SUPERVISE-CHECK>` 标签
- 确认 dev-ship 的自检段中铁律 7 标记为豁免

- [x] **Unit 6: docs/supervise/ 目录结构 + .gitignore 更新**

**Goal:** 创建 `docs/supervise/` 目录结构占位文件，更新 `.gitignore` 确保运行时数据不入 repo。

**Requirements:** R2, R4（输出目录）

**Dependencies:** None（可与 Unit 1 并行）

**Files:**
- Create: `docs/supervise/feedback/.gitkeep`
- Create: `docs/supervise/aggregated/.gitkeep`
- Modify: `.gitignore`

**Approach:**
- 创建 `docs/supervise/feedback/` 和 `docs/supervise/aggregated/` 目录（.gitkeep 占位）
- `.gitignore` 追加 `~/.claude/state/` 相关说明注释（实际路径在家目录，不需要 gitignore 条目）
- 确认 `.gitignore` 已包含 `.worktrees/`

**Test expectation:** none — 纯目录结构和配置，无行为变化

**Verification:**
- `ls docs/supervise/feedback/ docs/supervise/aggregated/` 确认目录存在
- `.gitignore` 内容正确

## System-Wide Impact

- **Interaction graph:** L1 hook 在每次 Bash/Write/Edit 工具调用时触发，是全局拦截点；L2 通过 dev-learn 子步触发，仅在 Phase 7 执行；L3 是独立命令，不影响其他 phase
- **Error propagation:** L1 hook 失败（脚本异常）必须静默放行（输出 `{}`），绝不阻断用户正常工作流
- **State lifecycle risks:** incidents.jsonl 是 append-only，无并发写入风险（单 session 单进程）；feedback 文件是 append-only Markdown，多 session 不会同时写同一文件
- **API surface parity:** `/dev:supervise` 是新增命令，不影响现有 `dev:*` 命令；SUPERVISE-CHECK 段对 Claude Code 环境透明
- **Unchanged invariants:** 所有现有 `dev-*` skill 的路由逻辑不变；`dev-learn` 仅追加子步，不修改现有 Route A-F

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| L1 hook 脚本异常阻断用户工作流 | 所有异常路径输出 `{}`（静默放行），try/except 包裹全部逻辑 |
| Transcript 路径发现失败（CLAUDE_PROJECT_DIR 未暴露） | 降级为仅工作区/提交规则，phase 相关检查跳过 |
| L2 信号提取误报（framework tags 干扰） | 剥离 `<system-reminder>` 等标签后再分析 |
| Feedback 文件无限增长 | L3 报告提供聚合视图，用户可定期清理；首版不自动清理 |
| Codex transcript 格式不兼容 | 首版仅支持 Claude Code，Codex 留 TODO，SUPERVISE-CHECK 段兜底 |

## Sources & References

- **Origin document:** [docs/superpowers/specs/2026-04-20-dev-supervise-design.md](docs/superpowers/specs/2026-04-20-dev-supervise-design.md)
- Hook 契约参考: gstack `freeze`/`careful` 的 PreToolUse 实现
- Transcript 解析参考: CE `extract-metadata.py`、`extract-skeleton.py`
- Skill 结构参考: `claude-skills/dev-learn/SKILL.md`、`claude-skills/dev-doctor/SKILL.md`



