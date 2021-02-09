from collections import deque
import nltk
import functools
import pickle

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


def search(query, dict):
    query_queue = query_shunting(query)
    posting_file = open('postings.txt', 'rb')
    operators = ['(', ')', 'NOT', 'AND', 'OR']
    eval_stack = deque([])

    # read out the query_queue
    while len(query_queue) != 0:
        token = query_queue.popleft()
        if token not in operators:
            if token in dict:
                pointer = dict[token][1]
                posting_file.seek(pointer)
                eval_stack.append(pickle.load(posting_file))
            else:
                eval_stack.append([])
        elif token == 'NOT':
            operand = eval_stack.pop()
            eval_stack.append(list(set(dict['ALL POSTING']).difference(operand)))
        elif token == 'AND':
            operand_1 = eval_stack.pop()
            operand_2 = eval_stack.pop()
            eval_stack.append(list(set(operand_1).intersection(operand_2)))
        elif token == 'OR':
            operand_1 = eval_stack.pop()
            operand_2 = eval_stack.pop()
            eval_stack.append(list(set(operand_1).union(operand_2)))
    if len(eval_stack[0]) != 0:
        eval_stack[0].sort()        # since we are using sets, must sort
        return functools.reduce(lambda x, y: str(x) + ' ' + str(y), eval_stack[0], '')
    else:
        return ''
