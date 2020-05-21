import sys
import os
import hashlib
import subprocess
import collections

import json
import tarfile
import io
import pickle as pkl

dm_single_close_quote = '\u2019' # unicode
dm_double_close_quote = '\u201d' 
dm__fi_unicode='\ufb01'
dm_ffi_unicode='\ufb03'

def convert_txt_json():
	# loop over all story files in directory
	#for file in os.listdir(r'/Users/neerajsudhakar/Documents/ByteSizeArxixv-master/library/toToken/0001004v1.txt'):
    file = r'/Users/neerajsudhakar/Desktop/0001004v1.txt'
    # empty lists for each story
    abstract_lines = list()
    article_lines = list()
    with open(file,'r') as f:
        hashfound = False
        for line in f.readlines():
            line=line.rstrip('\n').replace(dm_single_close_quote, '\'').replace(dm_double_close_quote, '\"').replace(dm__fi_unicode, 'fi').replace(dm_ffi_unicode, 'ffi')
            if line == '#####':
                hashfound = True
            elif hashfound:
                article_lines.append(line)
            else:
                abstract_lines.append(line)
    
    fileid=file.split('/')
    fileid=fileid[len(fileid)-1].replace('.txt', '')
		
    # make json data
    js_example = {}
    js_example['id'] = fileid
    js_example['article'] = article_lines
    js_example['abstract'] = abstract_lines


    with open(file.replace('.txt', '.json') , 'w') as outfile:
        json.dump(js_example, outfile)

#if __name__ == "__main__":
convert_txt_json()