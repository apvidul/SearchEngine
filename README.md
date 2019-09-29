# Search_Engine
Build a basic search engine

A high level view of the steps involved:

1. Data acquisition : First and foremost, we need data to work with. In case of web search, we obtain data through crawler and by accessing a real time stream of documents through document feeds. The obtained data is rarely in plain text and most search engine needs them to be converted to a consistent text plus metadata format. The Document data store is responsible for the storage and retrieval these documents (stored in compressed form for efficiency)

For this project, you would have to do the crawling manually by looking for the complete works of Shakespeare in text format or you could drop me an email requesting for the tokenized dataset of the same in JSON format. This dataset has been preprocessed by stripping out punctuation and stemmed using the Krovetz Stemmer. In our analogy, we would be considering the scenes in Shakespeare’s play as our documents. We would be using the term scene and document interchangeably.

Now once we have the data, what’s the next step?

To determine the next step, we need to know what we are going to build exactly. Remember we talked about something called Indexing process. To search the data in hand, we need an efficient data structure for fast search and retrieval. This is where inverted index comes into play. Inverted index in simple terms is something like the index you find in the back of a textbook.

The book index contains a set of words arranged in alphabetical order followed by a list of page numbers where that word can be found. This makes it easier for us to look up information regarding a particular term. We build our indexer in a similar way. For every word we encounter in a scene, we store it in a hash table along with a scene_id/document_id and its positional information (what position in the scene is the word located). Usually we consider words as a part of a document, here we are considering document/scene being associated with words. Hence the name inverted index. Now lets proceed as we know what to do with the text data in hand.

2. Transforming the text: Parse the data and Tokenize it. Tokenization is the process of breaking up a sequence of strings into individual elements such as words, keywords, phrases, symbols. Both the document and query text are transformed into tokens in the same manner so that they can be easily compared. The following code snippet shows how Tokenization is done with our dataset.

The dataset we have is already clean and all you need is to split the text on whitespace and we will have the list of words for each scene.

To make the indexer more efficient, we can do things like stop word removal. These are the words that are found in almost all documents like a, the, at, to etc and removing them makes the indexer size smaller and processing smaller number of documents. But you must be extra careful because there are queries like ‘to be or not to be’ which can end up being a blank query if you do too much of stop word removal. You can also do stemming  which is basically grouping words that are derived from a common stem like ‘fish’, ‘fishes’ and ‘fishing’ and replacing an exiting word in a query with another one from the group (all having the same root) inorder to maximize the matching of a query and a document. Case normalization, Link extraction and analysis (links are analyzed to find the popularity of the page), information extraction etc are other techniques that are used to improve the efficiency of the indexer. You can try implementing this and see how the indexer performs.

3. Building the Indexer

For each document/scene, assign an integer identifier which would serve as the document_id/doc_id
For each token/word, we keep track of what it position it is at in the document (the first word is at position 1).
Check if we have seen the word before, if not create a new list with the word as its index and add that token with its position and its document identifier to the list (The doc_id and position is coupled together in another list).  This outer list containing the list with doc_id and position is called the inverted list
If we have seen the word before, extract the first list from the inverted list. Check if the first element of the extracted list (doc_id) is the same as the document_id we are working on right now. If yes, append the position of the word to the inner list. Else, create a new list with the doc_id and the word position and append it to the outer list (inverted list). If this is difficult to follow, please refer to the format of the indexer given below. You can also try running the python code to make things clearer.
Based on the implementation, we may pass down more information (metadata) into the inverted list (like the number of occurrence of a word in a document, total number of occurrences of each word in the entire collection, total number of words etc). Alternatively a file can be saved with metadata like term statistics and collection statistics.

The indexer was implemented using a dictionary in python and it takes the following format.


{ 
word1 : [  [doc_id,pos1,pos2] , [doc_id,pos1,pos2].....[doc_id, pos1 pos2] ] 
 
word2 : [  [doc_id,pos1,pos2] , [doc_id,pos1,pos2].....[doc_id, pos1 pos2] ] 
.
.
.
 } 
Now suppose we have a 3 word query. For each word, we would use the indexer to lookup the scenes/documents containing the words. We would find the list of document_ids that are common to all three words, retrieve them and display it to the user. This is a naive implementation of an indexer.

4. Write the inverted list to disk We may choose to compress our data (Delta encoding and decoding with Vbyte compression). In practical scenarios, we cant keep the entire indexer in the memory. Instead, saving it to the disk after compression is the viable option. You can use the following code for delta encoding. Its really simple if you want to implement it. If you consider the document_ids and word positions within a particular document, they are in ascending order because that is the way we stored it. lets say it’s in the following form

1, 5, 9, 18, 23, 24, 30, 44, 45, 48

Since they are in order, we could find the difference between the adjacent items and store them. See how small the encoded numbers are below

1, 4, 4, 9, 5, 1, 6, 14, 1, 3

To find the initial numbers, we start from the first doc_id or word (whatever you have decided to encode) =1. We know that the second number is 4 more than the first element, so the 2nd element = 1 + 4 =5. And we know that the third element is 4 more than the second element, that is 5 + 4 =9. See how we are generating the first list (1,5,9..)? We keep doing this till the end of the list. This encoding is simple and saves a lot of space

This is the end of indexing process. Now we can extract all the documents containing any of the query words. However, we need to present them to the user in a particular order with the first result being the most relevant and the second being the next best result and so on. Further in a practical sense there would be millions of documents containing the query words. So there is a definite need for a ranking algorithm to rank the documents based on their relevance to the query. This ranking or equivalently scoring component is called query processing.

5. Scoring

Now what would be a good method? One approach is to select those documents containing all the terms in the query. This is called Boolean Retrieval. But all documents retrieved have equal relevance and there can be millions of them as well. Another approach is to count the number of query terms in each document and rank accordingly. This again we would face the same problem and its easy to fool this ranking algorithm (A document with only the query words will always make it to the top). A much better model will be the Vector Space Model which also has the advantage of being simple and intuitively appealing framework for implementing things like term weighting, ranking and relevance feedback.


