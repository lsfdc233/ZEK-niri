#!/usr/bin/env bash
# 一键切换 Waybar 配色：预设模式 <-> Noctalia 模式
#
# 用法：
#   toggle-colors.sh status   # 供 waybar custom 模块读取状态（JSON）
#   toggle-colors.sh toggle   # 切换配色并重载 waybar
#
# 切换逻辑：
#   - 改写 style.css 的 @import 行：colors.css（手写） <-> colors-noctalia.css
#   - Noctalia模式：启用并应用 Alacritty / cava 的 Noctalia 模板同时启用自动取色方案
#   - 预设模式：撤销并禁用模板，恢复固定主题
#
# 重载方式：不直接给 waybar 发 SIGUSR2，走 “noctalia msg templates-apply”
#   触发 waybar 用户模板的 post_hook 来完成一次重载。
#   原因：短时间内两次 SIGUSR2 会让 waybar 在重载未完成时再次重载而崩溃。
set -euo pipefail

STYLE="${WAYBAR_STYLE:-$HOME/.config/waybar/style.css}"
MANUAL="colors.css"
NOCTALIA="colors-noctalia.css"

CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/noctalia"
APPS_TOML="$CONF_DIR/templates-apps.toml"
APPS_OFF="$APPS_TOML.disabled"
ASSETS="/usr/share/noctalia/assets/templates"

# 预设模式方案（文件名.json）
PRESET_PALETTE="ZEKniri-preset"

# noctalia模式方案（NAME可切换想要的取色器）
NOCTALIA_SCHEME_SOURCE="wallpaper"
NOCTALIA_SCHEME_NAME="soft"

# 静默调用 noctalia IPC
ns() { noctalia msg "$@" >/dev/null 2>&1 || true; }

# 当前生效的配色文件名
active() {
    grep -oE '@import "(colors[^"]*\.css)"' "$STYLE" | head -1 | sed -E 's/@import "(.*)"/\1/'
}

# 启用 Alacritty / cava 模板并渲染；templates-apply 触发 waybar 模板的 post_hook 重载
apps_enable() {
    if [[ -f "$APPS_OFF" ]]; then
        mv -f "$APPS_OFF" "$APPS_TOML"
    fi
    ns config-reload
    sleep 0.3
    ns templates-apply
}

# 撤销并禁用 Alacritty / cava 模板
apps_disable() {
    if [[ -x "$ASSETS/alacritty/undo.sh" ]]; then
        bash "$ASSETS/alacritty/undo.sh" >/dev/null 2>&1 || true
    fi
    if [[ -x "$ASSETS/cava/undo.sh" ]]; then
        bash "$ASSETS/cava/undo.sh" >/dev/null 2>&1 || true
    fi
    if [[ -f "$APPS_TOML" ]]; then
        mv -f "$APPS_TOML" "$APPS_OFF"
    fi
    ns config-reload
}

case "${1:-status}" in
  status)
    if [[ "$(active)" == "$NOCTALIA" ]]; then
      printf '{"text":"󰏘","alt":"noctalia","class":"noctalia","tooltip":"当前状态：Noctalia\\n左键：切换方案"}\n'
    else
      printf '{"text":"󰏘","alt":"manual","class":"manual","tooltip":"当前状态：预设\\n左键：切换方案"}\n'
    fi
    ;;
  toggle)
    if [[ "$(active)" == "$NOCTALIA" ]]; then
      # -> 预设模式
      sed -i -E "s|@import \"$NOCTALIA\";|@import \"$MANUAL\";|" "$STYLE"
      apps_disable
      # 让 Noctalia 同步固定调色板
      ns color-scheme-set custom "$PRESET_PALETTE"
      # 单次重载：借 waybar 模板的 post_hook（已防抖）
      ns templates-apply
    else
      # -> Noctalia 模式
      sed -i -E "s|@import \"$MANUAL\";|@import \"$NOCTALIA\";|" "$STYLE"
      # 让 Noctalia 切到自动取色方案
      ns color-scheme-set "$NOCTALIA_SCHEME_SOURCE" "$NOCTALIA_SCHEME_NAME"
      # apps_enable 内部的 templates-apply 已触发 post_hook 重载（已防抖）
      apps_enable
    fi
    ;;
  *)
    echo "usage: $0 {status|toggle}" >&2
    exit 2
    ;;
esac
