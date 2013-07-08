#!/bin/sh
kill $(ps aux | grep '[e]nv/bin/python ~/app/tasks.py' | awk '{print $2}')
echo 'Starting tasks server'
~/env/bin/python ~/app/tasks.py &
