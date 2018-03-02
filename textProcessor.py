#!/usr/bin/python

import gensim
import os
import codecs
import requests
import wiki_extractor
from pymongo import MongoClient

##
# Mongo options
HOST = 'localhost'
PORT = 27017
DB_NAME = 'wikihistory_db'

##
# Wiki options
WIKI = 'https://en.wikipedia.org/'
LIMIT='1000'

class WikiIter(object):

    def __init__(self, title, for_remlist = False):
        self.title = title
        self.for_remlist = for_remlist

    def __iter__(self):
        mongo_collection = MongoClient(HOST, PORT)[DB_NAME][self.title]
        if self.for_remlist:
            cursor = mongo_collection.find({}, {'_id': 1, 'parentid':1, 'comment': 1})
            for item in cursor:
                yield item['_id'].encode('utf-8'), item['parentid'].encode('utf-8'), item['comment'].encode('utf-8')
        else:
            cursor = mongo_collection.find({}, {'_id': 1, 'timestamp':1, 'text': 1}).sort([('timestamp', 1)])
            #.sort([('_id', 1)])
            for item in cursor:
                yield item['_id'].encode('utf-8'), item['timestamp'].encode('utf-8'), item['text'].encode('utf-8')
        

class MyCorpus(object):
    def __init__(self, wikiiter, dictionary):
        self.wikiiter=wikiiter
        self.dictionary=dictionary
    def __iter__(self):
        for (rvid, time, doc) in self.wikiiter:
            yield self.dictionary.doc2bow(doc.split())


def cleanCorpus(title):
    mongo_collection = MongoClient(HOST, PORT)[DB_NAME][title]
    mongo_collection.remove({})

    for filename in os.listdir('full_histories/'+title):
        wiki_extractor.process_dump('full_histories/'+title+'/'+filename, \
                                    None, None)
    

def downloadAndExtractHistory(title):
    """
        Downloads the full history of Wikipedia page, title, into
            full_histories
    """
    print "Downloading . . ."

    mongo_collection = MongoClient(HOST, PORT)[DB_NAME][title]
    mongo_collection.remove({})
    mongo_collection.create_index('timestamp')
    offset='0'
    prev_offset=None
    i=0
    while offset!=prev_offset:
        print "Starting set " + str(i) + " . . ."
        i+=1
        downloadAndExtractFile(title, offset)
        prev_offset = offset
        offset = mongo_collection.find_one(sort=[("timestamp", -1)])['timestamp'].encode('utf-8')


def downloadAndExtractFile(title, offset):
    title=title.replace(' ', '_')
    api = WIKI+ 'w/index.php?title=Special:Export&pages=' + title + \
                '&offset='+offset+'&limit='+LIMIT+'&action=submit'

    # Set up folder for the new history, if needed
    if not os.path.isdir('full_histories'):
        os.mkdir('full_histories')
    if not os.path.isdir('full_histories/'+title):
        os.mkdir('full_histories/'+title)
    
    cachefile = 'full_histories/'+ title+'/'+title+'|'+offset+'.xml'
    file = open(cachefile, "w")

    # Download and save history
    r=requests.post(api, data="")
    file=codecs.open(cachefile, "w", "utf-8")
    file.write(r.text)
    file.close()

    wiki_extractor.process_dump(cachefile, None, None)


def saveAndReturnDictionary(title):
    """
    """
    if not os.path.isdir('dictionaries'):
        os.mkdir('dictionaries')

    wiki = WikiIter(title)
    dictionary=gensim.corpora.Dictionary(content.lower().split() 
            for (rvid, timestamp, content) in wiki.__iter__())
    stoplist=set('for a of the and to in'.split())

    stop_ids=[dictionary.token2id[stopword] for stopword in stoplist 
                if stopword in dictionary.token2id]
    once_ids=[tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq==1]
    dictionary.filter_tokens(stop_ids+once_ids)
    dictionary.compactify()

    title=title.replace(" ", "_")
    file='dictionaries/'+title+'.dict'
    dictionary.save(file)
    return dictionary 


def readDictionary(title):
    """Loads the gensim dictionary of title
    """
    title=title.replace(" ", "_")
    file='dictionaries/'+title+'.dict'
    if not os.path.isdir('dictionaries') or not os.path.isfile(file):
        print "File does not exist"
        return
    return gensim.corpora.Dictionary.load(file)


def saveAndReturnCorpus(title, dictionary):
    """Creates a corpus using the edit history of a page
    """
    if not os.path.isdir('corpus'):
        os.mkdir('corpus')

    wiki = WikiIter(title)

    corpus=MyCorpus(wiki.__iter__(), dictionary)
    file='corpus/' + title.replace(" ", "_")+'.mm'
    gensim.corpora.MmCorpus.serialize(file, corpus)
    return corpus


def readCorpus(title):
    """
    """
    file='corpus/' + title.replace(" ", "_")+'.mm'
    if not os.path.isdir('corpus') or not os.path.isfile(file):
        print "File does not exist."
        return
    return gensim.corpora.MmCorpus(file)


def saveAndReturnTfidf(title, bow_corpus, normalize):
    """
    """
    tfidf_model=gensim.models.TfidfModel(bow_corpus, normalize)
    if not os.path.isdir('tfidf'):
        os.mkdir('tfidf')
    file='tfidf/' + title.replace(" ", "_")+'.tfidf'
    tfidf_model.save(file)
    return tfidf_model


def loadTfidf(title):
    """
    """
    file='tfidf/' + title.replace(" ", "_")+'.tfidf'
    if not os.path.isdir('tfidf') or not os.path.isfile(file):
        print "File does not exist."
        return
    return gensim.models.TfidfModel.load(file)


def saveAndReturnLsi(title, tfidf, corpus, id2word, num_topics):
    """
    """
    lsi_model=gensim.models.LsiModel(tfidf[corpus], id2word=id2word, num_topics=num_topics)
    if not os.path.isdir('lsi'):
        os.mkdir('lsi')
    file='lsi/' + title.replace(" ", "_")+'.lsi'
    lsi_model.save(file)
    return lsi_model

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

def getRemlist(title):
    """
        Gets a list of ids of revisions that are bot reverts
        or that were reverted by bots
    """
    print "Removing bot rv."
    remList = []
    title=title.replace(" ", "_")
    
    wiki = WikiIter(title, for_remlist = True)

    for rvid, parentid, comment in wiki.__iter__():
        if 'BOT - rv' in comment:
            remList.append(rvid)
            remList.append(parentid)

    return remList
