#!/usr/bin/python3
from spimi import invert, merge_files
from config import make_pointer

import re
import nltk
import sys
import getopt
import os
import pickle
import math
import shutil

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")
    

# main function
def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """

    # constants
    BLOCK_SIZE = 2      # change this to set block size

    stemmer = nltk.stem.PorterStemmer()
    filename_list = []

    if (in_dir[-1] != '/'):
        in_dir += '/'

    for filename in os.listdir(in_dir):
        filename_list.append(int(filename))
    
    # sort filename before processing data 
    filename_list.sort()        
    
    # invert each block
    num_of_blocks = 0
    files_in_block = 0
    word_list = []

    # INVERTING STAGE
    #
    # output file is in this form:
    # >>> temp_dictionary_{1}_{2}.txt
    # {1} indicates the generation (relevant to merging process)
    # {2} indicates the num of blocks
    for filename in filename_list:
        document = open(in_dir + str(filename), 'r', encoding="utf8")
        word_list += list(map(lambda x: (stemmer.stem(x), int(filename)), nltk.tokenize.word_tokenize(document.read())))
        document.close()
        files_in_block += 1

        # If the number of files scanned has reach block size, then invert first
        if files_in_block == BLOCK_SIZE:
            # print('Inverting block number ' + str(num_of_blocks + 1))
            invert(word_list, 'temp_dictionary_0_' + str(num_of_blocks) + '.txt', 'temp_posting_0_' + str(num_of_blocks) + '.txt')
            num_of_blocks += 1
            files_in_block = 0
            word_list = []
    
    # invert the remaining block
    if (files_in_block != 0):
        # Inverting block number: str(num_of_blocks + 1)
        invert(word_list, 'temp_dictionary_0_' + str(num_of_blocks) + '.txt', 'temp_posting_0_' + str(num_of_blocks) + '.txt')
        num_of_blocks += 1

    
    # MERGING STAGE, binary merging (iterate until height of binary tree)
    for i in range(math.ceil(math.log(num_of_blocks, 2))): 
        # Generation: #i
        k = 0
        for j in range(0, num_of_blocks, 2):
            if j + 1 < num_of_blocks:
                # do the merging process
                # Merging block: j and j+1
                merge_files('temp_dictionary_' + str(i) + '_' + str(j) + '.txt', 'temp_posting_'+str(i) + '_' + str(j) + '.txt',
                            'temp_dictionary_' + str(i) + '_' + str(j+1) + '.txt', 'temp_posting_'+str(i) + '_' + str(j+1) + '.txt',
                            'temp_dictionary_' + str(i+1) + '_' + str(k) + '.txt', 'temp_posting_'+str(i+1) + '_' + str(k) + '.txt')
            else:
                # when the number is odd (left only the last data), copy the final block instead
                # Copying block: j
                shutil.copyfile('temp_dictionary_' + str(i) + '_' + str(j) + '.txt', 'temp_dictionary_' + str(i+1) + '_' + str(k) + '.txt')
                shutil.copyfile('temp_posting_' + str(i) + '_' + str(j) + '.txt', 'temp_posting_' + str(i+1) + '_' + str(k) + '.txt')
                os.remove('temp_dictionary_' + str(i) + '_' + str(j) + '.txt')
                os.remove('temp_posting_' + str(i) + '_' + str(j) + '.txt')            
            k += 1
        num_of_blocks = k

    # put the all posting in the dictionary and dump to a 'temporary final' file
    shutil.copyfile('temp_posting_' + str(i+1) + '_' + str(k-1) + '.txt', 'posting_no_skip_pointer.txt')
    shutil.copyfile('temp_dictionary_' + str(i+1) + '_' + str(k-1) + '.txt', 'dictionary_no_skip_pointer.txt')
    os.remove('temp_posting_' + str(i+1) + '_' + str(k-1) + '.txt')
    os.remove('temp_dictionary_' + str(i+1) + '_' + str(k-1) + '.txt')

    # adding skip pointers, load then dump the dictionary and postings
    dictionary_file = open('dictionary_no_skip_pointer.txt', 'rb')
    posting_file = open('posting_no_skip_pointer.txt', 'rb')
    final_posting_file = open(out_postings, 'wb')
    final_dictionary_file = open(out_dict, 'wb')
    # the following two lines are just for clarity purposes only
    final_posting_file.truncate(0)
    final_dictionary_file.truncate(0)
    dictionary = pickle.load(dictionary_file)

    # dictionary is in the form of: {word: (occurences, postings_pointer), ...}
    for word, data in dictionary.items():
        pointer = data[1]
        posting_file.seek(pointer)
        posting_list = pickle.load(posting_file)
        new_pointer = final_posting_file.tell()
        pickle.dump(make_pointer(posting_list), final_posting_file)
        dictionary[word] = (dictionary[word][0], new_pointer)

    dictionary['ALL POSTING'] = make_pointer(filename_list)     # add to have the full posting list
    pickle.dump(dictionary, final_dictionary_file)

    dictionary_file.close()
    posting_file.close()
    final_dictionary_file.close()
    final_posting_file.close()
    os.remove('dictionary_no_skip_pointer.txt')
    os.remove('posting_no_skip_pointer.txt')


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

print("start indexing...")
build_index(input_directory, output_file_dictionary, output_file_postings)
