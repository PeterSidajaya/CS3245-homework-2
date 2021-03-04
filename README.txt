This is the README file for A0184586M and A0170766X submission
E0196721@u.nus.edu and E0313575@u.nus.edu

== Python Version ==

I'm (We're) using Python Version <3.8.7> for this assignment.

== General Notes about this assignment ==

INDEXING

The indexing process is contained in index.py, with spimi.py containing the helper functions.
The process begins with by inverting the documents in blocks which size is determined beforehand.
In each blocks, the documents are indexed into a dictionary and a collection of posting lists, which
is put inside a posting file. The resulting blocks are then merged two by two until one set of
dictionary and posting files are left. Finally, skip pointers are added to the posting lists.

When running the process, make sure that the correct BLOCK_SIZE is set. If it is too small,
the indexing process will take ages. Conversely, if it is too large, the memory might not be able
to handle. A BLOCK_SIZE of 1,000 is a safe bet.

SEARCHING

The searching process is contained in search.py, with query.py containing the helper functions.
In the query process, the queries are first put into the shunting-yard algorithm, which will return
the query as a queue in Reverse Polish Notation (RPN). The queue can then be processed directly,
using set operations. The set operations are also sped up using skip pointers.

POSTING LIST

We implement the posting list using a normal Python list. The format of the elements of the posting list is
(int element, boolean have_skip_pointers, int pointer). pointer will be None if have_skip_pointers is False.

REMARKS

We assume the query to be sensical, e.g., no "AND NOT AND OR NOT".
Operators are case-sensitive ("NOT NOT and OR or" would still work).
github: https://github.com/PeterSidajaya/CS3245-homework-2

== Files included with this submission ==

index.py  : main file for indexing
search.py : main file for searching
spimi.py  : file containing helper functions, mostly for index.py
query.py  : file containing helper functions, mostly for search.py
config.py : file containing even additional helper functions, mostly for skip pointers.

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0184586M and A0170766X, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0184586M and A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason: -

We suggest that we should be graded as follows: -


== References ==

- We tested our code ourselves and also check for correctness of our output 
  based on someone's post in CS3245 piazza: https://github.com/fzdy1914/HW2-Queries
- Schütze, H., Manning, C.D. and Raghavan, P., 2008.
  Introduction to information retrieval (Vol. 39, pp. 234-265). Cambridge: Cambridge University Press.