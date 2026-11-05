#!/usr/bin/env bash
# EveryInfra SEO Skills — multi-host installer
# 真源装到 ~/.agents/skills/seo-suite(7 个宿主原生读取),再向检测到的宿主 skill 目录建 symlink。
# Claude Code / Codex / Cursor / VS Code Copilot / Gemini CLI / Windsurf / Goose / Amp / Kiro / ZCode
# Usage:  curl -fsSL https://raw.githubusercontent.com/everyinfra/seo-skills/main/install.sh | bash
#         install.sh [--help] [--version] [--dry-run] [--force] [--no-backup]
#                    [--all] [--agent name ...] [--uninstall]
set -euo pipefail

REPO="https://github.com/everyinfra/seo-skills.git"
SKILL_NAME="seo-suite"
VERSION="0.37.0"

DRY_RUN=0
FORCE=0
BACKUP=1
ALL=0
UNINSTALL=0
AGENTS=""

usage() {
  cat <<'EOF'
EveryInfra SEO Skills installer (multi-host)

usage: install.sh [--dry-run] [--force] [--no-backup] [--all] [--agent <name>...] [--uninstall] [--help] [--version]

options:
  --dry-run     Print what would happen, change nothing on disk
  --force       Overwrite an existing install (backup kept unless --no-backup)
  --no-backup   Skip the .bak backup of an existing install (with --force)
  --all         Install links into ALL known host dirs, not just detected ones
  --agent name  Only handle these hosts (repeatable / comma-separated):
                claude codex cursor copilot gemini windsurf goose amp kiro zcode agents
  --uninstall   Remove symlinks and the source install
  --help, -h    Show this help and exit 0
  --version, -V Show installer version and exit 0

environment:
  SEO_SKILLS_DIR  Source dir override (default: ~/.agents/skills/seo-suite)

notes:
  Source of truth lives in ~/.agents/skills/seo-suite (read natively by
  Codex/Cursor/Gemini CLI/Goose/Amp/Copilot/ZCode). Other hosts get a symlink.
  Host detection = host config dir exists. Verification hints print per host.
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --version|-V) echo "everyinfra-seo-skills installer $VERSION"; exit 0 ;;
    --dry-run) DRY_RUN=1 ;;
    --force) FORCE=1 ;;
    --no-backup) BACKUP=0 ;;
    --all) ALL=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --agent) shift; AGENTS="${AGENTS},${1:-}" ;;
    --agent=*) AGENTS="${AGENTS},${1#--agent=}" ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

SOURCE_BASE="${SEO_SKILLS_DIR:-$HOME/.agents/skills}"
SOURCE_DIR="$SOURCE_BASE/$SKILL_NAME"

# host|marker-dir|link-dir(空=读真源即可)|验证提示
HOST_SPECS="claude|$HOME/.claude|$HOME/.claude/skills|重启会话后输入 /skills 查看 $SKILL_NAME;/doctor 可体检
codex|$HOME/.codex||输入 /skills 或 \$seo-suite 调用;skill 列表有上下文预算,描述超长会被截断
cursor|$HOME/.cursor|$HOME/.cursor/skills|Customize 面板 → Skills;chat 输入 /seo-suite(建 ~/.cursor 链接后才能同步 Cloud Agents)
copilot|$HOME/.copilot|$HOME/.copilot/skills|chat 输入 /skills 打开 Configure Skills 菜单
gemini|$HOME/.gemini|$HOME/.gemini/skills|/skills list;首次激活会弹目录授权确认,属正常流程
windsurf|$HOME/.codeium|$HOME/.codeium/windsurf/skills|Cascade 面板 ⋯ 菜单 → Skills;chat 输入 @seo-suite
goose|$HOME/.config/goose||goose skills list 或会话 /skills(直读 ~/.agents/skills)
amp|$HOME/.config/amp|$HOME/.config/agents/skills|amp skills list(Amp 最高优先级目录是 ~/.config/agents/skills)
kiro|$HOME/.kiro|$HOME/.kiro/skills|Kiro 面板 Agent Steering & Skills;chat 输入 /seo-suite(全局 skill 不上 Web/Mobile)
zcode|$HOME/.zcode||新会话 skill 列表出现 seo-suite(直读 ~/.agents/skills;插件走 .zcode-plugin/)"

want_host() { # want_host <name>: --agent 过滤与检测
  case ",$AGENTS," in ",,") return 0 ;; esac
  case ",$AGENTS," in *",$1,"*) return 0 ;; *) return 1 ;; esac
}

run() {
  if [ "$DRY_RUN" -eq 1 ]; then echo "  [dry-run] would run: $*"
  else "$@"; fi
}

link_target_exists_bad() { # 非 symlink 的同名占用
  [ -e "$1" ] && [ ! -L "$1" ]
}

make_link() { # make_link <link-dir>
  local dir="$1"
  local dest="$dir/$SKILL_NAME"
  run mkdir -p "$dir"
  if link_target_exists_bad "$dest"; then
    if [ "$FORCE" -ne 1 ]; then
      echo "  [skip] $dest 已存在(非本安装器创建),用 --force 替换"
      return
    fi
    if [ "$BACKUP" -eq 1 ]; then
      run mv "$dest" "$dest.bak"
    else
      run rm -rf "$dest"
    fi
  elif [ -L "$dest" ]; then
    run rm "$dest"
  fi
  run ln -s "$SOURCE_DIR" "$dest"
}

# ---------- uninstall ----------
if [ "$UNINSTALL" -eq 1 ]; then
  echo "→ 卸载 $SKILL_NAME"
  while IFS='|' read -r host marker linkdir verify; do
    [ -z "$host" ] && continue
    want_host "$host" || continue
    if [ -n "$linkdir" ] && [ -L "$linkdir/$SKILL_NAME" ]; then
      echo "  [✓] remove link $linkdir/$SKILL_NAME"
      run rm "$linkdir/$SKILL_NAME"
    fi
  done <<EOF
$HOST_SPECS
EOF
  if [ -d "$SOURCE_DIR" ]; then
    echo "  [✓] remove source $SOURCE_DIR"
    run rm -rf "$SOURCE_DIR"
  fi
  echo "✓ 卸载完成(--dry-run 未实际改动)"
  exit 0
fi

# ---------- 检测宿主 ----------
DETECTED=""
while IFS='|' read -r host marker linkdir verify; do
  [ -z "$host" ] && continue
  want_host "$host" || continue
  if [ "$ALL" -eq 1 ] || [ -d "$marker" ] || [ "$host" = "claude" ] || [ "$host" = "codex" ]; then
    DETECTED="$DETECTED $host"
  fi
done <<EOF
$HOST_SPECS
EOF

# 默认至少装真源(~/.agents)
case ",$AGENTS," in
  ,,) DETECTED="$DETECTED agents" ;;
esac

echo "→ 计划: 真源 $SOURCE_DIR + 为以下宿主建入口:${DETECTED:- 无}"
[ "$DRY_RUN" -eq 1 ] && echo "  [dry-run] 模式:不做任何改动"

# ---------- 已存在真源时的保护 ----------
if [ -d "$SOURCE_DIR" ] && [ "$FORCE" -ne 1 ]; then
  echo "!! 真源 $SOURCE_DIR 已存在"
  echo "   默认只补建各宿主入口,不覆盖真源;要完整重装用 --force"
elif [ -d "$SOURCE_DIR" ] && [ "$FORCE" -eq 1 ]; then
  if [ "$BACKUP" -eq 1 ]; then
    echo "→ 备份旧真源到 $SOURCE_DIR.bak"
    run rm -rf "$SOURCE_DIR.bak"
    run mv "$SOURCE_DIR" "$SOURCE_DIR.bak"
  else
    run rm -rf "$SOURCE_DIR"
  fi
fi

# ---------- 获取并安装真源 ----------
if [ ! -d "$SOURCE_DIR" ]; then
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  echo "→ 克隆 EveryInfra SEO Skills..."
  run git clone -q --depth 1 "$REPO" "$TMP/seo-skills"
  run mkdir -p "$SOURCE_BASE"
  run cp -R "$TMP/seo-skills/skills/$SKILL_NAME" "$SOURCE_DIR"
fi

# ---------- 建宿主入口 ----------
RESULTS=""
while IFS='|' read -r host marker linkdir verify; do
  [ -z "$host" ] && continue
  want_host "$host" || continue
  active=0
  case " $DETECTED " in *" $host "*) active=1 ;; esac
  [ "$active" -eq 1 ] || continue
  if [ -n "$linkdir" ]; then
    make_link "$linkdir"
  fi
  RESULTS="$RESULTS$host|$verify
"
done <<EOF
$HOST_SPECS
EOF

# ---------- 汇总 ----------
N_REFS="0"; N_TMPL="0"; N_SCR="0"
[ -d "$SOURCE_DIR/references" ] && N_REFS="$(find "$SOURCE_DIR/references" -name '*.md' | wc -l | tr -d ' ')"
[ -d "$SOURCE_DIR/templates" ] && N_TMPL="$(find "$SOURCE_DIR/templates" -name '*.md' | wc -l | tr -d ' ')"
[ -d "$SOURCE_DIR/scripts" ] && N_SCR="$(find "$SOURCE_DIR/scripts" -name '*.py' | wc -l | tr -d ' ')"

echo ""
echo "✓ 安装完成: $SOURCE_DIR ($N_REFS refs / $N_TMPL templates / $N_SCR scripts)"
echo ""
echo "  各宿主验证方式:"
echo "$RESULTS" | while IFS='|' read -r host verify; do
  [ -z "$host" ] && continue
  printf '  [✓] %-9s %s\n' "$host" "$verify"
done
echo ""
echo "  无 API key、无模型、无运行时依赖——skill 是说明与参考,agent 与你的数据干活。"
echo "  试一试: 帮我做一次 SEO 整站诊断 / run a backlink profile analysis on example.com"
echo "  宿主适配详情: https://github.com/everyinfra/seo-skills#hosts--宿主适配"
