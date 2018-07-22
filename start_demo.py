#!/usr/bin/env python3
'''
Author: Ritwik Biswas
Description: Script for clean start of demo scripts on vision-kit and voice-kit
'''

from global_paths import *
import base64
import time
from datetime import datetime

import paramiko

#Pretty printing
import colorama
from colorama import Fore, Back
from colorama import init
init(autoreset=True)
def command(channel, cmd):
        channel.exec_command(cmd + ' > /dev/null 2>&1 &')
def vision_kit_init():
    '''
    Responsible for vision kit cleanup and start.
    '''

    #Credentials for visionkit login
    hostname = VISION_IP_ADDRESS_  
    myuser   = 'pi'
    mySSHK   = PATH_TO_KEY_
    passwd = 'suripre225'

    #initialize vision-kit client
    client   = paramiko.SSHClient()  # will create the object
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())# no known_hosts error
    client.connect(hostname, username=myuser, key_filename=mySSHK, password=passwd)

    #cd to correct directory
    #Run start_vision script which: run stop demo script, run stop vision script, start vision script
    
    # transport = client.get_transport()
    # channel = transport.open_session()
    # cmd = './/home/pi/~/joy_detection_fire/start_vision.sh;'
    (stdin, stdout, stderr) = client.exec_command('cd /home/pi/~/joy_detection_fire; bash start_vision.sh </dev/null >>/dev/null 2>&1; ')
    time.sleep(3)
    #command(channel,cmd)
    # for line in stdout:
    #      print(Fore.YELLOW + '... ' + line.strip('\n'))
    client.close()

def voice_kit_init():
    '''
    Responsible for voice kit cleanup and start.
    '''
    
    #Credentials for visionkit login
    hostname = VOICE_IP_ADDRESS_ 
    myuser   = 'pi'
    mySSHK   = PATH_TO_KEY_
    passwd = 'suripre225'

    #initialize vision-kit client
    client   = paramiko.SSHClient()  # will create the object
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())# no known_hosts error
    client.connect(hostname, username=myuser, key_filename=mySSHK, password=passwd)

    #cd to correct directory
    #Run start_vision script which: run stop demo script, run stop vision script, start vision script
    
    # transport = client.get_transport()
    # channel = transport.open_session()
    # cmd = './/home/pi/~/joy_detection_fire/start_vision.sh;'
    (stdin, stdout, stderr) = client.exec_command('cd /home/pi/~/joy_detection_voice; bash start_voice.sh </dev/null >>/dev/null 2>&1; ')
    time.sleep(3)
    #command(channel,cmd)
    # for line in stdout:
    #      print(Fore.YELLOW + '... ' + line.strip('\n'))
    client.close()

def main():
    '''Main driver'''
    t_init = time.localtime()
    
    # handle vision kit component
    print("Begin Vision Kit component")

    try:
        vision_kit_init()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")

    # handle voice kit component
    print("Begin Voice Kit component")
    try:
        voice_kit_init()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    
    # Finished! Do output printing
    t_final = time.localtime()
    elapsed_time = int(t_final.tm_sec) - int(t_init.tm_sec)
    print(Fore.GREEN + "DONE!\n")
    print(Back.GREEN + "Finished running startup scripts in ~" + str(elapsed_time) + " seconds!")


if __name__ == '__main__':
    main()
