#!/bin/sh
kill $(ps aux | grep 'slshr/app/tasks.py$' | awk '{print $2}')
echo 'Starting tasks server'
nohup ~/env/bin/python ~/app/tasks.py 
