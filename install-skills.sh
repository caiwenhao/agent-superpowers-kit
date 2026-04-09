#!/bin/bash
# install-skills.sh — 安装 dev- 系列技能到 Claude Code
#
# 用法:
#   bash install-skills.sh              # 安装
#   bash install-skills.sh --uninstall  # 卸载
#
# 安装后调用: /dev-discover /dev-design /dev-plan /dev-code /dev-verify /dev-ship /dev-learn /dev-flow

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$SCRIPT_DIR/claude-skills"
DEST_DIR="$HOME/.claude/skills"

SKILLS=(dev-discover dev-design dev-plan dev-code dev-verify dev-ship dev-learn dev-flow)
OLD_SKILLS=(dev dev-accept dev-eval dev-fix dev-pixel dev-qa dev-review-plan)

if [ "$1" = "--uninstall" ]; then
  echo "=== 卸载 dev- 技能 ==="
  for skill in "${SKILLS[@]}" "${OLD_SKILLS[@]}"; do
    if [ -d "$DEST_DIR/$skill" ]; then
      rm -rf "$DEST_DIR/$skill"
      echo "  已删除: $skill"
    fi
  done
  echo "卸载完成。运行 /reload-plugins 生效。"
  exit 0
fi

echo "=== dev- 技能安装器 ==="
echo ""

# 清理旧版
echo "--- 清理旧版 ---"
for skill in "${OLD_SKILLS[@]}"; do
  if [ -d "$DEST_DIR/$skill" ]; then
    rm -rf "$DEST_DIR/$skill"
    echo "  已删除: $skill"
  fi
done

# 安装
echo ""
echo "--- 安装 ---"
for skill in "${SKILLS[@]}"; do
  if [ ! -f "$SRC_DIR/$skill/SKILL.md" ]; then
    echo "  警告: $SRC_DIR/$skill/SKILL.md 不存在，跳过"
    continue
  fi
  mkdir -p "$DEST_DIR/$skill"
  cp "$SRC_DIR/$skill/SKILL.md" "$DEST_DIR/$skill/SKILL.md"
  echo "  已安装: $skill"
done

# 验证
echo ""
echo "--- 验证 ---"
OK=0
FAIL=0
for skill in "${SKILLS[@]}"; do
  if [ -f "$DEST_DIR/$skill/SKILL.md" ]; then
    OK=$((OK + 1))
  else
    echo "  缺失: $skill"
    FAIL=$((FAIL + 1))
  fi
done

echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "安装完成: $OK 个技能全部就绪"
  echo ""
  echo "运行 /reload-plugins 生效，然后即可使用:"
  echo "  /dev-flow      总编排器（推荐入口）"
  echo "  /dev-discover  Phase 1: 发现"
  echo "  /dev-design    Phase 2: 设计"
  echo "  /dev-plan      Phase 3: 规划"
  echo "  /dev-code      Phase 4: 实现"
  echo "  /dev-verify    Phase 5: 验证"
  echo "  /dev-ship      Phase 6: 交付"
  echo "  /dev-learn     Phase 7: 沉淀"
else
  echo "安装不完整: $OK 成功, $FAIL 失败"
  exit 1
fi
