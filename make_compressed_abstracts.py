import arxiv
import urllib.request as libreq
import feedparser
from io import StringIO
from pathlib import Path
import os
import argparse
import tokenizeText
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.sparse.csr import csr_matrix
import glob


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
        prePro(paper.title)
        print (newFile)
        with open(newFile, 'a+') as myfile:
            myfile.write(prePro(paper.title) + "#####" +prePro(paper.summary))

#Preprocess the text into bullets
def prePro(text):
    cleanedText=text
    cleanedText = re.sub(r'\n',' ',cleanedText)#Get rid of new lines replace with spaces
    cleanedText = re.sub(r'(\(([^)^(]+)\))','',cleanedText) #removes everything inside of parentheses, have to re-run for nested
    cleanedText = re.sub(r'(\[([^]^[]+)\])','',cleanedText) #removes everything inside of square brackets
    cleanedText = re.sub(r'(\{([^}^{]+)\})','',cleanedText) #removes everything inside of curly brackets 
    cleanedText = re.sub(r'[^\w^\s^.]',' ', cleanedText) #Remove all characters not [a-zA-Z0-9_] excluding spaces and periods
    cleanedText = re.sub(r'\d','', cleanedText) #Remove all numbers
    cleanedText = re.sub(r'(\. ){2,}', '. ', cleanedText).strip() #Replace all multiple period spaces with one
    return cleanedText

#make a tfidf vectoruzer
def tfIDF(corpusEntry):
    corpusSumm = []
    for entry in corpusEntry:
        corpusSumm.append(prePro(entry.summary))
    tf = TfidfVectorizer()
    tfidf_matrix =  tf.fit_transform(corpusSumm)
    feature_names = tf.get_feature_names()
    doc = 0
    feature_index = tfidf_matrix[doc,:].nonzero()[1]
    index_names = []
    for i in feature_index:
        index_names.append(feature_names[i])
    tfidf_scores = zip(index_names, [tfidf_matrix[doc,x] for x in feature_index])
    tfidf_dict = dict(tfidf_scores)
    return tfidf_dict

#Compress the abstract
def compress(tokenizedDir,tfidf_dict):
    library = []
    tokenizedDir = str(tokenizedDir)
    theFiles = glob.glob((tokenizedDir+"\*.txt"))
    for files in theFiles:
        with open(files, 'r') as theFile:
            for entry in theFile:
                #Get rid of the title
                title,entry = entry.split('#####')
                #Lists to hold the highest scoring sentences and their scores
                top3_sentences = []
                top3_scores = []
                for sentence in entry.split("."):
                    #how many scores are higher in top3 than this sentence, if all 3, delete and replace, otherwise delete lowest
                    higherScores =0
                    sentenceTotal = 0
                    index = 0
                    #keep track of words / sentence to get average score
                    word_count=0
                    for word in sentence.split(" "):
                        #Add up all of the tf_idf scores
                        if word.lower() in tfidf_dict:
                            sentenceTotal = sentenceTotal +tfidf_dict[word.lower()]
                    #Average by word
                        word_count = word_count + 1
                    sentenceTotal = sentenceTotal / word_count
                    min_score = 1000
                    #get index of min score and append if should
                    if top3_sentences:
                        #print (top3_scores)
                        if len(top3_scores) == 3:
                            for idx, score in enumerate(top3_scores):
                                if score > sentenceTotal:
                                    higherScores = higherScores+1
                                elif score < min_score:
                                    index = idx
                                    min_score = score
                            if higherScores <3:
                                del top3_sentences[index]
                                del top3_scores[index]
                                top3_sentences.append(sentence)
                                top3_scores.append(sentenceTotal)
                        else:
                            top3_sentences.append(sentence)
                            top3_scores.append(sentenceTotal)
                    else:
                        top3_sentences.append(sentence)
                        top3_scores.append(sentenceTotal)
            theFile.close()
        with open(files, 'w') as theFile:
            theFile.write(title + "\n")
            for sentence in top3_sentences:
                theFile.write(sentence[1:]+"\n")

                     


#Return Abstracts to pass them on to split abstract and the rest
def main(category):
    #run query
    corpusEntry,theDate = queryByCat(category)
    dictionary = tfIDF(corpusEntry)
    saveTXT(corpusEntry,theDate)
    tokenizedPath = Path(AbstractsDir)/ theDate / "Tokenized"
    if not os.path.exists(tokenizedPath):
        os.makedirs(tokenizedPath)
    tokenizeText.main(Path(AbstractsDir) / theDate ,tokenizedPath)
    compress(tokenizedPath, dictionary)
    #print (corpusAbstract)
    return corpusEntry

if __name__ == "__main__":
    main(Category)