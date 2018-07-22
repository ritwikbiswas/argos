#!/usr/bin/env python3
'''
Author: Ritwik Biswas
Description: -- Cleans all data files from vision/voice kit and locally
'''

from global_paths import *
import base64
import time
from datetime import datetime
import subprocess
import os
import sys
import paramiko

#Pretty print
import colorama
from colorama import Fore, Back
from colorama import init
init(autoreset=True)

def vision_kit_component():
    '''
    Clean vision kit files
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
    #Run stop vision script which: run stop demo script, run stop vision script
    stdin, stdout, stderr = client.exec_command('cd /home/pi/~/joy_detection_fire; rm -r *.csv; ')
    
    for line in stdout:
         print(Fore.YELLOW + '... ' + line.strip('\n'))
    client.close()

def voice_kit_component():
    '''
    Clean voice kit files
    '''
    #Credentials for visionkit login
    hostname = VOICE_IP_ADDRESS_ 
    myuser   = 'pi'
    mySSHK   = PATH_TO_KEY_
    passwd = 'suripre225'

    #initialize voice-kit client
    client   = paramiko.SSHClient()  # will create the object
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())# no known_hosts error
    client.connect(hostname, username=myuser, key_filename=mySSHK, password=passwd)

    #cd to correct directory
    #Run stop vision script which: run stop demo script, run stop vision script
    stdin, stdout, stderr = client.exec_command('cd /home/pi/~/joy_detection_voice; rm output/*; ')
    
    for line in stdout:
         print(Fore.YELLOW + '... ' + line.strip('\n'))

    client.close()

def local_component():
    '''
    Clean local files
    '''
    #Make sure we're in same directory as script
    os.chdir(PATH_TO_SCRIPT_ + "argos-demo")
    os.system("rm vision-dump/*; rm voice-dump/*; rm voice-output/*; rm zprocessed_files/*; rm r-script/*.pdf; rm r-script/*.csv; rm r-script/*.html")


def main():
    '''Main driver'''

       # handle local component
    print(Fore.RED + "Clean local files")
    try:
        local_component()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")


        # handle vision kit component
    print(Fore.RED + "\nClean Vision Kit files")

    try:
        vision_kit_component()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")

    # handle voice kit component
    print(Fore.RED + "Clean Voice Kit files")
    try:
        voice_kit_component()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")



    ####################### Output Printing #######################
    print("\n")

    print(Back.LIGHTGREEN_EX + "Finished Script.")
     
if __name__ == '__main__':
    main()