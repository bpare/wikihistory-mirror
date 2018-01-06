
# Contains all function that involve the full Wikipedia history
#    and forming the model/graph

import argparse
import os
import requests
import codecs
import textProcessor as proc
import networkx as nx
from Patch import PatchSet, PatchModel
import WikiObject

DATA_DIR = 
def applyModel(title, remove):

def getRemlist(title):

def readGraph(title, remove):

def readContent(title, remove):

def readModel(title, remove):

def wiki2graph(title, remove, download, process, new):
    """
        Returns a networkx graph, the content of the latest revision, and the 
            PatchModel for Wikipedia page, title.
        Setting remove to True removes bot reverses and vandalism from the data.
        Setting new to True applies the model whether or not it is cached
    """

    wiki_processor = WikiProcessor(data_dir, title if title != "-a" else None)

    if download:
        wiki_processor.download(force = True)
    else:
        wiki_processor.download()

    if process: 
        wiki_processor.process_dumps(force = True, process_count = 4)
    else:
        wiki_processor.process_dumps(process_count = 4)

    if graphs:
        wiki_processor.generate_graphs(force = True)
    else:
        scores = wiki_processor.generate_graphs()






def parse_args():
    """parse_args parses sys.argv for bulk2graph."""
    # Help Menu
    parser = argparse.ArgumentParser(usage='%prog [options] title')
    parser.add_argument('title', nargs=1, default='-a', help='article title, \'-a\' for all articles')
    parser.add_argument('-r', '--remove',
                      action='store_true', dest='remove', default=False,
                      help='remove mass deletions')
    parser.add_argument('-n', '--new',
                      action='store_true', dest='new', default=False,
                      help='reapply model even if cached')
    parser.add_argument('-d', '--download',
                  action='store_true', dest='download', default=False,
                  help='force download most recent wikipedia version')
    parser.add_argument('-p', '--process',
              action='store_true', dest='process', default=False,
              help='force process wikipedia files')

    n=parser.parse_args()
    
    wiki2graph(n.title[0], n.remove, n.download, n.new)


if __name__ == '__main__':
    parse_args()