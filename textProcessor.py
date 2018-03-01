#!/usr/bin/python

import gensim
import os
import codecs
import wiki_extractor
from pymongo import MongoClient

##
# Mongo options
HOST = 'localhost'
PORT = 27017
DB_NAME = 'wikihistory_db'

class WikiIter(object):

    def __iter__(self, title):
        mongo_collection = MongoClient(HOST, PORT)[DB_NAME][title]
        cursor = mongo_collection.find({}, {_id: 1, timestamp:1, text: 1}).noCursorTimeout()
        for item in cursor:
            yield item['_id'], item['timestamp'], item['text']
        

class MyCorpus(object):
    def __init__(self, wikiiter, dictionary):
        self.wikiiter=wikiiter
        self.dictionary=dictionary
    def __iter__(self):
        for (rvid, time, doc) in self.wikiiter:
            yield self.dictionary.doc2bow(doc.split())


def cleanCorpus(title):
    mongo_collection = MongoClient(HOST, PORT)[DB_NAME][title]
    wiki_extractor.process_dump('full_histories/'+title+'/'+title+'.xml', \
                                None, None, mongo_collection)


def saveDictionary(title):
    """
    """
    if not os.path.isdir('dictionaries'):
        os.mkdir('dictionaries')

    wiki = WikiIter()
    dictionary=gensim.corpora.Dictionary(content.lower().split() 
            for (rvid, timestamp, content) in wiki.__iter__(title))
    stoplist=set('for a of the and to in'.split())

    stop_ids=[dictionary.token2id[stopword] for stopword in stoplist 
                if stopword in dictionary.token2id]
    once_ids=[tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq==1]
    dictionary.filter_tokens(stop_ids+once_ids)
    dictionary.compactify()

    title=title.replace(" ", "_")
    file='dictionaries/'+title+'.dict'
    dictionary.save(file)


def readDictionary(title):
    """Loads the gensim dictionary of title
    """
    title=title.replace(" ", "_")
    file='dictionaries/'+title+'.dict'
    if not os.path.isdir('dictionaries') or not os.path.isfile(file):
        print "File does not exist"
        return
    return gensim.corpora.Dictionary.load(file)



def saveCorpus(title, dictionary):
    """Creates a corpus using the edit history of a page
    """
    if not os.path.isdir('corpus'):
        os.mkdir('corpus')

    wiki = WikiIter()

    corpus=MyCorpus(wiki.__iter__(title), dictionary)
    file='corpus/' + title.replace(" ", "_")+'.mm'
    gensim.corpora.MmCorpus.serialize(file, corpus)

def readCorpus(title):
    """
    """
    file='corpus/' + title.replace(" ", "_")+'.mm'
    if not os.path.isdir('corpus') or not os.path.isfile(file):
        print "File does not exist."
        return
    return gensim.corpora.MmCorpus(file)


def saveTfidf(title, bow_corpus, normalize):
    """
    """
    tfidf_model=gensim.models.TfidfModel(bow_corpus, normalize)
    if not os.path.isdir('tfidf'):
        os.mkdir('tfidf')
    file='tfidf/' + title.replace(" ", "_")+'.tfidf'
    tfidf_model.save(file)

def loadTfidf(title):
    """
    """
    file='tfidf/' + title.replace(" ", "_")+'.tfidf'
    if not os.path.isdir('tfidf') or not os.path.isfile(file):
        print "File does not exist."
        return
    return gensim.models.TfidfModel.load(file)

def saveLsi(title, tfidf, corpus, id2word, num_topics):
    """
    """
    tfidf_model=gensim.models.LsiModel(tfidf[corpus], id2word=id2word, num_topics=num_topics)
    if not os.path.isdir('lsi'):
        os.mkdir('lsi')
    file='lsi/' + title.replace(" ", "_")+'.lsi'
    tfidf_model.save(file)

def loadLsi(title):
    """
    """
    file='lsi/' + title.replace(" ", "_")+'.lsi'
    if not os.path.isdir('lsi') or not os.path.isfile(file):
        print "File does not exist."
        return
    return gensim.models.LsiModel.load(file)


def scoreDoc(title, prev_index, doc, dictionary, tfidf, lsi):
    """
    """
    if prev_index is None:
        index_bow=[dictionary.doc2bow([""])]
        lsi_index=lsi[tfidf[index_bow]]
        if not os.path.isdir('indexes'):
            os.mkdir('indexes')
        # index has to be a corpus, does not have to be the training corpus
        prev_index=gensim.similarities.Similarity('indexes/'+title, lsi_index, 300)

    title=title.replace(" ", "_")
    # use 200-500 topics for tfidf
    doc_bow=dictionary.doc2bow(doc.lower().split())
    lsi_doc=lsi[tfidf[doc_bow]]

    sims=prev_index[lsi_doc]
    prev_index.add_documents([lsi_doc])
    return sims, prev_index

