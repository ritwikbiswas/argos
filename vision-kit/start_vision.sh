#!/bin/bash
# Stop  demo code
echo "Killing demo script ..."
sudo systemctl stop joy_detection_demo 

# kill existing script
echo "kiiling existing script ..."
ppid=$(ps -aux | grep joy | grep python | awk ' {print $2} ')
sudo kill $ppid
echo "killing done .."

echo "starting script .."
./joy_fire_write.py &
