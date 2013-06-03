#!/bin/bash

# User Defined Variables
# H,M,S		系統時間
# rhflag	0 = 當日, 1 = 明天, 2 = 後天...
# strUsage	參數提示訊息
# timeoffset	使用者輸入的時間 (時:分:秒)
# oh,om,os	從 timeoffset 提列出來的 時, 分, 秒 (case 1) / 進位值 (case 2)
# rh,rm,rs	運算結果 時, 分, 秒
# offset	使用 -h, -m, -s 參數時, 使用者帶入的數值

# System Variables
# $#	參數數量
# $0	Shell Script 檔名
# $1	第一個參數
# $2	第二個參數

while ((1))
do
	read -n 1 yname
	if [ X"$yname" = X"c" ]; then
		aplaymidi --port=20:0 /home/pi/ukCchord.mid&
	fi
done
