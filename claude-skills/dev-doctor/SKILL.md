---
name: dev-doctor
description: "Use when starting work on this repo for the first time, after a fresh install, after moving to a new machine/harness, or when any /dev:* phase routes to a skill that reports 'not found' or behaves unexpectedly. Scans every dev-*/SKILL.md for downstream skill references (compound-engineering:*, superpowers:*, gstack-*, ce:*, CLI tools like dev-browser) and reports which are installed, which are missing, and which phases degrade as a result."
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

## When to Use

- 仓库第一次 clone 到新机器 / 新 harness（Claude Code / Codex / 其它）后，跑 `/dev:flow` 之前
- 某个 `/dev:*` phase 路由到的 skill 报 "not found" 或行为异常
- 上游 plugin（compound-engineering / superpowers / gstack）升级后，想确认没有重命名失效的引用
- CLAUDE.md / AGENTS.md 里的依赖清单与实际安装状态疑似不一致

**不适用**：日常写代码 / 审查 / 提交流程，已知环境稳定时无需频繁调用。

## Scan Strategy

### 1. 提取依赖集合

用 Grep / Bash 扫描 `claude-skills/*/SKILL.md`，按以下模式提取引用：

| 模式 | 含义 | 举例 |
|---|---|---|
| `compound-engineering:<name>` | CE plugin 命名空间技能 | `compound-engineering:git-worktree` |
| `superpowers:<name>` | Superpowers plugin 技能 | `superpowers:using-git-worktrees` |
| `gstack-<name>` | gstack plugin 技能（hyphen 形式） | `gstack-codex`, `gstack-qa` |
| `gstack/<name>` | gstack plugin 技能（slash 遗留形式，也要检查） | `gstack/cso` |
| `ce:<name>` / `ce-<name>` | CE 核心技能 | `ce:brainstorm`, `ce:plan` |
| `dev-browser` 等 CLI | 命令行工具 | `dev-browser`, `codex` |

去重后得到完整依赖清单。

### 2. 逐项存在性检查

| 类型 | 检查位置（按优先级） |
|---|---|
| plugin-namespaced (`compound-engineering:*` / `superpowers:*`) | **Claude Code**: `~/.claude/skills/<namespace>-<name>/SKILL.md` → `<project>/.claude/skills/<namespace>-<name>/SKILL.md` → `~/.claude/plugins/cache/<plugin>/<version>/skills/<name>/SKILL.md` → `~/.claude/plugins/**/skills/<name>/SKILL.md`（兜底 glob）<br>**Codex**: `~/.codex/skills/<name>/SKILL.md` → `~/.codex/superpowers/skills/<name>/SKILL.md` → `<project>/.agents/skills/<name>/SKILL.md` |
| `gstack-<name>` | **Claude Code**: `~/.claude/skills/gstack-<name>/SKILL.md` → `<project>/.claude/skills/gstack-<name>/SKILL.md` → `~/.claude/plugins/cache/*/*/skills/gstack-<name>/SKILL.md`<br>**Codex**: `~/.codex/skills/gstack-<name>/SKILL.md`（通常不存在——gstack 主要面向 Claude Code） |
| `ce:<name>` | **Claude Code**: `~/.claude/skills/compound-engineering-<name>/SKILL.md` → `~/.claude/plugins/cache/compound-engineering-plugin/*/skills/ce-<name>/SKILL.md`<br>**Codex**: `~/.codex/skills/ce-<name>/SKILL.md` |
| CLI 工具 | `command -v <name>` / `which <name>`（harness 无关） |

### 3. 报告格式

```
依赖健康检查报告（扫描 N 项依赖，来自 8 个 dev-* 技能）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 已安装（M 项）
   compound-engineering:git-worktree      ~/.claude/skills/compound-engineering-git-worktree/
   superpowers:using-git-worktrees        ~/.claude/skills/superpowers-using-git-worktrees/
   gstack-codex                           ~/.claude/skills/gstack-codex/
   ...

❌ 缺失（K 项）
   dev-browser (CLI)                      not on PATH                    → Phase 4/5 UI 验证降级为手动
   gstack-canary                          not found                      → Phase 6 部署后监控缺失
   ...

⚠️  可疑（L 项，引用存在但默认位置未找到）
   ce:brainstorm                          未在 ~/.claude/skills/ 找到；若走 plugin marketplace 请忽略

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

按 Phase 影响评估：
  Phase 1 (discover): ✅ OK
  Phase 2 (design):   ✅ OK
  Phase 3 (plan):     ⚠️  plan-design-review 缺失（UI 变更审查降级）
  Phase 4 (code):     ❌ dev-browser 缺失（UI 真机验证降级为手动）
  Phase 5 (verify):   ⚠️  gstack-codex 缺失（跨模型对抗审查跳过）
  Phase 6 (ship):     ❌ gstack-canary 缺失（无部署后监控）
  Phase 7 (learn):    ✅ OK

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

建议：
  - dev-browser: `npm install -g dev-browser && dev-browser install`
  - gstack-*: 安装 gstack plugin（参考 gstack/README.md）
  - Codex 环境下 gstack-* 缺失属于已知降级，不需修复（按方案 1 降级运行）
```

## Workflow

1. **宣告开始**：
   "开始依赖健康检查。扫描 `claude-skills/*/SKILL.md` 中的下游引用..."

2. **提取依赖**：

   ```bash
   # 三段式 plugin skill（compound-engineering:review:correctness-reviewer 这类）
   grep -hoE '(compound-engineering|superpowers):[a-z-]+(:[a-z-]+)?' claude-skills/*/SKILL.md
   # gstack 双形态（gstack-name 与遗留 gstack/name）
   grep -hoE 'gstack[-/][a-z][a-z0-9-]*' claude-skills/*/SKILL.md
   # CE 核心技能（ce: / ce- 前缀；要求后续至少 3 字符以避免 `ce-` 杂项词误匹配）
   grep -hoE '\bce[:-][a-z][a-z-]{2,}' claude-skills/*/SKILL.md
   # CLI 工具（白名单显式列出，避免吞掉所有连字符标识符）
   grep -hoE '\b(dev-browser|codex)\b' claude-skills/*/SKILL.md
   ```

   合并、去重、按类型分组。

3. **并行存在性检查**：
   对每项：
   - plugin skill → `ls ~/.claude/skills/<path>/SKILL.md`
   - CLI → `command -v <name>`
   记录 ✅ / ❌ / ⚠️ 三态。

4. **按 phase 交叉引用**：
   扫 `claude-skills/dev-<phase>/SKILL.md`,统计该 phase 引用的依赖中有多少缺失,给出降级描述。

5. **Wiki 健康检查**:
   ```bash
   [ -d "$(pwd)/wiki" ] && echo "PROJECT_WIKI:OK ($(find wiki -name '*.md' | wc -l) pages)" || echo "PROJECT_WIKI:MISSING"
   [ -d "$HOME/.claude/wiki" ] && echo "GLOBAL_WIKI:OK" || echo "GLOBAL_WIKI:MISSING"
   [ -f "$(pwd)/wiki/index.md" ] || echo "PROJECT_WIKI:NO_INDEX"
   [ -f "$HOME/.claude/wiki/index.md" ] || echo "GLOBAL_WIKI:NO_INDEX"
   ```
   三态映射:
   - 两侧都在 + 都有 index.md → ✅
   - 项目 wiki 缺失 → ⚠️(建议 `/dev:init` 初始化,非阻塞)
   - 全局 wiki 缺失 → ⚠️(跨项目知识无处存;可手动 `mkdir -p ~/.claude/wiki/{sources,entities,concepts,synthesis}`)
   - 目录存在但无 index.md → ⚠️ 结构不完整
   - `wiki/log.md` 超过 30 天未追加 → ⚠️ 可能停止维护,提醒用户

6. **输出报告**:
   控制台打印(不写文件)。结尾列出建议安装命令。新增 **Wiki 状态**一节:
   ```
   Wiki 状态:
     项目 wiki:  ✅ <project>/wiki/ (24 页, log 最新 2026-04-15)
     全局 wiki:  ⚠️  ~/.claude/wiki/ 未初始化 (跨项目知识无处沉淀)
     建议:      mkdir -p ~/.claude/wiki/{sources,entities,concepts,synthesis} && touch ~/.claude/wiki/{index,log}.md
   ```

7. **GATE**：
   "依赖检查完成。发现 K 项缺失、L 项可疑。是否要我展示某项的详细位置 / 安装命令？"

## Inputs / Outputs

| | Value |
|---|---|
| **Input** | 无（全量扫描）；可选 `--phase <n>` 只检查特定 phase 的依赖 |
| **Output** | 控制台诊断报告（✅/❌/⚠️ 三态 + phase 影响评估 + 可选安装建议） |
| **Side Effects** | 无（纯只读）|
| **Next** | 用户自行决定：安装缺失项 / 接受降级 / 切换 harness |

## Iron Laws

- **只读诊断**：绝不修改文件、创建提交、安装依赖
- **harness-aware**：先检测当前 harness（Claude Code 看 `~/.claude/`、Codex 看 `~/.codex/`），按对应路径树查找;两边路径都没找到再标 ❌
- **不伪装完整**：Codex 环境下 gstack-* 缺失是**预期降级**（见 CLAUDE.md 跨 harness 兼容说明），报告中标注"已知降级"而非"错误"
- **不预设位置**：plugin 加载路径因 harness 而异，所有默认位置都没找到时标 ⚠️ 而非 ❌
