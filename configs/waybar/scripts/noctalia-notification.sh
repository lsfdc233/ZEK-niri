#!/usr/bin/env bash
# Waybar 自定义模块：Noctalia 通知中心状态
# 通过 noctalia IPC 读取“请勿打扰”状态，输出 waybar JSON。
set -euo pipefail

dnd="$(noctalia msg notification-dnd-status 2>/dev/null || echo off)"

if [[ "$dnd" == "on" ]]; then
  # 请勿打扰开启：显示 DND 图标
  printf '{"text": "", "alt": "dnd", "tooltip": "请勿打扰已开启\\n左键：打开通知中心\\n右键：关闭请勿打扰", "class": "dnd"}\n'
else
  # 正常：显示通知铃铛图标
  printf '{"text": "", "alt": "active", "tooltip": "左键：打开通知中心\\n右键：开启请勿打扰", "class": "active"}\n'
fi
