import arxiv
import urllib.request as libreq
import feedparser
from io import StringIO
from pathlib import Path
import os
import argparse
import tokenizeText
import re


#Set location of saved abstracts
AbstractsDir = r'C:\Users\Al\Documents\ByteSizeArxiv\Abstracts'
#Set date 
#TheDate = "2020-06-01"
#Set category
#See Categories in Categories.txt, cs.LG = Machine Learning
Category = 'cs.LG'

#Run a query by Arxiv category
#Returns arrays of Entries, PDF's, and Abstracts
def queryByCat(Category):

    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?'

    # Search parameters
    #search_query = 'cat:cs.LG' # search in the machine learning category
    search_query = Category
    #max_results = maxResults
    #max_results = 100
    # Search parameters
    #search_query = 'cat:cs.LG' # search in the machine learning category

    query = 'search_query=%s&max_results=100&sortBy=submittedDate&sortOrder=descending' % (search_query)                                                
                                                
    #List of paper entries with all info
    corpusEntry=[]
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
    theDate = feed.entries[0].published[0:10]
    for entry in feed.entries:
        if entry.updated[0:10] == theDate:
            corpusEntry.append(entry)

    return corpusEntry, theDate

#Download the PDF's and save them as their Entry ID
def saveTXT(corpusEntry,theDate):
    library = Path(AbstractsDir) / theDate
    if not os.path.exists(library):
        os.makedirs(library)
    for paper in corpusEntry:
        theID = paper.id.rsplit('/',1)[1]
        newFile = Path(library / (theID+".txt")) 

        with open(newFile, 'a+') as myfile:
            myfile.write(prePro(paper.title) + "\n#####\n" +prePro(paper.summary))

#Preprocess the text into bullets
def prePro(text):
    cleanedText=text
    cleanedText = re.sub(r'(\(([^)^(]+)\))','',cleanedText) #removes everything inside of parentheses, have to re-run for nested
    cleanedText = re.sub(r'(\[([^]^[]+)\])','',cleanedText) #removes everything inside of square brackets
    cleanedText = re.sub(r'(\{([^}^{]+)\})','',cleanedText) #removes everything inside of curly brackets 
    cleanedText = re.sub(r'[^\w^\s^.]',' ', cleanedText) #Remove all characters not [a-zA-Z0-9_] excluding spaces and periods
    cleanedText = re.sub(r'\d','', cleanedText) #Remove all numbers
    cleanedText = re.sub(r'(\. ){2,}', '. ', cleanedText).strip() #Replace all multiple period spaces with one
    return cleanedText
#Return Abstracts to pass them on to split abstract and the rest
def main(category):
    #run query
    corpusEntry,theDate = queryByCat(category)
    #download new pdf's
    saveTXT(corpusEntry,theDate)
    tokenizedPath = Path(AbstractsDir)/ theDate / "Tokenized"
    if not os.path.exists(tokenizedPath):
        os.makedirs(tokenizedPath)
    tokenizeText.main(Path(AbstractsDir) / theDate ,tokenizedPath)
    #print (corpusAbstract)
    return corpusEntry

if __name__ == "__main__":
    main(Category)