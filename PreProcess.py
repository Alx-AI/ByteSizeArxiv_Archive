from pycontractions import Contractions
from PyPDF2 import PdfFileWriter, PdfFileReader #for deleting all images
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer 
import numpy as np  
import pandas as pd   
from io import StringIO
from bs4 import BeautifulSoup as bs
import nltk
import re
import heapq
import boto3
from pdfminer.layout import LAParams
import pdfminer.layout
import pdfminer.high_level
import os

#from keras.preprocessing.text import Tokenizer 
#from keras.preprocessing.sequence import pad_sequences  
#from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed, Bidirectional
#from tensorflow.keras.models import Model
#from tensorflow.keras.callbacks import EarlyStopping
import warnings
ps = PorterStemmer() 

#Convert papers from PDF to text
def convertPDF(activePDF):
    text = pdfminer.high_level.extract_text(activePDF, codec='utf-8', laparams=None)
    return text

#Clean the text
def cleanText(text):
    cleanedText = str(text)
    if "\nReferences\n" in text:
        cleanedText = cleanedText.rsplit("\nReferences\n", 1)[0] #Removes all references, starts from back
    cleanedText = re.sub(r"(\x0c)", '', cleanedText) #Remove page breaks and other pdf injections any combination of \x then two non whitespace characters
    cleanedText = re.sub(r'-\n','', cleanedText)
    cleanedText = re.sub(r'\n-','', cleanedText) #Hyphens before & after new lines are usually added for continuation of a word
    cleanedText = re.sub(r'\n',' ',cleanedText)#Get rid of new lines replace with spaces
    #Remove everything between parentheses or brackets 3 times to get most equations but leave most of the text
    for x in range(0,2):
        cleanedText = re.sub(r'(\(([^)^(]+)\))','',cleanedText) #removes everything inside of parentheses, have to re-run for nested
        cleanedText = re.sub(r'(\[([^]^[]+)\])','',cleanedText) #removes everything inside of square brackets
        cleanedText = re.sub(r'(\{([^}^{]+)\})','',cleanedText) #removes everything inside of curly brackets 
    cleanedText = re.sub(r'[^\w^\s^.]',' ', cleanedText) #Remove all characters not [a-zA-Z0-9_] excluding spaces and periods
    cleanedText = re.sub(r'\d','', cleanedText) #Remove all numbers
    cleanedText = re.sub(r' {2,}', ' ', cleanedText).strip() #Replace all multiple spaces with one space
    cleanedText = re.sub(r'(\. ){2,}', '. ', cleanedText).strip() #Replace all multiple period spaces with one space
    cleanedText = re.sub(r'(\s\.\s)', '. ', cleanedText).strip() #Replace all space period space with period space
    cleanedText = str(cleanedText)
    cleanedText = cleanedText.lower()
    return cleanedText

#Split the abstract and the rest of the paper after text was cleaned & clean the abstract
def splitText(cleanedText, abstract):
    cleanedAbs = cleanText(abstract)
    #get the last 10 characters of the abstract to split 
    lastWords = cleanedAbs[-10:]
    #ideally split at the last word of the abstract if it is the same
    if lastWords in cleanedText:
        cleanedBody = cleanedText.split(lastWords,1)[1]#Takes second part
    #Otherwise split at "introduction"
    elif "introduction" in cleanedText:
        cleanedBody = cleanedText.split("introduction",1)[1]
    #Otherwise split at abstract and remove the next 500 characters
    elif "abstract" in cleanedText:
        cleanedBody = cleanedText.split("abstract",1)[1]
        cleanedBody = cleanedBody[500:]
    #If nothing found, chop off the first 650 and hope for the best
    else:
        cleanedBody = cleanedText[650:]

    
    return cleanedBody, cleanedAbs 

#Combine cleaned abstract and text for saving
def concatText(cleanedAbs, cleanedBody):
    cleanedText = cleanedAbs + "\n" + "#####" + "\n" + cleanedBody
    return cleanedText

#Save the cleaned paper (abstract and body) in a .txt file
def savePaper(cleanedText, name, saveDir):
    #Create the whole path
    savePath = saveDir + '/' + name + '.txt'

    with open(str(savePath), 'w',encoding="utf8",newline='') as txtFile:
        txtFile.write(str(cleanedText))
    print (cleanedText)
        

#Go through preprocessing every file, return list of cleaned text combined with abstract and body separated by ##### and their IDs
def preprocessLibrary(libraryDir, libraryAbs):
    libraryPath = libraryDir + r'/library.txt'
    #iterate through each file
    with open(libraryPath) as lib:
        #create list that will be returned
        cleanedPapers = []
        names = []
        for idx, line in enumerate(lib):
            #the name of the pdf is the last 13 characters of the links saved in the library
            #name = line[-13:]
            #print(line)
            name = line.rsplit('/',1)[1]
            name = re.sub(r'\n','', name)
            activePDF = libraryDir + '/' + name + '.pdf'
            #Convert pdf to a string
            text = convertPDF(activePDF)
            #clean the text including removing artifacts of conversion
            cleanedText = cleanText(text)
            #clean the abstract and split the body and abstract to put together more clearly
            cleanedBody , cleanedAbs = splitText(cleanedText,libraryAbs[idx])
            cleanedText = concatText(cleanedAbs , cleanedBody)
            #Append to list
            cleanedPapers.append(cleanedText)
            names.append(name)
    return cleanedPapers, names



def main(corpusAbstracts,libraryDir = r'C:\Users\Al\Documents\ByteSizeArxiv\library'):
    cleanedPapers,names = preprocessLibrary(libraryDir,corpusAbstracts)
    for idx, paper in enumerate(cleanedPapers):
        savePaper(paper,names[idx],libraryDir)

if __name__ == "__main__":
    main()
        
         






    