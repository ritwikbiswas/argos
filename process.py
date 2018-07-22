#!/usr/bin/env python3
'''
Author: Ritwik Biswas
Description: -- Script for clean stop of demo scripts on vision-kit and voice-kit
             -- Processing the Audio into csv files to analyze
'''

from global_paths import *
import base64
import time
from datetime import datetime
import subprocess
import os
import sys
from textblob import TextBlob
#plotly tools
import paramiko
import plotly as py
import plotly.graph_objs as go
from plotly import tools
import random
from random import randint


from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import SentimentOptions, Features, EntitiesOptions, KeywordsOptions

natural_language_understanding = NaturalLanguageUnderstandingV1(
  username=SENTIMENT_USERNAME_,
  password=SENTIMENT_PASSWORD_,
  version='2018-03-16')


#Pretty print
import colorama
from colorama import Fore, Back
from colorama import init
init(autoreset=True)

DEBUG_MODE_ = False

############################################## PROCESSING FUNCTIONS ##############################################
def dprint(input):
    if DEBUG_MODE_:
        print(input)
def command(channel, cmd):
        channel.exec_command(cmd + ' > /dev/null 2>&1 &')

def vision_kit_component():
    '''
    Stop vision kit script and collect files
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
    stdin, stdout, stderr = client.exec_command('cd /home/pi/~/joy_detection_fire; ./stop_vision.sh; ')
    
    for line in stdout:
         print(Fore.YELLOW + '... ' + line.strip('\n'))
    print(Fore.GREEN + "DONE!\n")

    #Locate all csv's
    stdin, stdout, stderr = client.exec_command('ls /home/pi/~/joy_detection_fire | grep .csv')
    
    #Store csv names
    csv_names = []
    for line in stdout:
        csv_names.append(line.strip('\n'))
        #print(Fore.YELLOW + '... ' + line.strip('\n'))
    
    #Download csv files
    initial = 'sshpass -p "suripre225" scp pi@192.168.1.240:/home/pi/~/joy_detection_fire/'
    final = PATH_TO_SCRIPT_ + 'argos-demo/vision-dump'
    print("Found " + str(len(csv_names)) + " files.")
    count = 1
    for i in csv_names:
        print(Fore.MAGENTA + "Downloading[" + str(count) + "] --> " + i)
        total_call = initial + str(i) + " " + final
        #print(total_call)
        os.system(total_call)
        count += 1

    client.close()
    
def voice_kit_component():
    '''
    Stop voice kit script and collect all .wav files
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
    stdin, stdout, stderr = client.exec_command('cd /home/pi/~/joy_detection_voice; ./stop_voice.sh; ')
    
    for line in stdout:
         print(Fore.YELLOW + '... ' + line.strip('\n'))
    print(Fore.GREEN + "DONE!\n")

    #Locate all csv's
    stdin, stdout, stderr = client.exec_command('ls /home/pi/~/joy_detection_voice/output | grep .wav')

    #Store csv names
    wav_names = []
    for line in stdout:
        wav_names.append(line.strip('\n'))
        #print(Fore.YELLOW + '... ' + line.strip('\n'))

    initial = 'sshpass -p "suripre225" scp pi@192.168.1.239:/home/pi/~/joy_detection_voice/output/'
    final = PATH_TO_SCRIPT_ + 'argos-demo/voice-dump '
    print("Found " + str(len(wav_names)) + " files.") 
    count = 1 
    for i in wav_names:
        print(Fore.MAGENTA + "Downloading[" + str(count) + "] --> " + i)
        total_call = initial + str(i) + " " + final
        #print(total_call)
        os.system(total_call)
        count += 1
    
    client.close()

def file_name_to_date(s):
    '''
    Takes a string path/filename and removes everything but the date and returns
    '''
    split = s.split('/')
    file_name  = split[len(split)-1]
    split = file_name.split('_')
    date = split[len(split)-1]
    split = date.split('.')
    date = split[0]
    return str(date)

def process_vokaturi_output(output):
    '''
    Process raw string output from Vokaturi into array of audio emotions
    Order: [Neutral, Happy, Sad, Angry, Fear]
    '''
    #Decode byte string
    str_out = str(output, 'utf-8')

    #Split by '\n'
    split_output = str_out.split("\n")
    if "sonorancy" in str(split_output[10]):
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    #print(split_output[10])

    #Find specfic emotons and add
    emotions = []
    for i in range(len(split_output)-6, len(split_output)-1):
        split_num = split_output[i].split(":")
        #print(split_num)
        value = float(split_num[1])
        emotions.append(value)
    #print(emotions)
    return emotions
    #print(split_output)

# for ibm
def process_speech_text_output(output):
    '''
    Process raw string output of speech to text into array of sentiment scores and text
    Order: [neg, neu, pos, compound, text]
    '''
    #Decode byte string
    str_out = str(output, 'utf-8')

    #Split by '\n'
    split_output = str_out.split("\n")
    if "NULL" in str(split_output[0]):
        return "failed"
    dprint("foo")
    # print(split_output)
    main_text = ""
    dprint(split_output)
    for i in range(0,len(split_output)-2):
        dprint("m: " + main_text)
        main_text += str(split_output[i])
        main_text = main_text[:-1]
        main_text += ". "
    dprint("foo1")
    main_text = main_text[:-1]
    # Add each sentiment score and also string to output array
    sentiment_out = []
    sent_dict = eval(split_output[len(split_output)-2])
    for i in sent_dict:
        sentiment_out.append(sent_dict[i])
    dprint("foo3")
    sentiment_out.append(main_text)
    #print(sentiment_out)
    return sentiment_out

#for google
# def process_speech_text_output(output):
#     '''
#     Process raw string output of speech to text into array of sentiment scores and text
#     Order: [neg, neu, pos, compound, text]
#     '''
#     #Decode byte string
#     str_out = str(output, 'utf-8')

#     #Split by '\n'
#     split_output = str_out.split("\n")
#     if "Could not understand audio" in str(split_output[0]):
#         return [0.0,0.0,0.0,0.0,""]
#     # print(split_output)
#     main_text = str(split_output[0]) #store main text

#     # Add each sentiment score and also string to output array
#     sentiment_out = []
#     sent_dict = eval(split_output[1])
#     for i in sent_dict:
#         sentiment_out.append(sent_dict[i])
#     sentiment_out.append(main_text)
#     #print(sentiment_out)
#     return sentiment_out
  
def process_audio_files():
    '''
    Steps through all .wav files in voice-dump directory
    For each .wav:
        -- Determines transcription text and vader sentiment
        -- Runs vocatory on file name and collect/parses output into huge list
    Finally, outputs list and transcriptions into corresponding files
    '''
    
    #Iterate and collect all wav file names into list
    output_directory = PATH_TO_SCRIPT_ + "argos-demo/voice-dump/"
    all_wav_files = []
    listdir = os.listdir(output_directory)
    listdir = sorted(listdir)
    for filename in listdir:
        if filename.endswith(".wav"):
            all_wav_files.append(str(os.path.join(output_directory, filename)))
            #print(os.path.join(output_directory, filename))
            continue
        else:
            continue
    #print(all_wav_files)

    #Chdir to where script calls made
    call = PATH_TO_SCRIPT_ + "argos-demo/OpenVokaturi-3-0a/examples/"
    os.chdir(call)

    # Iterate through all wav file names and for each one, collect the data and append to master
    # Each row [filename, v1, v2,...,v5,s1,s2,...,s4,text]
    all_data = []
    count = 1
    for i in all_wav_files:
        print(Fore.YELLOW + "...Processing[" + str(count) + "] " + str(i))
        #Data storage for this specific wav file
        curr_wav_file = []
        
        #append just date to array
        curr_wav_file.append(file_name_to_date(i))
        
        # Run vokatori and collect results
        vokaturi = "python3 OpenVokaWavMean-mac64.py " + str(i)
        result = subprocess.check_output(vokaturi, shell=True)
        emotions = process_vokaturi_output(result)
        #print(emotions)
        print(Fore.YELLOW + ".....done vokaturi")
        #Add emotions to master array
        for val in emotions:
            curr_wav_file.append(val)
        
        # Run speech to text and collect results
        speech_text = "python3 -W ignore speech_to_text.py " + str(i)
        result = subprocess.check_output(speech_text, shell=True)
        dprint("REACHED HERE")
        sentiments = process_speech_text_output(result)
        if sentiments == "failed":
            count += 1
            continue
        dprint("DIDN'T REACHED HERE")
        #Add emotions to master array
        for val in sentiments:
            curr_wav_file.append(val)
        # Add emotion data to array
        print(Fore.YELLOW + ".....done speech-to-text")
        #Add all data to master data
        all_data.append(curr_wav_file)
        count += 1
    
    return all_data
def get_ibm_sent(text_sample):
    '''
    Analyze sentiment using IBM nlp API
    '''
    response = natural_language_understanding.analyze(
    text=text_sample,
    features=Features(
    sentiment=SentimentOptions()))

    score = response["sentiment"]["document"]["score"]
    #print(json.dumps(response, indent=2))
    return score

def get_textblob_sent(text_sample):
    '''
    Analyze sentiment using BlobText nlp 
    '''
    blob = TextBlob(text_sample)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

def get_composite(vader, ibm, blob):
    '''
    Calculates average of min diff between three scores
    '''
    diff_1 = abs(vader-ibm)
    diff_2 = abs(ibm-blob)
    diff_3 = abs(vader-blob)
    min_diff = min(diff_1, diff_2, diff_3)
    if min_diff == diff_1:
        return ((vader+ibm)/2.0)
    elif min_diff == diff_2:
        return ((blob+ibm)/2.0)
    else:
        return ((vader+blob)/2.0)

def binary_composite(vader, ibm, blob):
    nums = []
    nums.append(vader)
    nums.append(ibm)
    nums.append(blob)
    options = [-1,1]
    pos_count = 0
    neg_count = 0
    for i in nums:
        if i > 0:
            pos_count += 1
        elif i < 0:
            neg_count += 1
        else:
            choice = random.choice(options)
            if choice < 0:
                neg_count += 1
            else:
                pos_count += 1
    if pos_count > neg_count:
        return 1
    else:
        return -1

def write_to_file(all_data):
    '''
    Takes master array of all data and outputs them to a .csv and .txt file for processing
    '''
    # print(all_data)
    #Make sure we're in same directory as script
    # os.mkdir(PATH_TO_SCRIPT_ + "argos-demo/voice-output/")
    os.chdir(PATH_TO_SCRIPT_ + "argos-demo/voice-output/")
    
    #open two output files
    data_filename = "Voice_5_Data_" + all_data[0][0] + ".csv"
    text_filename = "Voice_5_Text_" + all_data[0][0] + ".txt"
    f_data = open(data_filename, 'w')
    f_text = open(text_filename, 'w')
    f_data.write("time_stamp, elapsed_time, v_neutral, v_happy, v_sad, v_angry, v_fear, s_neg, s_neutral, s_pos, vader_sentiment, word_count, ibm_sentiment, blob_sentiment, composite, binary_composite\n")
    
    #Loop through all data and write to output
    count = 1
    prev_time = datetime.strptime(all_data[0][0], '%Y-%m-%d-%H-%M-%S')
    # curr_time = datetime.strptime(all_data[0][0], '%Y-%m-%d-%H-%M-%S')
    #print(all_data)
    for row in all_data:
        #print(row)
        vader_sentiment = row[9]
        ibm_sentiment = get_ibm_sent(str(row[10]))
        text_blob_sentiment = get_textblob_sent(str(row[10]))
        composite = get_composite(vader_sentiment, ibm_sentiment, text_blob_sentiment)
        bin_comp = binary_composite(vader_sentiment, ibm_sentiment, text_blob_sentiment)
        print("vader: " + str(vader_sentiment))
        print("ibm: " + str(ibm_sentiment))
        print("textblob: " + str(text_blob_sentiment))
        print("composite: " + str(composite))
        print("bin_composite: " + str(bin_comp))
        curr_time = datetime.strptime(row[0], '%Y-%m-%d-%H-%M-%S')
        print(Fore.MAGENTA + "Writing row " + str(count) + " for " + row[0])
        delta = curr_time - prev_time
        elapsed_time_total_str = str(delta.total_seconds())
        #print(elapsed_time_total_str)
        #Create filewriting strings 
        data_str = ""
        text_str = ""

        #Write appropriate data to correct output file
        for i in range(0,len(row)-1):
            data_str += str(row[i]) + ", "
            if (i==0):
                data_str += str(elapsed_time_total_str) + ", "
        text_str = str(row[0]) + ": " + str(row[len(row)-1])
        words = row[len(row)-1].split(" ")
        word_count = len(words)
        #print("Word count: " + str(word_count))
        #print("Before: " + str(data_str))
        data_str = data_str[:-2] # to remove last unecessary comma and space
        data_str += ", " + str(word_count)
        #print("After: " + str(data_str))
        data_str += ", "
        data_str += str(ibm_sentiment)
        data_str += ", "
        data_str += str(text_blob_sentiment)
        data_str += ", "
        data_str += str(composite)
        data_str += ", "
        data_str += str(bin_comp)
        data_str += "\n"
        text_str += "\n"
        f_data.write(data_str)
        f_text.write(text_str)

        count += 1
    f_data.close()
    f_text.close()

def plot_FEQ_data():
    '''
    Plot FEQ data 
    '''
    output_directory = PATH_TO_SCRIPT_ + "argos-demo/vision-dump/"
    all_files = []
    listdir = os.listdir(output_directory)
    listdir = sorted(listdir)
    for filename in listdir:
        if filename.endswith(".csv"):
            all_files.append(str(os.path.join(output_directory, filename)))
            #print(os.path.join(output_directory, filename))
            continue
        else:
            continue
    #print(all_files)
    os.chdir(PATH_TO_SCRIPT_ + "argos-demo/r-script")
    call = "Rscript FEQ_Plot.R " + all_files[0]
    print(call)
    os.system(call)

def plot_merge_data():
    '''
    Plot merge data
    '''
    output_directory = PATH_TO_SCRIPT_ + "argos-demo/vision-dump/"
    all_files = []
    listdir = os.listdir(output_directory)
    listdir = sorted(listdir)
    for filename in listdir:
        if filename.endswith(".csv"):
            all_files.append(str(os.path.join(output_directory, filename)))
            #print(os.path.join(output_directory, filename))
            continue
        else:
            continue
    output_directory = PATH_TO_SCRIPT_ + "argos-demo/voice-output"
    all_veq_files = []
    listdir = os.listdir(output_directory)
    listdir = sorted(listdir)
    for filename in listdir:
        if filename.endswith(".csv"):
            all_veq_files.append(str(os.path.join(output_directory, filename)))
            #print(os.path.join(output_directory, filename))
            continue
        else:
            continue
    # print(all_veq_files)
    # print(all_files)
    os.chdir(PATH_TO_SCRIPT_ + "argos-demo/r-script")
    call = "Rscript VEQ_Plot.R " + all_files[0] + " " + all_veq_files[0]
    print(call)
    os.system(call)
    pass

def plot_VEQ_data(all_data):
    '''
    Plot VEQ data

    Process raw string output from Vokaturi into array of audio emotions
    Order: [Neutral, Happy, Sad, Angry, Fear][neg, neu, pos, compound, text]
  
    '''
    #Initialize all empty arrays
    time = []
    neutral = []
    happy = []
    sad = []
    angry = []
    fear = []
    compound = []
    #get all data into arrays
    for i in all_data:
        time.append(i[0])
        neutral.append(i[1])
        happy.append(i[2])
        sad.append(i[3])
        angry.append(i[4])
        fear.append(i[5])
        compound.append(i[9])

    #Sanity printing
    # print(time)
    # print(neutral)
    # print(happy)
    # print(sad)
    # print(angry)
    # print(fear)
    # print(compound)

    trace_neutral = go.Scatter(
        x = time,
        y = neutral,
        name = 'Neutral',
        line = dict(
            color = ('rgb(140, 65, 244)'),
            width = 2.5,
            dash = 'dash')
    )

    trace_happy = go.Scatter(
        x = time,
        y = happy,
        name = 'Happy',
        line = dict(
            color = ('rgb(89, 244, 66)'),
            width = 2.5,
            dash = 'dash')
    )

    trace_sad = go.Scatter(
        x = time,
        y = sad,
        name = 'Sad',
        line = dict(
            color = ('rgb(65, 178, 244)'),
            width = 2.5,
            dash = 'dash')
    )

    trace_angry = go.Scatter(
        x = time,
        y = angry,
        name = 'Angry',
        line = dict(
            color = ('rgb(244, 65, 65)'),
            width = 2.5,
            dash = 'dash')
    )

    trace_fear = go.Scatter(
        x = time,
        y = fear,
        name = 'Fear',
        line = dict(
            color = ('rgb(244, 157, 65)'),
            width = 2.5,
            dash = 'dash')
    )
    trace_sentiment = go.Scatter(
        x = time,
        y = compound,
        name = 'Sentiment',
        line = dict(
            color = ('rgb(0, 0, 0)'),
            width = 4)
    )

    data = [trace_neutral, trace_happy, trace_sad, trace_angry, trace_fear, trace_sentiment ]

    # Edit the layout
    layout = dict(title = 'Audio Emotion over Session',
                xaxis = dict(title = 'Time'),
                yaxis = dict(title = 'Emotion Level'),
                )

    fig = dict(data=data, layout=layout)
    py.offline.plot(fig, filename='audio_emotion.html')


def move_files():
    '''
    move files

    Move all the processed files in one directory: processed_data
  
    '''

    # Go to the parent directory
    os.chdir(PATH_TO_SCRIPT_ + "argos-demo/")

    # Create directory if it does not exist
    os.system("mkdir " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")

    # copy the files
    os.system("cp " + PATH_TO_SCRIPT_ + "argos-demo/vision-dump/* " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")
    os.system("cp " + PATH_TO_SCRIPT_ + "argos-demo/voice-dump/* " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")
    os.system("cp " + PATH_TO_SCRIPT_ + "argos-demo/r-script/FEQ_plot.pdf " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")
    os.system("cp " + PATH_TO_SCRIPT_ + "argos-demo/voice-output/* " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")
    os.system("cp " + PATH_TO_SCRIPT_ + "argos-demo/r-script/Merged_VEQ_FEQ.pdf " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")
    os.system("cp " + PATH_TO_SCRIPT_ + "argos-demo/r-script/audio_emotion.html " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")
    os.system("cp " + PATH_TO_SCRIPT_ + "argos-demo/r-script/Audio_video_Merged.csv " + PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/")


############################################## DRIVER FUNCTION ##############################################

def main():
    '''Main driver'''

    ## TO - DO
    # write clean data script (which goes and cleans everything)
    ###################### DATA COLLECTION ####################### 
    t_init = time.localtime()
    
    # # handle vision kit component
    # print("\nKill Vision Kit scripts")

    # try:
    #     vision_kit_component()
    # except Exception as e:
    #     print(Fore.RED + "Error: " + str(e))
    #     return
    # print(Fore.GREEN + "DONE!\n")

    # # handle voice kit component
    # print("Kill Voice Kit scripts")
    # try:
    #     voice_kit_component()
    # except Exception as e:
    #     print(Fore.RED + "Error: " + str(e))
    #     return
    
    # # Finished collecting data! Do output printing
    # t_final = time.localtime()
    # elapsed_time = int(t_final.tm_sec) - int(t_init.tm_sec)
    # print(Fore.GREEN + "DONE!\n")
    # print(Back.GREEN + "Finished killing processes and downloading data in ~" + str(elapsed_time) + " seconds!")



    ####################### RUN FEQ PLOT #######################
    print("\nBegin FEQ Plotting")
    try:
        plot_FEQ_data()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")
    print(Back.GREEN + "Finished plotting all Merged (VEQ + FEQ) data!")

    # # ####################### AUDIO PROCESSING ####################### 

    #Master array to hold all audio data
    all_audio_data = []

    print("\nBegin Audio Processing")
    try:
        all_audio_data = process_audio_files()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")
    print(Back.GREEN + "Finished processing all audio data!")

    print("\nBegin Writing Data")
    try:
        write_to_file(all_audio_data)
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")
    print(Back.GREEN + "Finished writing audio data!")
    

####################### RUN MERGE PLOTS #######################

    print("\nBegin Marged Plotting")
    try:
        plot_merge_data()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")
    print(Back.GREEN + "Finished plotting all VEQ data!")


    ####################### RUN VEQ PLOTS #######################

    # print("\nBegin VEQ Plotting")
    # try:
    #     plot_VEQ_data(all_audio_data)
    # except Exception as e:
    #     print(Fore.RED + "Error: " + str(e))
    #     return
    # print(Fore.GREEN + "DONE!\n")
    # print(Back.GREEN + "Finished plotting all VEQ data!")

    ####################### Output Printing #######################

    
    ###################### move all processed data in a directory #######################

    print("\nMoving processed files to directory zprocessed_data")
    try:
        move_files()
    except Exception as e:
        print(Fore.RED + "Error: " + str(e))
        return
    print(Fore.GREEN + "DONE!\n")
    print(Back.GREEN + "Finished moving directories!")

    ####################### Output Printing #######################


    print("\n")
    t_end = time.localtime()
    elapsed_time_total = int(t_end.tm_sec) - int(t_init.tm_sec)
    print(Back.LIGHTGREEN_EX + "Finished Script. Total time: ~" + str(elapsed_time_total) + " seconds!")
     
if __name__ == '__main__':
    main()
