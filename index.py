#!/usr/bin/python3
import re
import nltk
import sys
import getopt
import os
import pickle

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')

    word_list = []
    stemmer = nltk.stem.PorterStemmer()
    filename_list = []
    dictionary_file = open('dictionary.txt', 'wb')
    posting_file = open('postings.txt', 'wb')

    if (in_dir[-1] != '/'):
        print('missed a trailing slash!')
        in_dir += '/'
    for filename in os.listdir(in_dir):
        filename_list.append(int(filename))
        document = open(in_dir + filename, 'r', encoding="utf8")
        word_list = word_list + list(map(lambda x: (stemmer.stem(x), int(filename)), nltk.tokenize.word_tokenize(document.read())))
        document.close()
    
    word_list.sort()     # sort by word, then by posting
    dictionary = {}
    current_word = ''
    current_list = []
    count = 0

    for word, post in word_list:
        if word != current_word:
            # saves the pointer and saves the posting list to the disk
            pointer = posting_file.tell()
            pickle.dump(current_list, posting_file)
            dictionary[current_word] = (count, pointer)

            current_word = word
            current_list = [post,]
            count = 1
        else:
            if post != current_list[-1]:
                current_list.append(post)
                count += 1
    # for the last word
    pointer = posting_file.tell()
    pickle.dump(current_list, posting_file)
    dictionary[current_word] = (count, pointer)

    # add an additional entry for the full posting
    dictionary['ALL POSTING'] = filename_list
    pickle.dump(dictionary, dictionary_file)
    posting_file.close()
    dictionary_file.close()


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
