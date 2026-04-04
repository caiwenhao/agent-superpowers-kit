---
name: dev-review-plan
description: |
  对实施计划进行多轮深度审查。使用 gstack autoplan 流水线
  (CEO→Eng→Design→DX 四阶段审查)，确保计划在战略、工程、
  设计、开发者体验各维度都经过充分审查。
  Use when: "审查计划", "review the plan", "计划审查",
  "review my plan", "检查方案"
argument-hint: "[计划文件路径，默认自动检测]"
---

# /dev-review-plan - 计划文档多轮审查

对实施计划进行 gstack autoplan 全流程审查。

## 输入

<plan_path> #$ARGUMENTS </plan_path>

如果上面为空，自动查找当前目录下的计划文件：
1. 查找 `PLAN.md`
2. 查找最近的 `.md` 计划文件
3. 如果找不到，问用户提供路径

## 流程

### Step 1: 进入 plan mode

使用 EnterPlanMode 进入计划模式，将计划文件作为 plan file。

### Step 2: 调用 gstack-autoplan

使用 Skill tool 调用 `gstack-autoplan`。

autoplan 会自动执行完整审查流水线：
- **Phase 1 (CEO Review)**: 战略与范围审查，前提挑战，双模型对话
- **Phase 2 (Design Review)**: UI/UX 维度审查（如有 UI 变更）
- **Phase 3 (Eng Review)**: 架构、测试、性能、安全审查
- **Phase 3.5 (DX Review)**: 开发者体验审查（如有开发者接口）

每个阶段的中间决策由 autoplan 的 6 个决策原则自动处理。
品味决策（合理分歧的选择）会在最终审批门汇总呈现。

### Step 3: 审查通过后衔接

审查完成并通过后，退出 plan mode，告诉用户：

> 计划审查通过。下一步：
> - `/dev-code` - 开始编码
