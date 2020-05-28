import arxiv
import urllib.request as libreq
import feedparser
from io import StringIO
from pathlib import Path
import os
import argparse

#from keras.preprocessing.text import Tokenizer 
#from keras.preprocessing.sequence import pad_sequences  
#from tensorflow.keras.layers import Input, LSTM, Embedding, Dense, Concatenate, TimeDistributed, Bidirectional
#from tensorflow.keras.models import Model
#from tensorflow.keras.callbacks import EarlyStopping
import warnings
os.environ['LIB'] = r'C:\Users\Al\Documents\ByteSizeArxiv\library'
os.environ['DATA'] = r'C:\Users\Al\Documents\ByteSizeArxiv\library\Finished'

#Run a query by Arxiv category, in our case "cat:cs.LG" for machine learning
#Returns arrays of Entries, PDF's, and Abstracts
def queryByCat(Category, maxResults):

    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?'

    # Search parameters
    #search_query = 'cat:cs.LG' # search in the machine learning category
    search_query = Category
    start = 2000                     # retreive the first 5 results
    #max_results = maxResults
    max_results = 50
    # Search parameters
    #search_query = 'cat:cs.LG' # search in the machine learning category

    query = 'search_query=%s&start=%i&max_results=%i&submitted_date=' % (search_query,
                                                        start,
                                                        max_results)                                                    
                                                
    #List of paper entries with all info
    corpusEntry=[]
    #Corresponding list of pdf download links 
    corpusPDF=[]
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
        # get the links to the abs page and pdf for this e-print
        for link in entry.links:
            if link.rel == 'alternate':
                fillerVar = 0
                #print ('abs page link: %s' % link.href)
            elif link.title == 'pdf':
                corpusPDF.append({"pdf_url": link.href})
                #print ('pdf link: %s' % link.href)
        
        # The abstract is in the <summary> element
        #print ('Abstract: %s' %  entry.summary)
        corpusAbstract.append(entry.summary)
    return corpusEntry, corpusPDF, corpusAbstract

#Download the PDF's and save them as their Entry ID
def downloadNewPDFS(corpusEntry, corpusPDF, maxResults):
    library = Path(os.environ['LIB'])
    toDownload = library / "toDownload.txt"
    library = library / "library.txt"
    
    for i in range(0, maxResults):
        write = True
        with open(library, 'r+') as myfile:
            fileinQ= corpusPDF[i]['pdf_url']
            if  fileinQ in myfile.read():
                write = False
            else:
                if not os.stat(library).st_size==0:
                    myfile.write("\n")
                myfile.write(fileinQ)
            myfile.close()

        if write:
            with open(toDownload, 'a+') as myfile:
                fileinQ= corpusPDF[i]['pdf_url']
                if not os.stat(toDownload).st_size==0:
                    myfile.write("\n")
                myfile.write(fileinQ)
                myfile.close()
                # Override the default filename format by defining a slugify function. So can force pdf link for all even without listed
            arxiv.download(corpusPDF[i],os.environ['LIB'], slugify=lambda x: corpusEntry[i].get('id').split('/')[-1])

                


#Return Abstracts to pass them on to split abstract and the rest
def main(category ,maxResults):
    #create arrays for the corpus entries as a whole, the pdf download links, and the abstracts
    corpusEntry, corpusPDF, corpusAbstract = [],[],[]
    #run query
    corpusEntry, corpusPDF, corpusAbstract = queryByCat(category, maxResults)
    #download new pdf's
    downloadNewPDFS(corpusEntry, corpusPDF, maxResults)
    #print (corpusAbstract)
    return corpusAbstract

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Category and number of results to download')
    parser.add_argument('--category', type=str, default = 'cat:cs.LG', 
                        help = 'the arxiv category from which to download new papers')
    parser.add_argument('--results', type=int, default = '50', 
                        help = 'the number of most recent papers to query')
    args = parser.parse_args()                   
    main(category = args.category, maxResults = args.results)



