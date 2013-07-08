#!/bin/sh
kill -TERM $(cat tasks.pid)
echo 'Starting tasks server'
nohup  ~/env/bin/python ~/app/tasks.py > tasks.out 2> tasks.err < /dev/null &
echo $! > tasks.pid