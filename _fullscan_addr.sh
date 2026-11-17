#!/usr/bin/env bash
# 全盘 C/E/F 深扫: 目标地址 (小写+大写+去0x前缀), 所有文件, 含系统目录
ADDR_LC="0x6350761dfb1d20c30ba7ae9cb16560fbe67ddc38"
ADDR_UC="0x6350761dfb1d20c30ba7ae9cb16560fbe67ddc38"
ADDR_LCUC="0X6350761DFB1D20C30BA7AE9CB16560FBE67DDC38"
# 去 0x 前缀的裸 hex (防有人写 6350761d... 不带 0x)
BARE="6350761dfb1d20c30ba7ae9cb16560fbe67ddc38"
OUT="C:/Users/46012/AppData/Local/Temp/addr_scan_results.txt"
echo "=== 全盘 C/E/F 扫描开始: $(date) ===" > "$OUT"
for DRIVE in C: E: F:; do
  echo "" >> "$OUT"
  echo "########## 驱动盘 $DRIVE ##########" >> "$OUT"
  echo "----- 小写全地址 $ADDR_LC -----" >> "$OUT"
  # findstr 全盘 (跳过二进制大文件用 /C 精确保留; 超时靠 & 后台)
  findstr /S /I /C:"$ADDR_LC" "$DRIVE\*" >> "$OUT" 2>/dev/null
  echo "----- 大写全地址 $ADDR_LCUC (findstr /I 已含大小写, 跳过) -----" >> "$OUT"
  echo "----- 裸hex(去0x) $BARE -----" >> "$OUT"
  findstr /S /I /C:"$BARE" "$DRIVE\*" >> "$OUT" 2>/dev/null
  echo "[done $DRIVE: $(date)]" >> "$OUT"
done
echo "" >> "$OUT"
echo "===== 扫描结束: $(date) =====" >> "$OUT"
echo "结果写入: $OUT"
echo "命中行数(去重): $(grep -c "$ADDR_LC\|$BARE" "$OUT" 2>/dev/null || echo 0)"
