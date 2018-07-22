import speech_recognition as sr 
import sys
import string
from pydub import AudioSegment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

def print_sentiment_scores(sentence):
    sentence = sentence.replace("%HESITATION","")
    snt = analyser.polarity_scores(sentence)
    print("{:-<40}\n {}".format(sentence, str(snt)))

#file_name = "subir_today.wav"
file_name = sys.argv[1]
sound = AudioSegment.from_wav(file_name)
sound = sound.set_channels(1)
sound.export(file_name, format="wav")

r = sr.Recognizer() 
with sr.WavFile(file_name) as source: # use "test.wav" as the audio source 
    audio = r.record(source) # extract audio data from the file 

    try: 
        #speech = r.recognize_google(audio)
        # speech = r.recognize_ibm(audio,"91dcd1fe-307c-4b57-bcf7-15910f5ae5a7", "RnGMjQHw6OdW")
        speech = r.recognize_ibm(audio,"762f68db-a6af-4a41-b9e9-460405d7d383", "bycO08RLw2lo")
        # speech = r.recognize_ibm(audio,"0338bf84-8097-4d7f-bdfe-e7050264750f", "ICf3LZxK2vc3")
        #speech = r.recognize_ibm(audio,"5dc6de3b-2af9-4742-8d63-982e392f5398", "kM0kLnLeV2kE")
        print_sentiment_scores(speech)
        #print("Transcription: " + speech) # recognize speech using Google Speech Recognition 
    except: # speech is unintelligible 
        #continue
        print_sentiment_scores("NULL")
        #print("Couldn't process audio") 
