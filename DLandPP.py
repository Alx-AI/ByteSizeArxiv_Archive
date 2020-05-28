import arxiv
import urllib.request as libreq
import feedparser
import pdfminer.layout
import pdfminer.high_level
from io import StringIO
from pdfminer.layout import LAParams
import pdfminer3
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
import os
import Downloader
import PreProcess
import tokenizeText
import time
from pathlib import Path
start_time= time.time()
#Change this directory to where you want the pre-processed text files
os.environ['LIB'] = r'C:\Users\Al\Documents\ByteSizeArxiv\library'
os.environ['DATA'] = r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished'
#Downloads and pre-processes files, saving the text locally & times it 
def main():
    corpusAbstracts = Downloader.main('cat:cs.LG', 50)
    PreProcess.main(corpusAbstracts,os.environ['LIB'])
    tokenizeText.main(os.environ['LIB'],os.environ['DATA'])

if __name__ == "__main__":
    main()
    print(time.time()-start_time)


