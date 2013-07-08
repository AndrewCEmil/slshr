#!/bin/sh\
## Deployment scripts for Tasks.py
kill -TERM $(cat tasks.pid)
echo 'Starting tasks server'
nohup ~/env/bin/python ~/app/tasks.py &
echo $! > tasks.pid