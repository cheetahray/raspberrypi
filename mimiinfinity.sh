#!/bin/sh

### BEGIN INIT INFO
# Provides:          mathkernel
# Required-Start:    $local_fs 
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: mathkernel
### END INIT INFO

python3 /home/pi/raspberrypi/chapter9-mirror.py

