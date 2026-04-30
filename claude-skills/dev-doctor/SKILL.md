---
name: dev-doctor
description: "Use when starting work on this repo for the first time, after a fresh install, after moving to a new machine/harness, or when any /dev:* phase routes to a skill that reports 'not found' or behaves unexpectedly. Scans every dev-*/SKILL.md for downstream skill references (using the flat canonical names defined in claude-skills/README.md, plus gstack-*, CLI tools like dev-browser) and reports which are installed, which are missing, and which phases degrade as a result. Probes both Claude Code (~/.claude/plugins, ~/.claude/skills) and Codex (~/.codex/skills, ~/.codex/superpowers/skills) discovery paths."
---

# dev:doctor -- 依赖健康检查

## 通用规则

1. **始终用中文与用户交流。** 报告正文、状态标记、影响评估均使用中文。技能名和路径保持英文。
2. **只读诊断。** 本技能只读文件、运行 `which` / `ls`，**绝不**修改任何文件、安装任何依赖、创建提交。
3. **不受工作区前置约束。** 诊断操作无副作用，不要求在任务专属 worktree 中执行。
4. **不自动修复。** 发现缺失依赖时只报告，由用户显式决定是否安装。

## Overview

本技能回答一个问题：**"这台机器 / 这个 harness 上，`dev:*` 流程的所有下游依赖是否都可用？"**

扫描 `claude-skills/*/SKILL.md` 中引用的所有第三方技能与 CLI 工具，逐项检查是否已安装，并按 phase 交叉引用给出影响评估。

技能命名使用 `claude-skills/README.md` 的 **Skill Naming 表**：SKILL 正文里写扁平规范名（例如 `ce-brainstorm`、`using-git-worktrees`），本检查同时在 Claude Code（命名空间前缀形式）和 Codex（扁平名）两端探测。

## When to Use

- 仓库第一次 clone 到新机器 / 新 harness（Claude Code / Codex / 其它）后，跑 `/dev:flow` 之前
- 某个 `/dev:*` phase 路由到的 skill 报 "not found" 或行为异常
- 上游 plugin（compound-engineering / superpowers / gstack）升级后，想确认没有重命名失效的引用
- `claude-skills/README.md` 的 Skill Naming 表更新后，想验证两端都能解析

**不适用**：日常写代码 / 审查 / 提交流程，已知环境稳定时无需频繁调用。

## Scan Strategy

### 1. 提取依赖集合

扫描 `claude-skills/*/SKILL.md` 里 backtick 包围的技能名，按以下类型归类：

| 模式 | 含义 | Codex 位置 | Claude Code 位置 |
|---|---|---|---|
| `ce-<name>` | CE 核心技能 | `~/.codex/skills/ce-<name>/` | `~/.claude/plugins/**/compound-engineering*/skills/ce-<name>/` 或 `~/.claude/skills/compound-engineering-ce-<name>/` |
| `document-review` / `pr-comment-resolver` / `test-browser` / `writing-skills` / ... | CE plugin 里非 `ce-` 前缀的技能 | `~/.codex/skills/<name>/` | 同上但目录名可能为 `compound-engineering-<name>` |
| `using-git-worktrees` / `brainstorming` / `writing-plans` / `test-driven-development` / ... | Superpowers 技能 | `~/.codex/superpowers/skills/<name>/` 或 `~/.codex/skills/<name>/` | `~/.claude/plugins/**/superpowers*/skills/<name>/` 或 `~/.claude/skills/superpowers-<name>/` |
| `gstack-<name>` | gstack 技能 | `~/.codex/skills/gstack-<name>/` | `~/.claude/skills/gstack-<name>/` 或 `~/.claude/plugins/**/gstack*/skills/gstack-<name>/` |
| `dev-browser` / `codex` / 其它命令 | CLI 工具 | `command -v <name>` | `command -v <name>` |

权威别名表在 `claude-skills/README.md` 的 **Skill Naming** 节。本扫描以该表为目标集，只对**明确列出**的规范名做双端探测，避免把 `ce-based`（形容词）/`ce-dir`（普通词）之类 grep 假阳性当成技能。

### 2. 识别运行 harness

```bash
# 是否在 Claude Code 环境
[ -d "$HOME/.claude" ] && echo "CC_AVAILABLE" || echo "CC_MISSING"
# 是否有 Codex 环境
[ -d "$HOME/.codex" ] && echo "CODEX_AVAILABLE" || echo "CODEX_MISSING"
```

两套路径都扫，报告里同时给出 Claude Code / Codex 双栏状态。

### 3. 双端存在性检查

对每项规范名同时探测两端：

```bash
probe_codex() {
  local name="$1"
  [ -f "$HOME/.codex/skills/$name/SKILL.md" ] && echo "codex:hit:$HOME/.codex/skills/$name/" && return
  [ -f "$HOME/.codex/superpowers/skills/$name/SKILL.md" ] && echo "codex:hit:$HOME/.codex/superpowers/skills/$name/" && return
  echo "codex:miss"
}

probe_cc() {
  local name="$1"
  # 1. 项目本地
  [ -f ".claude/skills/$name/SKILL.md" ] && echo "cc:hit:.claude/skills/$name/" && return
  # 2. 用户级 skills 目录（命名空间拼接）
  for prefix in compound-engineering superpowers gstack; do
    [ -f "$HOME/.claude/skills/$prefix-$name/SKILL.md" ] && echo "cc:hit:$HOME/.claude/skills/$prefix-$name/" && return
  done
  # 3. 用户级 plugin 缓存
  local hit
  hit=$(find "$HOME/.claude/plugins" -path "*/skills/$name/SKILL.md" 2>/dev/null | head -n 1)
  [ -n "$hit" ] && echo "cc:hit:$hit" && return
  echo "cc:miss"
}
```

每项归为：
- ✅ 两端都命中
- 🅒 仅 Codex 命中 (Codex-only OK)
- 🅲 仅 Claude Code 命中 (CC-only OK)
- ❌ 两端都 miss

### 4. 仓库本地脚本检查

`dev-learn` 和 `dev-supervise` 依赖 `scripts/supervise/*.py`：

```bash
REPO=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
for f in scripts/supervise/extract_signals.py scripts/supervise/scan_history.py scripts/supervise/iron_law_guard.py; do
  [ -f "$REPO/$f" ] && echo "✅ $f" || echo "❌ $f (dev-learn L2 / dev-supervise L3 signal 采集将静默降级)"
done
```

### 5. 报告格式

```
依赖健康检查报告（扫描 N 项规范名 + K 个本地脚本；来自 13 个 dev-* 技能）
当前 harness: Claude Code ✅ / Codex ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

技能（双端状态）
  canonical name                    Codex                                   Claude Code
  ────────────────────────────────  ──────────────────────────────────────  ──────────────────────────────
  using-git-worktrees               ✅ ~/.codex/superpowers/skills/         ✅ ~/.claude/plugins/.../superpowers/skills/using-git-worktrees/
  ce-brainstorm                     ✅ ~/.codex/skills/ce-brainstorm/       ✅ ~/.claude/plugins/.../ce-brainstorm/
  ce-plan                           ✅                                      ✅
  ce-review                         ✅                                      ✅
  document-review                   ✅                                      ✅
  writing-skills                    ✅                                      ✅
  test-browser                      ✅                                      ✅
  gstack-plan-eng-review            ✅                                      ✅
  gstack-autoplan                   ❌ not found                            ✅
  ...

仓库脚本
  scripts/supervise/extract_signals.py   ✅
  scripts/supervise/scan_history.py      ✅
  scripts/supervise/iron_law_guard.py    ✅

CLI 工具
  dev-browser                       ❌ not on PATH              → Phase 4/5 UI 验证降级为手动

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

按 Phase 影响评估（以当前 harness 为准）：
  Phase 1 (discover): ✅ OK
  Phase 2 (design):   ✅ OK
  Phase 3 (plan):     ⚠️  Codex 缺 gstack-autoplan（大计划走 document-review fallback 或切换到 Claude Code）
  Phase 4 (code):     ❌ dev-browser 缺失（UI 真机验证降级为手动）
  Phase 5 (verify):   ✅ OK
  Phase 6 (ship):     ✅ OK
  Phase 7 (learn):    ✅ OK

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

建议：
  - dev-browser: `npm install -g dev-browser && dev-browser install`
  - Codex 侧 gstack-autoplan 未安装：`codex plugin install gstack` 或切换到 Claude Code 执行 Phase 3 大计划审查
  - 其余无需操作
```

## Workflow

1. **宣告开始**：
   "开始依赖健康检查。读取 `claude-skills/README.md` 的 Skill Naming 表..."

2. **识别当前 harness**（Claude Code / Codex / 混合）。

3. **提取规范名集合**：从 `claude-skills/README.md` 的 Skill Naming 表解析出 canonical 列；交叉验证 `claude-skills/*/SKILL.md` 里的 backtick 引用都在表内（若发现表外引用，标 ⚠️ `table-miss`，提示补表）。

4. **双端存在性检查**：对每项规范名调用 `probe_codex` 和 `probe_cc`，合并状态。

5. **仓库脚本检查**：探测 `scripts/supervise/*.py`。

6. **CLI 检查**：`command -v dev-browser` 等。

7. **按 phase 交叉引用**：扫 `claude-skills/dev-<phase>/SKILL.md`，统计该 phase 引用的依赖中哪些在**当前 harness**缺失，给出降级描述。

8. **Wiki 健康检查**:
   ```bash
   [ -d "$(pwd)/wiki" ] && echo "PROJECT_WIKI:OK ($(find wiki -name '*.md' | wc -l) pages)" || echo "PROJECT_WIKI:MISSING"
   [ -d "$HOME/.claude/wiki" ] && echo "GLOBAL_WIKI:OK" || echo "GLOBAL_WIKI:MISSING"
   [ -f "$(pwd)/wiki/index.md" ] || echo "PROJECT_WIKI:NO_INDEX"
   [ -f "$HOME/.claude/wiki/index.md" ] || echo "GLOBAL_WIKI:NO_INDEX"
   # 孤儿 migration 文件检测
   for wiki in "$(pwd)/wiki" "$HOME/.claude/wiki"; do
     mig="$wiki/_migration.md"
     [ -f "$mig" ] && echo "ORPHAN_MIGRATION:$mig" || true
   done
   ```
   三态映射:
   - 两侧都在 + 都有 index.md → ✅
   - 项目 wiki 缺失 → ⚠️(建议 `/dev:init` 初始化,非阻塞)
   - 全局 wiki 缺失 → ⚠️(跨项目知识无处存;可手动 `mkdir -p ~/.claude/wiki/{sources,entities,concepts,synthesis}`)
   - 目录存在但无 index.md → ⚠️ 结构不完整
   - `wiki/log.md` 超过 30 天未追加 → ⚠️ 可能停止维护,提醒用户
   - 检测到 `_migration.md` 且 mtime > 1 小时 → ⚠️ 孤儿批量 ingest，建议下次调 `/dev:wiki-ingest` 时处理

9. **输出报告**:
   控制台打印(不写文件)。结尾列出建议安装命令。

10. **GATE**：
    "依赖检查完成。发现 K 项缺失、L 项可疑。是否要我展示某项的详细位置 / 安装命令？"

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | 无（全量扫描）；可选 `--phase <n>` 只检查特定 phase 的依赖；可选 `--harness cc|codex|both` 强制只扫一端 |
| **Output** | 控制台诊断报告（双端状态 + phase 影响评估 + 可选安装建议） |
| **Side Effects** | 无（纯只读）|
| **Next** | 用户自行决定：安装缺失项 / 接受降级 / 切换 harness |

## Iron Laws

- **只读诊断**：绝不修改文件、创建提交、安装依赖
- **双端并行**：Claude Code 和 Codex 路径同时探测，不假定只跑一端
- **名字规范来自 README**：Skill Naming 表是唯一真理源；`claude-skills/*/SKILL.md` 的 backtick 引用若不在表内，标 ⚠️ 而非静默忽略
- **不预设位置**：plugin 加载路径因 harness 而异，所有默认位置都没找到时标 ❌；任一端命中即视为该端 OK
