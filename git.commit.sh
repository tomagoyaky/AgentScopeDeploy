#!/bin/bash
# 自动提交当前项目的所有更改

git add .
if [ -z "$1" ]; then
  msg="auto commit: $(date '+%Y-%m-%d %H:%M:%S')"
else
  msg="$1"
fi
git commit -m "$msg"
git push
