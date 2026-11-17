#!/usr/bin/env bash
# 二进制层全盘确认: 强制把二进制当文本搜 (grep -a), 扫 C/E/F 的非源码文件
ADDR="0x6350761dfb1d20c30ba7ae9cb16560fbe67ddc38"
BARE="6350761dfb1d20c30ba7ae9cb16560fbe67ddc38"
UC="0X6350761DFB1D20C30BA7AE9CB16560FBE67DDC38"
OUT="C:/Users/46012/AppData/Local/Temp/addr_scan_bin.txt"
echo "=== 二进制层全盘扫描: $(date) ===" > "$OUT"
for DRIVE in C: E: F:; do
  echo "" >> "$OUT"
  echo "########## $DRIVE (强制二进制当文本, -a) ##########" >> "$OUT"
  # grep -r -a -l 全盘, 排除超大目录; 三种形态
  grep -r -a -l -e "$ADDR" -e "$UC" "$DRIVE/" 2>/dev/null >> "$OUT.tmp" 2>/dev/null
  grep -r -a -l -e "$BARE" "$DRIVE/" 2>/dev/null >> "$OUT.tmp" 2>/dev/null
  # 过滤: 排除 node_modules/.git/我自己刚写的脚本/结果文件
  if [ -f "$OUT.tmp" ]; then
    grep -viE "node_modules|/\.git/|_find_addr|_fullscan_addr|addr_scan" "$OUT.tmp" >> "$OUT" 2>/dev/null
    echo "  [$DRIVE 命中文件数(过滤后): $(grep -c . "$OUT" 2>/dev/null)]" >> "$OUT"
  fi
  rm -f "$OUT.tmp"
  echo "[done $DRIVE: $(date)]" >> "$OUT"
done
echo "" >> "$OUT"; echo "===== 结束: $(date) =====" >> "$OUT"
echo "二进制层扫描写入: $OUT"
echo "--- 过滤后的真实命中 (排除 node_modules/.git/我的扫描脚本/结果文件) ---"
grep -viE "^===|^####|done|命中|二进制层|节点" "$OUT" 2>/dev/null | grep -viE "node_modules|/\.git/|_find_addr|_fullscan_addr|addr_scan" 2>/dev/null
