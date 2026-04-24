# Agent Superpowers Kit

AI 编码智能体的 **技能编排层**——用 `dev:*` 系列技能（12 个：7 阶段路由 + 1 编排器 + 4 工具技能）将四套上游技能库（120+ 技能）组合为 7 阶段研发流水线，让 AI Agent 按 发现 → 设计 → 规划 → 实现 → 验证 → 交付 → 沉淀 的节奏完成完整开发周期。

```
┌──────────────────────────────────────────────────────────────┐
│                  dev:flow — 智能编排器（单一入口）              │
│     自动检测当前阶段 · GATE 暂停等待确认 · 支持恢复/跳过/回退    │
└──────────────────────────────────────────────────────────────┘
     │
 ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
 │ 发现  │→│ 设计  │→│ 规划  │→│ 实现  │→│ 验证  │→│ 交付  │
 │  P1   │  │  P2   │  │  P3   │  │  P4   │  │  P5   │  │  P6  │
 └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘
     ↑                                                  │
     └──────────────── 沉淀 P7 ←────────────────────────┘
```

## 为什么需要编排层

上游四套技能库提供了 120+ 个独立技能，但直接使用面临三个问题：

- **选择困难** — 面对一个需求，该用哪些技能、按什么顺序组合？
- **纪律缺失** — AI Agent 容易跳过需求分析直接写代码，或忘记测试就声称完成
- **知识断裂** — 上一次解决的问题，下一次从零开始

`dev:*` 编排层解决这些问题：自动检测当前阶段并路由到正确的技能组合，用 GATE 机制在阶段间暂停等待用户确认，用铁律约束 Agent 行为，用 wiki 沉淀跨会话知识。

## 适用场景

面向使用 Claude Code 或 Codex 进行日常开发的工程师。无论是新功能开发、bug 修复还是重构，`/dev:flow` 都能根据任务规模自动选择合适的流程深度——小修复跳过设计和规划直达实现，大功能走完整 7 阶段。

## 核心理念

这不是一个应用，而是一套 **Markdown 技能文件**（`SKILL.md`），教 AI Agent 如何有纪律地写代码。

七条铁律贯穿所有阶段：

1. 设计先于实现 — 需求批准前不碰代码
2. 测试先于代码 — 先有失败测试再写实现
3. 根因先于修复 — 不理解原因不动手修
4. 证据先于断言 — 没跑过命令不说"好了"
5. 验证先于采纳 — Review 反馈先验证再实施
6. 工作区先于工作 — 必须在任务专属 worktree 中工作
7. 提交由用户触发 — Phase 1-5、7 绝不自动 commit

## 快速开始

### 前置条件

- [Claude Code](https://claude.ai/code) CLI（主要运行环境）
- 或 [OpenAI Codex CLI](https://github.com/openai/codex)（兼容运行，部分技能降级）

### 安装

#### 1. 安装上游技能库插件

`dev:*` 技能路由到四套上游库的下游技能，需要先安装对应插件：

```bash
# Claude Code 环境 — 安装为插件
claude plugin add superpowers
claude plugin add compound-engineering
claude plugin add gstack
claude plugin add agent-skills
```

Codex 环境下，上游技能通过仓库内 `.agents/skills/` 符号链接发现，无需额外安装插件。缺少对应技能时会优雅降级（用户手动执行或使用等价替代）。

#### 2. 克隆本仓库

```bash
git clone <repo-url> agent-superpowers-kit
cd agent-superpowers-kit

# 验证 Codex 侧技能发现路径（列出 .agents/skills/ 下的 SKILL.md）
bash install-skills.sh
```

`dev:*` 技能的发现机制因运行环境而异：

| 运行环境 | 发现机制 |
|---|---|
| Claude Code | 通过插件注册发现技能，无需文件系统符号链接 |
| Codex | `.agents/skills/<name>/SKILL.md` 符号链接到 `claude-skills/` |

### 在项目中启用

在你的目标项目中运行 `/dev:init`，它会：
- 在 `CLAUDE.md` 中写入 `dev:*` 前置约定（铁律、行为约束、中文工作语言）
- 建立 `AGENTS.md` 软链
- 运行 `/dev:doctor` 检查下游依赖状态

### 使用

```
/dev:flow          # 唯一入口 — 自动检测阶段并路由
/dev:discover      # 手动进入 Phase 1: 需求发现
/dev:design        # 手动进入 Phase 2: 视觉设计
/dev:plan          # 手动进入 Phase 3: 实施规划
/dev:code          # 手动进入 Phase 4: 编码实现
/dev:verify        # 手动进入 Phase 5: 质量验证
/dev:ship          # 手动进入 Phase 6: 交付部署
/dev:learn         # 手动进入 Phase 7: 知识沉淀
/dev:init          # 项目初始化 — 写入工作流契约到 CLAUDE.md
/dev:doctor        # 诊断下游依赖安装状态
/dev:wiki-search   # 查询项目/全局 wiki 知识库
/dev:wiki-ingest   # 编译知识源到结构化 wiki
```

推荐用 `/dev:flow` 作为唯一入口，它会根据仓库状态（分支、产物、PR）自动路由到正确阶段。

## 阶段详解

### Phase 1: 发现 — "做什么"

从模糊想法到带 R-ID 的需求文档。按意图清晰度智能分流：

- 无方向 → `ce:ideate`（创意发散）→ `ce:brainstorm`
- 有想法不确定价值 → `gstack-office-hours`（YC 式验证）→ `ce:brainstorm`
- 模糊功能需求 → `ce:brainstorm`（Standard/Deep）
- 清晰小范围 → `ce:brainstorm`（Lightweight）

产出：`docs/brainstorms/*-requirements.md`

### Phase 2: 设计 — "长什么样"

确定视觉语言和交互方案。按设计成熟度分流：

- 无 `DESIGN.md` → `gstack-design-consultation` → `gstack-design-shotgun`
- 有体系无视觉方向 → `gstack-design-shotgun`
- 纯后端 → 跳过

产出：`DESIGN.md` + `approved.json`

### Phase 3: 规划 — "怎么做"

从需求到可执行计划。`ce:plan` 创建，按规模自动选评审深度：

- 10+ 实施单元 → `gstack-autoplan`（CEO + Design + Eng + DX 串行评审）
- 3-9 单元 → `gstack-plan-eng-review` + 可选 `gstack-plan-design-review`
- 1-2 单元 → `gstack-plan-eng-review` only

产出：`docs/plans/*.md`

### Phase 4: 实现 — "写代码"

`ce:work` 自动检测执行策略（内联 / 串行 / 并行 Agent / Swarm），内嵌 TDD、调试、前端设计等辅助技能。收尾时 `/simplify` 三维扫描（复用/质量/效率）。

### Phase 5: 验证 — "质量关"

`ce:review` 多人格代码审查 + 可选叠加层（浏览器测试、QA、安全审计、性能基准）。

### Phase 6: 交付 — "上线"

用户触发 commit → PR → 部署 → canary 验证。这是整个流程中唯一允许 git commit 的阶段。

### Phase 7: 沉淀 — "学到什么"

将解决方案、回顾、可复用方法沉淀为结构化知识（wiki 页面），供后续 Phase 1/3 查询注入。

## 目录结构

```
agent-superpowers-kit/
├── claude-skills/           # 单一事实源 — dev:* 技能文件
│   ├── dev-flow/            #   智能编排器
│   ├── dev-discover/        #   Phase 1: 发现
│   ├── dev-design/          #   Phase 2: 设计
│   ├── dev-plan/            #   Phase 3: 规划
│   ├── dev-code/            #   Phase 4: 实现
│   ├── dev-verify/          #   Phase 5: 验证
│   ├── dev-ship/            #   Phase 6: 交付
│   ├── dev-learn/           #   Phase 7: 沉淀
│   ├── dev-init/            #   项目初始化
│   ├── dev-doctor/          #   依赖诊断
│   ├── dev-wiki-search/     #   Wiki 查询
│   └── dev-wiki-ingest/     #   Wiki 编译
├── docs/                    # 工作流设计文档 + 各阶段分析
│   └── ai-coding-workflow.md  # 权威工作流设计
├── superpowers/             # 上游: Superpowers 技能库 (14 skills)
├── compound-engineering-plugin/  # 上游: CE 技能库 (49 skills)
├── gstack/                  # 上游: gstack 技能库 (41 skills)
├── agent-skills/            # 上游: Agent Skills 库 (21 skills)
├── .agents/skills/          # Codex 发现路径 (符号链接)
└── install-skills.sh        # 技能路径烟雾测试
```

## 跨环境兼容

`dev:*` 技能以 Claude Code 为主要目标环境，同时兼容 Codex：

- Claude Code：所有 `ce:*` / `gstack-*` / `superpowers:*` 下游技能通过插件直接可用
- Codex：`gstack-*` 引用优雅降级——用户手动执行或替换为 `ce:*` / `superpowers:*` 等价技能
- 技能文件格式（frontmatter + Markdown）跨环境一致，不维护环境特定分支

## 贡献

- 编辑 `claude-skills/<name>/SKILL.md`（真实文件），`.agents/skills/` 符号链接自动更新
- 修改路由逻辑时同步更新 `docs/ai-coding-workflow.md`
- 不创建 Claude Code 专属变体；跨环境兼容说明写在 `claude-skills/README.md`

## 许可

见各上游技能库的 LICENSE 文件。
