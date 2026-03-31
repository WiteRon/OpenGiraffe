#!/usr/bin/env bash
# 在项目根目录执行：生成 trip-mobile-minimal.tgz（最小可运行集合）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/trip-mobile-minimal.tgz"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/trip-mobile/backend" "$TMP/trip-mobile/static"

cp "$ROOT/backend/server_mobile_minimal.py" "$TMP/trip-mobile/backend/"
cp "$ROOT/backend/requirements.txt" "$TMP/trip-mobile/backend/"
cp "$ROOT/mini-trip-mobile.html" "$TMP/trip-mobile/"
cp -R "$ROOT/static/"* "$TMP/trip-mobile/static/"

# Mac 上避免把 xattr 打进包，Linux 解压时就不会刷 LIBARCHIVE.xattr.apple 警告
( cd "$TMP" && COPYFILE_DISABLE=1 tar czf "$OUT" trip-mobile )
echo "已生成: $OUT"
du -h "$OUT"
