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

H=`date +%H`
M=`date +%M`
S=`date +%S`
rhflag=0
strUsage="Usage:\n$0 hh:mm:ss\nor\n$0 [-h|-m|-s] number\n"
rm=$M	
rs=$S
while ((1))
do
	if [ X"$M" = X"$rm" ] && [ X"$S" = X"$rs" ]; then
		aplaymidi --port=20:0 /home/pi/Desktop/beer.mid&
		case "$#" in
		1)
			timeoffset=$1
			oh=`echo $timeoffset | awk -F ':' '{print $1}'`
			om=`echo $timeoffset | awk -F ':' '{print $2}'`
			os=`echo $timeoffset | awk -F ':' '{print $3}'`
			rs=`expr $S + $os`
			if [ $rs -gt 59 ]; then
				((rs -= 60))
				om=`expr $om + 1`
			fi
			rm=`expr $M + $om`
			if [ $rm -gt 59 ]; then
				((rm -= 60))
				oh=`expr $oh + 1`
			fi
			rh=`expr $H + $oh`
			if [ $rh -gt 24 ]; then
				((rhflag = rh / 24))
				((rh %= 24))
			fi
		;;
		
		2)
			offset=$2
			if [ $1 == "-h" ]; then
				rh=`expr $H + $offset`
				rm=$M
				rs=$S
				if [ $rh -gt 24 ]; then
					((rhflag = rh / 24))
					((rh %= 24))
				fi
			elif [ $1 == "-m" ]; then
				rh=$H
				rm=`expr $M + $offset`
				rs=$S
				if [ $rm -gt 59 ]; then
					((oh = rm / 60))
					((rm %= 60))
					rh=`expr $H + $oh`
					if [ $rh -gt 24 ]; then
						((rhflag = rh / 24))
						((rh %= 24))
					fi
				fi
			elif [ $1 == "-s" ]; then
				rh=$H
				rm=$M
				rs=`expr $S + $offset`
				if [ $rs -gt 59 ]; then
					((om = rs / 60))
					((rs %= 60))
					((rm += om))
					if [ $rm -gt 59 ]; then
						((oh = rm / 60))
						((rm %= 60))
						((rh += oh))
						if [ $rh -gt 24 ]; then
							((rhflag = rh / 24))
							((rh %= 24))
						fi
					fi
		
				fi
			else
				printf $strUsage
				exit 1
			fi
		;;
		
		*)
			offset="10"
			rh=$H
			rm=`expr $M + $offset`
			rs=$S
			if [ $rm -gt 59 ]; then
				((oh = rm / 60))
				((rm %= 60))
				rh=`expr $H + $oh`
				if [ $rh -gt 24 ]; then
					((rhflag = rh / 24))
					((rh %= 24))
				fi
			fi
			#printf $strUsage
			#exit 1
		;;
		esac
	fi	
	
	if [ $rh -eq 24 ]; then
		rh=0
		rhflag=1
	fi
	M=`date +%M`
	S=`date +%S`
	echo "$H:$M:$S"
	echo "$rhflag $rh:$rm:$rs"
	sleep 1
done