# oh-my-codex (OMX) 研发流程与技能命令全景分析

> 版本: 0.12.3 | 架构: TypeScript + Rust 混合 | 运行时: Node.js >=20

---

## 一、项目概览

oh-my-codex (OMX) 是一个**多智能体编排层**，封装 Codex CLI，提供技能调度、状态管理和并行执行能力。它通过关键词检测自动路由用户意图到对应技能，实现从需求澄清到代码交付的全链路自动化。

### 核心能力

- **36 个技能命令** — 覆盖规划、执行、审查、调试全场景
- **17+ Agent 角色** — 按复杂度路由到不同模型档位
- **5 种执行模式** — 从单人持久循环到多 Agent 并行协作
- **MCP 状态服务** — 跨迭代持久化模式状态
- **tmux 并行编排** — 最多 6 个 Agent 并发执行

---

## 二、项目结构

```
oh-my-codex/
├── src/                          # TypeScript 源码
│   ├── cli/                      #   CLI 路由入口 (omx.js)
│   ├── catalog/                  #   技能/Agent 注册表
│   │   ├── manifest.json         #     36 技能 + 26 Agent 清单
│   │   ├── schema.ts             #     类型定义 + 校验
│   │   └── reader.ts             #     运行时加载器 (带缓存)
│   ├── hooks/                    #   运行时集成
│   │   ├── keyword-detector.ts   #     关键词 → 技能路由
│   │   ├── keyword-registry.ts   #     关键词映射表
│   │   ├── agents-overlay.ts     #     AGENTS.md 运行时注入
│   │   └── extensibility/        #     Hook 插件系统
│   ├── mcp/                      #   Model Context Protocol 服务
│   │   ├── state-server.ts       #     状态持久化 (read/write)
│   │   ├── memory-server.ts      #     会话记忆
│   │   ├── code-intel-server.ts  #     符号智能
│   │   ├── trace-server.ts       #     执行追踪
│   │   └── bootstrap.ts          #     MCP 启动引导
│   ├── state/                    #   模式状态管理
│   ├── team/                     #   Team 模式协调
│   │   ├── tmux-session.ts       #     tmux 窗格管理
│   │   ├── worktree.ts           #     Git worktree 隔离
│   │   └── model-contract.ts     #     Worker 模型路由
│   ├── agents/                   #   Agent 角色定义
│   └── notifications/            #   通知系统 (Discord/Telegram/Slack)
├── crates/                       # Rust 二进制
│   ├── omx-explore-harness/      #   高速代码库索引
│   ├── omx-runtime/              #   多 Agent 运行时
│   ├── omx-runtime-core/         #   核心运行时工具
│   ├── omx-sparkshell/           #   Shell 命令隔离执行
│   └── omx-mux/                  #   多路复用协调
├── skills/                       # 技能定义 (36 个 SKILL.md)
├── prompts/                      # Agent 角色提示模板 (20+)
├── docs/                         # 文档、合约、指导片段
├── missions/                     # 测试任务 & 沙箱
├── playground/                   # 演示配置
├── templates/                    # 目录清单 & AGENTS 模板
├── AGENTS.md                     # 主运行时配置 (18.7 KB)
├── package.json                  # Node.js 项目配置
├── Cargo.toml                    # Rust Workspace 配置
└── tsconfig.json                 # TypeScript 编译配置
```

---

## 三、构建与开发流程

### 3.1 构建流水线

```bash
# TypeScript 编译
npm run build          # tsc → dist/, 自动 chmod dist/cli/omx.js

# Rust 编译 (可选)
npm run build:explore      # cargo build omx-explore-harness
npm run build:sparkshell   # Shell CLI 包装

# 开发模式
npm run dev            # TypeScript watch 模式

# 安装与验证
npm run setup          # 安装技能到 .codex/skills/
npm run doctor         # 安装健康检查
```

### 3.2 测试体系

```bash
npm run test:node                    # JS/TS 单元测试
npm run test:explore                 # Explore 路由测试
npm run test:team:cross-rebase-smoke # 跨平台 Team 执行冒烟测试
npm run coverage:team-critical       # 关键覆盖率 (78% 行 / 90% 函数 / 70% 分支)
npm run smoke:packed-install         # 安装验证冒烟测试
```

### 3.3 运行时状态目录

```
.omx/
├── context/     # 任务上下文快照 ({slug}-{YYYYMMDDTHHMMSSZ}.md)
├── plans/       # 规划产物
├── specs/       # Deep-interview 规格
├── state/       # 模式状态 ({scope}/{mode}-state.json)
│   ├── ralph/
│   ├── autopilot/
│   └── team/
└── hooks/       # 运行时插件钩子 (*.mjs)
```

---

## 四、五大执行模式

### 4.1 Deep-Interview 模式

| 属性 | 说明 |
|------|------|
| **命令** | `$deep-interview` |
| **触发词** | "interview", "ouroboros" |
| **用途** | 苏格拉底式需求澄清，消除歧义 |
| **深度级别** | Quick (0.30) / Standard (0.20) / Deep (0.15) |
| **输出** | `.omx/context/{slug}-*.md` |

**流程**: 通过多轮提问逐步降低歧义度，当歧义度低于阈值时输出结构化需求规格。

### 4.2 Planning 模式

| 属性 | 说明 |
|------|------|
| **命令** | `$ralplan` / `$plan --consensus` |
| **触发词** | "plan", "ralplan" |
| **用途** | 共识规划，多角色审议 |
| **流程** | Planner → Architect → Critic 循环 |
| **输出** | `.omx/plans/*.md` (含 ADR 架构决策记录) |

**RALPLAN-DR 结构化审议**: 规划者起草 → 架构师评审 → 批评家挑战 → 达成共识后输出实施计划。

### 4.3 Ralph 模式

| 属性 | 说明 |
|------|------|
| **命令** | `$ralph` |
| **触发词** | "ralph", "don't stop", "keep going" |
| **用途** | 单人持久化完成循环 |
| **特点** | 强制架构师验证 + deslop 清理 |
| **输出** | `.omx/state/{scope}/ralph-progress.json` |

**迭代追踪**: `[RALPH + ULTRAWORK - ITERATION {{N}}/{{MAX}}]`，每轮迭代后由架构师验证质量，不通过则继续循环。

### 4.4 Team 模式

| 属性 | 说明 |
|------|------|
| **命令** | `$team N:role-type "task"` |
| **触发词** | "team", "swarm" |
| **用途** | tmux 并行多 Agent 协作 |
| **最大并发** | 6 个 Agent |
| **隔离** | Git worktree 分支隔离 |

**协调机制**: Leader 分配任务 → Workers 在独立 worktree 中执行 → 通过 `.omx/state/team/` 文件协调状态。

### 4.5 Autopilot 模式

| 属性 | 说明 |
|------|------|
| **命令** | `$autopilot` |
| **触发词** | "autopilot", "build me", "I want a" |
| **用途** | 全自动端到端流水线 |

**六阶段流程**:

```
Phase 0: 展开 (Analyst + Architect)
    ↓
Phase 1: 规划 (Architect + Critic)
    ↓
Phase 2: 并行执行 (Ralph + Ultrawork)
    ↓
Phase 3: QA 循环 (最多 5 轮)
    ↓
Phase 4: 多视角验证
    ↓
Phase 5: 清理 (state_clear)
```

---

## 五、全部 36 个技能命令

### 5.1 核心执行技能（4 个必需）

| 技能 | 命令 | 说明 |
|------|------|------|
| Ralph | `$ralph` | 持久完成循环 + 架构师验证 |
| Team | `$team` / `$swarm` | N 个协调 Agent (tmux 并行) |
| Autopilot | `$autopilot` | 全自动端到端流水线 |
| Ultrawork | `$ultrawork` | 并行 Agent 执行引擎 |

### 5.2 规划技能

| 技能 | 命令 | 说明 |
|------|------|------|
| Deep-Interview | `$deep-interview` | 苏格拉底式需求澄清 |
| Ralplan | `$ralplan` | 共识规划 (`$plan --consensus`) |
| Plan | `$plan` | 策略规划（可选 interview） |

### 5.3 专业快捷技能

| 技能 | 命令 | 说明 |
|------|------|------|
| Code Review | `$code-review` | 代码质量审查 |
| Security Review | `$security-review` | 安全漏洞审查 |
| Visual Verdict | `$visual-verdict` | 视觉/UI 评估 |
| Web Clone | `$web-clone` | 网站克隆与验证 |
| TDD | `$tdd` | 测试驱动开发工作流 |
| Analyze | `$analyze` | 调试分析 (别名 `$debugger`) |
| Deep Search | `$deepsearch` | 深度代码库搜索 (别名 `$explore`) |
| Ask Claude | `$ask-claude` | 调用外部 Claude 模型 |
| Ask Gemini | `$ask-gemini` | 调用外部 Gemini 模型 |
| AI Slop Cleaner | `$ai-slop-cleaner` | AI 生成代码质量清理 |
| Build Fix | `$build-fix` | 构建失败自动诊断修复 |

### 5.4 工具与管理技能

| 技能 | 命令 | 说明 |
|------|------|------|
| Cancel | `$cancel` | 中止当前活动模式 |
| Doctor | `$doctor` | 安装健康检查 |
| Help | `$help` | 技能浏览与帮助 |
| Note | `$note` | 会话笔记管理 |
| Trace | `$trace` | 执行过程追踪 |
| Skill | `$skill` | 技能生命周期管理 |
| HUD | `$hud` | 状态仪表盘监控 |
| OMX Setup | `$omx-setup` | 安装与配置向导 |
| Notifications | `$configure-notifications` | 通知渠道配置 |

---

## 六、技能调度架构

### 6.1 调用流程

```
┌──────────────┐
│  用户输入     │  "$ralph 完成登录功能"
└──────┬───────┘
       ↓
┌──────────────────────────┐
│  关键词检测               │  keyword-detector.ts
│  30+ 关键词 → 技能映射    │  keyword-registry.ts
└──────┬───────────────────┘
       ↓
┌──────────────────────────┐
│  技能加载                 │  catalog/reader.ts
│  读取 skills/{name}/      │  SKILL.md (frontmatter + steps)
│  SKILL.md                 │
└──────┬───────────────────┘
       ↓
┌──────────────────────────┐
│  AGENTS.md 运行时注入     │  agents-overlay.ts
│  注入: 代码地图、模式状态  │  最大 3500 bytes
│  优先笔记、项目记忆       │
└──────┬───────────────────┘
       ↓
┌──────────────────────────┐
│  Steps 逐步执行           │  MCP 服务协调
│  state_read / state_write │  跨迭代状态持久化
│  Agent 角色委派           │
└──────┬───────────────────┘
       ↓
┌──────────────────────────┐
│  验证与完成               │  架构师验证 / QA 循环
│  输出产物到 .omx/         │
└──────────────────────────┘
```

### 6.2 关键词映射表

| 关键词 | 目标技能 |
|--------|----------|
| "ralph", "don't stop", "keep going" | `$ralph` |
| "autopilot", "build me", "I want a" | `$autopilot` |
| "interview", "ouroboros" | `$deep-interview` |
| "team", "swarm" | `$team` |
| "plan", "ralplan" | `$ralplan` |
| "analyze", "investigate" | `$analyze` |
| "review" | `$code-review` |
| "security" | `$security-review` |
| "test", "tdd" | `$tdd` |

### 6.3 委派层级

```
用户意图不明确
    ↓
$deep-interview (澄清)
    ↓
$ralplan (共识规划)
    ↓
┌─────────────┬──────────────┐
$ralph        $team          $autopilot
(单人持久)    (多人并行)      (全自动)
    ↓              ↓              ↓
$ultrawork    Worker agents   6 阶段流水线
(并行子任务)  (tmux 隔离)
```

---

## 七、Agent 角色体系

### 7.1 角色分类

**构建线 (Build Lane)**

| 角色 | 职责 | 模型档位 |
|------|------|----------|
| Explorer | 代码库映射与导航 | Low |
| Analyst | 需求分析与拆解 | Standard |
| Planner | 工作排期与依赖分析 | Standard |
| Architect | 系统设计与验证 | **High** |
| Debugger | 根因分析与修复 | Standard |
| Executor | 代码实现 | Standard / **High** |
| Team-Executor | Team 模式 Worker | Standard |
| Verifier | 最终验证 | Standard |

**审查线 (Review Lane)**

| 角色 | 职责 | 模型档位 |
|------|------|----------|
| Code-Reviewer | 代码质量审查 | Standard |
| Security-Reviewer | 安全漏洞审查 | Standard |
| Performance-Reviewer | 性能审查 | Standard |
| API-Reviewer | API 设计审查 | Standard |

**领域线 (Domain Lane)**

| 角色 | 职责 | 模型档位 |
|------|------|----------|
| Test-Engineer | 测试用例设计与执行 | Standard |
| Build-Fixer | 构建失败修复 | Standard |
| Designer | UI/UX 设计 | Standard |
| Writer | 文档撰写 | Low |
| Dependency-Expert | 依赖管理 | Standard |
| Git-Master | Git 操作专家 | Standard |
| Researcher | 技术调研 | Standard |
| Critic | 质量评估与挑战 | **High** |

### 7.2 工具访问模式

| 模式 | 权限 | 适用角色 |
|------|------|----------|
| `read-only` | 只读文件系统 | Explorer, Architect |
| `analysis` | 读取 + 分析工具 | Analyst, Debugger, Planner, Critic |
| `execution` | 完整读写 + 执行 | Executor, Team-Executor |
| `data` | 数据操作 | 特定领域角色 |

---

## 八、MCP 服务架构

```
┌─────────────────────────────────────────────┐
│                 MCP Bootstrap                │
│              (src/mcp/bootstrap.ts)          │
├─────────────┬──────────┬──────────┬─────────┤
│ State       │ Memory   │ Code     │ Trace   │
│ Server      │ Server   │ Intel    │ Server  │
├─────────────┼──────────┼──────────┼─────────┤
│ state_read  │ note_add │ symbols  │ trace   │
│ state_write │ note_get │ files    │ span    │
│ state_clear │ context  │ search   │ events  │
└──────┬──────┴────┬─────┴────┬─────┴────┬────┘
       ↓           ↓          ↓          ↓
  .omx/state/  .omx/notes/ 代码索引   .omx/trace/
```

| 服务 | 文件 | 职责 |
|------|------|------|
| State Server | `state-server.ts` | 模式状态持久化 (ralph/autopilot/team) |
| Memory Server | `memory-server.ts` | 会话记忆与笔记 |
| Code Intel Server | `code-intel-server.ts` | 符号搜索与文件智能 |
| Trace Server | `trace-server.ts` | 执行过程追踪与回放 |

---

## 九、AGENTS.md 运行时注入

AGENTS.md 是 OMX 的**主配置文件** (18.7 KB)，定义了自主执行的全部规则。

### 注入机制

`agents-overlay.ts` 在每次 Codex 启动前注入会话上下文:

```
<!-- OMX:RUNTIME:START -->
  - 代码库地图 (codebase map)
  - 活动模式状态 (active mode state)
  - 优先笔记本 (priority notepad)
  - 项目记忆 (project memory)
<!-- OMX:RUNTIME:END -->
```

- **幂等注入**: 标记边界保证重复注入不会累积
- **Token 效率**: 注入内容最大 3500 bytes
- **Worker 注入**: Team Worker 有独立标记区域 `<!-- OMX:TEAM:WORKER:START/END -->`

### 核心运行原则

1. **质量优先** — 宁可多迭代也不输出低质量
2. **证据驱动** — 所有决策基于代码证据
3. **最小委派** — 能自己完成的不委派
4. **模型路由** — 按复杂度选择模型档位 (Low/Standard/High)
5. **最大并发 6** — 子 Agent 不超过 6 个

---

## 十、技能定义规范

每个技能是 `skills/{name}/SKILL.md`，遵循统一结构:

```markdown
---
name: skill-name
description: 一行描述
argument-hint: 参数提示
---

<Purpose>
  技能的核心目标
</Purpose>

<Use_When>
  适用场景列表
</Use_When>

<Do_Not_Use_When>
  不适用场景列表
</Do_Not_Use_When>

<Execution_Policy>
  Agent 行为指令 (自主性级别、工具权限等)
</Execution_Policy>

<Steps>
  1. 阶段一: ...
  2. 阶段二: ...
  3. ...
</Steps>

<Tool_Usage>
  MCP/Codex 集成点说明
</Tool_Usage>
```

---

## 十一、集成与通知

### Codex CLI 集成

```
.codex/
├── config.toml        # Codex 配置
├── hooks.json         # 原生 Hook 注册
└── skills/            # 已安装技能副本
    ├── ralph/SKILL.md
    ├── team/SKILL.md
    └── ...
```

### 通知系统

| 渠道 | 说明 |
|------|------|
| Discord | Webhook 推送 |
| Telegram | Bot API 推送 |
| Slack | Incoming Webhook |
| OpenClaw | 原生集成 |

通过 `$configure-notifications` 配置通知渠道，支持任务完成、错误告警等事件推送。

---

## 十二、开发工作流总结

```
                    ┌─────────────────────┐
                    │     开发者输入       │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │   关键词检测 & 路由  │
                    └──────────┬──────────┘
                               ↓
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
     ┌────────────┐   ┌──────────────┐  ┌────────────┐
     │ 需求澄清   │   │  共识规划     │  │ 直接执行   │
     │ deep-      │   │  ralplan     │  │ ralph/team │
     │ interview  │   │  plan        │  │ autopilot  │
     └─────┬──────┘   └──────┬───────┘  └─────┬──────┘
           ↓                 ↓                 ↓
     ┌─────────────────────────────────────────────┐
     │              执行引擎                        │
     │  Ralph (单人) | Team (多人) | Ultrawork (并行)│
     └──────────────────────┬──────────────────────┘
                            ↓
     ┌─────────────────────────────────────────────┐
     │              质量保障                        │
     │  架构师验证 | QA 循环 | 多视角审查            │
     └──────────────────────┬──────────────────────┘
                            ↓
     ┌─────────────────────────────────────────────┐
     │              产物输出                        │
     │  .omx/plans/ | .omx/context/ | 代码提交      │
     └─────────────────────────────────────────────┘
```
