#STEPS TO ACCESSING PI

1. SSH to PI:
   - ssh pi@<IP_Address>
   - passwd:su*****2*5

2. Stop and Start Data Collection Script 
   - cd /home/pi/~/joy_detection_fire
   - sudo systemctl stop joy_detection_demo
   - ./joy_fire_write.py


3. Fetching Data
   - Start VSCode by dragging folder 
   - /Users/sbiswas/Synch_GDrive/1_Coding/23_In_Srch_For_Hppynss/ISFH_Control 
   - Command+Shift+P => Will open up command palette 
   - SFTP: Download (All the files in remote directory will be available in local directory) 

5. Stop script:
   - ps -aux | grep joy
   - kill -9 <PID>


   #For compiling graph to vision model
   