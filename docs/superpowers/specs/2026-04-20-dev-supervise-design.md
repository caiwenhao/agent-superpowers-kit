# dev-supervise 设计

日期: 2026-04-20
状态: 设计待实施

## 一、定位

`dev-supervise` 是 `dev:*` skill 库的**元 skill**:监督自身执行、收集纠正信号、产出改进建议,让 skill 库在使用中自我进化。

它不参与业务编排,只观察 `dev-*` / `ce:*` / `gstack-*` / `superpowers:*` 自己的行为。

与现有 utility skill 的关系:

| Skill | 职责 | 时机 |
|---|---|---|
| `dev-init` | 安装/初始化 CLAUDE.md | 一次性 |
| `dev-doctor` | 依赖健康检查 | 一次性/周期性 |
| `dev-supervise` | 运行期监督 + 改进建议 | 持续 + 手动复盘 |

## 二、三层结构

| 层 | 机制 | 触发 | 作用 |
|---|---|---|---|
| **L1 实时拦截** | Claude Code `PreToolUse`/`PostToolUse` hook(Python) | 每次工具调用 | 拦截 iron law 6/7 黑白违规 |
| **L2 会话复盘** | `dev-learn` 内置子步 `skill-self-review` | Phase 7 结束 | 本 session 信号 → `docs/supervise/feedback/<skill>.md` |
| **L3 历史扫描** | `/dev:supervise` 手动命令 | 用户触发 | 跨 session 聚合排行 + 结构化改进建议 |

`dev-supervise` 不进入 `dev-flow` 自动编排;入口仅有 L3 命令与 L2 子步。

## 三、L1 实时拦截

### 实现

`scripts/supervise/iron_law_guard.py`,在 `.claude/settings.json` 中注册 `PreToolUse`(匹配 `Bash|Write|Edit`)与 `PostToolUse`(匹配 `Bash`)。

### Phase 判定

不使用文件标记(避免残留、并发、竞态)。改为读当前 session transcript,倒序查找最近一次 `Skill` 工具调用,提取 skill 名,推断当前 phase。

环境变量来源:Claude Code hook 暴露的 `CLAUDE_PROJECT_DIR` + session id,定位到 `~/.claude/projects/<encoded-cwd>/conversations/<session>.jsonl`。若 hook 上下文不暴露 transcript 路径,L1 退化为只看 cwd/branch 规则,phase 相关检查跳过。

### 规则表

| 规则 | 检查 | 动作 |
|---|---|---|
| 工作区(铁律 6) | `git rev-parse --abbrev-ref HEAD` 为 main/master 且 cwd 不在 `<repo>/.worktrees/` 子路径下 | **阻断**,提示 "请通过 `compound-engineering:git-worktree` 创建任务级 worktree" |
| 提交触发(铁律 7) | Bash 命令匹配 `git commit\|git push\|gh pr create\|gh pr merge` 且最近 phase ≠ `dev-ship` | **阻断**,要求用户显式触发 `/dev:ship` 或在消息中明示授权 |
| 证据先行(铁律 4) | PostToolUse 阶段,助手最近文本含 `完成\|通过\|works\|passing\|all green` 且最近 N=10 步内无测试命令(`pytest\|npm test\|cargo test\|go test\|bundle exec` 等) | **warn**,不阻断,记录到 incidents 日志 |

### Codex 端退化

同规则以 `<SUPERVISE-CHECK>` 自检段写入每个 `dev-*/SKILL.md` 顶部,执行前 Claude 自报。不分叉文件。

### 事件日志

L1 拦截/警告事件追加到 `~/.claude/state/supervise-incidents.jsonl`(家目录,不入 repo)。每条:
```json
{"ts": "...", "session": "...", "rule": "commit-trigger", "tool": "Bash", "command": "git commit ...", "action": "block", "phase_inferred": "dev-code"}
```

## 四、L2 会话复盘

接入 `claude-skills/dev-learn/SKILL.md`,追加子步 `skill-self-review`。

### 信号提取

`scripts/supervise/extract_signals.py`,输入:本 session transcript。提取四类**结构信号**(不做语义/正则匹配):

| 信号 | 定义 | 含义 |
|---|---|---|
| 回滚 | 用户消息后,Claude 立即用 `Edit` 撤销自己上一次 `Edit`(diff 反向)/重写关键段 | 用户纠正了实现 |
| 打断 | 用户消息插入在 Claude 连续工具调用序列中间,而非自然轮次结束 | 用户中途叫停 |
| 重做 | 同一文件在 N=10 分钟内被 Claude 改 ≥3 次 | skill 输出质量低,反复修正 |
| L1 事件 | 读 `~/.claude/state/supervise-incidents.jsonl` 中本 session 的条目 | iron law 违规 |

### 输出

按 skill 分组追加到 `docs/supervise/feedback/<skill-name>.md`(入 git)。每条:
```markdown
- 2026-04-20 / sess: <path> / 信号: 重做 / 证据: src/foo.py 被改 4 次于 14:22-14:31 / phase: dev-code
```

**不生成 patch**,仅累积证据队列。SKILL.md 改动一律人工。

## 五、L3 历史扫描

### 命令

`/dev:supervise [--since 14d] [--scope project|global]`

参数:
- `--since`:回溯时间窗,默认 14d
- `--scope project`(默认):仅扫 cwd 命中当前 repo 的 session
- `--scope global`:扫所有 session,**输出强制路径** `~/.claude/skill-feedback/aggregated-<date>.md`(repo 外,避免数据泄漏)

### 实现

`scripts/supervise/scan_history.py`:

1. 枚举 transcript 源:
   - Claude Code: `~/.claude/projects/*/conversations/*.jsonl`
   - Codex: `~/.codex/sessions/**/*.jsonl`(若存在;首版仅 Claude Code,Codex 留 TODO)
2. project scope:解析每个 session 的 cwd,过滤命中当前 repo
3. 对每 session 跑 L2 信号提取
4. 按 `(skill, 信号类型)` 聚合排行
5. 输出报告 `docs/supervise/aggregated/<date>.md`(project scope)或家目录路径(global scope)

### 报告格式

```markdown
# Skill Supervise Report - 2026-04-20

## 排行榜(近 14d)

| Skill | 信号类型 | 次数 |
|---|---|---|
| dev-plan | 重做 | 12 |
| dev-ship | L1 拦截(过早 commit) | 8 |
| dev-verify | 回滚 | 5 |

## 结构化改进建议

### dev-plan / 重做
- 证据: [sess1#L120, sess2#L88, sess3#L45, ...]
- 建议方向: 检查 SKILL.md 中下游 ce:plan 触发条件描述,可能与实际可用性不一致;或计划模板对范围检测过宽
- 待人工: 阅读证据 → 改 SKILL.md → 走常规 review
```

报告**不嵌入 transcript 原文**,仅引用 session 路径 + 行号,降低隐私泄漏面。

## 六、文件落点

```
<repo>/
  claude-skills/dev-supervise/SKILL.md            # 主入口
  claude-skills/dev-learn/SKILL.md                # 追加 skill-self-review 子步
  scripts/supervise/
    iron_law_guard.py                             # L1
    extract_signals.py                            # L2
    scan_history.py                               # L3
  docs/supervise/
    feedback/<skill>.md                           # L2 队列(入 git)
    aggregated/<date>.md                          # L3 project 报告(入 git)
  .claude/settings.json                           # 注册 hook

~/.claude/                                        # 家目录,不入 repo
  state/supervise-incidents.jsonl                 # L1 事件
  skill-feedback/aggregated-<date>.md             # L3 global 报告
```

`.gitignore`: `.claude/state/`(已存在则跳过)。

## 七、自我边界

- 不入 `dev-flow` 自动编排
- 入口仅:`/dev:supervise`(L3)、`dev-learn` 子步(L2)
- L1 hook 是机械脚本,不算 skill 行为,不受自指约束
- `dev-supervise` 自身 SKILL.md 改动走常规 review,无特权
- L3 默认 project scope,global 必须显式指定且输出到家目录

## 八、已知权衡

- **信号提取仍可能漏**:用户用截图/语音/隐晦语气表达不满时无法捕获 → 接受,L1 + 大样本兜底
- **Phase 推断依赖 transcript 可读性**:若 hook 上下文不暴露路径,L1 phase 相关规则跳过,仅工作区规则生效
- **跨 repo session 过滤靠 cwd**:Codex transcript 格式可能不同,首版仅支持 Claude Code,Codex 留 TODO
- **不自动 patch SKILL.md**:抬高门槛,避免 skill 自我污染;代价是改进建议需人工落地

## 九、实施顺序(供 writing-plans 参考)

1. `scripts/supervise/iron_law_guard.py` + `.claude/settings.json` 注册 hook + `.gitignore` 更新
2. `scripts/supervise/extract_signals.py`(L2 提取核心,L3 复用)
3. `claude-skills/dev-learn/SKILL.md` 追加子步
4. `scripts/supervise/scan_history.py` + `claude-skills/dev-supervise/SKILL.md` 主入口
5. 每个 `dev-*/SKILL.md` 顶部追加 `<SUPERVISE-CHECK>` 自检段(Codex 退化用)
6. `docs/supervise/` 目录占位 + README
