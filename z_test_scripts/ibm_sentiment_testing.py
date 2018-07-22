#!/usr/bin/env python3

# sudo pip3 install --upgrade watson-developer-cloud

from global_paths import *
import base64
import time
from datetime import datetime
import subprocess
import os
import sys
import math
#plotly tools
import paramiko
import plotly as py
import plotly.graph_objs as go
from plotly import tools

#Pretty print
import colorama
from colorama import Fore, Back
from colorama import init
init(autoreset=True)

import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import SentimentOptions, Features, EntitiesOptions, KeywordsOptions

natural_language_understanding = NaturalLanguageUnderstandingV1(
  username='68d14296-27cb-4978-a875-07ffab179040',
  password='pZiUbN7M7V5c',
  version='2018-03-16')

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

def get_file_paths():
    '''
    Retrieve file paths pointing to csv and txt files
    '''
    print(Fore.MAGENTA + "\nBegin Looking for files in directory")
    #Loop through to find .txt
    output_directory = PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/"
    all_files = []
    listdir = os.listdir(output_directory)
    listdir = sorted(listdir)
    for filename in listdir:
        if filename.endswith(".txt"):
            all_files.append(str(os.path.join(output_directory, filename)))
            #print(os.path.join(output_directory, filename))
            continue
        else:
            continue
    text_file_name = all_files[0]
    print(Fore.YELLOW + "Found: " + text_file_name)

    #Loop through to find .csv
    output_directory = PATH_TO_SCRIPT_ + "argos-demo/zprocessed_files/"
    all_files_1 = []
    listdir = os.listdir(output_directory)
    listdir = sorted(listdir)
    for filename in listdir:
        if filename.endswith(".csv"):
            all_files_1.append(str(os.path.join(output_directory, filename)))
            #print(os.path.join(output_directory, filename))
            continue
        else:
            continue
    csv_file_name = all_files_1[0]
    print(Fore.YELLOW + "Found: " + csv_file_name)
    print(Fore.GREEN + "DONE!")
    #returrn text_file_name and csv_file_name
    return text_file_name, csv_file_name 

def add_ibm_sentiment(text_file, csv_file):
    '''
    1. Takes text, calculates ibm sentiment for each line
    2. Appends them to existing csv file
    '''
    # Parse text file and extract sentiment
    print(Fore.MAGENTA + "\nBegin Parsing text and analyzing sentiment")
    sentiment_list = []
    f = open(text_file,"r")
    for line in f:
        line_split = line.split(":")
        text = str(line_split[1])
        #print(text)
        sentiment_list.append(get_ibm_sent(text))
    f.close()
    print(sentiment_list)
    print(Fore.GREEN + "DONE!")

    print(Fore.MAGENTA + "\nBegin Parsing csv for data")
    
    # Parse csv file and extract lines
    f = open(csv_file,"r")
    csv_lines = []
    for line in f:
        csv_lines.append(line)
    f.close()
    print("csv_length: " + str(len(csv_lines)-1))
    
    print(Fore.GREEN + "DONE!")
    print(Fore.MAGENTA + "\nBegin adding data and writing to new csv")
    
    #Add header
    csv_lines[0] = csv_lines[0][:-1]
    csv_lines[0] += ', ibm_sentiment'
    csv_lines[0] += ', sentiment_difference'

    #add ibm sentiment in each line
    vader_sentiment_list= []
    difference_list = []
    for i in range(1,len(csv_lines)):
        csv_lines[i] = csv_lines[i][:-1]
        csv_lines[i] += ", " 
        csv_lines[i] += str(sentiment_list[i-1])
        comma_split = csv_lines[i].split(",")
        vader_score = float(comma_split[10])
        vader_sentiment_list.append(vader_score)
        difference = abs(float(vader_score) - float(sentiment_list[i-1]))
        difference_list.append(difference)
        
        csv_lines[i] += ", " 
        csv_lines[i] += str(difference)
        
        #print(vader_score)
        print(csv_lines[i])
    # print(sentiment_list)
    # print(len(sentiment_list))
    # print(text_file)
    # print(csv_file)
    #final output
    f = open(csv_file,"w")
    for line in csv_lines:
        f.write(line)
        f.write("\n")
    f.close()
    
    print(sentiment_list)
    print(vader_sentiment_list)
    print(difference_list)

    # trace_scatter = go.Scatter(
    #     x = time,
    #     y = neutral,
    #     name = 'Neutral',
    #     line = dict(
    #         color = ('rgb(140, 65, 244)'),
    #         width = 2.5,
    #         dash = 'dash')
    # )

    # trace = go.Scatter(
    #     x = random_x,
    #     y = random_y,
    #     mode = 'markers'
    # )

    trace1 = go.Scatter(
        x = sentiment_list,
        y = vader_sentiment_list,
        mode='markers',
        marker=dict(
            size='16',
            color = difference_list, #set color equal to a variable
            colorscale='Viridis',
            showscale=True
        )
    )
    data = [trace1]
    layout = dict(title = 'Vader vs IBM',
                xaxis = dict(title = 'Vader'),
                yaxis = dict(title = 'IBM'),
                )

    fig = dict(data=data, layout=layout)
    py.offline.plot(fig, filename='vader_ibm.html')
    # trace_difference = go.Scatter(
    #     x = time,
    #     y = happy,
    #     name = 'Happy',
    #     line = dict(
    #         color = ('rgb(89, 244, 66)'),
    #         width = 2.5,
    #         dash = 'dash')
    # )

    #final output
    f = open(csv_file,"w")
    for line in csv_lines:
        f.write(line)
        f.write("\n")
    f.close()


    print(Back.GREEN + Fore.BLACK + "\n!DONE WITH SCRIPT!")

def main():
    text= "which you can keep reading that night. my god I like saying that it is a big time they have big expectations yeah I'll take that as like a lot of the problem is they think that maybe can deliver yet nowhere to go but down after that at. so where you are at the ripe old age of something decide."

    #Parse and determine text and csv files in zprocessed
    text_file, csv_file = get_file_paths()

    #add ibm sentiment to csv file
    add_ibm_sentiment(text_file, csv_file)
    
if __name__ == '__main__':
    main()