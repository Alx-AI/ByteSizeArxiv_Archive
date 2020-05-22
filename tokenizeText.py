import sys
import os
os.environ['CLASSPATH'] = (r"C:\Users\Al\corenlp/*")
os.environ['JAVA_HOME'] = (r'C:\Program Files\Java\jdk-14.0.1')
import hashlib
import subprocess
import collections

import json
import tarfile
import io
import pickle as pkl
import time
start_time= time.time()

def tokenize_stories(textDir, tokedPapers):
    """Maps a whole directory of .story files to a tokenized version using
       Stanford CoreNLP Tokenizer
    """
    print("Preparing to tokenize {} to {}...".format(textDir,
                                                     tokedPapers))
    papers = os.listdir(textDir)
    # make IO list file
    print("Making list of files to tokenize...")
    with open("mapping.txt", "w") as f:
        for p in papers:
            f.write(
                "{} \t {}\n".format(
                    os.path.join(textDir, p),
                    os.path.join(tokedPapers, p)
                )
            )
    command = ['java', 'edu.stanford.nlp.process.PTBTokenizer',
               '-ioFileList', '-preserveLines', 'mapping.txt']
    print("Tokenizing {} files in {} and saving in {}...".format(
        len(papers), textDir, tokedPapers))
    subprocess.call('java -Xmx1g edu.stanford.nlp.pipeline.StanfordCoreNLP')
    subprocess.call(command)
    print("Stanford CoreNLP Tokenizer has finished.")
    #os.remove("mapping.txt")

    # Check that the tokenized stories directory contains the same number of
    # files as the original directory
    num_orig = len(os.listdir(textDir))
    num_tokenized = len(os.listdir(tokedPapers))
    if num_orig != num_tokenized:
        raise Exception(
            "The tokenized stories directory {} contains {} files, but it "
            "should contain the same number as {} (which has {} files). Was"
            " there an error during tokenization?".format(
                tokedPapers, num_tokenized, textDir, num_orig)
        )
    print("Successfully finished tokenizing {} to {}.\n".format(
        textDir, tokedPapers))


def main():
    textDir = r'C:\Users\Al\Documents\ByteSizeArxiv\library'
    tokenizedDir = r'C:\Users\Al\Documents\ByteSizeArxiv\library\toked'
    tokenize_stories(textDir,tokenizedDir)

if __name__ == "__main__":
    main()
    print(time.time()-start_time)