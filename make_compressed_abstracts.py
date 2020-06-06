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
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction import stop_words
import numpy as np
from scipy.sparse.csr import csr_matrix
import glob



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
    print(query)                                                
                                                
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
    
    ##theDate = feed.entries[0].published[0:10]
    theDate = '2020-06-02'  
    dates =['2020-05-31' ,'2020-06-01' ,'2020-06-02' ,'2020-06-03' ,'2020-06-04']
    totalCorpus = []
    for date in dates:
        corpus_Entry = []
        for entry in feed.entries:
            print(entry.published)
            if entry.published[0:10] == date:
                print("added")
                corpus_Entry.append(entry)
        totalCorpus.append(corpus_Entry)


    return totalCorpus, dates

#Download the PDF's and save them as their Entry ID
def saveTXT(corpusEntry,theDate,category):
    library = Path(AbstractsDir) / category / theDate 
    if not os.path.exists(library):
        os.makedirs(library)
    for paper in corpusEntry:
        if paper.published[0:10] ==theDate:
            library = Path(AbstractsDir) / category / theDate
            theID = paper.id.rsplit('/',1)[1]
            newFile = Path(library / (theID+".txt")) 
            #print (newFile)
            if not os.path.exists(newFile):
                with open(newFile, 'r+', encoding = 'utf-8') as myfile:
                    myfile.write(prePro(paper.title) + " ##### " +prePro(paper.summary))
            library = Path(AbstractsDir) / category
            newFile = Path(library / "Dictionary" / (theID+".txt")) 
            #print (newFile)
            if not os.path.exists(newFile):
                with open(newFile, 'r+', encoding = 'utf-8') as myfile:
                    myfile.write(prePro(paper.title) + " ##### " +prePro(paper.summary))

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

#For use in tf-idf
def extract_topn_from_vector(feature_names, sorted_items):
    """get the feature names and tf-idf score of top n items"""
    
    #use only topn items from vector
    #sorted_items = sorted_items[:topn]

    score_vals = []
    feature_vals = []

    for idx, score in sorted_items:
        fname = feature_names[idx]
        
        #keep track of feature name and its corresponding score
        score_vals.append(round(score, 3))
        feature_vals.append(feature_names[idx])

    #create a tuples of feature,score
    #results = zip(feature_vals,score_vals)
    results= {}
    for idx in range(len(feature_vals)):
        results[feature_vals[idx]]=score_vals[idx]
    
    return results

#for use in tfidf
def sort_coo(coo_matrix):
    tuples = zip(coo_matrix.col, coo_matrix.data)
    return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

#make a tfidf vectoruzer
def tfIDF(dictionary_Dir):
    stop_Words = stop_words.ENGLISH_STOP_WORDS
    
    corpusSumm = []
    dictionary_Dir = str(dictionary_Dir)
    theFiles = glob.glob((dictionary_Dir+"\*.txt"))
    for files in theFiles:
        with open(files,'r') as paper:
            text = paper.read().lower()
            title,entry = text.split(' ##### ')
        corpusSumm.append(entry)

    corpusSumm.append('inspired by how humans summarize long documents we propose an accurate and fast summarization model that first selects salient sentences and then rewrites them abstractively to generate a concise overall summary. we use a novel sentence level policy gradient method to bridge the non differentiable computation between these two neural networks in a hierarchical way while maintaining language fluency. empirically we achieve the new state of the art on all metrics on the CNN Daily Mail dataset as well as significantly higher abstractiveness scores. Moreover by first operating at the sentence level and then the word level we enable parallel decoding of our neural generative model that results in substantially faster inference speed as well as x faster training convergence than previous long paragraph encoder decoder models. We also demonstrate the generalization of our model on the test only DUC dataset where we achieve higher scores than a state of the art model.')
    cv = CountVectorizer(max_df=.85,stop_words=stop_Words)
    word_count_vector=cv.fit_transform(corpusSumm)
    tfidf_transformer=TfidfTransformer(smooth_idf=True,use_idf=True)
    tfidf_transformer.fit(word_count_vector)

    return cv,tfidf_transformer

#Compress the abstract
def compress(tokenizedDir,cv,tfidf_transformer):
    tokenizedDir = str(tokenizedDir)
    theFiles = glob.glob((tokenizedDir+"\*.txt"))
    feature_names = cv.get_feature_names()
    for files in theFiles:
        with open(files, 'r') as theFile:
            for entry in theFile:
                #Get rid of the title
                title,entry = entry.split(' ##### ')
                #generate tf-idf for the given document
                tf_idf_vector=tfidf_transformer.transform(cv.transform([entry]))
                #sort the tf-idf vectors by descending order of scores
                sorted_items=sort_coo(tf_idf_vector.tocoo())

                #extract only the top n; n here is 10
                keywords=extract_topn_from_vector(feature_names,sorted_items)

                # now print the results
                if title == 'Fast Abstractive Summarization with Reinforce Selected Sentence Rewriting':
                    print("\n=====Title=====")
                    print(title)
                    print("\n=====Body=====")
                    print(entry)
                    print("\n===Keywords===")
                    for k in keywords:
                        print(k,keywords[k])
                #Lists to hold the highest scoring sentences and their scores
                top3_sentences = []
                top3_scores = []
                top3_breakdown = []
                for sentence in entry.split("."):
                    #how many scores are higher in top3 than this sentence, if all 3, delete and replace, otherwise delete lowest
                    higherScores =0
                    sentenceTotal = 0
                    theSentence = []
                    breakdown = []
                    index = 0
                    #keep track of words / sentence to get average score
                    word_count=0
                    for word in sentence.split(" "):
                        #Add up all of the tf_idf scores
                        if word.lower() in keywords:
                            sentenceTotal = sentenceTotal +keywords[word.lower()]
                            breakdown.append(keywords[word.lower()])
                    #Average by word
                        theSentence.append(word.lower())
                        breakdown.append("0")
                        word_count = word_count + 1
                    sentenceTotal = sentenceTotal / word_count
                    min_score = 1000
                    #print (theSentence,sentenceTotal,word_count)
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
                                top3_breakdown.append(breakdown)
                                
                        else:
                            top3_sentences.append(sentence)
                            top3_scores.append(sentenceTotal)
                            top3_breakdown.append(breakdown)
                    else:
                        top3_sentences.append(sentence)
                        top3_scores.append(sentenceTotal)
                        top3_breakdown.append(breakdown)
            theFile.close()

        with open(files, 'w') as theFile:
            theFile.write(title + "\n")
            for sentence in top3_sentences:
                if sentence == '':
                    theFile.write(sentence)
                else:
                    if sentence[0] == ' ':
                        theFile.write(sentence[1:] + "\n")
                    else:
                        theFile.write(sentence +"\n")
            for sentence in top3_breakdown:
                theFile.write("\n")
                for word in sentence:
                    theFile.write(str(word)[:5] + " ")



                     


#Return Abstracts to pass them on to split abstract and the rest, if passed a boolean i.e. True, loop through all categories
def main(category,dictionary_Dir):
    #run query
    if type(category) == bool:
        theFile = Path(AbstractsDir)/'Categories.txt'
        with open(theFile,'r') as categories:
            for category in categories:
                category = category.split(' - ')[0]
                if category != '\n':
                    corpus_All,dates = queryByCat(category)
                    corpus_All.reverse()
                    dates.reverse()
                    for idx, corpusEntry in enumerate(corpus_All):
                        saveTXT(corpusEntry,dates[idx],category)
                    dictionary = tfIDF(dictionary_Dir)
                    for idx,corpusEntry in enumerate(corpus_All):
                        tokenizedPath = Path(AbstractsDir)/ category / dates[idx] / "Tokenized"
                        if not os.path.exists(tokenizedPath):
                            os.makedirs(tokenizedPath)
                        tokenizeText.main(Path(AbstractsDir) / category / dates[idx] ,tokenizedPath)
                        compress(tokenizedPath, dictionary)
                        #print (corpusAbstract)
                        #return corpusEntry
            
    else:
        corpus_All,dates = queryByCat(category)
        corpus_All.reverse()
        dates.reverse()
        for idx, corpusEntry in enumerate(corpus_All):
            saveTXT(corpusEntry,dates[idx],category)
        cv,tfidf_transformer = tfIDF(dictionary_Dir)
        for idx,corpusEntry in enumerate(corpus_All):
            tokenizedPath = Path(AbstractsDir)/ category / dates[idx] / "Tokenized"
            if not os.path.exists(tokenizedPath):
                os.makedirs(tokenizedPath)
            tokenizeText.main(Path(AbstractsDir) / category / dates[idx] ,tokenizedPath)
            compress(tokenizedPath, cv,tfidf_transformer)
            #print (corpusAbstract)
            #return corpusEntry

if __name__ == "__main__":
    #Set location of saved abstracts
    AbstractsDir = r'C:\Users\Al\Documents\ByteSizeArxiv\Abstracts'
    #Set date 
    #TheDate = "2020-06-01"
    #Set category
    #See Categories in Categories.txt, cs.LG = Machine Learning
    #Category = 'cs.LG'
    Category = 'cs.CL'
    dictionary_Dir = Path(r'C:\Users\Al\Documents\ByteSizeArxiv\Abstracts') / Category / "Dictionary"
    main(Category,dictionary_Dir)