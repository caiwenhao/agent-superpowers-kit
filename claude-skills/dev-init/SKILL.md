---
name: dev-init
description: "Use when adopting the dev:* workflow in a new or existing repository. Generates or appends a 'dev:* preamble' section to CLAUDE.md (seven iron laws, behavioral constraints, Chinese working language, commit-by-user-trigger rule) without clobbering existing content, then migrates any repo-level skill directories to a cross-harness dual-symlink pattern (single source `skills/` with `.claude/skills` and `.agents/skills` pointing to it). Ends by invoking dev:doctor to surface missing dependencies."
---

# dev:init -- 工作流契约初始化

## 通用规则

1. **始终用中文与用户交流。** 状态报告、写入预览、GATE 提示均使用中文。
2. **非破坏性。** 已存在的 CLAUDE.md **不覆盖**：只追加"dev:* preamble"节；若该节已存在，读取并询问用户是否更新。仓库级技能目录迁移前先展示 diff 并 GATE,**不破坏任何既有文件**。
3. **最小主义。** 只做五件事——写 CLAUDE.md preamble + 建 AGENTS.md 软链(Codex 侧) + 迁移仓库级技能目录(可选) + 初始化 wiki 骨架(可选 GATE) + 调 `dev:doctor`。不改 `.claude/settings.json`、不装 plugin。
4. **提交由用户触发。** 本技能写文件但不创建 commit；用户自行决定何时提交变更。

## 与 `/init` 的关系

| 场景 | 用哪个 |
|---|---|
| 仓库第一次接入 Claude Code，还没有 CLAUDE.md | **先 `/init`**（扫代码生成通用 CLAUDE.md）→ 再 `/dev:init`（追加工作流 preamble） |
| 已有 CLAUDE.md，想让本仓库开始遵循 `dev:*` 工作流 | 直接 `/dev:init` |
| 只想试 `dev:*` 的某个 phase，不想改 CLAUDE.md | **不用 `/dev:init`**，直接跑 `/dev:flow` |

`/init` 管"项目是什么"，`dev:init` 管"项目按什么工作流走"。两者正交。

## Scene Detection

### CLAUDE.md

```bash
test -f CLAUDE.md && echo "EXISTS" || echo "MISSING"
grep -qF "<!-- dev:* preamble: start -->" CLAUDE.md 2>/dev/null && echo "PREAMBLE_ALREADY" || echo "NO_PREAMBLE"
```

> 用 `grep -F` 按字面量匹配 HTML 注释锚点，避免 CLAUDE.md 正文里**讨论** preamble 的字符串触发误判。

| Finding | Action |
|---|---|
| `MISSING` | 创建 CLAUDE.md，内容 = preamble only；建议用户随后跑 `/init` 补充项目特定内容 |
| `EXISTS + NO_PREAMBLE` | 在文件末尾追加 preamble 节，带明确分隔线 |
| `EXISTS + PREAMBLE_ALREADY` | 展示现有 preamble，询问"保留 / 替换为最新版 / 手动编辑"，默认保留 |

### 仓库级技能目录(Skills dir)

目标形态 —— Claude Code 和 Codex 共用一份仓库级技能:

```
<project>/
├── skills/                     # 单源,实际文件在这里
├── .claude/skills -> ../skills # Claude Code 发现路径
└── .agents/skills -> ../skills # Codex 发现路径
```

扫描脚本:

```bash
# 三个候选位置的当前状态
for p in skills .claude/skills .agents/skills; do
  if [ -L "$p" ]; then echo "$p SYMLINK -> $(readlink $p)"
  elif [ -d "$p" ]; then echo "$p REAL_DIR ($(find $p -name SKILL.md 2>/dev/null | wc -l) skills)"
  else echo "$p ABSENT"
  fi
done
```

| 场景 | 判定 | 动作 |
|---|---|---|
| **S0** 三者均 ABSENT | 用户没有仓库级技能 | 跳过迁移,不建空目录 |
| **S1** `skills/` REAL + 两个 harness 路径已是指向 `../skills` 的软链 | 已是目标形态 | 跳过 |
| **S2** `skills/` REAL + harness 路径缺失或指错 | 只差软链 | 补两根软链即可 |
| **S3** `.claude/skills/` REAL(内有技能) + 其它 ABSENT | Claude Code-only 历史布局 | `mv .claude/skills skills` → `ln -s ../skills .claude/skills` → `ln -s ../skills .agents/skills` |
| **S4** `.agents/skills/` REAL(内有技能) + 其它 ABSENT | Codex-only 历史布局 | `mv .agents/skills skills` → 建两根软链 |
| **S5** `.claude/skills/` 和 `.agents/skills/` 都是 REAL(均含技能) | 两 harness 各有一套,可能重复或分歧 | GATE:展示两边技能清单 + 重名/差异,询问合并策略(见下) |
| **S6** 任一 harness 路径是 SYMLINK 但指向非 `../skills`(例如指向 `../claude-skills/` 本仓自举场景) | 特殊约定,非通用模式 | **跳过**,提示用户当前是自举仓已有自定义布局 |

**S5 合并策略**(GATE 选项):

1. 选择权威侧(Recommended:选技能数多的一侧) → 权威侧 `mv` 到 `skills/`,另一侧**内容对比**:
   - 文件相同 → 直接删除原目录后建软链
   - 文件不同 → 保留备份到 `skills/_conflicts/<name>-from-<harness>/`,由用户事后合并
2. 手动 → 不动任何文件,只输出诊断报告,让用户自行决定

## Preamble 内容模板

追加的节如下（锚点 marker `<!-- dev:* preamble -->` 让未来的 `/dev:init` 可以识别）：

```markdown
<!-- dev:* preamble: start -->
## dev:* 工作流契约

本仓库采用 `dev:*` 7-phase 工作流（discover → design → plan → code → verify → ship → learn）。进入任何阶段前调用 `/dev:flow` 自动路由；环境诊断用 `/dev:doctor`。

### 七条铁律

1. **设计先于实现** —— 需求文档批准前不碰代码
2. **测试先于代码** —— 无失败测试不写生产代码
3. **根因先于修复** —— 不理解为什么坏就不能修
4. **证据先于断言** —— 没跑命令不能说"通过了"
5. **验证先于采纳** —— 审查反馈先验证再实现
6. **工作区先于工作** —— 每次创建文档或代码前必须在任务专属 worktree / feature branch 中
7. **提交由用户触发** —— Phase 1-5 和 7 不主动 `git commit` / `git push` / 创建 PR；提交仅在 Phase 6 `/dev:ship` 由用户显式触发

### 编码行为约束（贯穿 Phase 4-5）

- **明确假设 / 不懂就问**：实现前列出关键假设；多解释时让用户选，不静默挑一个；更简单方案主动说。**调用澄清工具时必须带推荐标识**——推荐项排第一并标 `(Recommended)`；无倾向时明说"无明确推荐"。
- **手术刀修改**：只改任务直接相关的行；不顺手改相邻代码/注释/格式；匹配现有风格；发现无关 dead code 只提及不删除。
- **孤儿清理**：仅清理本次改动产生的未使用 import/变量；不动原有 dead code。

### 工作语言

所有 GATE 提示、状态报告、路由宣告使用**中文**；技能名、文件路径、命令保持英文。

### 提交规则

提交仅由用户显式触发（说"提交/commit/push/PR"或调用 `/dev:ship`）。commit message 用简洁中文，第一行讲**为什么变**，不讲变了什么。
<!-- dev:* preamble: end -->
```

> **注**：preamble 只复述**锚点级规则**，不重复 `docs/ai-coding-workflow.md` 里的详细路由逻辑——后者是 workflow 引用的权威，preamble 是宪法摘要。

## Workflow

1. **宣告开始**：
   "开始初始化 `dev:*` 工作流契约。检查 CLAUDE.md 状态..."

2. **检测场景**（Scene Detection 脚本）。

3. **GATE（展示写入预览）**：
   - 场景 A（MISSING）："当前无 CLAUDE.md。将创建并仅写入 preamble 节。建议后续手动或通过 `/init` 补充项目特定内容。" 展示将写入的完整内容，等用户确认。
   - 场景 B（EXISTS + NO_PREAMBLE）："已有 CLAUDE.md（X 行）。将在末尾追加 preamble 节，不修改现有内容。" 展示将追加的 diff，等用户确认。
   - 场景 C（EXISTS + PREAMBLE_ALREADY）：展示现有 preamble 内容 + 最新版对比，调用澄清工具询问 `保留 (Recommended) / 替换 / 手动编辑`。

4. **写入**（用户确认后）。

5. **建立 AGENTS.md 软链（Codex 兼容）**：
   ```bash
   test -e AGENTS.md && echo "EXISTS" || ln -s CLAUDE.md AGENTS.md
   ```
   - 不存在 → 创建 `AGENTS.md -> CLAUDE.md` 软链，Codex agent 自动看到同一份 preamble
   - 已存在普通文件 → 不覆盖，提示用户："检测到已有 AGENTS.md（非软链）。Codex 会读它而非 CLAUDE.md;若希望两边同源,请手动合并或改为 `ln -sf CLAUDE.md AGENTS.md`"
   - 已是软链指向 CLAUDE.md → 跳过

6. **迁移仓库级技能目录(cross-harness 单源)**:
   - 运行 Skills dir 扫描脚本,分类到 S0-S6
   - GATE:展示当前布局 + 目标布局 + 需要执行的 `mv`/`ln -s` 命令清单,等用户确认
   - 按场景执行:
     - **S0** → 跳过,宣告"无仓库级技能,略过迁移"
     - **S1** → 跳过,宣告"已是目标形态"
     - **S2** → 补软链:
       ```bash
       mkdir -p .claude
       [ -e .claude/skills ] || ln -s ../skills .claude/skills
       [ -e .agents/skills ] || ln -s ../skills .agents/skills
       ```
     - **S3 / S4** → 真目录迁移 + 双软链:
       ```bash
       mv <source-dir> skills
       mkdir -p .claude .agents
       ln -s ../skills .claude/skills
       ln -s ../skills .agents/skills
       ```
     - **S5** → 按用户选择的合并策略执行;冲突文件进 `skills/_conflicts/`
     - **S6** → 只输出诊断,不动文件
   - 迁移完成后检查 `.gitignore`:若 `.claude/` 或 `.agents/` 被整目录忽略,提示用户追加白名单:
     ```
     .claude/*
     !.claude/skills
     .agents/*
     !.agents/skills
     ```
     **不自动改 `.gitignore`** —— 由用户决定。

7. **调用 `/dev:doctor`**：
   "preamble 已写入,AGENTS.md 软链就绪,仓库级技能目录迁移完成。接下来扫描本仓库的 `dev:*` 依赖..."
   委托给 `dev:doctor` 输出依赖健康报告。

8. **可选:初始化 wiki 骨架(GATE)**:
   检查 `<project>/wiki/` 是否存在。若不存在,询问用户:
   `初始化项目 wiki 骨架? (Recommended) 用于 dev:learn 沉淀和 dev:discover/plan 的 Wiki Query / 跳过 / 同时建 ~/.claude/wiki/ 全局骨架`

   用户同意 → 创建:
   ```bash
   mkdir -p wiki/{sources,entities,concepts,synthesis}
   cat > wiki/index.md <<'EOF'
   # Project Wiki

   > 项目知识的结构化编译。原始源在 `docs/solutions/` / retro 报告;本目录是它们的可检索摘要 + 互链。

   ## Entities
   <!-- 一行一个: - [redis](entities/redis.md) — 缓存层主存储 -->

   ## Concepts
   <!-- 一行一个: - [caching-strategy](concepts/caching-strategy.md) — 我们的缓存决策与 trade-off -->

   ## Sources
   <!-- 最近 ingest 的源,自动追加 -->

   ## Synthesis
   <!-- Wiki Query 沉淀的高质量答案 -->
   EOF
   touch wiki/log.md
   ```

   全局骨架同理,目标 `~/.claude/wiki/`。

9. **收尾指路**：
   "初始化完成。下一步：
   - 开始工作：调用 `/dev:flow`
   - 体检依赖：调用 `/dev:doctor`
   - 新增仓库级技能:`mkdir skills/<name> && $EDITOR skills/<name>/SKILL.md`(两个 harness 自动发现)
   - 查 wiki:调用 `/dev:wiki-search`;沉淀新源:调用 `/dev:wiki-ingest`
   - 提交变更：由你触发(commit message 参考 preamble 里的提交规则)"

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | 无（在当前仓库根目录执行） |
| **Output** | 新建或追加的 CLAUDE.md + AGENTS.md 软链 + `skills/` 单源目录 + `.claude/skills` / `.agents/skills` 双软链 + `dev:doctor` 健康报告 |
| **Side Effects** | 文件写入(CLAUDE.md)+ 软链创建(AGENTS.md / harness skills 路径)+ 技能目录迁移(`mv` + `ln -s`,S3-S5 场景)+ 一次只读诊断 |
| **Next** | 用户提交变更；调用 `/dev:flow` 开始工作 |

## Iron Laws

- **不覆盖既有内容**：CLAUDE.md 只追加 preamble 节，带明确 marker;AGENTS.md / 技能目录已存在普通文件时绝不删除或覆盖
- **不替用户决策**：场景 C(已有 preamble)和 S5(双 harness 技能合并)必问,不默认动手
- **迁移幂等**:S1(已是目标形态)直接跳过;重复跑 `/dev:init` 不应产生任何 diff
- **不扩张职责**：不改 settings、不装 plugin、不写 `.gitignore` —— 这些由用户按需独立执行
- **不创建 commit**：写完文件 / 建完软链即止，提交留给用户
