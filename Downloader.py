import arxiv
import urllib.request as libreq
import feedparser
import pdfminer.layout
import pdfminer.high_level
from io import StringIO
from pdfminer.layout import LAParams
from bs4 import BeautifulSoup as bs
import nltk
import re
import heapq
import boto3
import pdfminer3
import os
from pycontractions import Contractions
from PyPDF2 import PdfFileWriter, PdfFileReader #for deleting all images
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from nltk.stem import PorterStemmer 
import numpy as np  
import pandas as pd   
#from keras.preprocessing.text import Tokenizer 
#from keras.preprocessing.sequence import pad_sequences  
#from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed, Bidirectional
#from tensorflow.keras.models import Model
#from tensorflow.keras.callbacks import EarlyStopping
import warnings
ps = PorterStemmer() 



def queryByCat(Category, maxResults):
    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?'

    # Search parameters
    #search_query = 'cat:cs.LG' # search in the machine learning category
    search_query = Category
    start = 10000                     # retreive the first 5 results
    max_results = maxResults

    query = 'search_query=%s&start=%i&max_results=%i' % (search_query,
                                                        start,
                                                        max_results)
    #List of paper entries with all info
    corpusEntry=[]
    #Corresponding list of pdf download links 
    corpusPDF=[]
    #Corresponding list of Paper ID's
    corpusID = []
    #Corresponding list of Paper Abstracts
    corpusAbstract = []
    # Opensearch metadata such as totalResults, startIndex, 
    # and itemsPerPage live in the opensearch namespase.
    # Some entry metadata lives in the arXiv namespace.
    # This is a hack to expose both of these namespaces in
    # feedparser v4.1
    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'

    # perform a GET request using the base_url and query
    with libreq.urlopen(base_url+query) as url:
        response = url.read()

    # parse the response using feedparser
    feed = feedparser.parse(response)


    # Run through each entry, and print out information
    for entry in feed.entries:
        corpusEntry.append(entry)
        corpusID.append(entry.id.split('/abs/')[-1])
        # feedparser v4.1 only grabs the first author
        author_string = entry.author
        
        # grab the affiliation in <arxiv:affiliation> if present
        # - this will only grab the first affiliation encountered
        #   (the first affiliation for the first author)
        # Please email the list with a way to get all of this information!
        try:
            author_string += ' (%s)' % entry.arxiv_affiliation
        except AttributeError:
            pass

        # get the links to the abs page and pdf for this e-print
        for link in entry.links:
            if link.rel == 'alternate':
                print ('abs page link: %s' % link.href)
            elif link.title == 'pdf':
                corpusPDF.append({"pdf_url": link.href})
                #print ('pdf link: %s' % link.href)
        
        # The journal reference, comments and primary_category sections live under 
        # the arxiv namespace
        try:
            journal_ref = entry.arxiv_journal_ref
        except AttributeError:
            journal_ref = 'No journal ref found'
        #print ('Journal reference: %s' % journal_ref)
        
        try:
            comment = entry.arxiv_comment
        except AttributeError:
            comment = 'No comment found'
        #print ('Comments: %s' % comment)
        
        # Since the <arxiv:primary_category> element has no data, only
        # attributes, feedparser does not store anything inside
        # entry.arxiv_primary_category
        # This is a dirty hack to get the primary_category, just take the
        # first element in entry.tags.  If anyone knows a better way to do
        # this, please email the list!
       # print ('Primary Category: %s' % entry.tags[0]['term'])
        
        # Lets get all the categories
        all_categories = [t['term'] for t in entry.tags]
        #print ('All Categories: %s' % (', ').join(all_categories))
        
        # The abstract is in the <summary> element
        print ('Abstract: %s' %  entry.summary)
        corpusAbstract.append(entry.summary)
    return corpusEntry, corpusPDF, corpusAbstract

def downloadNewPDFS(corpusEntry, corpusPDF, maxResults):
    library = r'C:\Users\Al\Documents\ByteSizeArxiv\library'
    for i in range(0, maxResults-1):
        with open(r'C:\Users\Al\Documents\ByteSizeArxiv\library/library.txt', 'r+') as myfile:
            if  corpusPDF[i]['pdf_url'] not in myfile.read():
                myfile.write(corpusPDF[i]['pdf_url'])
                myfile.write("\n")
                # Override the default filename format by defining a slugify function. So can force pdf link for all even without listed
                arxiv.download(corpusPDF[i],library, slugify=lambda x: corpusEntry[i].get('id').split('/')[-1])
                



def main():
    #define category to query by and how many to query
    category = 'cat:cs.LG'
    maxResults = 10
    #create arrays for the corpus entries as a whole, the pdf download links, and the abstracts
    corpusEntry, corpusPDF, corpusAbstract = [],[],[]
    #run query
    corpusEntry, corpusPDF, corpusAbstract = queryByCat(category, maxResults)
    #download new pdf's
    downloadNewPDFS(corpusEntry, corpusPDF, maxResults)

if __name__ == "__main__":
    main()



