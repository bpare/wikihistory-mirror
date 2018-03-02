#!/usr/bin/python


# Contains all function that involve the full Wikipedia history
#    and forming the model/graph

import argparse
import os
import textProcessor as proc
import networkx as nx
from pymongo import MongoClient
from Patch import PatchSet, PatchModel

##
# Wiki options
WIKI = 'https://en.wikipedia.org/'
LIMIT='1000'



def applyModel(title, remove):
    """
        Applies PatchModel to the history for Wikipedia page, title.
        Returns the full history tranformed into a graph according to the model,
            the PatchModel, and the most recent content.
    """

    title=title.replace(" ", "_")

    # Make folders for model, graph, and content files
    if not os.path.isdir('GMLs'):
        os.mkdir('GMLs')
    if not os.path.isdir('models'):
        os.mkdir('models')
    if not os.path.isdir('content'):
        os.mkdir('content')

    print "Setting up distance comparison . . ."
    
    #TODO find a way of confirming that there's stuff in the db
    if not os.path.isdir("full_histories") or not os.path.isdir('full_histories/'+title):
        proc.cleanCorpus(title)

    # Set up semantic distance comparison
    if not os.path.isdir("dictionaries") or not os.path.isfile('dictionaries/'+title+'.dict'):
        dictionary = proc.saveAndReturnDictionary(title)
    else:
        dictionary = proc.readDictionary(title)
    
    #TODO do we need to save dictionary/corpus?
    if not os.path.isdir("corpus") or not os.path.isfile('corpus/'+title+'.mm'):
        corpus = proc.saveAndReturnCorpus(title, dictionary)
    else:
        corpus = proc.readCorpus(title)
    
    if not os.path.isdir("tfidf") or not os.path.isfile('tfidf/'+title+'.tfidf'):
        tfidf = proc.saveAndReturnTfidf(title, corpus, True)
    else:
        tfidf = proc.loadTfidf(title)

    if not os.path.isdir("lsi") or not os.path.isfile('lsi/'+title+'.lsi'):
        lsi = proc.saveAndReturnLsi(title, tfidf, corpus, dictionary, 300)
    else:
        lsi = proc.loadLsi(title)


    # Get the list of vertices to remove
    if remove:
        remList = proc.getRemlist(title)
       

    print "Applying model . . ."

    model = PatchModel()
    prev = ""
    pid=0
    wikiit=proc.WikiIter(title)
    prev_index = None
    set_id = 0

    for (rvid, timestamp, content) in wikiit.__iter__():
       
        # Apply to the PatchModel and write dependencies to graph.
        if remove and rvid in remList:
            remList.remove(rvid)
    
        else:
            # Get semantic distance
            sims, prev_index = proc.scoreDoc(title, prev_index, content, dictionary, tfidf, lsi)
            
            dists = [1-sim for sim in sims]
            # Apply PatchModel
            #content=content.encode("ascii", "replace")
            content_split=content.split()
            prev_split=prev.split()
            ps = PatchSet.psdiff(pid, set_id, prev_split, content_split)
            pid+=len(ps.patches)
            set_id += 1
            for p in ps.patches:
                model.apply_patch(p, timestamp, dists) #list of out-edges from rev
            
            prev = content
        
    if remove:
        cachefile = title.replace(" ", "_")+'_rem.txt'
    else:
        cachefile = title.replace(" ", "_")+'.txt'

    # Writes graph to file
    nx.write_gml(model.graph, "GMLs/"+cachefile)
        
    # Write model to file
    modelFile = open("models/"+ cachefile, "w")
    line = ""
    for patch in model.model:
        line+= str(patch[0])+' '+str(patch[1])+'\n'
    modelFile.write(line)
    modelFile.close()

    # Write content to file
    contentFile = open("content/"+ cachefile, "w")
    contentFile.write(content)
    contentFile.close()
    
    return model.graph, content, model.model








def readGraph(title, remove):
    """
        Reads a networkx graph from a file for Wikipedia page, title, with
            remove 
    """
    print "Reading graph . . ."
    if remove:
        file = "GMLs/" + title.replace(" ", "_")+'_rem.txt'
    else:
        file = "GMLs/" + title.replace(" ", "_")+'.txt'

    assert os.path.isfile(file), "Graph file does not exist."

    return nx.read_gml(file, label='id')




def readContent(title, remove):
    """
        Reads and returns a string from a file
    """
    print "Reading content . . ."

    if remove:
        file = "content/"+title.replace(" ", "_")+"_rem.txt"
    else:
        file = "content/"+title.replace(" ", "_")+".txt"

    assert os.path.isfile(file), "Content file does not exist."

    contentFile = open(file, "r")
    content = ""
    for line in contentFile:
        content+=line
    contentFile.close()
    return content




def readModel(title, remove):
    """
        Reads and returns a PatchModel from a file
    """
    print "Reading model . . ."
    if remove:
        file = "models/"+title.replace(" ", "_")+"_rem.txt"
    else:
        file = "models/"+title.replace(" ", "_")+".txt"

    assert os.path.isfile(file), "Model file does not exist."

    modelFile = open(file, "r")
    model=[]

    # Read model
    for line in modelFile:
        line=line.split()
        model.append((int(line[0]), int(line[1])))
    modelFile.close()
    return model




def wiki2graph(title, remove, new):
    """
        Returns a networkx graph, the content of the latest revision, and the 
            PatchModel for Wikipedia page, title.
        Setting remove to True removes bot reverses and vandalism from the data.
        Setting new to True applies the model whether or not it is cached
    """
    if remove:
        file = title.replace(" ", "_")+"_rem.txt"
    else:
        file = title.replace(" ", "_")+".txt"

    # Check if files exist to avoid reapplying model
    if not new and \
        os.path.isdir('GMLs') and os.path.isfile("GMLs/"+file) and \
        os.path.isdir('content') and os.path.isfile("content/"+file) and \
        os.path.isdir('models/') and os.path.isfile("models/"+file):

        graph = readGraph(title, remove)
        content = readContent(title, remove)
        model = readModel(title, remove)


    # Apply model. Download full history if necessary
    else:
        if not os.path.isdir('full_histories') or not os.path.isdir("full_histories/"+title.replace(' ', '_')):
            proc.downloadAndExtractHistory(title)
        (graph, content, model) = applyModel(title, remove)

    return graph, content, model





def parse_args():
    """parse_args parses sys.argv for wiki2graph."""
    # Help Menu
    parser = argparse.ArgumentParser(usage='%prog [options] title')
    parser.add_argument('title', nargs=1)
    parser.add_argument('-r', '--remove',
                      action='store_true', dest='remove', default=False,
                      help='remove mass deletions')
    parser.add_argument('-n', '--new',
                      action='store_true', dest='new', default=False,
                      help='reapply model even if cached')

    n=parser.parse_args()

    wiki2graph(n.title[0], n.remove, n.new)


if __name__ == '__main__':
    parse_args()
