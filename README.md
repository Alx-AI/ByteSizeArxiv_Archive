For use downloading, preprocessing, and ideally summarizing arxiv articles as they are posted.

Model compatability checklist:
word2vec - done
extraction labels - done
-------------------------
abstractor - incomplete
extractor - incomplete
full model - incomplete


Use "DL&PP" to download and preprocess 
"tokenizeText" to tokenize
run new make data to pack the tokenized data into jsons within tars
unzip the tars and you are prepared for the original "Train your own models" section here:https://github.com/ChenRocks/fast_abs_rl pasted below
Make sure to change the 'DATA' environmental variable, universal pathing structure under construction



To re-train our best model:

    pretrained a word2vec word embedding

python train_word2vec.py --path=[path/to/word2vec]

    make the pseudo-labels

python make_extraction_labels.py

    train abstractor and extractor using ML objectives

python train_abstractor.py --path=[path/to/abstractor/model] --w2v=[path/to/word2vec/word2vec.128d.226k.bin]
python train_extractor_ml.py --path=[path/to/extractor/model] --w2v=[path/to/word2vec/word2vec.128d.226k.bin]

    train the full RL model

python train_full_rl.py --path=[path/to/save/model] --abs_dir=[path/to/abstractor/model] --ext_dir=[path/to/extractor/model]

After the training finishes you will be able to run the decoding and evaluation following the instructions in the previous section.

The above will use the best hyper-parameters we used in the paper as default. Please refer to the respective source code for options to set the hyper-parameters.
