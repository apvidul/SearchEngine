# Search_Engine
Build a basic search engine

A high level view of the steps involved:

1. Data acquisition : First and foremost, we need data to work with. In case of web search, we obtain data through crawler and by accessing a real time stream of documents through document feeds. The obtained data is rarely in plain text and most search engine needs them to be converted to a consistent text plus metadata format. The Document data store is responsible for the storage and retrieval these documents (stored in compressed form for efficiency)

For our project, you would have to do the crawling manually by looking for the complete works of Shakespeare in text format for download or you could drop me an email requesting for the tokenized dataset of the same in JSON format. This dataset has been preprocessed by stripping out punctuation and stemmed using the Krovetz Stemmer. In our analogy, we would be considering the scenes in Shakespeare’s play as our documents. We would be using the term scene and document interchangeably. Here is how a scene would look like in my dataset.
