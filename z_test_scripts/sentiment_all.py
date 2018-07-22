#!/usr/bin/env python3

from global_paths import *
import base64
import time
import random
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

#ALL NLP IMPORTS
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import SentimentOptions, Features, EntitiesOptions, KeywordsOptions
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

analyser = SentimentIntensityAnalyzer()
natural_language_understanding = NaturalLanguageUnderstandingV1(
  username='68d14296-27cb-4978-a875-07ffab179040',
  password='pZiUbN7M7V5c',
  version='2018-03-16')


def get_vader_sent(text_sample):
    '''
    Analyze sentiment using vader
    '''
    snt = analyser.polarity_scores(text_sample)
    return snt["compound"]

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

def get_all_sent(text_sample):
    '''
    Analyze sentiment using BlobText nlp 
    '''
    blob = TextBlob(text_sample)
    print("\nTextBlob: ")
    for sentence in blob.sentences:
        try:
            print("vader: " + str(get_vader_sent(str(sentence))))
            print("ibm: " + str(get_ibm_sent(str(sentence))))
            print("blob: " + str(sentence.sentiment.polarity))
            print("\n")
        except:
            continue
    #sentiment_score = blob.sentiment.polarity
    #return sentiment_score

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

def extract_all_files():
    '''
    Retrieve file paths pointing to csv
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
    
    print(Fore.YELLOW + "Found: " + str(len(all_files)))
    return all_files

def read_and_write(all_files):
    f_out = open("all_sent_out.csv","w")
    f_out.write("vader, ibm, blob, composite\n")
    #Parse through all files
    count = 1
    for file in all_files:
        print(Fore.BLUE + "Analyzing[" + str(count)+"]: " + str(file))
        f = open(file,"r")
        #For each line split and keep text
        for line in f:
            split_line = line.split(':')
            text = split_line[1]
            #Get scores
            vader_score = get_vader_sent(text)
            ibm_score = get_ibm_sent(text)
            blob_score = get_textblob_sent(text)
            composite = get_composite(vader_score,ibm_score,blob_score)
            output_line = str(vader_score) + ", " + str(ibm_score) + ", " + str(blob_score) + ", " + str(composite) + "\n"
            f_out.write(output_line)
            print(output_line)
        f.close()
        count += 1
    f_out.close()

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
def main():    
    
    # #Extract all files
    # all_files = extract_all_files()

    # #Read and write
    # read_and_write(all_files)
    # text = '''
    # wow that was great! I'm so glad you've joined our team. Phil is a terrible coworker though, he never talks to us. I'm so happy about our new repository.
    # '''
    # print(get_vader_sent(text))
    # print(get_ibm_sent(text))
    # print(get_textblob_sent(text))
    #get_all_sent(text)
    print(binary_composite(1,0,-.3))
    
if __name__ == '__main__':
    main()