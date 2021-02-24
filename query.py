from collections import deque
from config import make_pointer
import nltk
import functools
import pickle
import math

def query_shunting(query):
    stemmer = nltk.stem.PorterStemmer()
    operators = {'AND', 'OR', 'NOT'}
    brackets = {'(', ')'}
    output_queue, operator_stack = deque([]), deque([])
    query = deque(query.split())
    while query:
        token = query.popleft()

        # separate the brackets from the word
        if token[0] == '(':
            query.appendleft(token[1:])
            token = '('
        elif token != ')' and token[-1] == ')':
            query.appendleft(')')
            token = token[:-1]
        
        # print()
        # print("TOKEN:", token, "QUERY:", query)
        # print("OUT:", output_queue, "OPER:", operator_stack)
        # print()
        # shunting-yard algortihm, see wikipedia for full (note that NOT is right-associative unary operator)
        if (token not in operators) and (token not in brackets):
            output_queue.append(stemmer.stem(token))
        elif token in operators:
            while ((len(operator_stack) != 0) and
                (precedence(operator_stack[0], token)) and
                (operator_stack[0] != '(')):
                output_queue.append(operator_stack.popleft())
            operator_stack.appendleft(token)
        elif token == '(':
            operator_stack.appendleft(token)
        elif token == ')':
            while (operator_stack[0] != '('):
                output_queue.append(operator_stack.popleft())
            if (operator_stack[0] == '('):
                operator_stack.popleft()
    while (len(operator_stack) != 0):
        output_queue.append(operator_stack.popleft())
    return output_queue


def precedence(op1, op2):
    operators = ['(', ')', 'NOT', 'AND', 'OR']
    return operators.index(op1) < operators.index(op2)


def get_intersection(left, right):
    # left/right : [(1, True, 2), (5, False, None), (8, True, 4), (9, False, None),
    #               (10, True, 6), (13, False, None), (15, False, None)]

    left_pointer = 0
    right_pointer = 0

    result = []

    while (left_pointer < len(left) and right_pointer < len(right)):
        # print("===============")
        # print("LEFT_POINT:", left_pointer, "\nLEFT:", left)
        # print("RIGHT_POINT:", right_pointer, "\nRIGHT:", right)
        # print("===============")
        if (left[left_pointer][0] == right[right_pointer][0]):
            result.append(left[left_pointer][0])
            left_pointer += 1
            right_pointer += 1
        elif (left[left_pointer][0] < right[right_pointer][0]):
            if (left[left_pointer][1] and
                left[left[left_pointer][2]][0] <= right[right_pointer][0]):
                while (left[left_pointer][1] and
                       left[left[left_pointer][2]][0] <= right[right_pointer][0]):
                    left_pointer = left[left_pointer][2]
                continue

            left_pointer += 1
        else:
            if (right[right_pointer][1] and
                right[right[right_pointer][2]][0] <= left[left_pointer][0]):
                while (right[right_pointer][1] and
                       right[right[right_pointer][2]][0] <= left[left_pointer][0]):
                    right_pointer = right[right_pointer][2]
                continue

            right_pointer += 1

    return result


def get_union(left, right):
    get_left_val = [i for i, j, k in left]
    get_right_val = [i for i, j, k in right]

    return list(set(get_left_val).union(get_right_val))
    

def search(query, new_dict, postings_file):
    query_queue = query_shunting(query)
    posting_file = open(postings_file, 'rb')
    operators = ['(', ')', 'NOT', 'AND', 'OR']
    eval_stack = deque([])

    # read out the query_queue
    while len(query_queue) != 0:
        token = query_queue.popleft()
        if token not in operators:
            if token in new_dict:
                pointer = new_dict[token][1]
                posting_file.seek(pointer)
                eval_stack.append(pickle.load(posting_file))
            else:
                eval_stack.append([])
        elif token == 'NOT':
            operand = eval_stack.pop()
            list_diff = list(set(new_dict['ALL POSTING']).difference(operand))
            eval_stack.append(make_pointer(list_diff))
        elif token == 'AND':
            operand_1 = eval_stack.pop()
            operand_2 = eval_stack.pop()
            intersect = get_intersection(operand_1, operand_2)
            eval_stack.append(make_pointer(intersect))
        elif token == 'OR':
            operand_1 = eval_stack.pop()
            operand_2 = eval_stack.pop()
            eval_stack.append(make_pointer(get_union(operand_1, operand_2)))

    if len(eval_stack[0]) != 0:
        get_val = sorted([i for i, j, k in eval_stack[0]])
        print("RESULT:", get_val)
        return " ".join([str(i) for i in get_val])
    else:
        return ''
