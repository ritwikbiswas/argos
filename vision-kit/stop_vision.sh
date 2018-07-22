#!/bin/bash
# Stop  demo code
echo "Killing demo script (if running)"
sudo systemctl stop joy_detection_demo 

# kill existing script
echo "Kiiling existing script"
ppid=$(ps -aux | grep joy | grep python | awk ' {print $2} ')
sudo kill $ppid
echo "Killing done"
