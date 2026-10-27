#!/bin/sh
# Claude Code 개인 스킬 폴더에 doc-theme 스킬을 설치한다. 엔진과 테마를 스킬 폴더에 함께 복사한다.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
repo=$(cd "$here/../.." && pwd)
dest="${1:-$HOME/.claude/skills/doc-theme}"
mkdir -p "$dest"
cp "$here/doc-theme/SKILL.md" "$dest/SKILL.md"
cp "$repo/theme.py" "$dest/theme.py"
rm -rf "$dest/themes"
cp -R "$repo/themes" "$dest/themes"
echo "설치했다: $dest"
