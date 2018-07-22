#!/bin/bash
# kill existing script
echo "Kiiling existing script"
ppid=$(ps -aux | grep voice | grep python | awk ' {print $2} ')
sudo kill $ppid
echo "Killing done"

